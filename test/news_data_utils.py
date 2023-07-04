import json
from datetime import datetime
import copy

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


def refactor_json(data: dict):
    # Refactor the data
    news_data = []
    for item in data:
        news_item = copy.deepcopy(item)

        # Extract the 'kind' key and remove it from the original dict
        kind = news_item.pop("kind")

        # Wrap the rest of the dict in a 'data' key
        news_data.append({"kind": kind, "data": news_item})

    return news_data


# data = reset_index(data)
# data = refactor_json(data=data)

# with open("test/news_data.json", "w") as f:
#     json.dump(data, f, indent=4)
