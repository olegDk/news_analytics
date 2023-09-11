import os
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv
from datetime import datetime, timedelta
import arrow


load_dotenv()


def convert_date_format(date_str: str) -> str:
    # Parse the date from ISO 8601 format
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Convert to the desired format
    converted_date_str = date_obj.strftime("%-m/%-d/%Y")

    return converted_date_str


def convert_date_format_with_arrow(date_str: str) -> str:
    # Parse the date using arrow
    date_obj = arrow.get(date_str)

    # Convert to the desired format
    converted_date_str = date_obj.format("M/D/YYYY")

    return converted_date_str


# Replace 'your_api_key_here' with your FRED API key
api_key = os.environ.get("FRED_API_KEY")
fred = Fred(api_key=api_key)
fred_casual_to_formal = {
    "2 Years Treasury Bonds": "GS2",
    "10 Years Treasury Bonds": "GS10",
    "6 Months Treasury Bonds": "GS6M",
}


def calculate_yield_metrics(asset_casual: str, starting: str, ending: str) -> str:
    asset = fred_casual_to_formal.get(asset_casual, "")
    result = ""
    if asset:
        if not starting or not ending:
            ending_datetime = datetime.now()
            ending = ending_datetime.strftime("%Y-%-m-%-d")
            print(ending)
            starting_datetime = ending_datetime - timedelta(days=365)
            starting = starting_datetime.strftime("%Y-%-m-%-d")
            print(starting)
        bond_yields = pd.DataFrame(fred.get_series(asset, starting, ending))
        bond_yields.columns = ["Yield"]
        bond_yields.index.name = "Date"

        current_yield = bond_yields["Yield"].values[-1]
        result = result + f"Treasury Bond Yield: {current_yield}%" + "\n\n"

        # Calculate simple metrics
        average_yield = bond_yields["Yield"].mean()
        yield_volatility = bond_yields["Yield"].std()
        max_yield = bond_yields["Yield"].max()
        min_yield = bond_yields["Yield"].min()

        result = (
            result
            + "Simple Metrics:\n"
            + f"Average Yield: {average_yield:.2f}%\n"
            + f"Yield Volatility: {yield_volatility:.2f}%\n"
            + f"Max Yield: {max_yield:.2f}%\n"
            + f"Min Yield: {min_yield:.2f}%"
        )
    else:
        result = f"Unknown asset: {asset_casual}"

    return result


def get_effective_ffr_data():
    series_id = "FEDFUNDS"
    data = fred.get_series_latest_release(series_id)

    output = f"Current rate as of {data.index[-1].strftime('%Y-%m-%d')}: {data[-1]:.2f} %\n\n"

    output += "Previous five data points:\n"

    for i in range(2, 7):
        output += f"{data.index[-i].strftime('%Y-%m-%d')}: {data[-i]:.2f} %\n"

    return output


def get_target_ffr_data():
    lower_limit_series_id = "DFEDTARL"
    upper_limit_series_id = "DFEDTARU"
    lower_data = fred.get_series_latest_release(lower_limit_series_id)
    upper_data = fred.get_series_latest_release(upper_limit_series_id)

    # Build the output string
    output = f"Current target rate range as of {lower_data.index[-1].strftime('%Y-%m-%d')}: {lower_data[-1]:.2f} - {upper_data[-1]:.2f} %\n\n"
    output += "Previous five data points:\n"

    for i in range(2, 7):
        output += f"{lower_data.index[-i].strftime('%Y-%m-%d')}: {lower_data[-i]:.2f} - {upper_data[-i]:.2f} %\n"

    return output


def get_cpi(starting: str, ending: str):
    series_id = "CPIAUCNS"
    data = fred.get_series_latest_release(series_id)

    if starting:
        starting = convert_date_format(starting)
    if ending:
        ending = convert_date_format(ending)

    output = f"Current cpi rate as of {data.index[-1].strftime('%Y-%m-%d')}: {float(data[-1] / 100):.2f} %\n\n"

    output += "Previous five data points:\n"

    for i in range(2, 7):
        output += f"{data.index[-i].strftime('%Y-%m-%d')}: {data[-i]:.2f} %\n"

    return output


def get_unemployment_rate(starting: str, ending: str):
    series_id = "UNRATE"
    data = fred.get_series_latest_release(series_id)

    if starting:
        starting = convert_date_format(starting)
    if ending:
        ending = convert_date_format(ending)

    output = f"Current unemployment rate as of {data.index[-1].strftime('%Y-%m-%d')}: {data[-1]:.2f} %\n\n"

    output += "Previous five data points:\n"

    for i in range(2, 7):
        output += f"{data.index[-i].strftime('%Y-%m-%d')}: {data[-i]:.2f} %\n"

    return output


def get_gdp(starting: str, ending: str):
    series_id = "GDP"
    data = fred.get_series_latest_release(series_id)

    if starting:
        starting = convert_date_format(starting)
    if ending:
        ending = convert_date_format(ending)

    output = f"Current gross domestic product as of {data.index[-1].strftime('%Y-%m-%d')}: {data[-1]:.2f} bln $\n\n"

    output += "Previous five data points:\n"

    for i in range(2, 7):
        output += f"{data.index[-i].strftime('%Y-%m-%d')}: {data[-i]:.2f} bln $\n"

    return output


def get_payrolls(starting: str, ending: str):
    series_id = "PAYEMS"
    data = fred.get_series_latest_release(series_id)

    if starting:
        starting = convert_date_format(starting)
    if ending:
        ending = convert_date_format(ending)

    output = f"Current payrolls as of {data.index[-1].strftime('%Y-%m-%d')}: {data[-1]:.2f} new employees over last month\n\n"

    output += "Previous five data points:\n"

    for i in range(2, 7):
        output += f"{data.index[-i].strftime('%Y-%m-%d')}: {data[-i]:.2f} new employees over last month\n"

    return output
