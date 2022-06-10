from os import urandom
from flask import Flask, render_template, request, session, redirect, copy_current_request_context
from db import *
from cards import createCardList, allCards
import sqlite3, os.path
import json
import urllib
import random
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from threading import Lock
from lobby import *

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_ = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
app.secret_key = urandom(32)

def islogged():
    return 'username' in session.keys()

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/logout",  methods=['GET', 'POST'])
def logout():
    # try except is for when user is not logged in and does /logout anyways and a KeyError occurs
    try:
        session.pop('username')
        session.pop('password')
    except KeyError:
        return redirect("/")
    return redirect("/")

#login takes the user object and sets cookies
@app.route("/login",  methods=['GET', 'POST'])
def login():
    if islogged():
        return redirect('/')

    return render_template('login.html')

# authentication of login; verifies login information
@app.route("/auth", methods=['GET', 'POST'])
def auth():
    if (request.method == 'POST'):

        username = request.form.get("username")
        password = request.form.get("password")

        #error handling for empty username
        if username == '':
            return render_template("login.html", error="Empty username")

        if not checkUser(username):
            return render_template("login.html", error="Wrong username, double check spelling or register")

        if not (checkPass(username, password)):
            return render_template("login.html", error="Wrong password")

        session['username'] = username
        session['password'] = password
        print(session['username'])
        return redirect('/')

    return redirect('/login')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if (request.method == 'POST'):
        username = request.form.get("username")
        password = request.form.get("password")
        reenterpasswd = request.form.get("reenterpasswd")

        if username == '':
            return render_template("register.html", error="Empty username")
        if password == '':
            return render_template("register.html", error="Empty password")
        if password != reenterpasswd:
            return render_template("register.html", error="Passwords don't match")

        if (checkUser(username)):
            return render_template("register.html", error="Username taken already")

        addUser(username, password)

        return redirect("/login")

    return render_template("register.html")

@app.route('/join_lobby', methods=['GET', 'POST'])
def joinLobby():
    if "username" in session:
        return render_template('join_lobby.html')
    else:
        return redirect('/login')

listLobbies;

def createLobby(room_code):
    global currentPot
    currentPot = 0
    lobbyID = urandom(32)
    data = {
        "id" : lobbyID,
        'numPlayers': 0,
        "gameState": "not started",
        1:["P1", "1000"],
        2:["P2", "1000"],
        3:["P3", "1000"],
        4:["P4", "1000"],
        5:["P5", "1000"],
        "start_turn":1,
        "turn":1,
        'deck': createDeck()
    }

