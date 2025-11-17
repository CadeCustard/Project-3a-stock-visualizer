import requests
import pygal
from datetime import datetime

API_KEY = "6S6GQ8K8UNOSFDJS"
BASE_URL = "https://www.alphavantage.co/query"


def fetch_stock_data(symbol, function_choice):
    # Map choices → AlphaVantage params
    if function_choice == "1":
        function = "TIME_SERIES_INTRADAY"
        interval = "60min"
    elif function_choice == "2":
        function = "TIME_SERIES_DAILY"
        interval = None
    elif function_choice == "3":
        function = "TIME_SERIES_WEEKLY"
        interval = None
    elif function_choice == "4":
        function = "TIME_SERIES_MONTHLY"
        interval = None
    else:
        return None, "Invalid function choice"

    params = {
        "function": function,
        "symbol": symbol,
        "apikey": API_KEY
    }

    if interval:
        params["interval"] = interval

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        return None, f"Error fetching data: {e}"

    if "Note" in data:
        return None, "API limit reached. Wait 1 minute and try again."

    if "Error Message" in data:
        return None, "Invalid symbol. Try again."

    # Find Time Series key
    ts_key = None
    for k in data.keys():
        if "Time Series" in k:
            ts_key = k

    if not ts_key:
        return None, "No valid data returned."

    return data[ts_key], None


def filter_data(time_series_data, start_date, end_date):
    filtered_dates = []
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []

    for date_str, values in time_series_data.items():
        try:
            date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d").date()

            if start_date <= date_obj <= end_date:
                filtered_dates.append(date_obj)
                open_prices.append(float(values["1. open"]))
                high_prices.append(float(values["2. high"]))
                low_prices.append(float(values["3. low"]))
                close_prices.append(float(values["4. close"]))
        except:
            continue

    if not filtered_dates:
        return None, "No data found in date range."

    # Sort by date
    filtered_dates, open_prices, high_prices, low_prices, close_prices = zip(
        *sorted(zip(filtered_dates, open_prices, high_prices, low_prices, close_prices))
    )

    return (filtered_dates, open_prices, high_prices, low_prices, close_prices), None


def create_chart(chart_type, dates, open_prices, high_prices, low_prices, close_prices):
    if chart_type == "2":
        chart = pygal.Bar(x_label_rotation=45)
        chart.title = "Stock Prices (Bar Chart)"
    else:
        chart = pygal.Line(x_label_rotation=45)
        chart.title = "Stock Prices (Line Chart)"

    chart.x_labels = [d.strftime("%Y-%m-%d") for d in dates]
    chart.add("Open Price", open_prices)
    chart.add("High Price", high_prices)
    chart.add("Low Price", low_prices)
    chart.add("Close Price", close_prices)
    chart.x_title = "Date"
    chart.y_title = "Price (USD)"

    # Save chart (Flask will display it)
    chart_path = "static/chart.svg"
    chart.render_to_file(chart_path)

    return chart_path
