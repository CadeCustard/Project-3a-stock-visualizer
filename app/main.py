from flask import Flask, render_template, request
from stock_logic import get_stock_data, load_symbols

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    symbols = load_symbols()  # Populate dropdown

    chart_html = None
    error = None

    if request.method == "POST":
        symbol = request.form.get("symbol")
        chart_type = request.form.get("chart_type")
        series = request.form.get("series")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        try:
            chart_html = get_stock_data(symbol, chart_type, series, start_date, end_date)
        except Exception as e:
            error = str(e)

    return render_template("index.html", symbols=symbols, chart_html=chart_html, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
