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


async def run():
    nc = NATS()

    # Connect to the NATS server
    await nc.connect("nats:4222")

    connected = False
    while not connected:
        try:
            async with websockets.connect(
                "ws://news_simulator_benzinga:5678",
                max_size=10_000_000_000,
            ) as websocket:
                print("Connected to WebSocket server")
                connected = True

                try:
                    async for message in websocket:
                        payload = json.loads(message)
                        if "content" in payload["data"]:
                            if "securities" in payload["data"]["content"]:
                                securities = [
                                    Security(
                                        symbol=s["symbol"],
                                        exchange=s["exchange"],
                                    )
                                    for s in payload["data"]["content"]["securities"]
                                ]
                                content = Content(
                                    title=BeautifulSoup(
                                        payload["data"]["content"]["title"],
                                        "html.parser",
                                    ).text,
                                    body=BeautifulSoup(
                                        payload["data"]["content"]["body"],
                                        "html.parser",
                                    ).text,
                                    securities=securities,
                                )
                            else:
                                print("No securities in message, skipping.")
                                continue
                        else:
                            print("No content in message, skipping.")
                            continue

                        news = News(
                            content=content,
                            timestamp=payload["data"]["timestamp"],
                            sources=["Benzinga"],  # Add this line
                        )
                        await nc.publish("news", news.SerializeToString())
                        logging.info(f"Published message to NATS: {news}")

                except Exception as e:
                    print(f"Exception in WebSocket for loop: {e}")
                    raise e
        except ConnectionRefusedError:
            print("Connection failed. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Exception in WebSocket with statement: {e}")
            raise e

    print("Exiting run function.")
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
