import random
import websockets
import asyncio
import json

connected_people = set()

async def listen(ws, path):
    async for message in ws:
        temp_dict = json.loads(message)
        if (temp_dict.get("data-type") == "button-response"):
            if (temp_dict.get("value") == "hello-message"):
                await respond_hi(ws, path, temp_dict)
        if (temp_dict.get("data-type") == "joining"):
            if (ws not in connected_people):
                connected_people.add(ws)
                for users in connected_people.copy():
                    if (users != ws):
                        data = {
                            "data-type" : "text-return",
                            "data" : "New User has joined"
                        }
                        x = json.dumps(data)
                        await users.send(x)
                await join_user(ws, path)
            else:
                data = {
                    "data-type" : "error",
                    "error" : "Already Joined!"
                }
                x = json.dumps(data)
                await ws.send(x)

async def respond_hi(ws, path, message):
    for users in connected_people.copy():
        if (users == ws): #sends if user that sent message
            data = {
                "data-type" : "text-return",
                "data" : "Hi back from server"
            }
            x = json.dumps(data)
            await users.send(x)
        else:
            data = {
                "data-type" : "text-return",
                "data" : message.get("user") + " says hi."
            }
            x = json.dumps(data)
            await users.send(x)

async def join_user(ws, path):
    number_of_users = len(connected_people)
    data = {
        "data-type" : "user-num-return",
        "user-num" : number_of_users
    }
    x = json.dumps(data)
    await ws.send(x)

async def random_number(ws, path):
    while True:
        response = str(int(random.random()*20))
        data = {
            "data-type" : "text-return",
            "data" : response
        }
        x = json.dumps(data)
        for users in connected_people.copy(): #sends every user
            await users.send(x)
        await asyncio.sleep(3)

async def messenger(ws, path):
    while True:
        data = {
            "data-type" : "text-return",
            "data" : "Baluga"
        }
        x = json.dumps(data)

        await ws.send(x)
        await asyncio.sleep(5)

async def full_all(ws, path):
    try:
        # await asyncio.gather(messenger(ws, path), random_number(ws, path), listen(ws, path))
        await asyncio.gather(listen(ws, path))
        # for user in connected_people.copy():
        #     await asyncio.gather(messenger(user, path), random_number(user, path), listen(user, path))
    except websockets.exceptions.ConnectionClosed as e:
        connected_people.remove(ws)
        # for users in connected_people.copy():
        #     if (users != ws):
        #         data = {
        #             "data-type" : "text-return",
        #             "data" : "User has left"
        #         }
        #         x = json.dumps(data)
        #         await users.send(x)
        #breaks
    # await messenger(ws, path)
    # await random_number(ws, path)
    # await connected_message(ws, path)

start_server = websockets.serve(full_all, "localhost", 8080)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
