from flask import Flask, render_template, request, session, jsonify
from services.stock_service import StockService
import decimal
from flask import Flask, session
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Service instance
stock_service = StockService()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    profit_print = None
    if request.method == 'POST':
        action = request.form.get('action')
        symbol = request.form.get('symbol')
        quantity = int(request.form.get('quantity', 0))
        price = decimal.Decimal(request.form.get('price', 0))
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

    return render_template('dashboard.html', stocks=stocks, invested_amount=stock_service.calculate_invested_amount()[0],
                           net_worth=net_worth, realized_profit=realized_profit, total_current_profit=total_current_profit,
                           holdings=holdings, transactions=transactions, profit=profit_print)

@app.route('/stock_stats/<symbol>', methods=['GET'])
def stock_stats(symbol):
    stats = stock_service.get_stock_stats(symbol)
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
