import requests
import json
from datetime import date

base_url = "http://localhost:8000"

# Update these values to the symbol and date you want to use
symbol = "AAPL"
date = date.today().isoformat()

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
