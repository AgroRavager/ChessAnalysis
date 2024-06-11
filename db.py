# Shaurya Jeloka, Akshay Vakharia, Ian Jeong
# 6/9/2024

# This script creates and manages a SQLite database that stores pricing data for Amazon 
# items, stocks, and cryptocurrencies. The database contains three tables: amazon_items,
# stocks, and cryptocurrencies. Each table stores the name, price, and timestamp of the 
# items being tracked. This program defines functions to create the database and insert 
# pricing information into each of the three tables. This setup allows for more 
# structured and efficient management of pricing data.

import sqlite3

# Define function to create the SQL database that will store all pricing info
def create_database():
    
    # Create a database and connection and cursor objects for it
    con = sqlite3.connect('prices.db')
    cursor = con.cursor()

    # Create tables for storing pricing data on amazon items,stocks, and cryptos
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

# Define function to insert information into the amazon_items table
def insert_amazon_item(con, item_name, price, timestamp):
    
    # Create a cursor using the connection object passed in as an argument
    cursor = con.cursor()
    
    # Use a SQL insert statement to put the item name, price, and timestamp into the database
    cursor.execute('''INSERT INTO amazon_items (item_name, price, timestamp) VALUES (?, ?, ?);''', 
                   (item_name, price, timestamp))

    # Commit changes
    con.commit()

# Define function to insert information into the stocks table
def insert_stock(con, stock_symbol, price, timestamp):

    # Create a cursor using the connection object passed in as an argument
    cursor = con.cursor()

    # Use a SQL insert statement to put the stock symbol, price, and timestamp into the database
    cursor.execute('''INSERT INTO stocks (stock_symbol, price, timestamp) VALUES (?, ?, ?);''', 
                   (stock_symbol, price, timestamp))

    # Commit changes
    con.commit()

# Define function to insert information into the cryptocurrencies table
def insert_cryptocurrency(con, crypto_name, price, timestamp):
    
    # Create a cursor using the connection object passed in as an argument
    cursor = con.cursor()

    # Use a SQL insert statement to put the crypto name, price, and timestamp into the database
    cursor.execute('''INSERT INTO cryptocurrencies (crypto_name, price, timestamp) VALUES (?, ?, ?);''',
                    (crypto_name, price, timestamp))

    # Commit changes
    con.commit()