# Yael Romero
# 109210768
# CSE 310 Project Server Code

# import modules
from socket import *
import random

lower = 0
upper = 2
moves = ["R", "P", "S"]
choices = ["R", "P", "S", "L", "T", "I"]
newGame = "The game has now officially begun!"
serverDone = "The server has thrown its object. You have 5 seconds to respond."
serverDoneRepeat = "The server has thrown another object. You have 5 seconds to respond."
timeOut = "The game has been timed out.\n | HTTP/1.1 200 OK"
invalid = "That is invalid input!\n | HTTP/1.1 200 OK"

W = 0 # Number of wins
G = 0 # Number of games
O = 0 # Number of timed-out games

def getObjectName(move): # This function maps the move (by the player or server) to the object it represents
    objectName = " "
    if move == "S":
        objectName = "Scissors"
    elif move == "R":
        objectName = "Rock"
    else:
        objectName = "Paper"
    return objectName

def main():
    global W 
    global G
    global O

    # Prepare a server socket

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverPort = 5768
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1) # Server begins listening for incoming TCP requests

    while True:
        # Establish the connection
        print "Waiting for a player..."
        connectionSocket, addr = serverSocket.accept()
        try:
            useridMessage = connectionSocket.recv(1024) # Read bytes from socket
            userid = useridMessage.split()[1] # Get the user id from the message it receives
            
            success = userid + " has been logged in.\n | HTTP/1.1 200 OK" # Print back the user id to the user
            print success.split("|")[0]
            connectionSocket.send(success)

            repeat = False # Boolean to symbolize whether there needs to be a repeat throw
            restart = True # Boolean to symbolize the start of a new game

            while(restart == True):
                end = False # Game has started, not the end of a game
                while(end == False):
                    serverChoice = random.randint(lower, upper) # Pick a random number between 0 and 2
                    serverMove = moves[serverChoice] # Maps the number to the index of the moves array
                    if(repeat == False): # It is a new game
                        print newGame
                        print serverDone
                        connectionSocket.send(newGame + "\n" + serverDone)
                    else: # There needs to be a repeat
                        print serverDoneRepeat
                        connectionSocket.send(serverDoneRepeat)

                    clientMessage = connectionSocket.recv(1024)
                    playerMove = clientMessage.split()[0][0] # Get the first letter of the client message (either "R", "S", "P", or "T")
                    if(playerMove != choices[3]): # If the player move is not a logout request
                        if(playerMove == serverMove): # It is a tie
                            tieAnnounce = ("It is a tie. You and the server both threw " +
                                           getObjectName(playerMove) + ". Try again!" + " | HTTP/1.1 200 OK")
                            print tieAnnounce.split("|")[0]
                            connectionSocket.send(tieAnnounce)
                            repeat = True
                            end = False # Not the end of a game
                        elif(playerMove == "T"): # A timeout occured
                            print timeOut.split("|")[0]
                            connectionSocket.send(timeOut)
                            G = G + 1
                            O = O + 1
                            end = True # End of a game, not a tie
                            repeat = False
                            restart = True # Start a new game
                        elif(playerMove == "I"): # Invalid input received
                            print invalid.split("|")[0]
                            connectionSocket.send(invalid)
                            repeat = True
                            end = False
                        elif((playerMove == "R" and serverMove == "S") # The player has won
                             or (playerMove == "P" and serverMove == "R")
                             or (playerMove == "S" and serverMove == "P")):
                            winAnnounce = ("You win! You threw " + getObjectName(playerMove) +
                                           " and the server threw " + getObjectName(serverMove) + ".\n" + "| HTTP/1.1 200 OK \n")
                            print winAnnounce.split("|")[0]
                            connectionSocket.send(winAnnounce)
                            G = G + 1
                            W = W + 1
                            repeat = False
                            end = True
                        else: # The player has lost
                            loseAnnounce = ("You lost! You threw " + getObjectName(playerMove) +
                                            " and the server threw " + getObjectName(serverMove) + ".\n" + "| HTTP/1.1 200 OK\n")
                            print loseAnnounce.split("|")[0]
                            connectionSocket.send(loseAnnounce)
                            G = G + 1
                            repeat = False
                            end = True
                    else: # Player move is a logout request
                        result = ("The player " + userid + " has been logged out.\n" +
                                  "Here are the statistics from the session: \n" + 
                                  "Total number of games played: " + str(G) + "\n" +
                                  "Total number of wins: " + str(W) + "\n" +
                                  "Total number of timed-out games: " + str(O) + "\n" + "| HTTP/1.1 200 OK")
                        connectionSocket.send(result)
                        print "The player " + userid + " has been logged out.\n"
                        end = True
                        repeat = False
                        restart = False
                        W = 0
                        G = 0
                        O = 0
                        connectionSocket.close() # Close the connection   
        except:
            # Send response message for any errors
            connectionSocket.send('\nHTTP/1.1 400 Bad Request\n\n')

            # Close client socket
            connectionSocket.close()
    serverSocket.close()
main()
