from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit, join_room, leave_room
import random
import websockets
import asyncio
import json

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on('connect')
def test_connect():
    emit('after connect',  {'data':'Lets dance'})

@socketio.on('Slider value changed')
def value_changed(message):
    message['who'] = message['data']
    emit('update value', message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
