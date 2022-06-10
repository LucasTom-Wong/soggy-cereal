from os import urandom
from flask import Flask, render_template, request, session, redirect, copy_current_request_context
from db import *
from cards import createCardList, allCards
import sqlite3, os.path
import json
import urllib
import random
from flask_socketio import SocketIO, emit, disconnect
from threading import Lock

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

def createLobby():
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
        print("username is:", username)
        return render_template('poker.html', player_list=playerList, username = username, async_mode=socket_.async_mode)
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
        y = json.dumps(returnMessage)
        print(playerList)
        print(numPlayers)
        emit('response',
             {'data': y, 'count': session['receive_count']}, broadcast=True)

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
            endTheGame(winner, money)
        else :
            emit('fold_response',
                {'data': y, 'count': session['receive_count']},
                broadcast=True)

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
    emit('check_response',
         {'data': y, 'count': session['receive_count']},
         broadcast=True)

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
    emit('call_response',
         {'data': y, 'count': session['receive_count']},
         broadcast=True)

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
    emit('raise_response',
         {'data': y, 'count': session['receive_count']},
         broadcast=True)

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
    }

@socket_.on("talking", namespace="/test")
def checkingUser(message):
    emit('checking', {"data":"hi"})

@socket_.on('disconnect')
def test_disconnect():
    print('Client disconnected')

def determineWinner():
    global setOfPlayers
    global playerList
    for player in setOfPlayers:
        if (player not in playerList["folded"]):
            return player
    return "Bob"
def determineMoney():
    global currentPot
    return currentPot;

def endTheGame(winner, money):
    returnMessage = {
        "data-type" : "message",
        "winner" : winner,
        "amountWon" : money
    }
    y = json.dumps(returnMessage)

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
    global currentPot
    currentPot = 0
    global setOfPlayers
    setOfPlayers = set()

    emit("endTheGame", {'data': y} ,broadcast=True)


if __name__ == "__main__":
    app.debug = True
    socket_.run(app, debug=True)
