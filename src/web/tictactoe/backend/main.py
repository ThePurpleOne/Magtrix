import time
import json
import random
import websocket
from websocket import create_connection, WebSocketConnectionClosedException
import serial

import asyncio
import websockets

async def handle_client(websocket, ser):
    try:
        async for message in websocket:
            message = json.loads(message)
            print(f"Received message: {message}")
            index = message.get('index')
            action = message.get('action')

            # Transform into x, y coordinates
            if index is not None:
                x = index % 3
                y = index // 3
                # Transform into ASCII characters
                x = chr(x + ord('0'))
                y = chr(y + ord('0'))
            else:
                x = chr(3 + ord('0'))
                y = chr(3 + ord('0'))

            if action == 'reset':
                x = chr(3 + ord('0'))
                y = chr(3 + ord('0'))

            START_BYTE = 0x02
            STOP_BYTE = 0x03

            print("Sending data")
            data = [START_BYTE, ord(x), ord(y), STOP_BYTE]
            ser.write(data)

            #time.sleep(2)
            response = ser.readline().decode('utf-8').strip()
            print(f"Received response: {response}")
            await websocket.send("ACK")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        print("Client disconnected")

async def simple_server():
    while True:
        try:
            print("Starting WebSocket server")
            async with websockets.serve(handle_client_with_serial, "localhost", 6789):
                print("WebSocket server running on ws://localhost:6789")
                await asyncio.Future()  # Run forever
        except Exception as e:
            print(f"Server error: {e}. Restarting in 5 seconds...")
            time.sleep(5)

async def handle_client_with_serial(websocket, path):
    while True:
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()

            for port, desc, hwid in sorted(ports):
                ser = serial.Serial(port, 115200)
                print("{}: {} [{}]".format(port, desc, hwid))

        #ser = serial.Serial('/dev/ttyACM0', 115200)


            print("Serial port connected")
            await handle_client(websocket, ser)
        except serial.SerialException as e:
            print(f"Serial port error: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}. Restarting in 5 seconds...")
            time.sleep(5)
        finally:
            if ser and ser.is_open:
                ser.close()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(simple_server())
    except KeyboardInterrupt:
        print("Server shutdown")
