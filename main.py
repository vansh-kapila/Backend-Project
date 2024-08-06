from flask import Flask, render_template, request, session, jsonify
import pymysql
import yfinance as yf
import decimal
import random
import json

# Parameters -
# 1) Total invested amount (amount currently invested in stocks): buyprice*qty of holding
# 2) Current portfolio value (current value of invested money)
# 3) Realized profit (profit for sold stocks)
# 4) Net worth = unrealized profit + realized profit + total invested amount till date (whether sold or unsold)
# 5) Total current profit = Realized profit + current portfolio value - total invested amount.
# two tables - stock details and transactions.

# Doubt - let's say for an apple stock
# 1 unit purchased at 100
# 1 unit purchased at 110
# 1 unit sold at 140
# what is the current invested amount of portfolio? Should we let the investor choose that he wants to sell 100 or

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return pymysql.connect(host="localhost", user="root", password="c0nygre", database="stock_management")

@app.route('/')
def home():
    return render_template('index.html')

invested_amount = 0
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        action = request.form.get('action')
        symbol = request.form.get('symbol')
        quantity = decimal.Decimal(request.form.get('quantity', 0))
        price = decimal.Decimal(request.form.get('price', 0))
        
        if action == 'buy':
            buy_stock(symbol, quantity)
        elif action == 'sell':
            sell_stock(symbol, quantity, price)
        elif action == 'reset':
            reset_portfolio()
    
    stocks = get_all_stocks() 
    current_value = decimal.Decimal(calculate_portfolio_value(stocks))
    realized_profit = decimal.Decimal(calculate_realized_profit())
    global invested_amount
    net_worth=get_networth()

    total_current_profit = calculate_current_profit()
    holdings = get_holdings()
    transactions = get_transactions()

    return render_template('dashboard.html', stocks=stocks, invested_amount=invested_amount,
                           current_value=current_value, realized_profit=realized_profit,
                           net_worth=net_worth, total_current_profit=total_current_profit,
                           holdings=holdings, transactions=transactions)

@app.route('/stock_stats/<symbol>', methods=['GET'])
def stock_stats(symbol):
    stock = yf.Ticker(symbol)
    stats = stock.info
    return jsonify({
        'currentPrice': stats.get('regularMarketPrice', 'N/A'),
        'marketCap': stats.get('marketCap', 'N/A'),
        'peRatio': stats.get('trailingPE', 'N/A')
    })

#working on this
@app.route('/update_prices', methods=['GET'])
def update_prices():
    symbols = request.args.getlist('symbols')
    updated_prices = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        price = stock.history(period='1d').iloc[0]['Close']
        # Apply a random change to the price
        change = price * random.uniform(-0.01, 0.01)
        updated_price = price + change
        updated_prices[symbol] = round(updated_price, 2)
    return jsonify(updated_prices)

def buy_stock(symbol, quantity):
    connection = get_db_connection()
    cursor = connection.cursor()
    stock = yf.Ticker(symbol)
    price = decimal.Decimal(stock.history(period='1d').iloc[0]['Close'])
    cursor.execute("""
        INSERT INTO Transactions (Symbol, TransactionType, Quantity, Price)
        VALUES (%s, 'buy', %s, %s)
    """, (symbol, quantity, price))
    connection.commit()
    cursor.close()
    connection.close()
    
    if 'purchased_stocks' not in session:
        session['purchased_stocks'] = []
    if symbol not in session['purchased_stocks']:
        session['purchased_stocks'].append(symbol)
    session.modified = True

def sell_stock(symbol, quantity, sell_price):
    connection = get_db_connection()
    cursor = connection.cursor()
    price = decimal.Decimal(sell_price)
    cursor.execute("""
        INSERT INTO Transactions (Symbol, TransactionType, Quantity, Price)
        VALUES (%s, 'sell', %s, %s)
    """, (symbol, quantity, price))
    connection.commit()
    cursor.close()
    connection.close()
    
    if 'purchased_stocks' in session and symbol in session['purchased_stocks']:
        session['purchased_stocks'].remove(symbol)
        session.modified = True

def reset_portfolio():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Transactions")
    connection.commit()
    cursor.close()
    connection.close()
    session['purchased_stocks'] = []
    session.modified = True

def get_all_stocks():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Symbol FROM Transactions GROUP BY Symbol")
    stocks = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return stocks
def calculate_current_profit():
    realized_profit=calculate_realized_profit()
    net_worth=get_networth()
    connection=get_db_connection()
    cursor=connection.cursor()
    cursor.execute("""
            SELECT SUM(Price * Quantity) FROM Transactions
            WHERE TransactionType = 'buy'

        """)
    buy_amount = cursor.fetchone()[0] or decimal.Decimal(0)

    total_current_profit = realized_profit + (net_worth- buy_amount)
    return total_current_profit

