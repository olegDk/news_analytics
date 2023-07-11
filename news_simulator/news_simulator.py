import asyncio
import websockets
import json

connected = set()


async def send_json(websocket):
    # Register.
    connected.add(websocket)
    try:
        with open("news_data_test.json", "r") as f:
            data = json.load(f)

        while True:
            for item in data:
                for ws in connected:
                    if not ws.closed:
                        print("Sending message...")
                        await ws.send(json.dumps(item))
                await asyncio.sleep(1)  # wait for 1 second
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        # Unregister.
        connected.remove(websocket)


start_server = websockets.serve(send_json, "0.0.0.0", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
