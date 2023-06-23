import os
import asyncio
import asyncpg
from nats.aio.client import Client as NATS
from news_pb2 import News  # news_pb2 is the generated module from news.proto
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.environ.get("POSTGRES_USER", default="")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", default="")
POSTGRES_DB = os.environ.get("POSTGRES_DB", default="")


async def run(loop):
    nc = NATS()

    # Connect to the NATS server
    await nc.connect("nats:4222", loop=loop)

    # Create a connection pool to your database
    db_pool = await asyncpg.create_pool(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        host="postgres",
    )

    async def message_handler(msg):
        subject = msg.subject
        data = News()
        data.ParseFromString(msg.data)
        print(f"Received a message on '{subject}':\n{data}")

        # Insert the data into your database
        async with db_pool.acquire() as conn:
            # Begin a transaction
            async with conn.transaction():
                # Insert news data
                result = await conn.execute(
                    """
                    INSERT INTO news (kind, action, content, timestamp)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id;
                    """,
                    data.kind,
                    data.action,
                    f"{data.content.title} - {data.content.body}",
                    data.timestamp,
                )

                # Get the id of the news we just inserted
                news_id = result.split()[-1]

                # Insert securities data
                for s in data.content.securities:
                    try:
                        result = await conn.execute(
                            """
                            INSERT INTO securities (symbol, exchange)
                            VALUES ($1, $2)
                            ON CONFLICT (symbol) DO NOTHING
                            RETURNING id;
                            """,
                            s.symbol,
                            s.exchange,
                        )
                    except Exception as e:
                        print(e)
                        continue

                    # Get the id of the security we just inserted
                    security_id = result.split()[-1]

                    # Link the news and security in the join table
                    try:
                        await conn.execute(
                            """
                            INSERT INTO news_securities (news_id, security_id)
                            VALUES ($1, $2);
                            """,
                            news_id,
                            security_id,
                        )
                    except Exception as e:
                        print(e)
                        continue

    sid = await nc.subscribe("news", cb=message_handler)

    try:
        await asyncio.sleep(999999)
    except asyncio.CancelledError:
        pass
    finally:
        await nc.unsubscribe(sid)
        await nc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
