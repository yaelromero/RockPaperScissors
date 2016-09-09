# Yael Romero
# 109210768
# CSE 310 Project Client Code

# import modules
from socket import *
import sys
import signal

TIMEOUT = 5
commands = ["HELP", "LOGIN", "R", "P", "S", "LOGOUT"]
welcome = "Welcome to Rock-Paper-Scissors!\n" + "To see a list of valid commands for this game, please type \"help\" before you log in.\n"
helpline = ("List of supported commands in this game:\n" +
"help: Prints a list of supported commands with descriptions of their functions and syntax of usage\n" + 
"login: Takes your player name (userid or nickname that uniquely identifies you) as an argument and sends it to the server\n" +
"r: Takes no arguments. Used by the player to throw a Rock to the server (the opponent)\n" +
"p: Takes no arguments. Used by the player to throw Paper to the server (the opponent)\n" +
"s: Takes no arguments. Used by the player to throw Scissors to the server (the opponent)\n" +
"logout: Takes no arguments. Sends a logout request to the server, displys game statistics, and terminates the connection\n")
rules = ("Throwing a Rock against Scissors results in a win.\n" +
"Throwing Paper against Rock results in a win.\n" +
"Throwing Scissors against Paper results in a win.\n" +
"A tie occurs when you throw the same object as your opponent (Rock and Rock, Paper and Paper, and Scissors and Scissors).\n")
rockMessage = 'ROCK ' + 'HTTP/1.1'
paperMessage = 'PAPER ' + 'HTTP/1.1'
scissorsMessage = 'SCISSORS ' + 'HTTP/1.1'
logoutMessage = 'LOGOUT ' + 'HTTP/1.1'
timeoutMessage = 'TIMEOUT ' + 'HTTP/1.1'
invalid = 'INVALID ' + 'HTTP/1.1'
checkSyntax = "Please check your syntax for login."

class TimeoutException(Exception): # Create a custom exception class to handle timeouts
    pass
    
def timeout(signum, frame): # Defines what happens when a timeout occurs
    raise TimeoutException
signal.signal(signal.SIGALRM, timeout)

def main():
    # Get the server hostname and port as command line arguments
    argv = sys.argv                      
    host = argv[1]
    port = argv[2]
    port = int(port) # Change the port to an integer

    # Prepare a client socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((host, port))

    print welcome
    print rules

    validLogin = False # Boolean to symbolize that the user has not logged in successfully
    while(validLogin == False): # While the user has not been logged in
        inputMessage = raw_input('View the help menu or login: ') # Prompt the user
        if(inputMessage.upper() == commands[0]): # If they ask to see the help menu
            print helpline
        elif(len(inputMessage.split()) == 2): # If their input is two words
            if ((inputMessage.split()[0]).upper() == commands[1]): # If the first word is "login"
                clientSocket.send('LOGIN ' + inputMessage.split()[1] + ' ' + 'HTTP/1.1') # Send login message to server
                validLogin = True
            else:
                print checkSyntax # If first word is not login, not valid
                validLogin = False
        else:
            print checkSyntax # If input is not two words, not valid
            validLogin = False
        
    serverMessage = clientSocket.recv(1024) # Receive login confirmation
    success = serverMessage.split("|")[0]
    print success

    end = False # Boolean to symbolize end of player input
    
    while(end == False):
        message = clientSocket.recv(1024) # Receive begin message and server choice message
        print message
        signal.alarm(TIMEOUT)
        try:
            playerChoice = raw_input('Throw an object or logout: ') # Prompt the user
            if(playerChoice.upper() == commands[2]): # If the player choice is to throw rock, send rock message
                clientSocket.send(rockMessage)
                serverMessage = clientSocket.recv(1024) # Receive outcome from server
                serverResponse = serverMessage.split("|")[0]
                print serverResponse
                end = False
            elif(playerChoice.upper() == commands[3]): # If the player choice is to throw paper, send paper message
                clientSocket.send(paperMessage)
                serverMessage = clientSocket.recv(1024) # Receive outcome from server
                serverResponse = serverMessage.split("|")[0]
                print serverResponse
                end = False
            elif(playerChoice.upper() == commands[4]): # If the player choice is to throw scissors, send scissors message
                clientSocket.send(scissorsMessage) 
                serverMessage = clientSocket.recv(1024) # Receive outcome from server
                serverResponse = serverMessage.split("|")[0]
                print serverResponse
                end = False
            elif(playerChoice.upper() == commands[5]): # If the player choice is to logout, send logout message
                clientSocket.send(logoutMessage)
                end = True
                serverMessage = clientSocket.recv(1024) # Receive logout and stats from server
                logout = serverMessage.split("|")[0]
                print "\n" + logout
                clientSocket.close() # Close the client socket
            else:
                clientSocket.send(invalid) # Every other move is not valid
                end = False
                serverMessage = clientSocket.recv(1024)
                serverResponse = serverMessage.split("|")[0]
                print serverResponse
            signal.alarm(0)
        except TimeoutException:
            clientSocket.send(timeoutMessage) # If a timeout occurs, send a timeout message to the server
            serverMessage = clientSocket.recv(1024) # Receive message from the server acknowledging timeout
            serverResponse = serverMessage.split("|")[0]
            print "\n" + serverResponse
            end = False
main()
