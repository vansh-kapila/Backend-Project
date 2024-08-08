import pymysql
import yfinance as yf
import random

# Database connection
db = pymysql.connect(host="localhost", user="root", password="c0nygre", database="stock_management")
cursor = db.cursor()

# Generate a list of stock symbols (you can also use a predefined list or API)
symbols = [symbol for symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BABA', 'INTC', 'CSCO']]

# Fetch and insert stock data
for symbol in symbols:
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d").iloc[0]  # Get latest data
    try:
        cursor.execute("""
            INSERT INTO Stocks (Symbol, Name, CurrentPrice, HighPrice, LowPrice, OpenPrice, PreviousClose)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Name = VALUES(Name),
                CurrentPrice = VALUES(CurrentPrice),
                HighPrice = VALUES(HighPrice),
                LowPrice = VALUES(LowPrice),
                OpenPrice = VALUES(OpenPrice),
                PreviousClose = VALUES(PreviousClose)
        """, (symbol, stock.info['longName'], data['Close'], data['High'], data['Low'], data['Open'], data['Close']))

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to insert/update {symbol}: {e}")

db.close()
