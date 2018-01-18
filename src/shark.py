import os
import sys
import random

# Holds full representation of shark, including position, height, width,
# vertical and horizontal velocities, and ascii representation.
class Shark(object):
    def __init__(self, filename, startrow, startcol):
        self.shark = []
        self.col = startcol
        self.row = startrow
        self.vertMove = random.uniform(-.4, .4)
        self.horizMove = random.uniform(0.1, 1)
        with open(filename) as f:
            for line in f:
                tmp = line.split('\n')[0]
                tmp = list(tmp.encode("ascii"))
                self.shark.append(tmp)       

# updates location depending on horizontal and vertical velocities.
    def move(self, board):
        self.col += self.horizMove
        self.row += self.vertMove

        self.row %= (board.getHeight() - 1)


########### GETTERS AND SETTERS ###########
    def readShark(self):
        return self.shark 

    def getCol(self):
        return self.col

    def getRow(self):
        return self.row



