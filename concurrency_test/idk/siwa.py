import json
import websockets
import asyncio

PORT = 8080

print("Server listening on Port " + str(PORT))

connected = set()

async def echo(ws, path):
    print("Client just connected!")
    connected.add(ws)
    try:
        async for message in ws:
            print("Recieved message from client: " + message)
            for cos in connected:
                if cos != ws:
                    await cos.send("Someone said: " + message)
    except websockets.exceptions.ConnectionClosed as e:
        print("Client disconnected.")
        # print(e)

start_server = websockets.serve(echo, "localhost", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

# if __name__ == "__main__":
#     asyncio.run(main())
