# board.py
# Board module to represent the fish tank as a Pyro4 object.
# Each method is accessible to both clients and the server to update
# the current position of objects within the board, change game conditions
# (i.e. number of players, game status, current iteration of the game).



from __future__ import print_function
import Pyro4
import sys


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Board(object):
  """ Sole Pyro4 object for all processes to communicate with.
      Contains all necessary game information. 
  """
  def __init__(self):
      """ Initializes a blank board along with static parameters """
      self.board = []
      self.playerList = []
      self.started = False
      self.playerCount = 0
      self.wave = 1
      self.height = 40
      self.width = 170
      self.sharkChars = ["'", '`', ')', '(', '-', ',', '/',
                           '.', '0', ';', '|', '_', '~']
      for j in range(self.height):
        string = ['+']
        for i in range(self.width-1):
          if j != 0 and j != (self.height - 1):
            string.append(' ')
          else:
            string.append('-')
        string.append('+')
        self.board.append(string)

  def clearBoard(self):
    """ Removes all characters from the board """
    for i in range(1, self.height - 1):
        for j in range(1, self.width):
            self.board[i][j] = ' '
      
  def readBoard(self):
    """ Returns the current game board """
    return self.board
      

  def writeBoardShark(self, sharksInfo):

    """ Write method for sharks to the board.

        Currently called from the SharkManager thread on the server,
        which sends a list of shark information (in the form of the list
        sharksInfo) in order to minimize write calls.

        In this case, all sharks write to the board within a single 
        write call to help performance.

    """
    # Keeps list of which sharks have made it offscreen
    finished = []
    for s in sharksInfo:
        row = s['row']
        col = s['col']  
        vertMove = s['vertMove']
        horizMove = s['horizMove']
        height = 9
        width = 55
        shark = s['shark']
        # once a shark is offscreen
        if col > self.width + 1:    
          finished.append(True)
          continue
        if row == 0:
          if vertMove < 0:
              row = self.height - 2
          else:
              row += 1
        if row < 0:
          row %= (self.height - 1)

        tmprow = int(row)

        for line in shark:

          if tmprow == 0:
            tmprow += 1
            continue
          elif tmprow < 1:
            tmprow += 1
            continue
          if tmprow >= self.height - 1:
            tmprow = 1

          tmpcol = int(col)

          for c in line:
            if tmpcol > (self.width - 1):
              tmpcol += 1
              continue
            elif tmpcol < 0:
              tmpcol += 1
              continue
            if tmpcol == 0:
              tmpcol += 1
            if c != ' ':
              self.board[tmprow][tmpcol] = c
            tmpcol += 1
          tmprow += 1
        finished.append(False)
    return finished

  def writeBoardFish(self, row, col, fish, name):
    """ Write method for fish. 

        Checks for collisions by comparing a current board location
        that a fish will move into with any of the ascii characters
        that compose a shark.

    """

    tmpcol = int(col)
    tmprow = int(row)
    for c in name:
        self.board[tmprow][tmpcol] = c
        tmpcol += 1

    tmprow = int(row) + 1
    for line in fish:
      tmpcol = int(col)
      for c in line:
        # If a fish tries to overwrite a shark, collision
        if self.board[tmprow][tmpcol] in self.sharkChars:
          return True
        else:
          self.board[tmprow][tmpcol] = c
        tmpcol += 1
      tmprow += 1
    return False
      
  def getHeight(self):
    """ Returns the height of the board """
    return self.height

  def getWidth(self):
    """ Returns the width of the board """
    return self.width

  def numPlayers(self):
    """ Returns the current number of players in the game """
    return self.playerCount

  def addPlayer(self, name):
    """ Adds a player and their username to the game """
    self.playerList.append(name)
    self.playerCount += 1

  def decrementPlayer(self, username):
    """ Removes a player of the given username from the game.
        Called upon death of a player or upon an exit signal.
     """
    self.playerCount -= 1
    self.playerList.remove(username)

  def getPlayers(self):
    """ Returns the list of players in the game """
    return self.playerList

  def startGame(self):
    """ Sets the game status to True, signally the start of the game """
    self.started = True

  def endGame(self):
    """ Sets the game status to False, signally the end of the game """
    self.started = False

  def gameStarted(self):
    """ Returns whether the game has started or not """
    return self.started

  def getWave(self):
    """ Returns the current 'wave' of the game.
        Each wave corresponds to the number of sharks
        spawned.
    """
    return self.wave

  def updateWave(self):
    """ Updates the current game wave. """
    self.wave += 1

def main(args):
  """ Initializes the Pyro4 board object on a currently running NS """
  Pyro4.config.SERVERTYPE = "multiplex"
  Pyro4.Daemon.serveSimple(
          {
              Board: "example.board"
          },
          ns = True,
          host = args[1])

if __name__=="__main__":
  main(sys.argv)
