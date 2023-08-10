import asyncio
import websockets
import json
import copy
from datetime import datetime

connected = set()


def update_to_todays_date(data: dict):
    new_data = []
    for original_item in data:
        item = copy.deepcopy(original_item)
        if "timestamp" in item["data"]:
            original_datetime = datetime.fromisoformat(
                item["data"]["timestamp"].replace("Z", "+00:00")
            )
            today = datetime.now().replace(
                hour=original_datetime.hour,
                minute=original_datetime.minute,
                second=original_datetime.second,
                microsecond=original_datetime.microsecond,
                tzinfo=original_datetime.tzinfo,
            )
            item["data"]["timestamp"] = today.isoformat(timespec="microseconds")

            new_data.append(item)

    return new_data


async def send_json(websocket):
    # Register.
    connected.add(websocket)
    try:
        with open("news_data.json", "r") as f:
            data = json.load(f)

        data = update_to_todays_date(data=data)

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
