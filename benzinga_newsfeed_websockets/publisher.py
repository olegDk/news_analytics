import asyncio
from nats.aio.client import Client as NATS
import os
import signal
import json
import websockets
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from news_pb2 import (
    News,
    Content,
    Security,
)  # news_pb2 is the generated module from news.proto

load_dotenv()

BZ_API_KEY = os.environ.get("BZ_API_KEY", default="")


async def run(loop):
    nc = NATS()

    # Connect to the NATS server
    await nc.connect("localhost:4222", loop=loop)
    # await nc.connect("nats:4222", loop=loop)

    async with websockets.connect(
        "wss://api.benzinga.com/api/v1/news/stream?token={key}".format(key=BZ_API_KEY),
        max_size=10_000_000_000,
    ) as websocket:
        # Listen for SIGTERM signal to close WebSocket connection.
        loop.add_signal_handler(signal.SIGTERM, loop.create_task, websocket.close)

        async for message in websocket:
            payload = json.loads(message)

            if "content" in payload["data"]:
                print("content here")
                if "securities" in payload["data"]["content"]:
                    print("securities here")
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
                            payload["data"]["content"]["title"], "html.parser"
                        ).text,
                        body=BeautifulSoup(
                            payload["data"]["content"]["body"], "html.parser"
                        ).text,
                        securities=securities,
                    )
                else:
                    continue
            else:
                continue

            news = News(
                kind=payload["kind"],
                action=payload["data"]["action"],
                id=payload["data"]["id"],
                content=content,
                timestamp=payload["data"]["timestamp"],
            )
            await nc.publish("news", news.SerializeToString())

    await nc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
