import sys
sys.setrecursionlimit(100000)

from Coach import Coach
from project5100.Project5100Game import Project5100Game as Game
from project5100.keras.NNet import NNetWrapper as nn
from utils import *

args = dict({
    'numIters': 1000,
    'numEps': 100,
    'tempThreshold': 15,
    'updateThreshold': 0.55,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 20,
    'arenaCompare': 40,
    'cpuct': 1,

    'checkpoint': './temp/',
    'numItersForTrainExamplesHistory': 20,
})

if __name__=="__main__":
    g = Game()

    start_iter = int(sys.argv[1])
    action = sys.argv[2]

    if action == "gen_samples":
        nnet = nn(g, multigpu=False)
        if start_iter != 1:
            nnet.load_checkpoint(args["checkpoint"], "checkpoint_%d.pth.tar" % (start_iter-1))
        c = Coach(g, nnet, args)

        c.gen_samples(start_iter)
    elif action == "fit":
        nnet = nn(g, multigpu=True)
        if start_iter != 1:
            nnet.load_checkpoint(args["checkpoint"], "checkpoint_%d.pth.tar" % (start_iter-1))

        c = Coach(g, nnet, args)
        c.fit(start_iter)
    elif action == "pit":
        nnet = nn(g, multigpu=False)
        if start_iter != 1:
            nnet.load_checkpoint(args["checkpoint"], "checkpoint_%d.pth.tar.next" % start_iter)

        c = Coach(g, nnet, args)
        c.pit(start_iter)



        # if args["load_model"]:
        # print("Load trainExamples from file")
    # c.learn()
