#   client.py 
#   Client code for playing the game, organized by an initial
#   startup process, and then splitting off into two threads.
#
#   The DisplayThread class handles displaying the current iteration
#   of the board to the user, while the FishThread handles accepting
#   user input for control over the movement of their fish object.
#


import sys
import os
import threading
from fish import *
from title import *
import Pyro4
import socket
import time
import random
from datetime import datetime
import curses
from curses import wrapper
import signal
import re
import argparse

board = []
dead = False

class DisplayThread(threading.Thread):
  """ The DisplayThread class handles displaying the current game status
      to the user. It derives its methods from Python's threading.Thread
      object, allowing it to run as a thread but giving flexibility with
      class specific variables and state.

  """

  def __init__(self, stdscr, username):
    """ Initializes display parameters, especially the shutdown_flag
        to check for exit signals from the user.
    """
    threading.Thread.__init__(self)

    self.user = username
    self.shutdown_flag = threading.Event()
    self.stdscr = stdscr

  def run(self):
    """ Main thread exec function. Loops until the user exits with a 
        SIGINT or SIGTERM.

        Utilizes Python curses to handle effective terminal output, 
        printing out the current board from the Pyro remote object,
        and then other specific strings indicating game status.
    """
    global board
    lastTime = datetime.now()
    counter = 0
    # until clean exit
    while not self.shutdown_flag.is_set():
        # currTime = datetime.now()
        # delta = currTime - lastTime
        # lastTime = currTime
        # counter += delta.microseconds
        # draw current board
        b = board.readBoard()
        wave = board.getWave()
        string = ''
        for line in b:
            for c in line:
                string += c
            string += '\n'
        self.stdscr.addstr(string, curses.color_pair(1))
        players = board.getPlayers()
        # if in a lobby
        if not board.gameStarted():
          board.clearBoard()
          self.stdscr.addstr("Waiting for players...\n")
        # if the player dies
        elif self.user not in players:
          self.stdscr.addstr("Game Over...you died!\n")
        else:
          s = "Current wave: " + str(wave) + ", Players alive: " + \
                                            " ".join(players) + "\n"
          self.stdscr.addstr(s, curses.A_BOLD)
        self.stdscr.addstr(titleString)
        self.stdscr.move(0, 0)

class FishThread(threading.Thread):
  """ The FishThread class manages receiving user input and updating 
      the player's position.
      
  """
  def __init__(self, stdscr, username):
    """ Initializes the player's fish and terminal screen manager """
    threading.Thread.__init__(self)

    self.shutdown_flag = threading.Event()
    self.username = username
    self.stdscr = stdscr
    self.username = username

  def run(self):
    """
        Main loop through for Fish thread.
        Upon either the user signally SIGTERM/SIGINT
        the main loop terminates and exits to the main program. 

        If a collision occurs between a player and a shark, sets the
        user as dead to prevent them from playing (but they can
        still watch their friends)!
    """
    global board
    global dead
    fish = Fish("models/fish.txt", 15, 75, self.username)
    while not self.shutdown_flag.is_set():
      # gets key press from user
      key = self.stdscr.getch()
      curses.flushinp
      currCol = fish.getCol()
      currRow = fish.getRow()
      if not dead:
        boardWidth = board.getWidth()
        boardHeight = board.getHeight()
        fishWidth = fish.getFishWidth()
        fishHeight = fish.getFishHeight()
        # depending on direction moves fish
        if key == ord('w') and currRow != 1:
            fish.setRow(currRow - 1)
        elif key == ord('d') and currCol != boardWidth-fishWidth:
            diff = boardWidth-currCol-1
            if fish.getDisplayNameLen() > diff:
                fish.setDisplayName(fish.getDisplayName()[:diff])
            fish.setCol(currCol + 1)
        elif key == ord('s') and currRow != boardHeight-fishHeight-2:
            fish.setRow(currRow + 1)
        elif key == ord('a') and currCol != 1:
            if fish.getDisplayNameLen() < fish.getNameLen():
                fish.oneMoreChar()
            fish.setCol(currCol - 1)
        # checks if there was collision on write 
        collision = board.writeBoardFish(fish.getRow(), fish.getCol(), \
                                     fish.getFish(), fish.getDisplayName())
        if collision:
            dead = True
            board.decrementPlayer(self.username)

class ServiceExit(Exception):
  """ Custom exception to safely end threads before exitting """
  pass

def receive_sig(signum, stack):
  """ Signal handler to raise exception, allowing the shutdown_flag for
      each thread to be set.
  """
  raise ServiceExit


def initializeGame(ip):
  """ Initializes the game by connecting to the nameserver and retrieving
      the board Pyro4 object.

      Retrieves username and game mode the user wishes to play.
  """

  # locate nameserver
  NS = Pyro4.locateNS(host=ip, port=9090, broadcast=True)

  uri = NS.lookup("example.board")
  global board
  # retrieve board object
  board = Pyro4.Proxy(uri)
  username = raw_input("Please choose your username: ")
  username = re.sub(r'[^a-zA-Z]', '', username)
  # only allow unique usernames
  while username in board.getPlayers():
      username = raw_input("Username already taken. Choose another: ")
      username = re.sub(r'[^a-zA-Z]', '', username)
  board.addPlayer(username)
  waiting = raw_input("Wait for more players? (y?): ")
  # check if we need to put player in a lobby or not
  if waiting != 'y':
      board.startGame()
  elif board.numPlayers() > 1:
      board.startGame()
  return username

def parseArgs(argv):
  """ Parses IP command line argument """
  parser = argparse.ArgumentParser(description='Client program for SharksAndMinnows game!')
  parser.add_argument('-i', dest='ip', type=str,
                      help='IPv4 Address of Name Server')

  return parser.parse_args().ip


def main(stdscr, username, ip):
  """ Main for client, initializing signal handlers and launching threads.
      Waits for signal to begin shutdown process.
  """
  # signal handlers for clean exit  
  signal.signal(signal.SIGTERM, receive_sig)
  signal.signal(signal.SIGINT, receive_sig)
  curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
  stdscr.nodelay(True)

  dispThread = DisplayThread(stdscr, username)
  fishThread = FishThread(stdscr, username)
  b = board.readBoard()

  # until signal exit just start threads and loop
  try:
    dispThread.start()
    fishThread.start()
    while True:
        time.sleep(0.5)

  except ServiceExit:
    # set flags for threads to clean up and finish
    dispThread.shutdown_flag.set()
    fishThread.shutdown_flag.set()
    if username in board.getPlayers():
        board.decrementPlayer(username)
    dispThread.join()
    fishThread.join()

if __name__ == "__main__":
  ip = parseArgs(sys.argv)
  username = initializeGame(ip)
  wrapper(main, username, ip)


