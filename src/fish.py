# Holds full representation of fish, including position, height, width,
# username, and ascii representation.
class Fish(object):
    def __init__(self, filename, startrow, startcol, username):
        self.fish = []
        self.name = username
        self.displayName = username
        self.height = 1
        self.width = 3
        self.col = startcol
        self.row = startrow
        with open(filename) as f:
            for line in f:
                tmp = line.split('\n')[0]
                tmp = list(tmp.encode("ascii"))
                self.fish.append(tmp)

########### GETTERS AND SETTERS ###########
    def getName(self):
        return self.name

    def oneMoreChar(self):
        self.displayName = self.displayName + self.name[len(self.displayName)]

    def getNameLen(self):
        return len(self.name)

    def getDisplayName(self):
        return self.displayName

    def getDisplayNameLen(self):
        return len(self.displayName)

    def setDisplayName(self, newName):
        self.displayName = newName

    def getCol(self):
        return self.col

    def getRow(self):
        return self.row

    def getFish(self):
        return self.fish

    def setCol(self, col):
        self.col = col

    def setRow(self, row):
        self.row = row

    def getFishHeight(self):
        return self.height

    def getFishWidth(self):
        return self.width
