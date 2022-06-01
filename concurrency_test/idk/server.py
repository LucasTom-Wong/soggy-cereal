import random
import websockets
import asyncio

async def listen(ws, path):
    async for message in ws:
        await ws.send("Hi back!")

# async def connected_message(ws, path):
#     # print("Client just connected!")
#     # connected.add(ws)
#     try:
#         async for message in ws:
#             await ws.send("New Connection")
#             # print("Recieved message from client: " + message)
#             # for cos in connected:
#             #     if cos != ws:
#             #         await cos.send("Someone said: " + message)
#     except websockets.exceptions.ConnectionClosed as e:
#         await ws.send("Disconnected")
#         # print(e)

async def random_number(ws, path):
    while True:
        await ws.send(str(int(random.random() * 20)))
        await asyncio.sleep(3)

async def messenger(ws, path):
    while True:
        await ws.send("Baluga")
        await asyncio.sleep(5)

async def full_all(ws, path):
    await asyncio.gather(messenger(ws, path), random_number(ws, path), listen(ws, path))
    # await messenger(ws, path)
    # await random_number(ws, path)
    # await connected_message(ws, path)

start_server = websockets.serve(full_all, "localhost", 8080)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
