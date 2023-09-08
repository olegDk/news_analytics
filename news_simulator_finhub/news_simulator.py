import asyncio
import websockets
import json
import copy
from datetime import datetime
import logging


connected = set()
# Set up logging
LOG_FILENAME = "news_simulator_finhub.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


def update_to_todays_date(data: list):
    new_data = []
    for original_item in data:
        item = copy.deepcopy(original_item)
        updated_news_items = []
        for news_item in item["data"]:
            if "datetime" in news_item:
                original_datetime = datetime.utcfromtimestamp(news_item["datetime"])
                today = datetime.now().replace(
                    hour=original_datetime.hour,
                    minute=original_datetime.minute,
                    second=original_datetime.second,
                    microsecond=original_datetime.microsecond,
                )
                news_item["datetime"] = int(today.timestamp())
                updated_news_items.append(news_item)
        item["data"] = updated_news_items
        new_data.append(item)
    return new_data


async def send_json(websocket, path):
    # Register.
    connected.add(websocket)
    try:
        with open("news_data.json", "r") as f:
            data = json.load(f)

        print("Read data...")
        logging.info(f"First element of data: {data[0]}")

        data = update_to_todays_date(data=data)

        logging.info(f"First element of data: {data[0]}")

        print("Connection established. Sending data immediately.")
        logging.info(f"Connection established. Sending data immediately.")

        if websocket.closed:
            logging.info("WebSocket is closed. Cannot send data.")
            return

        for item in data:
            if websocket.closed:
                logging.info("WebSocket is closed. Cannot send data.")
                return
            if not websocket.closed:
                logging.info(f"Sending message: {item}")
                await websocket.send(json.dumps(item))
                await asyncio.sleep(1)  # wait for 1 second

        # Keep the connection open and wait for further messages
        while True:
            try:
                message = await asyncio.wait_for(
                    websocket.recv(), timeout=2
                )  # 2-second timeout
                if message == "close":
                    break
                elif "subscribe-news" in message:
                    logging.info(f"Ignoring subscription message: {message}")
                    continue
            except asyncio.TimeoutError:
                # No message received within the timeout
                pass

    except Exception as e:
        logging.error(f"Exception: {e}")
    finally:
        # Unregister.
        connected.remove(websocket)


start_server = websockets.serve(send_json, "0.0.0.0", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
