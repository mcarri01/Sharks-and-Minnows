# COMP50CP Final Project: SharksAndMinnows
Team Members: Matthew Carrington-Fair, Matthew Epstein, David Stern

## Usage: 

To start nameserver, run the command:

```
python game.py
```

This will start a nameserver on your IP address accessible to others.
Once the server is running, a message will be printed to the terminal,
giving the IP address of the now running server.

**Note: Client should not be attempted to run until the affirmation text has been printed to the window running the server.**

To connect to this nameserver, run 

```
python client.py -i [IP]
```

With the IP being the IP address of the host containing the nameserver.

**Note: The client will not work with a terminal screen that is too small.  We have added a command that should change the window size to 200 x 60.  This seems to work on Macs, but not windows.  If the screen does not increase as expected, we recommend increasing the terminal screen to dimensions of 200 x 60.**

Use WASD controls to move the fish through the ocean and enjoy!

## Directories:

### src/
Contains all python source code

### src/models/
Contains text models for shark, fish, and title screen

### documentation/
Contains pdfs containing design progress

## Files
In `src`/

### title.py
A python representation of the title string.

### fish.py
Class representation of fish object

### shark.py
Class representation of shark object

### game.py
Initializes the server for the program, which includes starting
the Pyro nameserver and setting up our board object to be 
available to client programs. It does both by launching python
subprocesses that can run in the background while the rest of
the program can continue to the main server loop, handling
the game status and creating sharks. Upon successful start-up
of both the nameserver and the game board, it will output the
IP that the nameserver is running on so clients can connect to it.

### client.py
Handles the gameplay experience for the users. It requires the 
IP address of a nameserver, and upon start-up prompts the user
for a username and whether they will want to wait and play with
a friend or play solo. From there the program branches into two
threads, one to handle user input and controlling their fish
object (obtained through fish.py), and the other to keep a clear
display (with the help of the curses library).

### board.py
Contains our Pyro class object. It is the centerpiece of our game,
containing all information regarding the current game state
(the board itself, whether the game has started, the number
of players/their usernames, etc.) and with methods to update
the game information and board through read & write operations.
It is made accessible to both the server and client programs
throughout the game.

There are also a few additional files containing the ascii art pictures used by the game

