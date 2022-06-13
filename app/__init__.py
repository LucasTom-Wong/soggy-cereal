from os import urandom
from flask import Flask, render_template, request, session, redirect, copy_current_request_context
from db import *
from cards import createCardList, allCards
import sqlite3, os.path
import json
import urllib
import random
import string
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

lobbies = {}
lobbies.update({"" : Lobby()})

def findLobby(roomCode):
    listOfLobbiesRoomCode = lobbies.keys()
    checker = False
    for lobby in listOfLobbiesRoomCode:
        if (lobby == roomCode):
            checker = True
    if (not checker):
        createLobby(roomCode)

def createLobby(roomCode):
    lobbies.update({roomCode : Lobby()})
    # return lobbies(roomCode)

@app.route("/poker", methods=['GET', 'POST'])
def game():
    username = "bob"
    if "username" in session:
        username = session["username"]
        # print("username is:", username)
        room_code = ""
        if (request.method == 'POST'):
            room_code = request.form.get("lobbyCode")
        # grabs the lobbycode

        findLobby(room_code) #ensures that the lobby exists

        playerList = lobbies[room_code].returnPlayerList()

        # print("room code is: " + room_code)
        return render_template('poker.html', player_list=playerList, username = username, room_code = room_code, async_mode=socket_.async_mode)
    else:
        return redirect('/login')

@app.route("/reveal_cards", methods=['GET'])
def reveal_cards(room_code):
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        room = lobbies[room_code]
        cards = {
            "p1c1": room.returnDeck()[0],
            "p1c2": room.returnDeck()[1],
            "p2c1": room.returnDeck()[2],
            "p2c2": room.returnDeck()[3],
            "p3c1": room.returnDeck()[4],
            "p3c2": room.returnDeck()[5],
            "p4c1": room.returnDeck()[6],
            "p4c2": room.returnDeck()[7],
            "p5c1": room.returnDeck()[8],
            "p5c2": room.returnDeck()[9],
        }
        return json.dumps(cards)
    else:
        return redirect("/")

@app.route("/flop", methods=['GET'])
def flop(room_code):
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        room = findLobby(room_code)
        flop = {
            "1":room.returnDeck()[47],
            "2":room.returnDeck()[48],
            "3":room.returnDeck()[49],
        }
        return json.dumps(flop)
    else:
        return redirect("/")

@app.route("/turn", methods=['GET'])
def turn(room_code):
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        room = lobbies[room_code]
        turn = {
            "1":room.returnDeck()[50],
        }
        return json.dumps(turn)
    else:
        return redirect("/")

@app.route("/river", methods=['GET'])
def river(room_code):
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        room = lobbies[room_code]
        river = {
            "1":room.returnDeck()[51],
        }
        return json.dumps(river)
    else:
        return redirect("/")

@app.route("/previous_bet", methods=['GET'])
def getBet(room_code):
    if (request.headers.get("X-Requested-With") == "XMLHttpRequest"):
        room = lobbies[room_code]
        bet = {
            "bet":room.returnPlayerList()['check'],
        }
        return json.dumps(bet)
    else:
        return redirect("/")

@socket_.on('connecting', namespace='/test')
def test_message(message):
    x = json.loads(message["data"])
    room_code = x["room"]
    room = lobbies[room_code]
    playerList = room.returnPlayerList()
    if (room.returnNumPlayers() < 5):
        session['receive_count'] = session.get('receive_count', 0) + 1
        deck = room.returnDeck()
        room.updateNumPlayers(room.returnNumPlayers()+1)
        numPlayers = room.returnNumPlayers()
        room.updatePlayerList(numPlayers, [x['user'], getMoney(x['user'])])
        room.sop_add(x['user'])
        if (numPlayers == 5):
            room.updatePlayerList('gameState', playerList['gameState']+1)
            room.updatePlayerList('turn',playerList['turn']+3 )
        returnMessage = {
            "hole1": [deck[0], deck[1]],
            "hole2": [deck[2], deck[3]],
            "hole3": [deck[4], deck[5]],
            "hole4": [deck[6], deck[7]],
            "hole5": [deck[8], deck[9]],
            "playerList": room.returnPlayerList(),
            "data-type" : "console message",
            "message" : "connected!!! lets go! welcome user: " + x.get("user")
        }
        y = json.dumps(returnMessage)
        print(room.returnPlayerList())
        print(room.returnNumPlayers())
        emit('response',
             {'data': y, 'count': session['receive_count']}, broadcast=True, to=room_code)

@socket_.on("fold_event", namespace="/test")
def fold_message_global(message):
    x = json.loads(message["data"])
    room_code = x["room"]
    room = lobbies[room_code]
    currentPot = room.returnCurrentPot()
    playerList = room.returnPlayerList()
    if (x['user'] == playerList['turn']):
        current = playerList['turn']
        room.addToPlayerList('folded', playerList['turn'])
        print(playerList['folded'])
        if (playerList['turn'] == 5):
            room.updatePlayerList('turn', 1)
        else:
            room.updatePlayerList('turn', playerList['turn']+1)

        while playerList['turn'] in playerList['folded']:
            if (playerList['turn'] == 5):
                room.updatePlayerList('turn', 1)
            else:
                room.updatePlayerList('turn', playerList['turn']+1)
        if (playerList['turn'] == playerList['start_turn']):
            room.updatePlayerList('gameState', playerList['gameState']+1)
            room.updatePlayerList('check', True)
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
            endTheGame(winner, money, room_code)
        else :
            emit('fold_response',
                {'data': y, 'count': session['receive_count']},
                broadcast=True, to=room_code)

