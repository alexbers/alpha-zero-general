import copy
import random
import sys
sys.path.append('..')

from Game import Game
from .Project5100Logic import Board
import numpy as np


class Project5100Game(Game):
    """
    This class specifies the base Game class. To define your own game, subclass
    this class and implement the functions below. This works when the game is
    two-player, adversarial and turn-based.

    Use 1 for player1 and -1 for player2.

    See othello/OthelloGame.py for an example implementation.
    """
    def __init__(self):
        pass

    def getInitBoard(self):
        b = Board()
        return b

    def getBoardSize(self):
        # return (3 * 2 + 1 * 2 + 15 * 2 + 15, 1)
        return (183, 1)

    def getActionSize(self):
        """
        Returns:
            actionSize: number of all possible actions
        """
        # self_casts + enemy_casts + drop + skip
        return 15 + 15 + 15 + 1

    def getNextState(self, board, player, action):
        """
        Input:
            board: current board
            player: current player (1 or -1)
            action: action taken by current player

        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """

        # print("getNextState", board)
        ret_b = copy.deepcopy(board)
        
        if player == 1:
            if 0 <= action < 15:
                if action in [0, 1, 6, 7, 14]:
                    ret_b.myEffectsTimeLeft[action] = 1
                elif action in [8]:
                    ret_b.myEffectsTimeLeft[action] = 4
                elif action in [12]:
                    ret_b.myEffectsTimeLeft[action] = 12
                else:
                    ret_b.myEffectsTimeLeft[action] = 5
                new_card = random.choice([i for i in range(15) if ret_b.myCardsAvailable[i] == 0])
                ret_b.myCardsAvailable[action] = 0
                ret_b.myCardsAvailable[new_card] = 1

                ret_b.myCooldown = 5 if (action) != 14 else 15
            elif 15 <= action < 30:
                if action-15 in [0, 1, 6, 7, 14]:
                    ret_b.enemyEffectsTimeLeft[action-15] = 1
                elif action-15 in [8]:
                    ret_b.enemyEffectsTimeLeft[action-15] = 4
                elif action-15 in [12]:
                    ret_b.enemyEffectsTimeLeft[action-15] = 12
                else:
                    ret_b.enemyEffectsTimeLeft[action-15] = 5

                new_card = random.choice([i for i in range(15) if ret_b.myCardsAvailable[i] == 0])
                ret_b.myCardsAvailable[action-15] = 0
                ret_b.myCardsAvailable[new_card] = 1

                ret_b.myCooldown = 5 if (action - 15) != 14 else 15

            elif 30 <= action < 45:
                new_card = random.choice([i for i in range(15) if ret_b.myCardsAvailable[i] == 0])
                ret_b.myCardsAvailable[action-30] = 0
                ret_b.myCardsAvailable[new_card] = 1
                ret_b.myCooldown = 2
        else:
            # the same, but vice versa
            if 0 <= action < 15:
                if action in [0, 1, 6, 7, 14]:
                    ret_b.enemyEffectsTimeLeft[action] = 1
                elif action in [8]:
                    ret_b.enemyEffectsTimeLeft[action] = 4
                elif action in [12]:
                    ret_b.enemyEffectsTimeLeft[action] = 12
                else:
                    ret_b.enemyEffectsTimeLeft[action] = 5

                new_card = random.choice([i for i in range(15) if ret_b.enemyCardsAvailable[i] == 0])
                ret_b.enemyCardsAvailable[action] = 0
                ret_b.enemyCardsAvailable[new_card] = 1

                ret_b.enemyCooldown = 5 if (action) != 14 else 15
            elif 15 <= action < 30:
                if action-15 in [0, 1, 6, 7, 14]:
                    ret_b.myEffectsTimeLeft[action-15] = 1
                elif action-15 in [8]:
                    ret_b.myEffectsTimeLeft[action-15] = 4
                elif action-15 in [12]:
                    ret_b.myEffectsTimeLeft[action-15] = 12
                else:
                    ret_b.myEffectsTimeLeft[action-15] = 5

                new_card = random.choice([i for i in range(15) if ret_b.enemyCardsAvailable[i] == 0])
                ret_b.enemyCardsAvailable[action-15] = 0
                ret_b.enemyCardsAvailable[new_card] = 1

                ret_b.enemyCooldown = 5 if (action - 15) != 14 else 15
            elif 30 <= action < 45:
                new_card = random.choice([i for i in range(15) if ret_b.enemyCardsAvailable[i] == 0])
                ret_b.enemyCardsAvailable[action-30] = 0
                ret_b.enemyCardsAvailable[new_card] = 1
                ret_b.enemyCooldown = 2

        ret_b.turn_number += 1
        if ret_b.turn_number % 2 == 0:
            ret_b.calc_next_round()
        # print("next", ret_b)
        return (ret_b, -player)


    def getValidMoves(self, board, player):
        ret = [0] * self.getActionSize() # skip move is always available
        ret[15+15+15]  = 1
        if player == 1:
            if board.myCooldown != 0:
                return ret

            for i in range(len(board.myCardsAvailable)):
                if board.myCardsAvailable[i]:
                    ret[i] = 1
                    ret[i+15] = 1
                    ret[i+30] = 1
        else:
            if board.enemyCooldown != 0:
                return ret

            for i in range(len(board.enemyCardsAvailable)):
                if board.enemyCardsAvailable[i]:
                    ret[i] = 1
                    ret[i+15] = 1
                    ret[i+30] = 1
        

        return ret


    def getGameEnded(self, board, player):
        WIN_M = 5000000000
        # WIN_M = 5000
        if player == 1:
            if board.myS <= 0:
                print("enemy won by S")
                return -1
            elif board.enemyS <= 0:
                print("me won by S")
                return 1

            if board.myM >= WIN_M:
                print("me won by M")
                return 1
            elif board.enemyM >= WIN_M:
                print("enemy won by M")
                return -1

            if board.turn_number > 1400:
                print("DRAW", board)
                return 0.000001
        else:
            if board.myS <= 0:
                print("me won by S")
                return 1
            elif board.enemyS <= 0:
                print("enemy won by S")
                return -1

            if board.myM >= WIN_M:
                print("enemy won by M")
                return -1
            elif board.enemyM >= WIN_M:
                print("me won by M")
                return 1

            if board.turn_number > 1400:
                print("DRAW", board)
                return 0.000001

        return 0


    def getCanonicalForm(self, board, player):
        if player == 1:
            return board
        else:
            b = copy.deepcopy(board)
            b.myS, b.enemyS = b.enemyS, b.myS
            b.myB, b.enemyB = b.enemyB, b.myB
            b.myM, b.enemyM = b.enemyM, b.myM
            b.myCooldown, b.enemyCooldown = b.enemyCooldown, b.myCooldown
            b.myEffectsTimeLeft, b.enemyEffectsTimeLeft = b.enemyEffectsTimeLeft, b.myEffectsTimeLeft
            b.myCardsAvailable, b.enemyCardsAvailable = b.enemyCardsAvailable, b.myCardsAvailable
            return b

        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            canonicalBoard: returns canonical form of board. The canonical form
                            should be independent of player. For e.g. in chess,
                            the canonical form can be chosen to be from the pov
                            of white. When the player is white, we can return
                            board as is. When the player is black, we can invert
                            the colors and return the board.
        """
        

    def getSymmetries(self, board, pi):
        """
        Input:
            board: current board
            pi: policy vector of size self.getActionSize()

        Returns:
            symmForms: a list of [(board,pi)] where each tuple is a symmetrical
                       form of the board and the corresponding pi vector. This
                       is used when training the neural network from examples.
        """
        return [(board, pi)]

    def stringRepresentation(self, board):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        return str(board)


def display(board):
    EFFECTS = [
        "BPlus", "BMinus", "BIPlus", "BIMinus", "BDPlus",
        "BDMinus", "SPlus", "SMinus", "SIPlus", "SIMinus",
        "SDPlus", "SDMinus", "IPSPlus", "IPSMinus", "Centerer"
    ]

    print(" -------- turn %s --------------- " % board.turn_number)
    print("P1:")
    print(" S=%s B=%s M=%s" % (board.myS, board.myB, board.myM))
    print(" Cooldown:", board.myCooldown)
    

    for i in range(len(board.myEffectsTimeLeft)):
        if board.myEffectsTimeLeft[i]:
            print(" %s: %s" % (EFFECTS[i], board.myEffectsTimeLeft[i]))

    for i in range(len(board.myCardsAvailable)):
        if board.myCardsAvailable[i]:
            print(EFFECTS[i], end=",")

    print("\nP2:")
    print(" S=%s B=%s M=%s" % (board.enemyS, board.enemyB, board.enemyM))
    print(" Cooldown:", board.enemyCooldown)
    

    for i in range(len(board.enemyEffectsTimeLeft)):
        if board.enemyEffectsTimeLeft[i]:
            print(" %s: %s" % (EFFECTS[i], board.enemyEffectsTimeLeft[i]))

    for i in range(len(board.enemyCardsAvailable)):
        if board.enemyCardsAvailable[i]:
            print(EFFECTS[i], end=",")
    
    print("\n   -----------------------")
