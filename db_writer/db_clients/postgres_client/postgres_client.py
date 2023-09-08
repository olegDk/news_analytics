import os
import asyncpg
import time
from typing import List
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
                        INSERT INTO news (title, content, timestamp)
                        VALUES ($1, $2, $3)
                        RETURNING id;
                        """,
                        data.content.title,
                        data.content.body,
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

                # Insert sources data
                for source in data.sources:
                    try:
                        await conn.execute(
                            """
                            INSERT INTO news_sources (news_id, source)
                            VALUES ($1, $2)
                            ON CONFLICT (news_id, source) DO NOTHING;
                            """,
                            news_id,
                            source,
                        )
                    except Exception as e:
                        print("Failed to insert into news_sources: ", e)
                        raise

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
                # Fetching the summary.
                summary_record = await conn.fetchrow(
                    """
                    SELECT ss.summary, ss.date FROM securities AS s
                    INNER JOIN securities_summaries AS ss
                    ON s.id = ss.security_id
                    WHERE s.symbol = $1 AND ss.date = $2
                    """,
                    symbol,
                    date,
                )

                if not summary_record:
                    return None

                # Fetching related news articles for the summary.
                news_records = await conn.fetch(
                    """
                    SELECT n.content, n.timestamp, nsrc.source 
                    FROM news_securities AS ns
                    INNER JOIN news AS n ON ns.news_id = n.id
                    INNER JOIN news_sources AS nsrc ON n.id = nsrc.news_id
                    WHERE ns.security_id = (
                        SELECT id FROM securities WHERE symbol = $1
                    ) AND DATE(n.timestamp) = $2
                    """,
                    symbol,
                    date,
                )

                return {"summary": summary_record, "news": news_records}

            except Exception as e:
                print("Failed to get summary by symbol: ", e)
                return None

    async def get_news_by_symbol(self, symbol, date):
        async with self.db_pool.acquire() as conn:
            try:
                # Fetch news content and timestamp
                news_records = await conn.fetch(
                    """
                    SELECT n.id, n.content, n.timestamp FROM news AS n
                    INNER JOIN news_securities AS ns
                    ON n.id = ns.news_id
                    INNER JOIN securities AS s
                    ON s.id = ns.security_id
                    WHERE s.symbol = $1 AND DATE(n.timestamp) = $2
                    """,
                    symbol,
                    date,
                )

                # Create a list to store the final news records with sources
                final_news_records = []

                # Fetch sources for each news record and add to final_news_records
                for record in news_records:
                    sources = await conn.fetch(
                        """
                        SELECT source FROM news_sources
                        WHERE news_id = $1
                        """,
                        record["id"],
                    )
                    # Create a new dictionary for each news record with sources added
                    news_with_sources = {
                        "id": record["id"],
                        "content": record["content"],
                        "timestamp": record["timestamp"],
                        "sources": [src["source"] for src in sources],
                    }
                    final_news_records.append(news_with_sources)

                return final_news_records

            except Exception as e:
                print("Failed to get news by symbol: ", e)
                return None

    async def get_news_details_by_source_ids(self, source_ids: List[int]):
        async with self.db_pool.acquire() as conn:
            # Fetch news content and timestamp for the provided news_ids (source_ids)
            news_records = await conn.fetch(
                """
                SELECT id, content, timestamp FROM news
                WHERE id = ANY($1)
                """,
                source_ids,
            )

            # Create a list to store the final news records with their sources
            final_news_records = []

            for record in news_records:
                # Fetch sources for each news record
                sources = await conn.fetch(
                    """
                    SELECT source FROM news_sources
                    WHERE news_id = $1
                    """,
                    record["id"],
                )

                news_details = {
                    "content": record["content"],
                    "sources": [src["source"] for src in sources],
                    "timestamp": record[
                        "timestamp"
                    ].isoformat(),  # Convert datetime to ISO string format
                }

                final_news_records.append(news_details)

            return final_news_records

    async def close(self):
        await self.db_pool.close()
