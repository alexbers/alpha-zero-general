import Arena
from MCTS import MCTS
from project5100.Project5100Game import Project5100Game as Game
from project5100.Project5100Game import display
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
#gp = GreedyOthelloPlayer(g).play
hp = HumanProject5100Player(g).play

# nnet players
n1 = NNet(g)
n1.load_checkpoint('./temp/','best.pth.tar')
args1 = dict({'numMCTSSims': 50, 'cpuct':1.0})
mcts1 = MCTS(g, n1, args1)
n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))


#n2 = NNet(g)
#n2.load_checkpoint('/dev/8x50x25/','best.pth.tar')
#args2 = dotdict({'numMCTSSims': 25, 'cpuct':1.0})
#mcts2 = MCTS(g, n2, args2)
#n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))

arena = Arena.Arena(n1p, rp, g, display=display)
print(arena.playGames(2, verbose=False))
