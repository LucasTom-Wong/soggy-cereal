from os import urandom
from flask import Flask, render_template, request, session, redirect
from db import *
import sqlite3, os.path
import json
import urllib
import random

app = Flask(__name__)
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
        return render_template('poker.html')

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

ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
suites = ["C", "D", "H", "S"]
allCards = []

for rank in ranks:
  for suite in suites:
    allCards.append("/static/card_svgs/"+rank + suite + ".svg")

def createCardList(player_num):
    cardList = []
    player = 0
    index = 0
    while (player < player_num):
        cardList.append("/static/card_svgs/back.svg")
        cardList.append("/static/card_svgs/back.svg")
        index+=2
        player+=1
    cardList.append(allCards[index])
    cardList.append(allCards[index+1])
    index+=2
    player+=1
    while (player < 5):
        cardList.append("/static/card_svgs/back.svg")
        cardList.append("/static/card_svgs/back.svg")
        player+=1
    print(cardList)
    return cardList

@app.route("/poker", methods=['GET', 'POST'])
def game():
    return render_template('poker.html', listCards = createCardList(0))


if __name__ == "__main__":
    app.debug = True
    app.run()