#TEMPORARY (adapted for lobbies later)
global numPlayers
numPlayers = 0
global playerList
playerList = {
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

global setOfPlayers
setOfPlayers = set()

global currentPot
currentPot = 0

global playerNum
playerNum=5

@app.route("/poker", methods=['GET', 'POST'])
def game():
    username = "bob"
    if "username" in session:
        username = session["username"]
        # print("username is:", username)
        room_code = ""
        if (request.method == 'POST'):
            room_code = request.form.get("lobbyCode")
            # print("room code is: " + room_code)
        return render_template('poker.html', player_list=playerList, username = username, room_code = room_code, async_mode=socket_.async_mode)
    else:
        return redirect('/login')

@app.route("/reveal_cards", methods=['GET'])
def reveal_cards():
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        cards = {
            "p1c1": allCards[0],
            "p1c2": allCards[1],
            "p2c1": allCards[2],
            "p2c2": allCards[3],
            "p3c1": allCards[4],
            "p3c2": allCards[5],
            "p4c1": allCards[6],
            "p4c2": allCards[7],
            "p5c1": allCards[8],
            "p5c2": allCards[9],
            "length": len(playerList)
        }
        return json.dumps(cards)
    else:
        return redirect("/")

@app.route("/flop", methods=['GET'])
def flop():
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        flop = {
            "1":allCards[47],
            "2":allCards[48],
            "3":allCards[49],
        }
        return json.dumps(flop)
    else:
        return redirect("/")

@app.route("/turn", methods=['GET'])
def turn():
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        turn = {
            "1":allCards[50],
        }
        return json.dumps(turn)
    else:
        return redirect("/")

@app.route("/river", methods=['GET'])
def river():
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        river = {
            "1":allCards[51],
        }
        return json.dumps(river)
    else:
        return redirect("/")

@app.route("/previous_bet", methods=['GET'])
def getBet():
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        bet = {
            "bet":playerList['check'],
        }
        return json.dumps(bet)
    else:
        return redirect("/")

@socket_.on('connecting', namespace='/test')
def test_message(message):
    global numPlayers
    if (numPlayers < 5):
        session['receive_count'] = session.get('receive_count', 0) + 1
        x = json.loads(message["data"])
        numPlayers = numPlayers + 1
        global playerList
        playerList[numPlayers] = [x['user'], getMoney(x['user'])]
        global setOfPlayers
        setOfPlayers.add(x["user"])
        if (numPlayers == 5):
            playerList['gameState'] = 0
            playerList['turn'] = playerList['turn']+3
        returnMessage = {
            "hole1": [allCards[0], allCards[1]],
            "hole2": [allCards[2], allCards[3]],
            "hole3": [allCards[4], allCards[5]],
            "hole4": [allCards[6], allCards[7]],
            "hole5": [allCards[8], allCards[9]],
            "playerList": playerList,
            "data-type" : "console message",
            "message" : "connected!!! lets go! welcome user: " + x.get("user")
        }
        room = x.get("room")
        y = json.dumps(returnMessage)
        print(playerList)
        print(numPlayers)
        emit('response',
             {'data': y, 'count': session['receive_count']}, broadcast=True, to=room)

@socket_.on("fold_event", namespace="/test")
def fold_message_global(message):
    x = json.loads(message["data"])
    global currentPot
    currentPot = x.get('pot')
    if (x['user'] == playerList[playerList['turn']][0]):
        current = playerList['turn']
        playerList['folded'].append(playerList['turn'])
        print(playerList['folded'])
        if (playerList['turn'] == 5):
            playerList['turn'] = 1;
        else:
            playerList['turn'] = playerList['turn']+1

        while playerList['turn'] in playerList['folded']:
            if (playerList['turn'] == 5):
                playerList['turn'] = 1;
            else:
                playerList['turn'] = playerList['turn']+1
        if (playerList['turn'] == playerList['start_turn']):
            playerList['gameState'] = playerList['gameState'] +1
            playerList['check'] = True
        returnMessage = {
            "data-type" : "console message",
            "gameState" : playerList['gameState'],
            "fold_user" : x['user'],
            "current_turn" : current,
            "next_turn" : playerList['turn'],
            "next_user" : playerList[playerList['turn']][0]
        }
        y = json.dumps(returnMessage)

        if (len(playerList['folded']) >= 4):
            print("ending game")
            winner = determineWinner()
            money = determineMoney()
            room = x.get("room")
            endTheGame(winner, money, room)
        else :
            room = x.get("room")
            emit('fold_response',
                {'data': y, 'count': session['receive_count']},
                broadcast=True, to=room)

@socket_.on("kick_event", namespace="/test")
def kick_message_global(message):
    x = json.loads(message["data"])
    global currentPot
    currentPot = x.get('pot')

    current = playerList['turn']
    playerList['folded'].append(playerList['turn'])
    if (playerList['turn'] == 5):
        playerList['turn'] = 1;
    else:
        playerList['turn'] = playerList['turn']+1

    while playerList['turn'] in playerList['folded']:
        if (playerList['turn'] == 5):
            playerList['turn'] = 1;
        else:
            playerList['turn'] = playerList['turn']+1
    if (playerList['turn'] == playerList['start_turn']):
        playerList['gameState'] = playerList['gameState'] +1
        playerList['check'] = True
    returnMessage = {
        "data-type" : "console message",
        "gameState" : playerList['gameState'],
        "fold_user" : playerList[current][0],
        "current_turn" : current,
        "next_turn" : playerList['turn'],
        "next_user" : playerList[playerList['turn']][0]
    }
    y = json.dumps(returnMessage)

    if (len(playerList['folded']) >= 4):
        print("ending game")
        winner = determineWinner()
        money = determineMoney()
        room = x.get("room")
        endTheGame(winner, money, room)
    else :
        room = x.get("room")
        emit('fold_response',
            {'data': y, 'count': session['receive_count']},
            broadcast=True, to=room)

@socket_.on("check_event", namespace="/test")
def check_message_global(message):
    x = json.loads(message["data"])
    current = playerList['turn']
    if (playerList['turn'] == 5):
        playerList['turn'] = 1;
    else:
        playerList['turn'] = playerList['turn']+1
    while playerList['turn'] in playerList['folded']:
        if (playerList['turn'] == 5):
            playerList['turn'] = 1;
        else:
            playerList['turn'] = playerList['turn']+1
    if (playerList['turn'] == playerList['start_turn']):
        playerList['gameState'] = playerList['gameState'] +1
        playerList['check'] = True
    returnMessage = {
        "data-type" : "console message",
        "gameState" : playerList['gameState'],
        "bet" : playerList['check'],
        "current_turn" : current,
        "next_turn" : playerList['turn'],
        "next_user" : playerList[playerList['turn']][0]
    }
    y = json.dumps(returnMessage)
    room = x.get("room")
    emit('check_response',
         {'data': y, 'count': session['receive_count']},
         broadcast=True, to=room)

@socket_.on("call_event", namespace="/test")
def call_message_global(message):
    x = json.loads(message["data"])
    current = playerList['turn']
    if (playerList['turn'] == 5):
        playerList['turn'] = 1;
    else:
        playerList['turn'] = playerList['turn']+1
    while playerList['turn'] in playerList['folded']:
        if (playerList['turn'] == 5):
            playerList['turn'] = 1;
        else:
            playerList['turn'] = playerList['turn']+1
    if (playerList['turn'] == playerList['start_turn']):
        playerList['gameState'] = playerList['gameState'] +1
        playerList['check'] = True
    returnMessage = {
        "data-type" : "console message",
        "gameState" : playerList['gameState'],
        "call_user" : x['user'],
        "previous_bet" : playerList['previous_bet'],
        "current_turn" : current,
        "next_turn" : playerList['turn'],
        "next_user" : playerList[playerList['turn']][0]
    }
    y = json.dumps(returnMessage)
    room = x.get("room")
    emit('call_response',
         {'data': y, 'count': session['receive_count']},
         broadcast=True, to=room)

@socket_.on("raise_event", namespace="/test")
def raise_message_global(message):
    x = json.loads(message["data"])
    current = playerList['turn']
    playerList['check'] = False
    playerList['start_turn'] = playerList['turn']
    if (playerList['turn'] == 5):
        playerList['turn'] = 1;
    else:
        playerList['turn'] = playerList['turn']+1
    while playerList['turn'] in playerList['folded']:
        if (playerList['turn'] == 5):
            playerList['turn'] = 1;
        else:
            playerList['turn'] = playerList['turn']+1
    playerList['previous_bet'] = playerList['previous_bet']+100
    returnMessage = {
        "data-type" : "console message",
        "gameState" : playerList['gameState'],
        "raise_user" : x['user'],
        "previous_bet" : playerList['previous_bet'],
        "current_turn" : current,
        "next_turn" : playerList['turn'],
        "next_user" : playerList[playerList['turn']][0]
    }
    y = json.dumps(returnMessage)
    room = x.get("room")
    emit('raise_response',
         {'data': y, 'count': session['receive_count']},
         broadcast=True, to=room)

@socket_.on("update_money", namespace="/test")
def updateMoney(message):
    print("updating money")
    x = json.loads(message["data"])
    updateUserMoney(x['user'], x['new_money'])

@socket_.on("reset", namespace="/test")
def resetter():
    print("reseeting")
    global numPlayers
    numPlayers = 0
    global playerList
    playerList = {
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
    setOfPlayers = set()
    }

# @socket_.on("talking", namespace="/test")
# def checkingUser(message):
#     emit('checking', {"data":"hi"})

# @socket_.on('disconnect')
# def test_disconnect():
#     print('Client disconnected')

@socket_.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', to=room)

@socket_.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)
   
