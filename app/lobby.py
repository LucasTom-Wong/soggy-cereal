from cards import *

class Lobby:
    def __init__(self):
        self.numPlayers = 0
        self.playerList = {
        "gameState": -1,
        1:["P1", "1000"],
        2:["P2", "1000"],
        3:["P3", "1000"],
        4:["P4", "1000"],
        5:["P5", "1000"],
        "folded": [],
        "dealer":1,
        "start_turn":3,
        "turn":1,
        "previous_bet":100,
        "check":False
        }
        self.deck = createDeck()
        self.setOfPlayers = set()
        self.currentPot = 0

    def returnNumPlayers(self):
        return self.numPlayers

    def updateNumPlayers(self, new):
        self.numPlayers = new

    def returnPlayerList(self):
        return self.playerList

    def updatePlayerList(self, key, value):
        self.playerList[key] = value

    def addToPlayerList(self, key, value):
        self.playerList[key].append(value)

    def returnSetOfPlayers(self):
        return self.setOfPlayers

    def newSetOfPlayers(self):
        self.setOfPlayers = set()

    def sop_add(self, user):
        self.setOfPlayers.add(user)

    def returnCurrentPot(self):
        return self.currentPot

    def updateCurrentPot(self, new):
        self.currentPot = new

    def returnDeck(self):
        return self.deck
