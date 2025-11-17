import requests
import pygal
from datetime import datetime
import csv
import os

API_KEY = "6S6GQ8K8UNOSFDJS"
BASE_URL = "https://www.alphavantage.co/query"

def load_symbols():
    symbols = []
    csv_path = os.path.join(os.path.dirname(__file__), "stocks.csv")
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbols.append(row["Symbol"])
    return symbols


def get_stock_data(stock_symbol, chart_type, series_choice, start_date, end_date):
    # Determine function type
    if series_choice == "1":
        function = "TIME_SERIES_INTRADAY"
        interval = "60min"
    elif series_choice == "2":
        function = "TIME_SERIES_DAILY"
        interval = None
    elif series_choice == "3":
        function = "TIME_SERIES_WEEKLY"
        interval = None
    elif series_choice == "4":
        function = "TIME_SERIES_MONTHLY"
        interval = None
    else:
        raise ValueError("Invalid time series selected.")

    params = {"function": function, "symbol": stock_symbol, "apikey": API_KEY}
    if interval:
        params["interval"] = interval

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    # error handling
    if "Note" in data:
        raise Exception("API rate limit reached. Try again later.")
    if "Error Message" in data:
        raise Exception("Invalid stock symbol.")

    # get time series key
    ts_key = None
    for key in data.keys():
        if "Time Series" in key:
            ts_key = key
            break
    if not ts_key:
        raise Exception("No valid data returned.")

    ts_data = data[ts_key]

    # date filter
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    filtered = []
    for date_str, values in ts_data.items():
        date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        if start_dt <= date_obj <= end_dt:
            filtered.append((date_obj,
                             float(values["1. open"]),
                             float(values["2. high"]),
                             float(values["3. low"]),
                             float(values["4. close"])))

    if not filtered:
        raise Exception("No data found in that date range.")

    filtered.sort()

    dates = [f[0] for f in filtered]
    opens = [f[1] for f in filtered]
    highs = [f[2] for f in filtered]
    lows = [f[3] for f in filtered]
    closes = [f[4] for f in filtered]

    # chart
    if chart_type == "2":
        chart = pygal.Bar(x_label_rotation=45)
    else:
        chart = pygal.Line(x_label_rotation=45)

    chart.title = f"{stock_symbol} Price Chart"
    chart.x_labels = [d.strftime("%Y-%m-%d") for d in dates]
    chart.add("Open", opens)
    chart.add("High", highs)
    chart.add("Low", lows)
    chart.add("Close", closes)

    return chart.render(is_unicode=True).decode("utf-8")
