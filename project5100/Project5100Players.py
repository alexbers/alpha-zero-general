import numpy as np
import random

class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valids = self.game.getValidMoves(board, 1)
        actions = [i for i in range(self.game.getActionSize()) if valids[i]]
        return random.choice(actions)


class HumanProject5100Player():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        # display(board)
        valid = self.game.getValidMoves(board, 1)

        EFFECTS = [
        "BPlus", "BMinus", "BIPlus", "BIMinus", "BDPlus",
        "BDMinus", "SPlus", "SMinus", "SIPlus", "SIMinus",
        "SDPlus", "SDMinus", "IPSPlus", "IPSMinus", "Centerer"
        ]

        action_desc = {}
        for i in range(len(EFFECTS)):
            action_desc[i] = "cast me " + EFFECTS[i]
            action_desc[i+15] = "cast enemy " + EFFECTS[i]
            action_desc[i+30] = "drop " + EFFECTS[i]

        action_desc[45] = "skip"

        for i in range(len(valid)):
            if valid[i]:
                print("%s: %s" % (i, action_desc[i]))
        while True:
            a = int(input())

            if valid[a]:
                break
            else:
                print('Invalid')

        return a


# class GreedyOthelloPlayer():
#     def __init__(self, game):
#         self.game = game

#     def play(self, board):
#         valids = self.game.getValidMoves(board, 1)
#         candidates = []
#         for a in range(self.game.getActionSize()):
#             if valids[a]==0:
#                 continue
#             nextBoard, _ = self.game.getNextState(board, 1, a)
#             score = self.game.getScore(nextBoard, 1)
#             candidates += [(-score, a)]
#         candidates.sort()
#         return candidates[0][1]