#Start Combo
def findCombo(list):
    list1 = list.copy()
    sorted = list1.sort()
    
    comboList = []

    comboList.append(royalStraightFlush(list1))
    comboList.append(straightFlush(list1))
    comboList.append(fourOfAKind(list1))
    comboList.append(house(list1))
    comboList.append(flush(list1))
    comboList.append(straight(list1))
    comboList.append(threeOfAKind(list1))
    comboList.append(twoPair(list1))
    comboList.append(aPair(list1))
    comboList.append(highestCard(list1))

    res = []
    for val in comboList:
        if val != None:
            res.append(val)
            
    if not comboList:
        print("sum ting wong")
    else:
        return res

def royalStraightFlush(list):
    suitList = []
    rankList = []
    
    for card in list:
        suitList.append(card % 10)
        rankList.append(int((card - (card % 10)) / 100))
        
    
    if (suitList.count(max(set(suitList), key = suitList.count)) >= 5):
        bsList = []
        brList = []
        mode = max(set(suitList), key = suitList.count)
        while mode in suitList:
            if (suitList[0] == mode):
                bsList.append(mode)
                brList.append(rankList[0])
            suitList.pop(0)
            rankList.pop(0)
        
        count = 1
        sort = brList.sort()
        previousRank = brList[0]
        
        for rank in brList:
            if (isIncrement(previousRank, rank)):
                count += 1
            elif (rank == previousRank):
                count += 0
            else:
                count = 1
            previousRank = rank
        if (count >= 4) and (previousRank == 13) and (brList[0] == 1):
            return ["RSF"]

