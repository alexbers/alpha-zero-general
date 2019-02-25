import random
import numpy as np

# bad code
def itb(num: int, length: int):
    """
    Converts integer to bit array
    Someone fix this please :D - it's horrible
    :param num: number to convert to bits
    :param length: length of bits to convert to
    :return: bit array
    """
    if num >= 2**length:
        num = 2**length - 1
    num = int(num)
    if length == 13:
        return [int(i) for i in '{0:013b}'.format(num)]
    if length == 16:
        return [int(i) for i in '{0:016b}'.format(num)]
    if length == 17:
        return [int(i) for i in '{0:017b}'.format(num)]
    if length == 23:
        return [int(i) for i in '{0:023b}'.format(num)]

def onehot(num, length):
    if num >= length:
        return [0] * length
    return [0] * num + [1] + [0] * (length-num-1)

class Board:
    def __init__(self):
        self.myS = 10000
        self.myB = 200
        self.myM = 0

        self.myCooldown = 0

        # BPlus BMinus BIPlus BIMinus BDPlus BDMinus SPlus SMinus SIPlus SIMinus SDPlus SDMinus IPSPlus IPSMinus Centerer 
        #  S×=0.5 разово B×=0.5 разово если S>15000 и B>200
        self.myEffectsTimeLeft = [0] * 15
        self.myCardsAvailable = [0] * 15

        self.enemyS = 10000
        self.enemyB = 200
        self.enemyM = 0

        self.enemyCooldown = 0

        self.enemyEffectsTimeLeft = [0] * 15
        self.enemyCardsAvailable = [0] * 15

        self.turn_number = 0

        for i in random.sample(range(15), 5):
            self.myCardsAvailable[i] = 1

        for i in random.sample(range(15), 5):
            self.enemyCardsAvailable[i] = 1


    def __str__(self):
        ret = "%s %s %s %s %s %s %s %s %s %s %s %s %s" % (self.myS, self.myB, self.myM, 
            self.myCooldown, self.myEffectsTimeLeft, self.myCardsAvailable, self.enemyS, 
            self.enemyB, self.enemyM, self.enemyCooldown, self.enemyEffectsTimeLeft, 
            self.enemyCardsAvailable, self.turn_number)
        # print(ret)
        return ret

    def as_float_list(self):
        ret = []
        ret += itb(self.myS, 17)
        ret += itb(self.myB, 13)
        ret += itb(self.myM//1000, 23)
        ret += onehot(self.myCooldown, 16)
        ret += self.myEffectsTimeLeft
        ret += self.myCardsAvailable

        ret += itb(self.enemyS, 17)
        ret += itb(self.enemyB, 13)
        ret += itb(self.enemyM//1000, 23)
        ret += onehot(self.enemyCooldown, 16)
        ret += self.enemyEffectsTimeLeft

        # 183
        # print(len(ret))
        return np.array(ret)


    def calc_next_round(self):
        mySI = 1.1
        myBI = 0.04
        mySD = 0.0005
        myBD = 0.8
        myIPS = 1000

        enemySI = 1.1
        enemyBI = 0.04
        enemySD = 0.0005
        enemyBD = 0.8
        enemyIPS = 1000

        if self.myEffectsTimeLeft[0]:
            self.myB += 20
        if self.myEffectsTimeLeft[1]:
            self.myB -= 10
        if self.myEffectsTimeLeft[2]:
            myBI = myBI * 1.35
        if self.myEffectsTimeLeft[3]:
            myBI = myBI * 0.65
        if self.myEffectsTimeLeft[4]:
            myBD = myBD * 1.1
        if self.myEffectsTimeLeft[5]:
            myBD = myBD * 0.92
        if self.myEffectsTimeLeft[6]:
            self.myS += 1000
        if self.myEffectsTimeLeft[7]:
            self.myS -= 500
        if self.myEffectsTimeLeft[8]:
            mySI *= 1.05
        if self.myEffectsTimeLeft[9]:
            mySI *= 0.96
        if self.myEffectsTimeLeft[10]:
            mySD *= 1.30
        if self.myEffectsTimeLeft[11]:
            mySD *= 0.70
        if self.myEffectsTimeLeft[12]:
            myIPS *= 2.0
        if self.myEffectsTimeLeft[13]:
            myIPS *= 0.75
        if self.myEffectsTimeLeft[14]:
            if self.myS > 15000 and self.myB > 200:
                self.myS //= 2
                self.myB //= 2

        myS_old = self.myS
        myB_old = self.myB
        self.myS = int(myS_old*mySI - myB_old*myS_old*mySD)
        self.myB = max(0, int(myB_old*myBD + myB_old*myS_old*mySD*myBI + 0.9999999999))
        self.myM = self.myM + myS_old*myIPS

        if self.enemyEffectsTimeLeft[0]:
            self.enemyB += 20
        if self.enemyEffectsTimeLeft[1]:
            self.enemyB -= 10
        if self.enemyEffectsTimeLeft[2]:
            enemyBI = enemyBI * 1.35
        if self.enemyEffectsTimeLeft[3]:
            enemyBI = enemyBI * 0.65
        if self.enemyEffectsTimeLeft[4]:
            enemyBD = enemyBD * 1.1
        if self.enemyEffectsTimeLeft[5]:
            enemyBD = enemyBD * 0.92
        if self.enemyEffectsTimeLeft[6]:
            self.enemyS += 1000
        if self.enemyEffectsTimeLeft[7]:
            self.enemyS -= 500
        if self.enemyEffectsTimeLeft[8]:
            enemySI *= 1.05
        if self.enemyEffectsTimeLeft[9]:
            enemySI *= 0.96
        if self.enemyEffectsTimeLeft[10]:
            enemySD *= 1.30
        if self.enemyEffectsTimeLeft[11]:
            enemySD *= 0.70
        if self.enemyEffectsTimeLeft[12]:
            enemyIPS *= 2.0
        if self.enemyEffectsTimeLeft[13]:
            enemyIPS *= 0.75
        if self.enemyEffectsTimeLeft[14]:
            if self.enemyS > 15000 and self.enemyB > 200:
                self.enemyS //= 2
                self.enemyB //= 2

        enemyS_old = self.enemyS
        enemyB_old = self.enemyB
        self.enemyS = int(enemyS_old*enemySI - enemyB_old*enemyS_old*enemySD)
        self.enemyB = max(0, int(enemyB_old*enemyBD + enemyB_old*enemyS_old*enemySD*enemyBI + 0.9999999999))
        self.enemyM = self.enemyM + enemyS_old*enemyIPS


        # recalc cooldowns
        self.myCooldown = max(0, self.myCooldown-1)
        self.enemyCooldown = max(0, self.enemyCooldown-1)

        self.myEffectsTimeLeft = [max(0, self.myEffectsTimeLeft[i]-1) for i in range(len(self.myEffectsTimeLeft))]
        self.enemyEffectsTimeLeft = [max(0, self.enemyEffectsTimeLeft[i]-1) for i in range(len(self.enemyEffectsTimeLeft))]
