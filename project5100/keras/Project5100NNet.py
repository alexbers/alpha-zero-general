import sys
sys.path.append('..')
from utils import *

import argparse
from keras.models import *
from keras.layers import *
from keras.optimizers import *
from keras.utils import multi_gpu_model

class Project5100NNet():
    def __init__(self, game, args, multigpu=False):
        # game params
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args

        # Neural Net
        self.input_boards = Input(shape=(self.board_x, ))    # s: batch_size x board_x x board_y

        x_image = Reshape((self.board_x, 1))(self.input_boards)                # batch_size  x board_x x board_y x 1
        h_conv1 = Activation('relu')(BatchNormalization(axis=2)(Conv1D(2, 3, padding='same', use_bias=False)(x_image)))         # batch_size  x board_x x board_y x num_channels
        #h_conv2 = Activation('relu')(BatchNormalization(axis=2)(Conv1D(2, 3, padding='same', use_bias=False)(h_conv1)))         # batch_size  x board_x x board_y x num_channels
        #h_conv3 = Activation('relu')(BatchNormalization(axis=2)(Conv1D(2, 3, padding='valid', use_bias=False)(h_conv2)))        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        #h_conv4 = Activation('relu')(BatchNormalization(axis=2)(Conv1D(args["num_channels"], 4, padding='valid', use_bias=False)(h_conv3)))        # batch_size  x (board_x-4) x (board_y-4) x num_channels
        h_conv4_flat = Flatten()(h_conv1)
        s_fc1 = Dropout(args["dropout"])(Activation('relu')(BatchNormalization(axis=1)(Dense(1024, use_bias=False)(h_conv4_flat))))  # batch_size x 1024
        s_fc2 = Dropout(args["dropout"])(Activation('relu')(BatchNormalization(axis=1)(Dense(1536, use_bias=False)(s_fc1))))          # batch_size x 1024
        s_fc3 = Dropout(args["dropout"])(Activation('relu')(BatchNormalization(axis=1)(Dense(384, use_bias=False)(s_fc2))))          # batch_size x 1024
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc3)   # batch_size x self.action_size
        self.v = Dense(1, activation='tanh', name='v')(s_fc3)                    # batch_size x 1

        self.model = Model(inputs=self.input_boards, outputs=[self.pi, self.v])
        if multigpu:
            self.pmodel = multi_gpu_model(self.model, gpus=3)
        else:
            self.pmodel = self.model
        self.pmodel.compile(loss=['categorical_crossentropy','mean_squared_error'], optimizer=Adam(args["lr"]))

