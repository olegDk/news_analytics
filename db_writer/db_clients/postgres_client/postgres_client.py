import os
import asyncpg
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = "postgres"


class PostgresClient:
    def __init__(self, retries=5, delay=5):
        self.retries = retries
        self.delay = delay
        self.db_pool = None

    async def connect(self):
        for i in range(self.retries):
            print(f"Establishing postgres connection, attempt {i + 1}...")
            try:
                self.db_pool = await asyncpg.create_pool(
                    user=POSTGRES_USER,
                    password=POSTGRES_PASSWORD,
                    database=POSTGRES_DB,
                    host=POSTGRES_HOST,
                )
                return
            except Exception:
                print(
                    f"Failed to connect to database, sleeping for {self.delay} seconds..."
                )
                if i < self.retries - 1:  # i is zero indexed
                    time.sleep(self.delay)  # wait before trying to reconnect
                else:
                    raise

    async def insert_news(self, data):
        news_id = None
        async with self.db_pool.acquire() as conn:
            # Begin a transaction
            async with conn.transaction():
                # Insert news data
                timestamp = datetime.fromisoformat(
                    data.timestamp.replace("Z", "+00:00")
                )
                timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)

                try:
                    news_id = await conn.fetchval(
                        """
                        INSERT INTO news (kind, action, content, timestamp)
                        VALUES ($1, $2, $3, $4)
                        RETURNING id;
                        """,
                        data.kind,
                        data.action,
                        f"{data.content.title} - {data.content.body}",
                        timestamp,
                    )
                except Exception as e:
                    print("Failed to insert into news: ", e)
                    raise  # Propagate the exception up

                # Insert securities data
                for s in data.content.securities:
                    # Try to get the id of the security if it already exists
                    security_id = await conn.fetchval(
                        """
                        SELECT id FROM securities WHERE symbol = $1
                        """,
                        s.symbol,
                    )

                    # If security_id is None, it means the security doesn't exist yet
                    if security_id is None:
                        try:
                            security_id = await conn.fetchval(
                                """
                                INSERT INTO securities (symbol, exchange)
                                VALUES ($1, $2)
                                RETURNING id;
                                """,
                                s.symbol,
                                s.exchange,
                            )
                        except Exception as e:
                            print("Failed to insert into securities: ", e)
                            raise  # Propagate the exception up

                    # Link the news and security in the join table
                    try:
                        await conn.execute(
                            """
                            INSERT INTO news_securities (news_id, security_id)
                            VALUES ($1, $2)
                            ON CONFLICT (news_id, security_id) DO NOTHING;
                            """,
                            news_id,
                            security_id,
                        )
                    except Exception as e:
                        print("Failed to insert into news_securities: ", e)
                        raise  # Propagate the exception up

        return news_id

    async def close(self):
        await self.db_pool.close()