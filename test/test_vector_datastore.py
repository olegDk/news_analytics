import json
from datetime import datetime
import copy
import asyncio
from db_writer.db_clients.vector_datastore_client.pinecone_datastore import (
    PineconeDataStore,
)

# Load the data from the JSON file
with open("test/news_data.json", "r") as f:
    data = json.load(f)


def reset_index(data: dict) -> dict:
    news_data = copy.deepcopy(data)
    # Convert timestamps to datetime objects
    for item in news_data:
        item["timestamp"] = datetime.fromisoformat(
            item["timestamp"].replace("Z", "+00:00")
        )

    # Sort the data by timestamp
    news_data.sort(key=lambda x: x["timestamp"])

    # Reassign id incrementally
    for i, item in enumerate(news_data, start=1):
        item["id"] = i
        item["content"]["id"] = i

    # Convert timestamps back to strings
    for item in news_data:
        item["timestamp"] = item["timestamp"].isoformat()

    return news_data


# data = reset_index(data)

# # Save the data back to the JSON file
# with open("test/news_data_updated_ids.json", "w") as f:
#     json.dump(data, f, indent=4)

pinecone_client = PineconeDataStore()


async def insert_news(news: dict):
    await pinecone_client.insert_news(
        news_id="93",
        document=f'{news["content"]["title"]}-{news["content"]["body"]}',
    )


asyncio.run(insert_news(data[300]))
