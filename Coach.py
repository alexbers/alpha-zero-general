import time
import os
import sys
import copy
from pickle import Pickler, Unpickler
from random import shuffle

import numpy as np

from collections import deque
from Arena import Arena
from MCTS import MCTS
from pytorch_classification.utils import Bar, AverageMeter

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

            valids = self.game.getValidMoves(canonicalBoard, 1)
            if sum(valids) != 1:
                sym = self.game.getSymmetries(canonicalBoard, pi)
                for b,p in sym:
                    trainExamples.append([b, curPlayer, p, None])

            action = np.random.choice(len(pi), p=pi)
            board, curPlayer = self.game.getNextState(board, curPlayer, action)
            # print("board", board)

            r = self.game.getGameEnded(board, curPlayer)

            if r!=0:
                return [(x[0],x[2],r*((-1)**(x[1]!=curPlayer))) for x in trainExamples]

    def gen_samples(self, iteration, proc_num):
            print('------ITER ' + str(iteration) + '------')

            iterationTrainExamples = deque([], maxlen=self.args["maxlenOfQueue"])
            eps_time = AverageMeter()
            bar = Bar('Self Play', max=self.args["numEps"]//self.args["genFilesPerIteration"])
            end = time.time()

            for eps in range(self.args["numEps"] // self.args["genFilesPerIteration"]):
                self.mcts = MCTS(self.game, self.nnet, self.args)   # reset search tree

                iterationTrainExamples += self.executeEpisode()
    
                # bookkeeping + plot progress
                eps_time.update(time.time() - end)
                end = time.time()
                bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=self.args["numEps"]//self.args["genFilesPerIteration"], et=eps_time.avg,
                                                                                                            total=bar.elapsed_td, eta=bar.eta_td)
                bar.next()
            bar.finish()
            
            self.saveTrainExamples(iteration-1, proc_num, iterationTrainExamples)

    def fit(self, iteration):

        all_iterations = range(0, iteration)
        trainExamples = []
        for i in all_iterations[-self.args["numItersForTrainExamplesHistory"]:]:
            for input_board, target_pi, target_v in self.loadTrainExamples(i):
                input_board = input_board.as_float_list()
                target_pi = np.random.choice(49, p=target_pi)

                trainExamples.append((input_board, target_pi, target_v))

        t = time.time()
        shuffle(trainExamples)
        print("SHUFFLED IN %.03f" % (time.time() - t))

        # training new network, keeping a copy of the old one
        #if iteration == 1:
        #    self.nnet.save_checkpoint(folder=self.args["checkpoint"], filename='checkpoint_0.pth.tar')
        self.nnet.train(trainExamples)
        self.nnet.save_checkpoint(folder=self.args["checkpoint"], filename='checkpoint_%d.pth.tar.next' % iteration)
    

    def pit(self, iteration, proc_num):
        self.pnet = self.nnet.__class__(self.game)  # the competitor network
        if iteration != 1:
            self.pnet.load_checkpoint(folder=self.args["checkpoint"], filename="checkpoint_%d.pth.tar" % (iteration-1))

        nmcts = MCTS(self.game, self.nnet, self.args)
        pmcts = MCTS(self.game, self.pnet, self.args)
        
        print('PITTING AGAINST PREVIOUS VERSION')
        
        arena = Arena(lambda x: np.argmax(nmcts.getActionProb(x, temp=0)),
                      lambda x: np.argmax(pmcts.getActionProb(x, temp=0)), self.game)
        nwins, pwins, draws = arena.playGames(self.args["arenaCompare"] // self.args["genFilesPerIteration"])
        # nwins = 1
        # pwins = 2
        # draws = 0

        print('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
        self.savePit(iteration, proc_num, nwins, pwins, draws)


    def verdict(self, iteration):
        nwins, pwins, draws = self.loadPit(iteration)

        print('ALL NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))

        if nwins + pwins == 0 or float(nwins)/(pwins+nwins) < self.args["updateThreshold"]:
            self.pnet = self.nnet.__class__(self.game)  # the competitor network
            self.pnet.load_checkpoint(folder=self.args["checkpoint"], filename="checkpoint_%d.pth.tar" % (iteration-1))

            print('REJECTING NEW MODEL')
            self.pnet.save_checkpoint(folder=self.args["checkpoint"], filename="checkpoint_%d.pth.tar" % iteration)
        else:
            print('ACCEPTING NEW MODEL')
            self.nnet.save_checkpoint(folder=self.args["checkpoint"], filename="checkpoint_%d.pth.tar" % iteration)
            self.nnet.save_checkpoint(folder=self.args["checkpoint"], filename='best.pth.tar')                


    def savePit(self, iteration, proc_num, nwins, pwins, draws):
        folder = self.args["checkpoint"]
        if not os.path.exists(folder):
            os.makedirs(folder)
        # print("iteration", iteration)
        filename = os.path.join(folder,"checkpoint_%d.pth.tar.%d.txt" % (iteration, proc_num))
        with open(filename, "w") as f:
            f.write(" ".join(map(str, [nwins, pwins, draws])))

    def loadPit(self, iteration):
        print("load pit", iteration)

        nwins = 0
        pwins = 0
        draws = 0

        for proc_num in range(self.args["genFilesPerIteration"]):
            pitResultsFile = os.path.join(self.args["checkpoint"], "checkpoint_%d.pth.tar.%d.txt" % (iteration, proc_num))

            if not os.path.isfile(pitResultsFile):
                print(pitResultsFile)
                print("File with pitExamples not found. Exiting")
                sys.exit()
            else:
                with open(pitResultsFile, "r") as f:
                    n_w, p_w, d = map(int, f.read().split())
                    nwins += n_w
                    pwins += p_w
                    draws += d
    
        return nwins, pwins, draws



    def saveTrainExamples(self, iteration, proc_num, examples):
        folder = self.args["checkpoint"]
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder,'checkpoint_%d.pth.tar.examples.%d' % (iteration, proc_num))
        with open(filename, "wb+") as f:
            Pickler(f).dump(examples)

    def loadTrainExamples(self, iteration):
        print("load", iteration)

        iterationTrainExamples = deque([], maxlen=self.args["maxlenOfQueue"])

        gen_files_num = self.args["genFilesPerIteration"]
        if iteration < 15:
            gen_files_num = 36

        for proc_num in range(gen_files_num):
            examplesFile = os.path.join(self.args["checkpoint"], "checkpoint_%d.pth.tar.examples.%d" % (iteration, proc_num))
            if not os.path.isfile(examplesFile):
                print(examplesFile)
                print("File with trainExamples not found. Exiting")
                sys.exit()
            else:
                with open(examplesFile, "rb") as f:
                    iterationTrainExamples += Unpickler(f).load()
        return iterationTrainExamples
        # self.trainExamplesHistory.append(iterationTrainExamples)
