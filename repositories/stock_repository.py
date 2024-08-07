import pymysql

class StockRepository:
    def get_db_connection(self):
        return pymysql.connect(host="localhost", user="root", password="25058966", database="stock_management")