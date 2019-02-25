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
    'load_model': False,
    'load_folder_file': ('./temp','checkpoint_3.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

if __name__=="__main__":
    g = Game()
    nnet = nn(g)

    if args["load_model"]:
        nnet.load_checkpoint(args["load_folder_file"][0], args["load_folder_file"][1])

    c = Coach(g, nnet, args)
    if args["load_model"]:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
