import sqlite3

def create_database():
    # Connect to the database (or create it)
    con = sqlite3.connect('prices.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS amazon_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name TEXT NOT NULL,
                        price REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                      )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS stocks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stock_symbol TEXT NOT NULL,
                        price REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                      )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS cryptocurrencies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        crypto_name TEXT NOT NULL,
                        price REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                      )''')
    
    # Commit changes and close the connection
    con.commit()
    con.close()

# Call the function to create the database and tables
#create_database()

def insert_amazon_item(con, item_name, price, timestamp):
    cursor = con.cursor()
    cursor.execute('''INSERT INTO amazon_items (item_name, price, timestamp) VALUES (?, ?, ?);''', (item_name, price, timestamp))
    con.commit()

def insert_stock(con, stock_symbol, price, timestamp):
    cursor = con.cursor()
    cursor.execute('''INSERT INTO stocks (stock_symbol, price, timestamp) VALUES (?, ?, ?);''', (stock_symbol, price, timestamp))
    con.commit()

def insert_cryptocurrency(con, crypto_name, price, timestamp):
    cursor = con.cursor()
    cursor.execute('''INSERT INTO cryptocurrencies (crypto_name, price, timestamp) VALUES (?, ?, ?);''', (crypto_name, price, timestamp))
    con.commit()