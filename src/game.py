import sys
import os
import threading
import Pyro4
from shark import *
import time
from datetime import datetime
import subprocess
import multiprocessing as mp
import signal
import socket
import random
import signal
from functools import reduce

# Semaphores and state variables
boardLock = threading.Semaphore(0)
processes = []
board = ''
running = True

class SharkManager(threading.Thread):
    def __init__(self, numSharks):
        threading.Thread.__init__(self)

        self.numSharks = numSharks
        # Contains each iteration of a shark
        self.sharks = []
        for i in range(self.numSharks):
            self.sharks.append(Shark("models/shark.txt",\
            						 random.randint(1, 28), -55))

    def run(self):
        sharksInfo = []
        offScreen = False
        lastTime = datetime.now()
        counter = 0

        # Sharks run until off screen (as long as game is continuing)
        while not offScreen and running:
        	# Buffered fps
            currTime = datetime.now()
            delta = currTime - lastTime
            lastTime = currTime
            counter += delta.microseconds

            # Clear the board, and then write to it.
            if counter >= 1000000/20:
                counter = 0
                board.clearBoard()
                sharksInfo = []
                for s in self.sharks:
                    sharksInfo.append({'row': s.row, 'col': s.col,\
                    				   'vertMove': s.vertMove,\
                    				   'horizMove': s.horizMove,\
                    				   'shark': s.shark})
                status = board.writeBoardShark(sharksInfo)

                # Checks if all sharks are off screen
                offScreen = reduce((lambda x, y: x and y), status, True)

                for shark in self.sharks:
                    shark.move(board)



# Launches Pyro4 server, accessible by given IP address
def startBoard(IP):
    command = "python -m Pyro4.naming -n %s > /dev/null" % IP
    processes.append(subprocess.Popen(command,shell=True,preexec_fn=os.setsid))
    time.sleep(3)
    command = "python board.py %s > /dev/null" % IP
    processes.append(subprocess.Popen(command,shell=True,preexec_fn=os.setsid))
    time.sleep(3)
    boardLock.release()

# Callback function for signal receiver.
def endserver(signum, stack):
    global running
    running = False

# Main server driver.  Launches a Pyro4 using IP of hosting computer,
# Once the server is running, players are kept track of, and sharks
# are spawned from within a while loop that continues until receiving
# the Ctrl-C signal.
def main(argv):
	# Retrieve the host's currennt IP.
    signal.signal(signal.SIGINT, endserver)
    processesStart = []
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
    s.close()
    # Start server to host board object.
    processesStart.append(threading.Thread(target = startBoard, args = [IP]))
    for p in processesStart:
        p.start()
    # Wait for the server to be running.
    boardLock.acquire()
    boardLock.release()

    # Reciece copy of board object
    NS = Pyro4.locateNS(host=IP, port=9090, broadcast=True)
    time.sleep(5)
    uri = NS.lookup("example.board")
    global board
    board = Pyro4.Proxy(uri)

    print ("Running server on " + IP + "...let the games begin!")
    prevPlayers = board.numPlayers()

    # Loop which controls game.  Spawns sharks (as many as the wave value),
    # Only starts sharks spawning once a player has entered the game.
    while running:
        currPlayers = board.numPlayers()
        if currPlayers > prevPlayers:
            print ("Player joined the game!")
            prevPlayers = currPlayers
        elif currPlayers < prevPlayers:
            print ("Player has died!")
            prevPlayers = currPlayers
        if board.gameStarted():
            wave = board.getWave()
            sharkManager = SharkManager(wave)
            sharkManager.start()
            sharkManager.join()
            board.updateWave()

    # Ends the server if Ctrl-C is input.
    board.endGame()
    for process in processes:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)

if __name__ == "__main__":
    main(sys.argv)
