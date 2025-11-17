from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd

from stock_logic import fetch_stock_data, filter_data, create_chart

app = Flask(__name__)

# Load dropdown symbols
def load_symbols():
    df = pd.read_csv("stocks.csv")
    return df["Symbol"].tolist()


@app.route("/", methods=["GET", "POST"])
def index():
    symbols = load_symbols()
    chart_path = None
    error = None

    if request.method == "POST":
        symbol = request.form.get("symbol")
        chart_type = request.form.get("chart_type")
        function_choice = request.form.get("function_choice")

        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()

        # Fetch data
        ts_data, error = fetch_stock_data(symbol, function_choice)
        if error:
            return render_template("index.html", symbols=symbols, error=error)

        # Filter data
        filtered, error = filter_data(ts_data, start_date, end_date)
        if error:
            return render_template("index.html", symbols=symbols, error=error)

        dates, o, h, l, c = filtered

        # Create chart file
        chart_path = create_chart(chart_type, dates, o, h, l, c)

    return render_template("index.html", symbols=symbols, chart=chart_path, error=error)
