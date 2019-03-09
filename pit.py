import Arena
from MCTS import MCTS
from project5100.Project5100Game import Project5100Game as Game
from project5100.Project5100Game import display
from project5100.keras_v1.NNet import NNetWrapper as NNet_v1
from project5100.keras_v2_c1.NNet import NNetWrapper as NNet_v2_c1
from project5100.keras_v3_c4.NNet import NNetWrapper as NNet_v3_c4
from project5100.keras_v4_c4.NNet import NNetWrapper as NNet_v4_c4
from project5100.keras_v5_c8.NNet import NNetWrapper as NNet_v5_c8

from project5100.keras.NNet import NNetWrapper as NNet

from project5100.Project5100Players import *

import numpy as np
from utils import *

"""
use this script to play any two agents against each other, or play manually with
any agent.
"""

g = Game()

# all players
rp = RandomPlayer(g).play
rsp = RandomSmartPlayer(g).play
pp = PassivePlayer(g).play
#gp = GreedyOthelloPlayer(g).play
hp = HumanProject5100Player(g).play

# nnet players
n1 = NNet(g)
n1.load_checkpoint('./temp/','checkpoint_86.pth.tar.next')
args1 = dict({'numMCTSSims': 20, 'cpuct':1.0})
mcts1 = MCTS(g, n1, args1)
n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))


n2 = NNet_v5_c8(g)
n2.load_checkpoint('./temp/','best.pth_1_8_k3.tar')
args2 = dict({'numMCTSSims': 20, 'cpuct':1.0})
mcts2 = MCTS(g, n2, args2)
n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))

arena = Arena.Arena(n1p, n1p, g, display=display)
print(arena.playGames(50, verbose=False))
