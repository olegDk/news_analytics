import asyncio
from nats.aio.client import Client as NATS
from news_pb2 import News  # news_pb2 is the generated module from news.proto
from db_clients.postgres_client.postgres_client import PostgresClient
from db_clients.vector_datastore_client.pinecone_datastore import PineconeDataStore


async def run(loop):
    nc = NATS()

    # Connect to the NATS server
    # await nc.connect("localhost:4222", loop=loop)
    await nc.connect("nats:4222", loop=loop)

    # Create a connection to your databases
    db_client = PostgresClient()
    await db_client.connect()

    pinecone_client = PineconeDataStore()

    async def message_handler(msg):
        subject = msg.subject
        data = News()
        data.ParseFromString(msg.data)
        print(f"Received a message on '{subject}':\n{data}")

        # Insert the data into your database
        try:
            news_id = await db_client.insert_news(data)
            _ = await pinecone_client.insert_news(
                str(news_id), f"{data.content.title} - {data.content.body}"
            )
        except Exception as e:
            print(e)
            print("Failed to insert news")

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
