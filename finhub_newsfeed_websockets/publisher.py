import asyncio
from nats.aio.client import Client as NATS
import os
import json
import websocket
from datetime import datetime
from news_pb2 import News, Content, Security
import time
import logging

LOG_FILENAME = "publisher.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

FINNHUB_TOKEN = os.environ.get("FINNHUB_API_KEY", default="")
nc = NATS()  # Global NATS client


async def connect_to_nats():
    await nc.connect("nats:4222")
    logging.info("Connected to NATS server")


async def on_message_async(payload):
    logging.info(f"Received payload: {payload}")
    if payload["type"] == "news":
        for news_item in payload["data"]:
            securities = [
                Security(
                    symbol=news_item["related"],
                    exchange="NASDAQ",
                )
            ]
            content = Content(
                title=news_item["headline"],
                body=news_item["summary"],
                securities=securities,
            )

            timestamp = (
                datetime.utcfromtimestamp(news_item["datetime"]).isoformat() + "+00:00"
            )

            news = News(
                content=content,
                timestamp=timestamp,
                sources=[news_item["url"]],  # Ensuring sources is a list
            )
            await nc.publish("news", news.SerializeToString())
            logging.info(f"Published message to NATS: {news}")


def on_message(ws, message):
    logging.info(f"Received message from WebSocket: {message}")
    payload = json.loads(message)
    asyncio.get_event_loop().run_until_complete(on_message_async(payload))


def on_error(ws, error):
    logging.error(f"WebSocket Error: {error}")


def on_close(ws):
    logging.info("WebSocket closed")


def on_open(ws):
    logging.info("WebSocket opened")
    asyncio.get_event_loop().run_until_complete(connect_to_nats())
    symbols = ["AAPL", "AMZN", "MSFT", "NVDA"]
    for symbol in symbols:
        ws.send(f'{{"type":"subscribe-news","symbol":"{symbol}"}}')


if __name__ == "__main__":
    print("Starting run function.")
    print("Waiting for nats to start")
    time.sleep(15)
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "ws://news_simulator_finhub:5678",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.on_open = on_open
    ws.run_forever()