def straightFlush(list):
    suitList = []
    rankList = []
    
    for card in list:
        suitList.append(card % 10)
        rankList.append(int((card - (card % 10)) / 100))
        
    
    if (suitList.count(max(set(suitList), key = suitList.count)) >= 5):
        bsList = []
        brList = []
        mode = max(set(suitList), key = suitList.count)
        while mode in suitList:
            if (suitList[0] == mode):
                bsList.append(mode)
                brList.append(rankList[0])
            suitList.pop(0)
            rankList.pop(0)
        
        count = 1
        sort = brList.sort()
        previousRank = brList[0]
        
        for rank in brList:
            if (isIncrement(previousRank, rank)):
                count += 1
            elif (rank == previousRank):
                count += 0
            else:
                count = 1
            previousRank = rank
        if count > 5:
            return ["SF", brList[len(brList) - 1]]

def fourOfAKind(list):
    rankList = []
    
    for card in list:
        rankList.append(int((card - (card % 10)) / 100))
    
    if (rankList.count(max(set(rankList), key = rankList.count))) == 4:
        return ["FOAK", rankList[len(rankList) - 1]]

def house(list):
    rankList = []
    
    for card in list:
        rankList.append(int((card - (card % 10)) / 100))
    
    if (rankList.count(max(set(rankList), key = rankList.count))) == 3:
        tripleRank = max(set(rankList), key = rankList.count)
        for _ in range(3):
            rankList.remove(tripleRank)
        if (rankList.count(max(set(rankList), key = rankList.count))) == 3:
            return False
        else:
            if (rankList.count(max(set(rankList), key = rankList.count))) == 2:
                doubleRank = max(set(rankList), key = rankList.count)
                for _ in range(2):
                    rankList.remove(doubleRank)
                if (rankList.count(max(set(rankList), key = rankList.count))) == 2:
                    return ["HOUSE", tripleRank, max(set(rankList), key = rankList.count)]
                else:
                    return ["HOUSE", tripleRank, doubleRank]

def flush(list):
    rankList = []
    suitList = []
    sortL = suitList.sort()
    

    for card in list:
        suitList.append(card % 10)
        rankList.append(int((card - (card % 10)) / 100))

    bsList = []
    brList = []
    mode = max(set(suitList), key = suitList.count)
    while mode in suitList:
        if (suitList[0] == mode):
            bsList.append(mode)
            brList.append(rankList[0])
        suitList.pop(0)
        rankList.pop(0)
    
    if (len(bsList)) >= 5:
        return ["FLUSH", brList[len(rankList) - 1]]

