import random
import websockets
import asyncio
import json

connected_people = set()

async def listen(ws, path):
    async for message in ws:
        for users in connected_people.copy():
            if (users == ws): #sends if user that sent message
                await users.send("Hi back!")
            else:
                await users.send("Hi there!")
        # await ws.send("Hi back!")

async def random_number(ws, path):
    while True:
        response = str(int(random.random()*20))
        for users in connected_people.copy(): #sends every user
            await users.send(response)
        await asyncio.sleep(3)

async def messenger(ws, path):
    while True:
        await ws.send("Baluga")
        await asyncio.sleep(5)

async def full_all(ws, path):
    connected_people.add(ws)
    for users in connected_people.copy():
        if (users != ws):
            await users.send("New User has joined")
    try:
        await asyncio.gather(messenger(ws, path), random_number(ws, path), listen(ws, path))
        # for user in connected_people.copy():
        #     await asyncio.gather(messenger(user, path), random_number(user, path), listen(user, path))
    except websockets.exceptions.ConnectionClosed as e:
        connected_people.remove(ws)
        for users in connected_people.copy():
            await users.send("User has left")
    # await messenger(ws, path)
    # await random_number(ws, path)
    # await connected_message(ws, path)

start_server = websockets.serve(full_all, "localhost", 8080)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
