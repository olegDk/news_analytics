import os
import asyncpg
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")


class PostgresClient:
    def __init__(self, retries=5, delay=5, min_pool_size=2, max_pool_size=5):
        self.retries = retries
        self.delay = delay
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
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
                    port=POSTGRES_PORT,
                    min_size=self.min_pool_size,  # Minimum number of connection in the pool.
                    max_size=self.max_pool_size,  # Maximum number of connection in the pool.
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

    async def get_or_insert_security(self, symbol, exchange):
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                try:
                    security_id = await conn.fetchval(
                        """
                        SELECT id FROM securities WHERE symbol = $1
                        """,
                        symbol,
                    )

                    if security_id is None:
                        print("====================================")
                        print(security_id)
                        print(symbol)
                        print("====================================")
                        try:
                            security_id = await conn.fetchval(
                                """
                                INSERT INTO securities (symbol, exchange)
                                VALUES ($1, $2)
                                RETURNING id;
                                """,
                                symbol,
                                exchange,
                            )
                        except Exception as e:
                            print("Failed to insert into securities: ", e)
                            raise  # Propagate the exception up
                except Exception as e:
                    print("Failed to get security_id: ", e)
                    raise  # Propagate the exception up

        return security_id

    async def get_summary(self, security_id, date):
        async with self.db_pool.acquire() as conn:
            try:
                summary = await conn.fetchval(
                    """
                    SELECT summary FROM securities_summaries 
                    WHERE security_id = $1 AND date = $2
                    """,
                    security_id,
                    date,
                )
                return summary
            except Exception as e:
                print("Failed to get summary: ", e)
                return None

    async def insert_summary(self, security_id, date, summary):
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        """
                        INSERT INTO securities_summaries (security_id, date, summary)
                        VALUES ($1, $2, $3);
                        """,
                        security_id,
                        date,
                        summary,
                    )
                except Exception as e:
                    print("Failed to insert summary: ", e)
                    raise

    async def update_summary(self, security_id, date, summary):
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        """
                        UPDATE securities_summaries
                        SET summary = $1
                        WHERE security_id = $2 AND date = $3;
                        """,
                        summary,
                        security_id,
                        date,
                    )
                except Exception as e:
                    print("Failed to update summary: ", e)
                    raise

    async def get_summary_by_symbol(self, symbol, date):
        async with self.db_pool.acquire() as conn:
            try:
                summary = await conn.fetchval(
                    """
                    SELECT ss.summary FROM securities AS s
                    INNER JOIN securities_summaries AS ss
                    ON s.id = ss.security_id
                    WHERE s.symbol = $1 AND ss.date = $2
                    """,
                    symbol,
                    date,
                )
                return summary
            except Exception as e:
                print("Failed to get summary by symbol: ", e)
                return None

    async def get_news_by_symbol(self, symbol, date):
        async with self.db_pool.acquire() as conn:
            try:
                news = await conn.fetch(
                    """
                    SELECT n.content FROM news AS n
                    INNER JOIN news_securities AS ns
                    ON n.id = ns.news_id
                    INNER JOIN securities AS s
                    ON s.id = ns.security_id
                    WHERE s.symbol = $1 AND DATE(n.timestamp) = $2
                    """,
                    symbol,
                    date,
                )
                return news
            except Exception as e:
                print("Failed to get news by symbol: ", e)
                return None

    async def close(self):
        await self.db_pool.close()