def straight(list):
    rankList = []
    
    for card in list:
        rankList.append(int((card - (card % 10)) / 100))

    
    count = 1
    previousRank = rankList[0]
    
    for rank in rankList:
        if (isIncrement(previousRank, rank)):
            count += 1
        elif (rank == previousRank):
            count += 0
        else:
            count = 1
        previousRank = rank
    if count >= 5:
        return ["STRAIGHT", previousRank]

def threeOfAKind(list):
    rankList = []
    
    for card in list:
        rankList.append(int((card - (card % 10)) / 100))
    
    if (rankList.count(max(set(rankList), key = rankList.count))) == 3:
        tripleRank = max(set(rankList), key = rankList.count)
        for _ in range(3):
            rankList.remove(tripleRank)
        if (rankList.count(max(set(rankList), key = rankList.count))) == 3:
            return ["TOAK", max(set(rankList), key = rankList.count)]
        else:
            return ["TOAK", tripleRank]

def twoPair(list):
    rankList = []
    
    for card in list:
        rankList.append(int((card - (card % 10)) / 100))
    
    if (rankList.count(max(set(rankList), key = rankList.count))) == 2:
        doubleRank = max(set(rankList), key = rankList.count)
        for _ in range(2):
            rankList.remove(doubleRank)
        if (rankList.count(max(set(rankList), key = rankList.count))) == 2:
            doubleRank2 = max(set(rankList), key = rankList.count)
            for _ in range(2):
                rankList.remove(doubleRank2)
            if (rankList.count(max(set(rankList), key = rankList.count))) == 2:
                return ["TP", max(set(rankList), key = rankList.count), doubleRank2]
            else:
                return [doubleRank2, doubleRank]

def aPair(list):
    rankList = []
    
    for card in list:
        rankList.append(int((card - (card % 10)) / 100))
    
    if (rankList.count(max(set(rankList), key = rankList.count))) == 2:
        doubleRank = max(set(rankList), key = rankList.count)
        for _ in range(2):
            rankList.remove(doubleRank)
        if (rankList.count(max(set(rankList), key = rankList.count))) == 2:
            doubleRank2 = max(set(rankList), key = rankList.count)
            for _ in range(2):
                rankList.remove(doubleRank2)
            if (rankList.count(max(set(rankList), key = rankList.count))) == 2:
                return ["AP", max(set(rankList), key = rankList.count)]
            else:
                return ["AP", doubleRank1]
        else:
            return ["AP", doubleRank]

def highestCard(list):
    rankList = []
    suitList = []
    for card in list:
        suitList.append(card % 10)
        rankList.append(int((card - (card % 10)) / 100))
    sortcry = rankList.sort(reverse=True)
    sortcryagaing = suitList.sort(reverse=True)
    
    return ["HC", rankList[0], suitList[0]]
        
def isIncrement(num1, num2):
    return num2 == num1 + 1


