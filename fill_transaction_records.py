import mysql.connector
from datetime import datetime, timedelta

# Establish a connection to the MySQL database
conn = mysql.connector.connect(host="localhost", user="root", password="c0nygre", database="stock_management")

# Create a cursor object
cursor = conn.cursor()

# Sample data to insert
transactions = [
    ('AAPL', 'buy', 10, 150.00, datetime.now() - timedelta(days=5)),
    ('GOOG', 'buy', 5, 2700.00, datetime.now() - timedelta(days=10)),
    ('TSLA', 'sell', 8, 700.00, datetime.now() - timedelta(days=15)),
    ('MSFT', 'buy', 20, 290.00, datetime.now() - timedelta(days=20)),
    ('AMZN', 'buy', 7, 3300.00, datetime.now() - timedelta(days=25)),
    ('NFLX', 'sell', 3, 510.00, datetime.now() - timedelta(days=30)),
    ('FB', 'buy', 12, 340.00, datetime.now() - timedelta(days=35)),
    ('NVDA', 'sell', 15, 600.00, datetime.now() - timedelta(days=40)),
    ('INTC', 'buy', 25, 55.00, datetime.now() - timedelta(days=45)),
    ('AMD', 'sell', 30, 90.00, datetime.now() - timedelta(days=50)),
    ('BABA', 'buy', 18, 220.00, datetime.now() - timedelta(days=55)),
    ('V', 'sell', 6, 230.00, datetime.now() - timedelta(days=60)),
    ('JPM', 'buy', 22, 155.00, datetime.now() - timedelta(days=65)),
    ('DIS', 'sell', 9, 175.00, datetime.now() - timedelta(days=70)),
    ('PYPL', 'buy', 14, 190.00, datetime.now() - timedelta(days=75)),
]


# SQL query to insert data
insert_query = """
INSERT INTO Transactions (Symbol, TransactionType, Quantity, Price, TransactionDate)
VALUES (%s, %s, %s, %s, %s)
"""

# Execute the query for each transaction
for transaction in transactions:
    cursor.execute(insert_query, transaction)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()

print("Records inserted successfully!")
