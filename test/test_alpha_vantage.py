from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey={ALPHA_VANTAGE_API_KEY}"
r = requests.get(url)
data = r.json()

print(data.keys())


# def fetch_data(symbol):
#     API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"  # Replace with your API Key
#     BASE_URL = "https://www.alphavantage.co/query"

#     # Fetch the company overview metrics
#     response = requests.get(
#         BASE_URL, params={"function": "OVERVIEW", "symbol": symbol, "apikey": API_KEY}
#     )

#     data = response.json()

#     # Extracting specific metrics from the data
#     revenue_growth = data.get("QuarterlyRevenueGrowthYOY", "Data not available")
#     profit_margin = data.get("ProfitMargin", "Data not available")
#     debt_to_equity = data.get("DebtToEquityRatio", "Data not available")
#     free_cash_flow = data.get("FreeCashFlow", "Data not available")
#     pe_ratio = data.get("PERatio", "Data not available")

#     print(f"Revenue Growth: {revenue_growth}")
#     print(f"Profit Margin: {profit_margin}")
#     print(f"Debt-to-Equity Ratio: {debt_to_equity}")
#     print(f"Free Cash Flow: {free_cash_flow}")
#     print(f"Price-to-Earnings Ratio (P/E): {pe_ratio}")


# if __name__ == "__main__":
#     ticker_symbol = input(
#         "Enter the ticker symbol of the company (e.g. AAPL for Apple): "
#     )
#     fetch_data(ticker_symbol)
