import asyncio
import websockets
import json
import time

async def handler_receive(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")

        parsed = json.loads(message)

        print(f"Received message: {parsed}")
        
        time.sleep(5)

        await websocket.send(f"ACK")

start_server = websockets.serve(handler_receive, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()