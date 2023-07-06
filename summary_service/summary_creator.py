import os
import json
import asyncio
from datetime import datetime
from nats.aio.client import Client as NATS
from news_pb2 import News
from db_clients.postgres_client.postgres_client import PostgresClient
import openai_client  # assuming you have a separate module named 'openai_client'


async def run(loop):
    nc = NATS()

    # Connect to the NATS server
    await nc.connect("nats:4222", loop=loop)

    # Create a connection to your databases
    db_client = PostgresClient()
    await db_client.connect()

    async def message_handler(msg):
        subject = msg.subject
        data = News()
        data.ParseFromString(msg.data)
        print(f"Received a message on '{subject}':\n{data}")

        # For each security, check if a summary for today already exists,
        # if not, create a new one, otherwise update the existing one
        for security in data.content.securities:
            symbol = security.symbol
            today = datetime.date.today()
            news_text = f"{data.content.title} - {data.content.body}"

            security_id = await db_client.get_security_id(symbol)
            existing_summary = await db_client.get_summary(security_id, today)

            if existing_summary is None:
                # Create a new summary
                summary = openai_client.create_summary(news_text)
                await db_client.insert_summary(security_id, today, summary)
            else:
                # Update the existing summary
                updated_summary = openai_client.update_summary(
                    existing_summary, news_text
                )
                await db_client.update_summary(security_id, today, updated_summary)

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
