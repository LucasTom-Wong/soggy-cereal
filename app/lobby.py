class Lobby:
    def __init__(self, name):
        self.name = name
        self.numPlayers;
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
        self.setOfPlayers = set()
        self.currentPot = 0
        self.playerNum=5

    def returnNumPlayers(self):
        return self.numPlayers

    def updateNumPlayers(self, new):
        self.numPlayers = new
        return null

    def returnPlayerList(self):
        return self.playerList

    def returnSetOfPlayers(self):
        return self.setOfPlayers

    def returnCurrentPot(self):
        return self.currentPot

    def updateCurrentPot(self, new):
        self.currentPot = new
        return null

    def returnPlayerNum(self):
        return self.playerNum

    def updatePlayerNum(self, new):
        self.playerNum = new
        return null
