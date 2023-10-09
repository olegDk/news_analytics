from dotenv import load_dotenv
import os
import requests
import csv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
OVERVIEW_METRICS = [
    "MarketCapitalization",
    "EBITDA",
    "GrossProfitTTM",
    "RevenueTTM",
    "EPS",
    "PERatio",
    "ProfitMargin",
    "OperatingMarginTTM",
    "QuarterlyEarningsGrowthYOY",
    "QuarterlyRevenueGrowthYOY",
]


def format_to_bln(value_str):
    # Convert the string to a float
    value = float(value_str)

    # Convert to billions
    value_bln = value / 10**9

    # Format the value to have two decimal points
    formatted_value = "{:.2f} bln $".format(value_bln)

    return formatted_value


def get_company_overview(symbol: str) -> dict:
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    r = requests.get(url)
    data = r.json()

    return data


def get_metric_explanation(symbol: str, metric: str) -> str:
    if not symbol:
        return "Please, specify symbol"

    if not metric in OVERVIEW_METRICS:
        return f"Unknown metric, currently supported metrics: {OVERVIEW_METRICS}"

    company_overview = get_company_overview(symbol=symbol)

    metric_value = company_overview.get(
        metric, "No such metric, please try another one"
    )

    if metric == "MarketCapitalization":
        return f"MarketCapitalization of {symbol} is {format_to_bln(metric_value)}"
    elif metric == "EBITDA":
        return f"EBITDA of {symbol} is {format_to_bln(metric_value)}"
    elif metric == "GrossProfitTTM":
        return f"GrossProfitTTM of {symbol} is {format_to_bln(metric_value)}"
    elif metric == "RevenueTTM":
        return f"RevenueTTM of {symbol} is {format_to_bln(metric_value)}"
    elif metric == "EPS":
        return f"EPS of {symbol} is {metric_value} $ per share"
    elif metric == "PERatio":
        return f"PERatio of {symbol} is {metric_value}"
    elif metric == "ProfitMargin":
        return f"ProfitMargin of {symbol} is {float(metric_value) * 100} %"
    elif metric == "QuarterlyEarningsGrowthYOY":
        return (
            f"QuarterlyEarningsGrowthYOY of {symbol} is {float(metric_value) * 100} %"
        )
    elif metric == "QuarterlyRevenueGrowthYOY":
        return f"QuarterlyRevenueGrowthYOY of {symbol} is {float(metric_value) * 100} %"
    elif metric == "ProfitMargin":
        return f"ProfitMargin of {symbol} is {metric_value}"

    return metric_value


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
