from repositories.stock_repository import StockRepository
from repositories.transaction_repository import TransactionRepository
from repositories.active_holdings_repository import ActiveHoldingsRepository
import yfinance as yf
import decimal
import heapq
from flask import Flask, session
class StockService:
    def __init__(self):
        self.stock_repository = StockRepository()
        self.transaction_repository = TransactionRepository()
        self.active_holdings_repository = ActiveHoldingsRepository()

    def buy_stock(self, symbol, quantity, buy_price): 
        self.transaction_repository.add_transaction(symbol, 'buy', quantity, buy_price)
        self.active_holdings_repository.add_transaction(symbol, 'buy', quantity, buy_price)
        self._update_session_purchased_stocks(symbol)

    def sell_stock(self, symbol, quantity, sell_price):
        self.transaction_repository.add_transaction(symbol, 'sell', quantity, sell_price)
        profit = self.active_holdings_repository.sell_transaction_dummy(symbol,'sell',quantity,sell_price)
        self._update_session_purchased_stocks(symbol, remove=True)
        return profit

    def reset_portfolio(self):
        self.active_holdings_repository.reset_transactions()
        self.transaction_repository.reset_transactions()
        self._reset_session_purchased_stocks()

    def get_all_stocks(self):
        return self.active_holdings_repository.get_all_stocks()

    def calculate_current_profit(self):
        invested_amount, realized_profit = self.calculate_invested_amount()
        return realized_profit

    def calculate_invested_amount(self): 
        transactions = self.transaction_repository.get_transactions()
        stocks_queues = {} 
        realized_profit = 0
        for trans in transactions:
            _, symbol, action, qty, price = trans
            if symbol not in stocks_queues:
                price_curr = self._get_current_price(symbol)
                stocks_queues[symbol] = []
            if action == 'buy':
                for _ in range(qty):
                    heapq.heappush(stocks_queues[symbol], price) 
            elif action == 'sell':
                for _ in range(qty):
                    if stocks_queues[symbol]:
                        selling_stock = heapq.heappop(stocks_queues[symbol]) 
                        realized_profit -= selling_stock
                        realized_profit += price 
        return self.active_holdings_repository.get_net_worth_amount(),realized_profit


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
            buy_price=self._get_current_price(symbol)
            sold_quantity = self.transaction_repository.get_total_quantity(symbol, 'sell') or int(0) 
            net_quantity = quantity - sold_quantity
            if net_quantity > 0:
                holdings.append({'symbol': symbol, 'quantity': net_quantity, 'price': buy_price})
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
            'top_5_losers': self.top_5_losers()
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