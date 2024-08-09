import pymysql
import decimal 
import yfinance as yf
import json
from collections import defaultdict
class ActiveHoldingsRepository:

    def get_db_connection(self):
        return pymysql.connect(host="localhost", user="root", password="c0nygre", database="stock_management")

    def add_transaction(self, symbol, action, quantity, price):
        if action=="buy":
            connection = self.get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO ACTIVE_HOLDINGS (Symbol, Quantity, Price)
                VALUES (%s, %s, %s)
            """, (symbol, quantity, price))
            connection.commit()
            cursor.close()
            connection.close()

    def reset_transactions(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM ACTIVE_HOLDINGS")
        connection.commit()
        cursor.close()
        connection.close()

    def get_active_stocks(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT Symbol FROM ACTIVE_HOLDINGS GROUP BY Symbol")
        stocks = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return stocks
    
    def sell_transaction(self, symbol, action, quantity, price): 
        if action=="sell":
            connection = self.get_db_connection()
            cursor = connection.cursor()
            profit = 0 
            tot_buy = 0
            
            for _ in range(quantity):
                cursor.execute("""Update ACTIVE_HOLDINGS
                               SET Quantity = Quantity-1 where Symbol = %s order by Price LIMIT 1
                               """, (symbol,))
                connection.commit() 
                cursor.execute("""
                           SELECT Quantity,ID,Price from ACTIVE_HOLDINGS 
                           WHERE Symbol = %s Order by Price LIMIT 1
                            """, (symbol,))
                currQuantityAndID = cursor.fetchone()
                if(currQuantityAndID):
                    tot_buy+=currQuantityAndID[2]
                    if(currQuantityAndID[0]==0):
                        cursor.execute("""
                           DELETE FROM ACTIVE_HOLDINGS 
                           WHERE ID = %s
                            """, (currQuantityAndID[1],))
                        connection.commit()

            cursor.close()
            connection.close()
            profit=price*quantity-tot_buy
            return profit


    def get_net_worth_amount(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUM(Price*Quantity) FROM ACTIVE_HOLDINGS
        """)
        buy_price = cursor.fetchone()[0] or decimal.Decimal(0)
        cursor.close()
        connection.close()
        return buy_price

    def get_transactions(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT ID, Symbol, Quantity, Price FROM ACTIVE_HOLDINGS")
        transactions = cursor.fetchall()
        cursor.close()
        connection.close()
        return transactions

    def get_total_quantity(self, symbol):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUM(Quantity) FROM ACTIVE_HOLDINGS
            WHERE Symbol = %s
        """, (symbol))
        quantity = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return quantity

    def get_holdings(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT Symbol, SUM(Quantity) AS Quantity FROM ACTIVE_HOLDINGS
            GROUP BY Symbol
        """)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results

    # def get_buy_price(self, symbol):
    #     connection = self.get_db_connection()
    #     cursor = connection.cursor()
    #     cursor.execute("""
    #         SELECT Price FROM ACTIVE_HOLDINGS
    #         WHERE Symbol = %s
    #         ORDER BY TransactionID ASC LIMIT 1
    #     """, (symbol,))
    #     buy_price = cursor.fetchone()[0] or decimal.Decimal(0)
    #     cursor.close()
    #     connection.close()
    #     return buy_price

    def sell_transaction_dummy(self, symbol, action, quantity, price): 
        if action=="sell":
            connection = self.get_db_connection()
            cursor = connection.cursor()
            profit = 0 
            tot_buy = 0
            
            for _ in range(quantity):
                cursor.execute("""Update ACTIVE_HOLDINGS
                               SET Quantity = Quantity-1 where Symbol = %s order by Price LIMIT 1
                               """, (symbol,))
                connection.commit() 
                cursor.execute("""
                           SELECT Quantity,ID,Price from ACTIVE_HOLDINGS 
                           WHERE Symbol = %s Order by Price LIMIT 1
                            """, (symbol,))
                
                currQuantityAndID = cursor.fetchone()

                if(currQuantityAndID):
                    tot_buy+=currQuantityAndID[2]
                    if(currQuantityAndID[0]==0):
                        cursor.execute("""
                           DELETE FROM ACTIVE_HOLDINGS 
                           WHERE ID = %s
                            """, (currQuantityAndID[1],))
                        connection.commit()

            cursor.close()
            connection.close()
            profit=price*quantity-tot_buy
            return profit
        
    def _get_current_price(self, symbol):
        # would work on this and change it by a rand(), till then we can use the form.
        stock = yf.Ticker(symbol)
        return decimal.Decimal(stock.history(period='1d').iloc[0]['Close'])
        
    def weighted_average(self,symbol):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUM(Price*quantity) FROM ACTIVE_HOLDINGS
            WHERE Symbol = %s
            ORDER BY ID ASC LIMIT 1
        """, (symbol,)) 
        
        total_price = cursor.fetchone()[0] or decimal.Decimal(0)
        cursor.execute("""
            SELECT SUM(quantity) FROM ACTIVE_HOLDINGS
            WHERE Symbol = %s
            ORDER BY ID ASC LIMIT 1
        """, (symbol,)) 
        
        total_qty = cursor.fetchone()[0] or decimal.Decimal(0)
        cursor.close()
        connection.close()
        if total_qty==0:
            return 0
        return total_price/total_qty
    
    def profit_percentage_of_stock(self,symbol):
        weighted_average = self.weighted_average(symbol)
        curr_price = self._get_current_price(symbol)
        if weighted_average==0:
           return None
        return (curr_price-weighted_average)/curr_price*100
        
    def get_all_stocks(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT Symbol FROM ACTIVE_HOLDINGS GROUP BY Symbol")
        stocks = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return stocks
    

    def top_5_gainers(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT DISTINCT Symbol FROM Transactions")
        symbols = cursor.fetchall()
        
        profit_percentages = []
        for symbol in symbols:
            symbol = symbol[0]
            profit_percentage = self.profit_percentage_of_stock(symbol)
            profit_percentages.append((symbol, profit_percentage))
        
        cursor.close()
        connection.close()
        
        top_5 = sorted(profit_percentages, key=lambda x: x[1], reverse=True)[:5]
        result = [{'symbol': symbol, 'profit_percentage': str(profit_percentage)} for symbol, profit_percentage in top_5]
        
        return json.dumps(result)

    def top_5_losers(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT DISTINCT Symbol FROM Transactions")
        symbols = cursor.fetchall()
        
        profit_percentages = []
        for symbol in symbols:
            symbol = symbol[0]
            profit_percentage = self.profit_percentage_of_stock(symbol)
            profit_percentages.append((symbol, profit_percentage))
        
        cursor.close()
        connection.close()
        
        bottom_5 = sorted(profit_percentages, key=lambda x: x[1])[:5]
        result = [{'symbol': symbol, 'profit_percentage': str(profit_percentage)} for symbol, profit_percentage in bottom_5]
        
        return json.dumps(result)