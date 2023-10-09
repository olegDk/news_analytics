from dotenv import load_dotenv
import os
import requests
import csv
import requests

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey={ALPHA_VANTAGE_API_KEY}"
r = requests.get(url)
data = r.json()

print(data.keys())


def fetch_ipo_data():
    # Load API key from environment variables
    load_dotenv()
    ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

    CSV_URL = f"https://www.alphavantage.co/query?function=IPO_CALENDAR&apikey={ALPHA_VANTAGE_API_KEY}"

    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode("utf-8")
        cr = csv.reader(decoded_content.splitlines(), delimiter=",")
        my_list = list(cr)

    return my_list


def get_ipo_calendar(ipoDate: str = None):
    my_list = fetch_ipo_data()

    headers = my_list[0]
    if ipoDate:
        data_rows = [
            row for row in my_list[1:] if row[headers.index("ipoDate")] == ipoDate
        ]
    else:
        data_rows = my_list[1:]

    output = []
    for idx, row in enumerate(data_rows, start=1):
        row_details = ", ".join([f"{headers[i]}: {item}" for i, item in enumerate(row)])
        output.append(f"{idx}. {row_details}")

    return "\n".join(output)


# Test the function
print(get_ipo_calendar())

ipoDate = "2023-10-09"
print(get_ipo_calendar(ipoDate))
