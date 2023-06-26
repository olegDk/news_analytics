# main.py

import asyncio
from nats.aio.client import Client as NATS
from news_pb2 import News  # news_pb2 is the generated module from news.proto
from postgres_client import PostgresClient


async def run(loop):
    nc = NATS()

    # Connect to the NATS server
    await nc.connect("localhost:4222", loop=loop)
    # await nc.connect("nats:4222", loop=loop)

    # # Create a connection to your database
    # db_client = PostgresClient()
    # await db_client.connect()

    async def message_handler(msg):
        subject = msg.subject
        data = News()
        data.ParseFromString(msg.data)
        print(f"Received a message on '{subject}':\n{data}")

        # # Insert the data into your database
        # await db_client.insert_news(data)

    sid = await nc.subscribe("news", cb=message_handler)

    try:
        await asyncio.sleep(999999)
    except asyncio.CancelledError:
        pass
    finally:
        await nc.unsubscribe(sid)
        await nc.close()
        await db_client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
