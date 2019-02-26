from collections import deque
from Arena import Arena
from MCTS import MCTS
import numpy as np
from pytorch_classification.utils import Bar, AverageMeter
import time, os, sys
from pickle import Pickler, Unpickler
from random import shuffle
import copy


class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """
    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.mcts = MCTS(self.game, self.nnet, self.args)
        self.trainExamplesHistory = []    # history of examples from args.numItersForTrainExamplesHistory latest iterations

    def executeEpisode(self):
        """
        This function executes one episode of self-play, starting with player 1.
        As the game is played, each turn is added as a training example to
        trainExamples. The game is played till the game ends. After the game
        ends, the outcome of the game is used to assign values to each example
        in trainExamples.

        It uses a temp=1 if episodeStep < tempThreshold, and thereafter
        uses temp=0.

        Returns:
            trainExamples: a list of examples of the form (canonicalBoard,pi,v)
                           pi is the MCTS informed policy vector, v is +1 if
                           the player eventually won the game, else -1.
        """
        trainExamples = []
        board = self.game.getInitBoard()
        curPlayer = 1
        episodeStep = 0

        while True:
            episodeStep += 1
            canonicalBoard = self.game.getCanonicalForm(board,curPlayer)
            # print("canonicalBoard", canonicalBoard)
            temp = int(episodeStep < self.args["tempThreshold"])

            pi = self.mcts.getActionProb(canonicalBoard, temp=temp)
            sym = self.game.getSymmetries(canonicalBoard, pi)
            for b,p in sym:
                trainExamples.append([b, curPlayer, p, None])

            action = np.random.choice(len(pi), p=pi)
            board, curPlayer = self.game.getNextState(board, curPlayer, action)
            # print("board", board)

            r = self.game.getGameEnded(board, curPlayer)

            if r!=0:
                return [(x[0],x[2],r*((-1)**(x[1]!=curPlayer))) for x in trainExamples]

    def gen_samples(self, iteration):
            print('------ITER ' + str(iteration) + '------')
        
            iterationTrainExamples = deque([], maxlen=self.args["maxlenOfQueue"])
            eps_time = AverageMeter()
            bar = Bar('Self Play', max=self.args["numEps"])
            end = time.time()

            for eps in range(self.args["numEps"]):
                self.mcts = MCTS(self.game, self.nnet, self.args)   # reset search tree

                iterationTrainExamples += self.executeEpisode()
    
                # bookkeeping + plot progress
                eps_time.update(time.time() - end)
                end = time.time()
                bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=self.args["numEps"], et=eps_time.avg,
                                                                                                               total=bar.elapsed_td, eta=bar.eta_td)
                bar.next()
            bar.finish()

            # save the iteration examples to the history 
            self.trainExamplesHistory.append(iterationTrainExamples)

            if len(self.trainExamplesHistory) > self.args["numItersForTrainExamplesHistory"]:
                print("len(trainExamplesHistory) =", len(self.trainExamplesHistory), " => remove the oldest trainExamples")
                self.trainExamplesHistory.pop(0)
            self.saveTrainExamples(iteration-1)

    def fit(self, iteration):
        trainExamples = []
        for e in self.trainExamplesHistory:
            trainExamples.extend(e)
        shuffle(trainExamples)

        # training new network, keeping a copy of the old one
        self.nnet.save_checkpoint(folder=self.args["checkpoint"], filename='checkpoint_%d.pth.tar.prev' % iteration)
        self.nnet.train(trainExamples)
        self.nnet.save_checkpoint(folder=self.args["checkpoint"], filename='checkpoint_%d.pth.tar.next' % iteration)
    

    def pit(self, iteration):
        self.pnet = self.nnet.__class__(self.game)  # the competitor network
        self.pnet.load_checkpoint(folder=self.args["checkpoint"], filename="checkpoint_%d.pth.tar.prev" % iteration)

        pmcts = MCTS(self.game, self.pnet, self.args)
        nmcts = MCTS(self.game, self.nnet, self.args)
        
        print('PITTING AGAINST PREVIOUS VERSION')
        
        arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=0)),
                      lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), self.game)
        pwins, nwins, draws = arena.playGames(self.args["arenaCompare"])

        print('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
        if pwins+nwins == 0 or float(nwins)/(pwins+nwins) < self.args["updateThreshold"]:
            print('REJECTING NEW MODEL')
            self.pnet.save_checkpoint(folder=self.args["checkpoint"], filename="checkpoint_%d.pth.tar" % iteration)
        else:
            print('ACCEPTING NEW MODEL')
            self.nnet.save_checkpoint(folder=self.args["checkpoint"], filename="checkpoint_%d.pth.tar" % iteration)
            self.nnet.save_checkpoint(folder=self.args["checkpoint"], filename='best.pth.tar')                


    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args["checkpoint"]
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration)+".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)

    def loadTrainExamples(self, iteration):
        modelFile = os.path.join(self.args["checkpoint"], "checkpoint_%d.pth.tar" % iteration)
        examplesFile = modelFile+".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Exiting")
            sys.exit()
        else:
            print("File with trainExamples found. Read it.")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
