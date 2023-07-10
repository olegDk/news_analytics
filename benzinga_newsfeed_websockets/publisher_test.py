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

load_dotenv()

BZ_API_KEY = os.environ.get("BZ_API_KEY", default="")


async def run():
    nc = NATS()

    # Connect to the NATS server
    await nc.connect("localhost:4222")

    connected = False
    while not connected:
        # print("Sleeping for 5 seconds to give time for news simulator to start")
        # time.sleep(5)
        try:
            async with websockets.connect(
                "ws://localhost:5678",
                max_size=10_000_000_000,
            ) as websocket:
                print("Connected to WebSocket server")
                connected = True

                try:
                    async for message in websocket:
                        print("Received message:", message)
                        payload = json.loads(message)
                        if "content" in payload["data"]:
                            if "securities" in payload["data"]["content"]:
                                securities = [
                                    Security(
                                        symbol=s["symbol"],
                                        exchange=s["exchange"],
                                        primary=s["primary"],
                                    )
                                    for s in payload["data"]["content"]["securities"]
                                ]
                                content = Content(
                                    id=payload["data"]["content"]["id"],
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
                            kind=payload["kind"],
                            action=payload["data"]["action"],
                            id=payload["data"]["id"],
                            content=content,
                            timestamp=payload["data"]["timestamp"],
                        )
                        print(news.SerializeToString())
                        await nc.publish("news", news.SerializeToString())
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
        asyncio.run(run())
    except Exception as e:
        print(f"Exception in run: {e}")
    finally:
        print("Exiting main.")
