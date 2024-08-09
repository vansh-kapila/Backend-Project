import pymysql
import decimal
import json 
class TransactionRepository:  
    def get_db_connection(self):
        return pymysql.connect(host="localhost", user="root", password="25058966", database="stock_management")

    def add_transaction(self, symbol, action, quantity, price, datetime):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Transactions (Symbol, TransactionType, Quantity, Price, TransactionDate)
            VALUES (%s, %s, %s, %s, %s)
        """, (symbol, action, quantity, price, datetime))
        connection.commit()
        cursor.close()
        connection.close()

    def reset_transactions(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Transactions")
        connection.commit()
        cursor.close()
        connection.close()

    def get_all_stocks(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT Symbol FROM Transactions GROUP BY Symbol")
        stocks = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return stocks

    def get_transactions(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT TransactionID, Symbol, TransactionType, Quantity, Price, TransactionDate FROM Transactions")
        transactions = cursor.fetchall()
        cursor.close()
        connection.close()
        return transactions

    def get_total_quantity(self, symbol, transaction_type):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUM(Quantity) FROM Transactions
            WHERE Symbol = %s AND TransactionType = %s
        """, (symbol, transaction_type))
        quantity = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return quantity

    def get_holdings(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT Symbol, SUM(Quantity) AS Quantity FROM Transactions
            WHERE TransactionType = 'buy'
            GROUP BY Symbol
        """)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results

    def get_buy_price(self, symbol):
        connection = self.get_db_connection()
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
    
    def profit_percentage_of_stock(self,symbol):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUM(Price*quantity) FROM Transactions
            WHERE Symbol = %s AND TransactionType = 'buy'
            ORDER BY TransactionID ASC LIMIT 1
        """, (symbol,)) 
        
        total_price = cursor.fetchone()[0] or decimal.Decimal(0)
        cursor.execute("""
            SELECT SUM(quantity) FROM Transactions
            WHERE Symbol = %s AND TransactionType = 'buy'
            ORDER BY TransactionID ASC LIMIT 1
        """, (symbol,)) 
        
        total_qty = cursor.fetchone()[0] or decimal.Decimal(0)
        cursor.close()
        connection.close()
        return total_price/total_qty
    
    def top_5_gainers(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT DISTINCT Symbol FROM Transactions")
        symbols = cursor.fetchall()
        
        profit_percentages = []
        for symbol in symbols:
            symbol = symbol[0]
            profit_percentage = self.stock_repository.profit_percentage_of_stock(symbol)
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
            profit_percentage = self.stock_repository.profit_percentage_of_stock(symbol)
            profit_percentages.append((symbol, profit_percentage))
        
        cursor.close()
        connection.close()
        
        bottom_5 = sorted(profit_percentages, key=lambda x: x[1])[:5]
        result = [{'symbol': symbol, 'profit_percentage': str(profit_percentage)} for symbol, profit_percentage in bottom_5]
        
        return json.dumps(result)