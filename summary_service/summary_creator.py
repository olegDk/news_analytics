import os
import json
import asyncio
from datetime import datetime
import logging
from nats.aio.client import Client as NATS
from news_pb2 import News
from db_clients.postgres_client.postgres_client import PostgresClient
from analytics.aiclient.openai_client import create_summary, update_summary

# Set up logging
LOG_FILENAME = "summary_creator.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


async def run(loop):
    nc = NATS()

    # Connect to the NATS server
    await nc.connect("nats:4222", loop=loop)

    # Create a connection to your databases
    db_client = PostgresClient()
    await db_client.connect()

    async def message_handler(msg):
        try:
            subject = msg.subject
            data = News()
            data.ParseFromString(msg.data)
            logging.info(f"Received a message on '{subject}':\n{data}")

            # For each security, check if a summary for today already exists,
            # if not, create a new one, otherwise update the existing one
            for security in data.content.securities:
                symbol = security.symbol
                exchange = security.exchange
                today = datetime.today().date()
                news_text = f"{data.content.title} - {data.content.body}"

                security_id = await db_client.get_or_insert_security(symbol, exchange)
                existing_summary = await db_client.get_summary(security_id, today)

                if existing_summary is None:
                    # Create a new summary
                    summary = create_summary(news_text)
                    await db_client.insert_summary(security_id, today, summary)
                else:
                    # Update the existing summary
                    updated_summary = update_summary(existing_summary, news_text)
                    await db_client.update_summary(security_id, today, updated_summary)

        except Exception as e:
            logging.error(f"Error in message_handler: {str(e)}", exc_info=True)

    sid = await nc.subscribe("news", cb=message_handler)

    try:
        await asyncio.sleep(999999)
    except asyncio.CancelledError:
        logging.warning("Asyncio sleep cancelled")
    finally:
        await nc.unsubscribe(sid)
        await nc.close()
        await db_client.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run(loop))
        loop.close()
    except Exception as e:
        logging.critical(f"Unhandled exception: {str(e)}", exc_info=True)
