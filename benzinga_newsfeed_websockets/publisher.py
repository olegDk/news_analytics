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

    await nc.connect("nats:4222", loop=loop)

    async with websockets.connect(
        "wss://api.benzinga.com/api/v1/news/stream?token={key}".format(key=BZ_API_KEY),
        max_size=10_000_000_000,
    ) as websocket:
        # Listen for SIGTERM signal to close WebSocket connection.
        loop.add_signal_handler(signal.SIGTERM, loop.create_task, websocket.close)

        async for message in websocket:
            payload = json.loads(message)

            if "content" in payload["data"]:
                securities = [
                    Security(
                        symbol=s["symbol"], exchange=s["exchange"], primary=s["primary"]
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
                # No content in this message, skip or use a default Content message.
                continue  # or replace with some default Content creation code.

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
