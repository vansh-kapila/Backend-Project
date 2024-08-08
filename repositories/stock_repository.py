import pymysql

class StockRepository:
    def get_db_connection(self):
        return pymysql.connect(host="localhost", user="root", password="c0nygre", database="stock_management")