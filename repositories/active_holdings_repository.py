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
        
    def get_all_stocks(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT Symbol FROM ACTIVE_HOLDINGS GROUP BY Symbol")
        stocks = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return stocks