import yfinance as yf
import pandas as pd
import json

def fetch_tickers_from_csv(filename):
    try:
        df = pd.read_csv(filename)
        tickers = df['Symbol'].tolist()
        return tickers
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def fetch_nasdaq_stock_data(tickers):
    stock_data = {}
    for ticker in tickers:
        try:
            stock_info = yf.Ticker(ticker).info
            stock_data[ticker] = stock_info
            print(f"Fetched data for {ticker}")
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    return stock_data

def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    csv_filename = 'nasdaq-listed.csv'
    nasdaq_tickers = fetch_tickers_from_csv(csv_filename)
    if nasdaq_tickers:
        nasdaq_stock_data = fetch_nasdaq_stock_data(nasdaq_tickers)
        save_to_json(nasdaq_stock_data, 'nasdaq_stock_data.json')
        print("Data saved to nasdaq_stock_data.json")
    else:
        print("No NASDAQ tickers were fetched.")
