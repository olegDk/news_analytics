import asyncio
from nats.aio.client import Client as NATS
import os
import json
import websockets
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from news_pb2 import (
    News,
    Content,
    Security,
)  # news_pb2 is the generated module from news.proto
import logging

LOG_FILENAME = "publisher.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

load_dotenv()

BZ_API_KEY = os.environ.get("BZ_API_KEY", default="")
uri = "wss://api.benzinga.com/api/v1/news/stream?token={key}".format(key=BZ_API_KEY)


async def run():
    nc = NATS()
    await nc.connect("nats:4222")

    connected = False
    while not connected:
        try:
            async with websockets.connect(uri, max_size=10_000_000_000) as websocket:
                logging.info("Connected to WebSocket server")
                connected = True

                try:
                    async for message in websocket:
                        try:
                            # Log received message
                            logging.debug(f"Received message: {message}")
                            payload = json.loads(message)

                            # Check if 'data' and 'content' exist in payload
                            data = payload.get("data")
                            if not data or "content" not in data:
                                logging.warning("No content in message, skipping.")
                                continue

                            content_data = data["content"]
                            securities_data = content_data.get("securities", [])

                            securities = [
                                Security(symbol=s["symbol"], exchange=s["exchange"])
                                for s in securities_data
                            ]
                            logging.info(f"Initialized securities: {securities}")

                            content = Content(
                                title=BeautifulSoup(
                                    content_data.get("title", ""), "html.parser"
                                ).text,
                                body=BeautifulSoup(
                                    content_data.get("body", ""), "html.parser"
                                ).text,
                                securities=securities,
                            )
                            logging.info(f"Initialized content: {content}")

                            news = News(
                                content=content,
                                timestamp=data["timestamp"],
                                sources=["Benzinga"],
                            )
                            await nc.publish("news", news.SerializeToString())
                            logging.info(f"Published message to NATS: {news}")

                        except json.JSONDecodeError as je:
                            logging.error(
                                f"Error decoding JSON: {je}. Message: {message}"
                            )
                        except KeyError as ke:
                            logging.error(
                                f"Missing expected key: {ke}. Message: {message}"
                            )
                        except Exception as e:
                            logging.error(f"An error occurred: {e}. Message: {message}")

                except Exception as e:
                    logging.error(f"Exception in WebSocket for loop: {e}")
                    raise e

        except ConnectionRefusedError:
            logging.warning("Connection failed. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Exception in WebSocket with statement: {e}")
            raise e

    logging.info("Exiting run function.")
    await nc.close()


if __name__ == "__main__":
    try:
        print("Starting run function.")
        print("Waiting for nats to start")
        time.sleep(15)
        asyncio.run(run())
    except Exception as e:
        print(f"Exception in run: {e}")
    finally:
        print("Exiting main.")
