import asyncio
import websockets
import json
import time
import random

async def handler_receive(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")

        parsed = json.loads(message)

        print(f"Received message: {parsed}")
        
        # Random time to simulate processing
        await asyncio.sleep(random.randint(1, 3))

        await websocket.send(f"ACK")
        print("Sent ACK")

start_server = websockets.serve(handler_receive, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()