import json
import os
from benzinga import news_data
from dotenv import load_dotenv
from datetime import datetime, timezone
from bs4 import BeautifulSoup

load_dotenv()


def get_cleaned_text(element):
    return " ".join(
        child.get_text()
        for child in element.children
        if child.name and child.name not in ["script", "style"]
    )


def parse_benzinga(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract all <p> tags
    paragraphs = soup.find_all("p")

    # Filter out paragraphs that might not be part of the main content
    cleaned_paragraphs = [p.get_text() for p in paragraphs if not p.attrs.get("style")]

    # Join the cleaned paragraphs to form the cleaned body
    cleaned_body = " ".join(cleaned_paragraphs)

    if not cleaned_body:
        print("DEBUG: Cleaned body is empty!")
        return ""

    return cleaned_body


class CustomNewsData:
    def __init__(self, api_key):
        self.paper = news_data.News(api_key)

    def fetch_all_news(self, **kwargs):
        all_news = []
        page = 0
        while True:
            response = self.paper.news(page=page, **kwargs)
            if not response:
                break
            all_news.extend(response)
            page += 1
        return all_news

    def format_news(self, news_items):
        formatted_news = []
        for item in news_items:
            dt = datetime.strptime(item["created"], "%a, %d %b %Y %H:%M:%S %z")
            formatted_timestamp = dt.astimezone(timezone.utc).isoformat()
            # Parse the body content using the parse_benzinga function
            cleaned_body = parse_benzinga(item["body"])

            formatted_item = {
                "kind": "News/v1",
                "data": {
                    "action": "Created",
                    "id": item["id"],
                    "content": {
                        "id": item["id"],
                        "title": item["title"],
                        "body": cleaned_body,
                        "securities": [
                            {
                                "symbol": stock["name"],
                                "exchange": "NASDAQ",
                                "primary": True,
                            }
                            for stock in item["stocks"]
                        ],
                    },
                    "timestamp": formatted_timestamp,
                },
            }
            formatted_news.append(formatted_item)
        return formatted_news

    def save_to_file(self, data, filename="history_data/news_data.json"):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == "__main__":
    api_key = os.environ.get("BZ_API_KEY")
    custom_paper = CustomNewsData(api_key)
    all_news = custom_paper.fetch_all_news(
        display_output="full",
        company_tickers="AAPL, TSLA",
        date_from="2023-08-01",
        date_to="2023-09-14",
    )
    formatted_news = custom_paper.format_news(all_news)
    custom_paper.save_to_file(formatted_news)
