import time
import json
import random
import websocket
from websocket import create_connection, WebSocketConnectionClosedException
import serial

import asyncio
import websockets

async def simple_server(websocket, path):
    print("Client connected")
    ser = serial.Serial('/dev/ttyACM0', 115200)

    try:
        async for message in websocket:
            message = json.loads(message)
            print(f"Received message: {message}")
            index = message.get('index')

            # Transform into x, y coordinates
            x = index % 3
            y = index // 3

            # Transform into ASCII characters
            x = chr(x + ord('0'))
            y = chr(y + ord('0'))

            START_BYTE = 0x02
            STOP_BYTE = 0x03
            #x = '1'
            #y = '2'

            print("Sending data")
            data = [START_BYTE, ord(x), ord(y), STOP_BYTE]
            ser.write(data)
            #print(f"Data sent {data}")

            time.sleep(2)
            await websocket.send("ACK")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        print("Client disconnected")

start_server = websockets.serve(simple_server, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
print("Simple WebSocket server running on ws://localhost:6789")
asyncio.get_event_loop().run_forever()


#def handler_receive():
#    websocket_url = "ws://localhost:6789"
#    ws = None

#    while ws is None:
#        try:
#            print(f"Attempting to connect to {websocket_url}...")
#            ws = create_connection(websocket_url)
#            print("WebSocket connected")
#        except ConnectionRefusedError as e:
#            print(f"Connection refused: {e}, retrying in 2 seconds...")
#            time.sleep(2)
#        except Exception as e:
#            print(f"An unexpected error occurred: {e}")
#            time.sleep(2)

#    try:
#        while True:
#            try:
#                result = ws.recv()
#                print(f"Received message: {result}")

#                parsed = json.loads(result)
#                print(f"Received message: {parsed}")

#                # Random time to simulate processing
#                time.sleep(random.randint(1, 3))

#                ws.send("ACK")
#                print("Sent ACK")
            
#            except WebSocketConnectionClosedException:
#                print("Connection closed, attempting to reconnect...")
#                ws = None
#                while ws is None:
#                    try:
#                        ws = create_connection(websocket_url)
#                        print("WebSocket reconnected")
#                    except ConnectionRefusedError as e:
#                        print(f"Connection refused: {e}, retrying in 2 seconds...")
#                        time.sleep(2)
#                    except Exception as e:
#                        print(f"An unexpected error occurred: {e}")
#                        time.sleep(2)

#    except KeyboardInterrupt:
#        print("Closing WebSocket connection")
#        if ws:
#            ws.close()

#handler_receive()



#def handler_receive():
#    ws = create_connection("ws://localhost:6789")

#    while True:
#        result = ws.recv()
#        print(f"Received message: {result}")

#        parsed = json.loads(result)
#        print(f"Received message: {parsed}")

#        # Random time to simulate processing
#        time.sleep(random.randint(1, 3))

#        ws.send("ACK")
#        print("Sent ACK")

#handler_receive()


#async def handler_receive(websocket, path):
#    async for message in websocket:
#        print(f"Received message: {message}")

#        parsed = json.loads(message)

#        print(f"Received message: {parsed}")
        
#        # Random time to simulate processing
#        await asyncio.sleep(random.randint(1, 3))

#        await websocket.send(f"ACK")
#        print("Sent ACK")

#start_server = websockets.serve(handler_receive, "localhost", 6789)

#asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().run_forever()