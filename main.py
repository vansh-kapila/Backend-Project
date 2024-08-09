from flask import Flask, request, jsonify
from services.stock_service import StockService
import decimal
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
import json
import datetime
app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = 'http://127.0.0.1:5000/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sample API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
app.secret_key = 'your_secret_key'

# Service instance
stock_service = StockService()

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Stock Management API!"})

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    profit_print = None
    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action') 
        symbol = data.get('symbol')
        quantity = int(data.get('quantity', 0))
        price = decimal.Decimal(data.get('price', 0)) 
        if action == 'buy':
            stock_service.buy_stock(symbol, quantity, price)
        elif action == 'sell':
            profit_print = stock_service.sell_stock(symbol, quantity, price)
        elif action == 'reset':
            stock_service.reset_portfolio()

    stocks = stock_service.get_all_stocks() 
    net_worth = stock_service.get_networth()
    realized_profit = stock_service.calculate_realized_profit()
    total_current_profit = stock_service.calculate_current_profit()
    holdings = stock_service.get_holdings()
    transactions = stock_service.get_transactions() 

    return jsonify({
        "stocks": stocks,
        "invested_amount": stock_service.calculate_invested_amount()[0],
        "net_worth": net_worth,
        "realized_profit": realized_profit,
        "total_current_profit": total_current_profit,
        "holdings": holdings,
        "transactions": transactions,
        "profit": profit_print
    })

@app.route('/stock_stats/<symbol>', methods=['GET'])
def stock_stats(symbol):
    stats = stock_service.get_stock_stats(symbol)
    return jsonify(stats)

@app.route('/realized_profit_stats', methods=['GET'])
def realized_profit_vs_time():
    realized_profit_vs_time = stock_service.calculate_invested_amount()
    return jsonify(realized_profit_vs_time[2])

@app.route('/sector_stats', methods=['GET'])
def sector():
    sectors = stock_service.sector_graphs()
    return jsonify(sectors)

@app.route('/cap_stats', methods=['GET'])
def cap():
    caps = stock_service.cap_graphs()
    return jsonify(caps)

@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "API documentation for Stock Portfolio app"
    return jsonify(swag)

@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(debug=True)
