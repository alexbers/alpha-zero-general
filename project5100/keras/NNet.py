import argparse
import os
import shutil
import time
import random
import numpy as np
import math
import sys
sys.path.append('../..')
sys.path.append('..')
sys.path.append('.')
from utils import *
from NeuralNet import NeuralNet

import argparse
from .Project5100NNet import Project5100NNet as project5100

args = {
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 80,
    'batch_size': 1024*3,
    'cuda': False,
    'num_channels': 32,
}

class NNetWrapper(NeuralNet):
    def __init__(self, game, multigpu=False):
        self.nnet = project5100(game, args, multigpu)
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray([b.as_float_list() for b in input_boards])
        # print("input_boards", input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)
        # self.nnet.model.fit(x = input_boards, y = [target_pis, target_vs], batch_size = args["batch_size"], epochs = args["epochs"])
        self.nnet.pmodel.fit(x = input_boards, y = [target_pis, target_vs], batch_size = args["batch_size"], epochs = args["epochs"], validation_split = 0.2)

    def predict(self, board):
        """
        board: np array with board
        """
        # timing
        start = time.time()

        # preparing input
        board = board.as_float_list()[np.newaxis, :]

        # print("BAY board", board)

        # board = board.repeat(10000,0)
        # for i in range(1000):
            # board.append(board[0].copy())

        # run
        # print("prediction", len(board))
        start = time.time()
        pi, v = self.nnet.model.predict(board)
        # end = time.time()
        # print("v=%s"%v,"time=%s"%(end-start))

        #print('PREDICTION TIME TAKEN : {0:03f}'.format(time.time()-start))
        return pi[0], v[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise("No model in path {}".format(filepath))
        self.nnet.model.load_weights(filepath)
