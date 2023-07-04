import asyncio
import websockets
import json
import time


async def send_json(websocket, path):
    with open("news_data.json", "r") as f:
        data = json.load(f)

    for item in data:
        item = {"data": item}
        await websocket.send(json.dumps(item))
        await asyncio.sleep(1)  # wait for 1 second


start_server = websockets.serve(send_json, "0.0.0.0", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