def calculate_invested_amount():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT SUM(Price * Quantity) FROM Transactions
        WHERE TransactionType = 'buy'
        
    """)
    buy_amount = cursor.fetchone()[0]
    total_invested = decimal.Decimal(0)
    # for symbol, buy_amount in results:
    #     cursor.execute("""
    #         SELECT SUM(Quantity*Price) FROM Transactions
    #         WHERE Symbol = %s AND TransactionType = 'sell'
    #     """, (symbol,))
    #
    #     sold_amount = cursor.fetchone()[0] or decimal.Decimal(0)
    #     total_invested += buy_amount+sold_amount
    #
    #     cursor.close()
    #     connection.close()
    realized_profit = calculate_realized_profit()
    total_invested += realized_profit + buy_amount
    return total_invested
global tot_buy=0
def calculate_main():
    connection=get_db_connection()
    cursor=connection.cursor()


def calculate_portfolio_value(stocks):
    connection = get_db_connection()
    cursor = connection.cursor()
    portfolio_value = decimal.Decimal(0)
    for symbol in stocks:
        stock = yf.Ticker(symbol)
        price = decimal.Decimal(stock.history(period='1d').iloc[0]['Close'])
        cursor.execute("""
            SELECT SUM(Quantity) FROM Transactions
            WHERE Symbol = %s AND TransactionType = 'buy'
        """, (symbol,))
        bought_quantity = cursor.fetchone()[0] or decimal.Decimal(0)
        cursor.execute("""
            SELECT SUM(Quantity) FROM Transactions
            WHERE Symbol = %s AND TransactionType = 'sell'
        """, (symbol,))
        sold_quantity = cursor.fetchone()[0] or decimal.Decimal(0)
        net_quantity = bought_quantity - sold_quantity
        portfolio_value += net_quantity * price
    cursor.close()
    connection.close()
    return portfolio_value

def calculate_realized_profit():
    #FLAWED LOGIC
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT SUM(Price * Quantity) FROM Transactions
        WHERE TransactionType = 'sell'
    """)
    sell_amount = cursor.fetchone()[0] or decimal.Decimal(0)
    
    cursor.execute("""
        SELECT Symbol, SUM(Price * Quantity) FROM Transactions
        WHERE TransactionType = 'buy' AND Symbol IN (
            SELECT DISTINCT Symbol FROM Transactions WHERE TransactionType = 'sell'
        )
        GROUP BY Symbol
    """)
    buy_amount_for_sold = decimal.Decimal(0)
    for symbol, amount in cursor.fetchall():
        cursor.execute("""
            SELECT SUM(Quantity) FROM Transactions
            WHERE Symbol = %s AND TransactionType = 'sell'
        """, (symbol,))
        sold_quantity = cursor.fetchone()[0] or decimal.Decimal(0)
        cursor.execute("""
            SELECT SUM(Quantity) FROM Transactions
            WHERE Symbol = %s AND TransactionType = 'buy'
        """, (symbol,))
        bought_quantity = cursor.fetchone()[0] or decimal.Decimal(0)
        if bought_quantity > sold_quantity:
            buy_amount_for_sold += amount
    global invested_amount
    invested_amount = invested_amount + buy_amount_for_sold
    realized_profit = sell_amount - buy_amount_for_sold
    cursor.close()
    connection.close()
    return realized_profit

def get_holdings():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT Symbol, SUM(Quantity) AS Quantity FROM Transactions
        WHERE TransactionType = 'buy'
        GROUP BY Symbol
    """)
    results = cursor.fetchall()
    holdings = []
    for symbol, quantity in results:
        #fetching current price for each symbol
        stock = yf.Ticker(symbol)
        curr_price = decimal.Decimal(stock.history(period='1d').iloc[0]['Close'])
        cursor.execute("""
            SELECT SUM(Quantity) FROM Transactions
            WHERE Symbol = %s AND TransactionType = 'sell'
        """, (symbol,))
        sold_quantity = cursor.fetchone()[0] or decimal.Decimal(0)
        net_quantity = quantity - sold_quantity
        if net_quantity > 0:
            holdings.append({'symbol': symbol, 'quantity': net_quantity,'price':curr_price})
    cursor.close()
    connection.close()
    return holdings
def get_networth():
    net_worth=0
    holdings=get_holdings()
    for i in holdings:
        net_worth+=i['quantity']*i['price']
    return net_worth





def get_transactions():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT Symbol, TransactionType, Quantity, Price FROM Transactions
    """)
    transactions = cursor.fetchall()
    cursor.close()
    connection.close()
    return transactions

def _get_buy_price(symbol):
    #Faulty logic buy price recurrring even after selling. Easier to implement an average prie logic
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT Price FROM Transactions
        WHERE Symbol = %s AND TransactionType = 'buy'
        ORDER BY TransactionID ASC LIMIT 1
    """, (symbol,))
    buy_price = cursor.fetchone()[0] or decimal.Decimal(0)
    cursor.close()
    connection.close()
    return buy_price

@app.context_processor
def utility_processor():
    def get_buy_price(symbol):
        return _get_buy_price(symbol)
    return dict(get_buy_price=get_buy_price)

if __name__ == '__main__':
    app.run(debug=True)
