import requests
import json
from datetime import date

base_url = "http://localhost:8000"
# base_url = "http://165.22.191.68:8000"

# Update these values to the symbol and date you want to use
symbol = "ITW"
date = date(year=2023, month=9, day=13).isoformat()

headers = {"Content-type": "application/json", "Accept": "text/plain"}

# For getting news
response = requests.post(
    f"{base_url}/get-news",
    data=json.dumps({"symbol": symbol, "date": date}),
    headers=headers,
)
print(response.json())

# For getting summaries
response = requests.post(
    f"{base_url}/get-summary",
    data=json.dumps({"symbol": symbol, "date": date}),
    headers=headers,
)
print(response.json())
