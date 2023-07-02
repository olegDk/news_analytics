import asyncio
import asyncpg
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5433"

print(f"PostgreSQL credentials: user={POSTGRES_USER} password={POSTGRES_PASSWORD}")


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
                    port=POSTGRES_PORT,
                )
                return
            except Exception as e:
                print(e)
                print(
                    f"Failed to connect to database, sleeping for {self.delay} seconds..."
                )
                if i < self.retries - 1:  # i is zero indexed
                    time.sleep(self.delay)  # wait before trying to reconnect
                else:
                    raise

    async def fetch_news(self):
        async with self.db_pool.acquire() as conn:
            # Fetch all news
            news_records = await conn.fetch(
                """
                SELECT * FROM news;
                """
            )

            # Initialize a list to hold the news data
            news_list = []

            # Loop over each news
            for news in news_records:
                # Fetch all securities associated with this news
                securities_records = await conn.fetch(
                    """
                    SELECT s.* FROM securities s
                    INNER JOIN news_securities ns ON ns.security_id = s.id
                    WHERE ns.news_id = $1;
                    """,
                    news["id"],
                )

                # Build a list of securities
                securities = [
                    {
                        "symbol": s["symbol"],
                        "exchange": s["exchange"],
                        "primary": True,
                    }  # assuming all securities as primary
                    for s in securities_records
                ]

                # Build the news data
                news_data = {
                    "kind": news["kind"],
                    "action": news["action"],
                    "id": news["id"],
                    "content": {
                        "id": news[
                            "id"
                        ],  # assuming the same id for content as for the news
                        "title": news["content"].split(" - ")[
                            0
                        ],  # assuming the title is the first part of the content
                        "body": news["content"].split(" - ")[
                            1
                        ],  # assuming the body is the second part of the content
                        "securities": securities,
                    },
                    "timestamp": news["timestamp"].isoformat()
                    + "Z",  # converting the timestamp to isoformat and appending "Z" to match the format
                }

                # Append the news data to the list
                news_list.append(news_data)

            # Return the list of news data
            return news_list

    async def close(self):
        await self.db_pool.close()


async def main():
    client = PostgresClient()
    await client.connect()

    news_data = await client.fetch_news()
    await client.close()

    # Load existing data
    try:
        with open("news_data.json", "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    # Merge new data with existing data
    merged_data = existing_data + news_data

    # Save to a JSON file
    with open("news_data.json", "w") as f:
        json.dump(merged_data, f, default=str)

    print("News data saved to news_data.json")


# Run the main function
asyncio.run(main())
