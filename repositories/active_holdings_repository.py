import pymysql
import decimal

class ActiveHoldingsRepository:
    def get_db_connection(self):
        return pymysql.connect(host="localhost", user="root", password="25058966", database="stock_management")

    def add_transaction(self, symbol, action, quantity, price):
        if action=="buy":
            connection = self.get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO ACTIVE_HOLDINGS (Symbol, Quantity, Price)
                VALUES (%s, %s, %s, %s)
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

    def get_active_transactions(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT ID, Symbol, TransactionType, Quantity, Price FROM ACTIVE_HOLDINGS")
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
        quantity = cursor.fetchone()[0] or decimal.Decimal(0)
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
