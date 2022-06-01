import sqlite3
import random

DB_FILE="users.db"

db = sqlite3.connect(DB_FILE)
c = db.cursor()

command = """CREATE TABLE IF NOT EXISTS users(
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    ID INTEGER NOT NULL)
"""
c.execute(command)

command2 = """CREATE TABLE IF NOT EXISTS profiles(
    ID INTEGER NOT NULL,
    wins INTEGER NOT NULL,
    losses INTEGER NOT NULL,
    money INTEGER NOT NULL,
    timesBroke INTEGER NOT NULL)
"""
c.execute(command2)


def addUser(username, password):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("INSERT INTO users VALUES(?, ?, ?)", (username, password, createID()))
    db.commit()
    db.close()

def createID():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT ID FROM users")
    idList = c.fetchall()
    id = random.randint(10000, 99999)
    while id in idList:
        id = random.randint(10000, 99999)
    db.commit()
    db.close()


def makeLoginsDict():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT * FROM logins")
    logininfo = c.fetchall()

    loginsinfo = {} # create a dictionary for all the login information

    for login in logininfo:
        loginsinfo[login[0]] = login[1]

    return loginsinfo
    db.commit()
    db.close()

def checkUser(username):
    loginsinfo = makeLoginsDict()
    return username in loginsinfo.keys()

def checkUserPass(username, password):
    loginsinfo = makeLoginsDict()
    return (username in loginsinfo.keys()) and (loginsinfo[username] == password)
