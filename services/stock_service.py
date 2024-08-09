from repositories.stock_repository import StockRepository
from repositories.transaction_repository import TransactionRepository
from repositories.active_holdings_repository import ActiveHoldingsRepository
import yfinance as yf
import decimal
import heapq
from flask import Flask, session
from collections import defaultdict
from datetime import datetime
class StockService:
    def __init__(self):
        self.stock_repository = StockRepository()
        self.transaction_repository = TransactionRepository()
        self.active_holdings_repository = ActiveHoldingsRepository()

    def buy_stock(self, symbol, quantity, buy_price, datetime): 
        self.transaction_repository.add_transaction(symbol, 'buy', quantity, buy_price, datetime)
        self.active_holdings_repository.add_transaction(symbol, 'buy', quantity, buy_price, datetime)
        self._update_session_purchased_stocks(symbol)

    def sell_stock(self, symbol, quantity, sell_price, datetime):
        self.transaction_repository.add_transaction(symbol, 'sell', quantity, sell_price, datetime)
        profit = self.active_holdings_repository.sell_transaction_dummy(symbol,'sell',quantity,sell_price, datetime)
        self._update_session_purchased_stocks(symbol, remove=True)
        return profit

    def reset_portfolio(self):
        self.active_holdings_repository.reset_transactions()
        self.transaction_repository.reset_transactions()
        self._reset_session_purchased_stocks()

    def get_all_stocks(self):
        return self.active_holdings_repository.get_all_stocks()

    def calculate_current_profit(self):
        invested_amount, realized_profit, temp = self.calculate_invested_amount()
        return realized_profit

    def calculate_invested_amount(self): 
        transactions = self.transaction_repository.get_transactions()
        stocks_queues = {} 
        realized_profit = 0
        realized_profit_vs_date = {}

        for trans in transactions:
            _, symbol, action, qty, price, transdate = trans
            if symbol not in stocks_queues:
                price_curr = self._get_current_price(symbol)
                stocks_queues[symbol] = []
            if action == 'buy':
                for _ in range(qty):
                    heapq.heappush(stocks_queues[symbol], price) 
            elif action == 'sell':
                days_profit = 0
                for _ in range(qty):
                    if stocks_queues[symbol]:
                        selling_stock = heapq.heappop(stocks_queues[symbol]) 
                        realized_profit -= selling_stock
                        realized_profit += price 
                date=transdate.date()
                dt_object= transdate.strftime("%Y-%m-%d")
                realized_profit_vs_date[dt_object]=realized_profit
        return self.active_holdings_repository.get_net_worth_amount(),realized_profit,realized_profit_vs_date
    
    def calculate_portfolio_value(self, stocks):
        portfolio_value = decimal.Decimal(0)
        for symbol in stocks:
            price = self.transaction_repository.get_buy_price(symbol)
            bought_quantity = self.transaction_repository.get_total_quantity(symbol, 'buy') or int(0)
            sold_quantity = self.transaction_repository.get_total_quantity(symbol, 'sell') or int(0)
            net_quantity = bought_quantity - sold_quantity 
            portfolio_value += net_quantity * price
        return portfolio_value

    def calculate_realized_profit(self):
        return self.calculate_invested_amount()[1]

    def get_holdings(self):
        holdings = []
        results = self.transaction_repository.get_holdings()
        for symbol, quantity in results:
            #buy_price = self.transaction_repository.get_buy_price(symbol) or decimal.Decimal(0)
            buy_price=self.active_holdings_repository.weighted_average(symbol)
            sold_quantity = self.transaction_repository.get_total_quantity(symbol, 'sell') or int(0) 
            net_quantity = quantity - sold_quantity
            if net_quantity > 0:
                holdings.append({'symbol': symbol, 'quantity': net_quantity, 'weighted average price': buy_price})
        return holdings

    def get_networth(self):
        return self.active_holdings_repository.get_net_worth_amount()

    def get_transactions(self):
        return self.transaction_repository.get_transactions()

    def get_buy_price(self, symbol):
        return self.transaction_repository.get_buy_price(symbol)

    def get_stock_stats(self, symbol):
        stock = yf.Ticker(symbol)
        stats = stock.info
        
        return {
            'currentPrice': stats.get('previousClose', 'N/A'),
            'marketCap': stats.get('marketCap', 'N/A'),
            'peRatio': stats.get('trailingPE', 'N/A'),
            'sector': stats.get('sector','N/A'),
            'profit_percent': self.profit_percentage_of_stock(symbol),
            'top_5_gainers': self.top_5_gainers(),
            'top_5_losers': self.top_5_losers(),
            'shortName': stats.get('shortName','N/A'),
            'volume': stats.get('volume','N/A')
            # if time permits, might plot 3m 6m 1y graphs using history method of api.
        }

    def _get_current_price(self, symbol):
        # would work on this and change it by a rand(), till then we can use the form.
        stock = yf.Ticker(symbol)
        return decimal.Decimal(stock.history(period='1d').iloc[0]['Close'])

    def _update_session_purchased_stocks(self, symbol, remove=False):
        if 'purchased_stocks' not in session:
            session['purchased_stocks'] = []
        if remove:
            if symbol in session['purchased_stocks']:
                session['purchased_stocks'].remove(symbol)
        else:
            if symbol not in session['purchased_stocks']:
                session['purchased_stocks'].append(symbol)
        session.modified = True

    def _reset_session_purchased_stocks(self):
        session['purchased_stocks'] = []
        session.modified = True

    def profit_percentage_of_stock(self,symbol):
        return self.active_holdings_repository.profit_percentage_of_stock(symbol)
    
    def top_5_gainers(self):
        return self.active_holdings_repository.top_5_gainers()
    
    def top_5_losers(self):
        return self.active_holdings_repository.top_5_losers()
    
    def realized_profit_graphs(self):
        return self
    
    def sector_graphs(self):
        symbols = self.active_holdings_repository.get_active_stocks()  # Fetch the active stock symbols
        sector_counts = defaultdict(int)  # Dictionary to hold sector counts

        for symbol in symbols:
            stock = yf.Ticker(symbol)  # Get stock info
            stats = stock.info
            sector = stats.get('sector', 'Unknown')  # Get the sector or use 'Unknown' if not available
            sector_counts[sector] += 1  # Increment the count for the sector

        return sector_counts
    
    def categorize_market_cap(self,market_cap):
        """Categorize stocks based on market cap."""
        if market_cap >= 10**11:  # Large-cap
            return 'Large Cap'
        elif 10**10 <= market_cap < 10**11:  # Mid-cap
            return 'Mid Cap'
        elif 10**9 <= market_cap < 10**10:  # Small-cap
            return 'Small Cap'
        else:  # Micro-cap and below
            return 'Micro/Other'

    def cap_graphs(self):
        symbols = self.active_holdings_repository.get_active_stocks() # Nested dictionary for sectors and caps
        cap_counts = defaultdict(int)
        for symbol in symbols:
            stock = yf.Ticker(symbol)  # Get stock info
            stats = stock.info  

            market_cap = stats.get('marketCap', 0)  # Get market cap or use 0 if not available

            cap_category = self.categorize_market_cap(market_cap) 
             # Increment the count for the sector and cap category
            cap_counts[cap_category]+=1

        return cap_counts
