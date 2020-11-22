# -*- coding: utf-8 -*-

# localhost : OK
# réseau local : OK (firewall à paramétrer)
# Internet : OK (box - routeur NAT à paramétrer)

# fonctionne aussi avec un simple client telnet
# telnet localhost 50026

"""
Commands :
/HINT:str
    set clients words hint
/DRAW
    allow client to draw
/NODRAW
    client cant draw
/END
    end the game, automatically disconnects the client

todo : clear, undo, skip, clearchat
"""

import socket, sys, threading, time, random

HOST = "" ; PORT = 50026 # host+port for serv

minPlayers = 2
playersList = []
maxDuration = 30

wordList = [
    ["plante", 1],
    ["arbre", 1],
    ["telephone", 1],
    ["ordinateur", 1],
    ["among us", 1],
    ["licorne", 1],
    ["gateau", 1],
    ["minecraft", 2],
    ["fortnite", 2],
    ["dragon", 2],
    ["ecole", 2],
    ["guerre", 3]
]

class Player():
    """
    Player
    """
    def __init__(self, connection):
        self.name = ""
        self.score = 0
        self.scores = []
        self.connection = connection
        self.messages = []
        self.readMsg = False

    def hasName(self):
        return False if self.name=="" else True

    def setName(self, name : str):
        self.name = name

    def addScore(self, points : int):
        self.score += points
        self.scores.append(points)

class ThreadClient(threading.Thread):
    """Thread for client"""

    def __init__(self,conn):
        threading.Thread.__init__(self)
        self.player = Player(conn)
        playersList.append(self.player)
        self.connection = conn
                
        self.name = self.getName() # thread id "<Thread-N>"
        
        print("Connexion du client", self.connection.getpeername(), self.name, self.connection)
        
        message = bytes("Vous êtes connecté au serveur.\n","utf-8")
        self.connection.send(message)
        
    def run(self):
        self.connection.send(b"Choisissez un pseudo :\n")
        pseudo = self.connection.recv(4096) # waiting for client answer
        pseudo = pseudo.decode(encoding="UTF-8")
        
        self.player.setName(pseudo)
        
        print("Client", self.connection.getpeername(),"> Server : Name > ", pseudo)
        # message = b"Attente des autres joueurs...\n"
        # self.connection.send(message)
    
        # answers
        while True:
            if self.player.readMsg :
                try :
                    answer = self.connection.recv(4096)
                    answer = answer.decode(encoding="UTF-8")
                except :
                    break
                    
                # on enregistre la première réponse
                # les suivantes sont ignorées
                
                # if self.name not in dict_reponses:
                    # dict_reponses[self.name] = answer, time.time()
                self.player.messages.append(answer)
                print("Client", self.name, "> Server : ", answer)

        print("\nFin du thread", self.name)
        self.connection.close()

def sendAll(message):
    """send message to all clients"""
    print("Server > * : " + message)
    for player in playersList:
        player.connection.send(bytes(message,"utf8"))

# Initialisation du serveur
# Mise en place du socket avec les protocoles IPv4 et TCP
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try :
    mySocket.bind((HOST, PORT))
except socket.error:
    print("Socket binding failed")
    sys.exit()
print("Server ready (port",PORT,") waiting for clients...")
mySocket.listen(5)

# Waiting for players
while len(playersList) < minPlayers:
    try:
        connection, adress = mySocket.accept()
    except:
        sys.exit()
    th = ThreadClient(connection) # new thread to handle the client
    th.setDaemon(1)
    th.start()

namesChosen = False
while not namesChosen:
    namesChosen = True
    for player in playersList:
        if not player.hasName():
            namesChosen = False

sendAll("\nLa partie va commencer !\n")

def checkAnswers(word : str, curPlayer : Player):
    for player in playersList:
        if word not in player.messages and player != curPlayer : return False
    return True

for player in playersList :
    sendAll(player.name + " choisit un thème\n")

    propWord = [random.choice(wordList), random.choice(wordList), random.choice(wordList)]
    while propWord[0] == propWord[1] or propWord[1] == propWord[2] or propWord[2] == propWord[0]:
        propWord = [random.choice(wordList), random.choice(wordList), random.choice(wordList)]

    msg = "Choisissez un thème :\n1 - " + propWord[0][0] + "\n2 - " + propWord[1][0] + "\n3 - " + propWord[2][0] + "\n"
    player.connection.send(bytes(msg, "UTF-8"))
    
    answer = ""
    while answer not in ["1", "2", "3"] :
        answer = player.connection.recv(4096).decode("UTF-8")
    theme = propWord[int(answer)-1]
    hint = "" ; hintChanges = 0
    for char in theme[0]:
        hint += "_" if char != " " else " "

    print("Player " + player.name + " chose theme " + theme[0] + " with diff " + str(theme[1]))

    sendAll(player.name + " commence à dessiner !\n")

    sendAll("/HINT:"+hint)
    player.connection.send(b"/DRAW\n")

    #reading players answers
    for player2 in playersList:
        if player.name != player2.name:
            player2.readMsg = True

    drawingTimeBegin = time.time()

    # waiting for all players to find the word or the end of the turn (maxDuration)
    while time.time() < drawingTimeBegin+maxDuration and not checkAnswers(theme[0], player):
        if time.time() > drawingTimeBegin+(maxDuration/2) and hintChanges==0 :
            hint = theme[0][0]+hint[1:]
            hintChanges += 1
            sendAll("/HINT:"+hint)

    # stop reading players answers
    for player2 in playersList:
        if player.name != player2.name:
            player2.readMsg = False

    player.connection.send(b"/NODRAW\n\n")


sendAll("\n/END\n")
sendAll("Fin de la partie\nVous pouvez fermer l'application...\n")

for player in playersList:
    player.connection.close()
    print("Déconnexion du socket", player.connection)

input("\nAppuyer sur Entrée pour quitter l'application...\n")