@socket_.on("kick_event", namespace="/test")
def kick_message_global(message):
    x = json.loads(message["data"])
    room_code = x["room"]
    room = lobbies[room_code]
    currentPot = room.returnCurrentPot()
    playerList = room.returnPlayerList()

    current = playerList['turn']
    room.addToPlayerList('folded', playerList['turn'])
    if (playerList['turn'] == 5):
        room.updatePlayerList('turn', 1)
    else:
        room.updatePlayerList('turn', playerList['turn']+1)

    while playerList['turn'] in playerList['folded']:
        if (playerList['turn'] == 5):
            room.updatePlayerList('turn', 1)
        else:
            room.updatePlayerList('turn', playerList['turn']+1)

    if (playerList['turn'] == playerList['start_turn']):
        room.updatePlayerList('gameState', playerList['gameState']+1)
        room.updatePlayerList('check', True)
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
        room_code = x.get("room")
        endTheGame(winner, money, room_code)
    else :
        room_code = x.get("room")
        emit('fold_response',
            {'data': y, 'count': session['receive_count']},
            broadcast=True, to=room_code)

@socket_.on("check_event", namespace="/test")
def check_message_global(message):
    x = json.loads(message["data"])
    room_code = x["room"]
    room = lobbies[room_code]
    playerList = room.returnPlayerList()
    current = playerList['turn']
    if (playerList['turn'] == 5):
        room.updatePlayerList('turn', 1)
    else:
        room.updatePlayerList('turn', playerList['turn']+1)

    while playerList['turn'] in playerList['folded']:
        if (playerList['turn'] == 5):
            room.updatePlayerList('turn', 1)
        else:
            room.updatePlayerList('turn', playerList['turn']+1)

    if (playerList['turn'] == playerList['start_turn']):
        room.updatePlayerList('gameState', playerList['gameState']+1)
        room.updatePlayerList('check', True)
    returnMessage = {
        "data-type" : "console message",
        "gameState" : playerList['gameState'],
        "bet" : playerList['check'],
        "current_turn" : current,
        "next_turn" : playerList['turn'],
        "next_user" : playerList[playerList['turn']][0]
    }
    y = json.dumps(returnMessage)
    room_code = x.get("room")
    emit('check_response',
         {'data': y, 'count': session['receive_count']},
         broadcast=True, to=room_code)

@socket_.on("call_event", namespace="/test")
def call_message_global(message):
    x = json.loads(message["data"])
    room_code = x["room"]
    room = lobbies[room_code]
    playerList = room.returnPlayerList()
    current = playerList['turn']
    if (playerList['turn'] == 5):
        room.updatePlayerList('turn', 1)
    else:
        room.updatePlayerList('turn', playerList['turn']+1)

    while playerList['turn'] in playerList['folded']:
        if (playerList['turn'] == 5):
            room.updatePlayerList('turn', 1)
        else:
            room.updatePlayerList('turn', playerList['turn']+1)

    if (playerList['turn'] == playerList['start_turn']):
        room.updatePlayerList('gameState', playerList['gameState']+1)
        room.updatePlayerList('check', True)
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
    room_code = x.get("room")
    emit('call_response',
         {'data': y, 'count': session['receive_count']},
         broadcast=True, to=room_code)

@socket_.on("raise_event", namespace="/test")
def raise_message_global(message):
    x = json.loads(message["data"])
    room_code = x["room"]
    room = lobbies[room_code]
    playerList = room.returnPlayerList()
    current = playerList['turn']
    room.updatePlayerList('check', False)
    room.updatePlayerList('start_turn', playerList['turn'])
    if (playerList['turn'] == 5):
        room.updatePlayerList('turn', 1)
    else:
        room.updatePlayerList('turn', playerList['turn']+1)

    while playerList['turn'] in playerList['folded']:
        if (playerList['turn'] == 5):
            room.updatePlayerList('turn', 1)
        else:
            room.updatePlayerList('turn', playerList['turn']+1)

    room.updatePlayerList('previous_bet', playerList['previous_bet']+100)
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
    room_code = x.get("room")
    emit('raise_response',
         {'data': y, 'count': session['receive_count']},
         broadcast=True, to=room_code)

@socket_.on("update_money", namespace="/test")
def updateMoney(message):
    print("updating money")
    x = json.loads(message["data"])
    updateUserMoney(x['user'], x['new_money'])

@socket_.on("reset", namespace="/test")
def resetter():
    print("reseeting")
    x = lobbies.copy().keys()
    for room_code in x:
        lobbies.pop(room_code)
    lobbies.update({"" : Lobby()})
    # room = lobbies[room_code]
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

    lobby = lobbies(room)

    lobbies(room).updateNumPlayers(0)

    playerList = lobby.returnPlayerList()

    i = 1
    while i < 6:
        addMoney(playerList[i][0])
        i = i+1

    lobbies(room).updatePlayerList({
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
    })

    lobbies(room).updateCurrentPot(0)

    lobbies(room).newSetOfPlayers()

    emit("endTheGame", {'data': y} ,broadcast=True, to=room)


if __name__ == "__main__":
    app.debug = True
    socket_.run(app, debug=True)
