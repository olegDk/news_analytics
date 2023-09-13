from dotenv import load_dotenv
import os
import requests

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
        return f"QuarterlyEarningsGrowthYOY of {symbol} is {metric_value} %"
    elif metric == "QuarterlyRevenueGrowthYOY":
        return f"QuarterlyRevenueGrowthYOY of {symbol} is {metric_value}"
    elif metric == "ProfitMargin":
        return f"ProfitMargin of {symbol} is {metric_value}"

    return metric_value
