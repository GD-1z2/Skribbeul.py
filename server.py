#! /usr/bin/python3
# -*- coding: utf-8 -*-

# python 3
# (C) Fabrice Sincère

# ubuntu : OK
# win XP, 7 : OK

# localhost : OK
# réseau local : OK (firewall à paramétrer)
# Internet : OK (box - routeur NAT à paramétrer)

# fonctionne aussi avec un simple client telnet
# telnet localhost 50026

import socket, sys, threading, time, random

# variables globales

# adresse IP et port utilisés par le serveur
HOST = ""
PORT = 50026

minPlayers = 1
dureemax = 120 # durée max question ; en secondes
pause = 3 # pause entre deux questions  ; en secondes

dict_reponses = {}  # dictionnaire des réponses des clients

# liste des questions
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

playersList = []

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

    def hasName(self):
        return False if self.name=="" else True

    def setName(self, name : str):
        self.name = name

    def addScore(self, points : int):
        self.score += points
        self.scores.append(points)

class ThreadClient(threading.Thread):
    """
    Thread for client
    """
    
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
        # attente réponse client
        pseudo = self.connection.recv(4096)
        pseudo = pseudo.decode(encoding='UTF-8')
        
        self.player.setName(pseudo)
        
        print("Pseudo du client", self.connection.getpeername(),">", pseudo)
        
        # message = b"Attente des autres joueurs...\n"
        # self.connection.send(message)
    
        # answers
        while True:
            try:
                answer = self.connection.recv(4096)
                answer = answer.decode(encoding='UTF-8')
            except:
                break
                
            # on enregistre la première réponse
            # les suivantes sont ignorées
            if self.name not in dict_reponses:
                dict_reponses[self.name] = answer, time.time()
                print("Réponse du client", self.name, ">", answer)

        print("\nFin du thread", self.name)
        self.connection.close()

def sendAll(message):
    """ message du serveur vers tous les clients"""
    for player in playersList:
        player.connection.send(bytes(message,"utf8"))


# Initialisation du serveur
# Mise en place du socket avec les protocoles IPv4 et TCP
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
try:
    mySocket.bind((HOST, PORT))
except socket.error:
    print("La liaison du socket à l'adresse choisie a échoué.")
    sys.exit()
print("Serveur prêt (port",PORT,") en attente de clients...")
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

for player in playersList :
    sendAll(player.name + " choisit un thème\n")

    propWord = [random.choice(wordList), random.choice(wordList), random.choice(wordList)]
    while propWord[0] == propWord[1] or propWord[1] == propWord[2] or propWord[2] == propWord[0]:
        propWord = [random.choice(wordList), random.choice(wordList), random.choice(wordList)]

    msg = "Choisissez un thème :\n1 - " + propWord[0][0] + "\n2 - " + propWord[1][0] + "\n3 - " + propWord[2][0] + "\n"
    player.connection.send(bytes(msg, "UTF-8"))

sendAll("\nFIN\nVous pouvez fermer l'application...\n")

for player in playersList:
    player.connection.close()
    print("Déconnexion du socket", player.connection)

input("\nAppuyer sur Entrée pour quitter l'application...\n")