# USE ME :D
def findWinner(playerList):
    communityCombo = findCombo(allCards[47], allCards[48], allCards[49], allCards[50], allCards[51])
    
    p1Combo = []
    p2Combo = []
    p3Combo = []
    p4Combo = []
    p5Combo = []
    
    tempWinnerList = []
    highestCombo = 0
    count = 0
    for player in playerList:
        tempCombo = findCombo(RSG(allCards[count]), RSG(allCards[count+1]), RSG(allCards[47]), RSG(allCards[48]), RSG(allCards[49]), RSG(allCards[50]), RSG(allCards[51]))
        count += 2
        
        # Makes sure the combinations are made by the players and not by community cards
        for combo in communityCombo:
            if combo in tempCombo:
                tempCombo.remove(combo)
        
        for fin in tempCombo:
            if (["RSF"] == fin):
                return [player]
            elif (fin[0] == "SF"):
                if highestCombo < 9:
                    tempWinnerList = [player]
                elif highestCombo == 9:
                    tempWinnerList.append[player]
                break
            elif (fin[0] == "FOAK"):
                if highestCombo < 8:
                    tempWinnerList = [player]
                elif highestCombo == 8:
                    tempWinnerList.append[player]
                break
            elif (fin[0] == "HOUSE"):
                if highestCombo < 7:
                    tempWinnerList = [player]
                elif highestCombo == 7:
                    tempWinnerList.append[player]
                break
            elif (fin[0] == "FLUSH"):
                if highestCombo < 6:
                    tempWinnerList = [player]
                elif highestCombo == 6:
                    tempWinnerList.append[player]
                break
            elif (fin[0] == "STRAIGHT"):
                if highestCombo < 5:
                    tempWinnerList = [player]
                elif highestCombo == 5:
                    tempWinnerList.append[player]
                break
            elif (fin[0] == "TOAK"):
                if highestCombo < 4:
                    tempWinnerList = [player]
                elif highestCombo == 4:
                    tempWinnerList.append[player]
                break
            elif (fin[0] == "TP"):
                if highestCombo < 3:
                    tempWinnerList = [player]
                elif highestCombo == 3:
                    tempWinnerList.append[player]
                break
            elif (fin[0] == "AP"):
                if highestCombo < 2:
                    tempWinnerList = [player]
                elif highestCombo == 2:
                    tempWinnerList.append[player]
                break
            elif (fin[0] == "HC"):
                if highestCombo < 1:
                    tempWinnerList = [player]
                elif highestCombo == 1:
                    tempWinnerList.append[player]
                break

    return tempWinnerList
    
# Rank and Suit Grabber
def RSG(string):
    rank = string[18]
    suit = string[-5]
    
    rankSuitCode = 0
    
    if (rank == "A"):
        rankSuitCode += 100
    elif (rank == "2"):
        rankSuitCode += 200
    elif (rank == "3"):
        rankSuitCode += 300
    elif (rank == "4"):
        rankSuitCode += 400
    elif (rank == "5"):
        rankSuitCode += 500
    elif (rank == "6"):
        rankSuitCode += 600
    elif (rank == "7"):
        rankSuitCode += 700
    elif (rank == "8"):
        rankSuitCode += 800
    elif (rank == "9"):
        rankSuitCode += 900
    elif (rank == "1"):
        rankSuitCode += 1000
    elif (rank == "J"):
        rankSuitCode += 1100
    elif (rank == "Q"):
        rankSuitCode += 1200
    elif (rank == "K"):
        rankSuitCode += 1300
    
    if (suit == "D"):
        rankSuitCode += 1
    elif (suit == "C"):
        rankSuitCode += 2
    elif (suit == "H"):
        rankSuitCode += 3
    elif (suit == "S"):
        rankSuitCode += 4
# End Combo

def determineWinner():
    global setOfPlayers
    global playerList
    foldedList = []
    i = 0
    while i < len(playerList['folded']):
        foldedList.append(playerList[playerList['folded'][i]][0])
        i = i+1
    print(foldedList)
    for player in setOfPlayers:
        if (player in foldedList):
            updateUserLoss(player)
    for player in setOfPlayers:
        if (player not in foldedList):
            updateUserWin(player)
            return player
    return "Bob"

def determineMoney():
    global currentPot
    return currentPot;

def endTheGame(winner, money, room):
    returnMessage = {
        "data-type" : "message",
        "winner" : winner,
        "amountWon" : money
    }
    y = json.dumps(returnMessage)

    updateUserMoney(winner, int(money[1:]))

    global numPlayers
    numPlayers = 0
    global playerList

    i = 1
    while i < 6:
        addMoney(playerList[i][0])
        i = i+1

    playerList = {
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
    global currentPot
    currentPot = 0
    global setOfPlayers
    setOfPlayers = set()
    emit("endTheGame", {'data': y} ,broadcast=True, to=room)


if __name__ == "__main__":
    app.debug = True
    socket_.run(app, debug=True)
