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
        self.currentPot = 0
