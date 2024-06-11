# Shaurya Jeloka, Akshay Vakharia, Ian Jeong
# 6/9/2024

# This program automates the process of scraping prices from Amazon, accessing stock prices using
# the Yahoo Finance API, and getting cryptocurrency prices from the CoinGecko API. It stores 
# the prices in an SQLite database and sends an email alert when any of the tracked 
# items, stocks, or cryptocurrencies reach their lowest price in the past two weeks. The script 
# uses Selenium with a headless Chrome browser for web scraping, and it is designed to run 
# periodically to ensure the database has accurate and up to date pricing.

import requests
from bs4 import BeautifulSoup
from lxml import etree as et
import datetime
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import yfinance as yf
from pycoingecko import CoinGeckoAPI

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import db
import sqlite3

# Set Chrome options to run headless to avoid opening GUI
chrome_options = Options()
chrome_options.add_argument("--headless") 

# Define function to access and return prices for a list of amazon links
def return_price(amazon_url_list):
    
    # Initialize webdriver using ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)  
    
    # Create empty return list
    return_list = []

    # Loop through each url, extract price, and append it to the return list
    for url in amazon_url_list:
        driver.get(url)
        
        # Extract the HTML page source
        page_content = driver.page_source
        
        # Parse page content using BeautifulSoup
        soup = BeautifulSoup(page_content, 'html.parser')
    
        # Use the class and id elements to find the name and price of the product at the url
        price_int = soup.find('span', class_="a-price-whole")
        price_decimal = soup.find('span', class_='a-price-fraction')
        price_total = price_int.get_text() + price_decimal.get_text()
        product_name = soup.find(id = 'productTitle').get_text().strip()

        # Append name and price information to return list
        return_list.append((product_name, price_total))
        
    
    # Close the browser
    driver.quit()

    # Return the list of product names and prices
    return return_list

# Define function to get the stock pricesof a list of stocks using the yfinance package
def return_stock_prices(stock_tickers):

    # Define an empty return list 
    return_list = []

    # Loop through stock tickers and append each ticker and price to the return list
    for ticker in stock_tickers:
        stock = yf.Ticker(ticker)
        current_price = stock.history(period='1d')['Close'].iloc[0]
        return_list.append((ticker, round(current_price, 2)))

    # Return the list of all stock tickers and prices
    return return_list

# Define function to get cryptocurrency prices using the CoinGecko API
def return_crypto_prices(crypto_currency):

    # Set desired currency to USD and get prices of the specified cryptocurrencies
    currency = 'usd'
    cg_client = CoinGeckoAPI()
    prices = cg_client.get_price(ids = crypto_currency, vs_currencies = currency)

    # Define empty return list
    return_list = []

    # Loop through each cryptocurrency and append its name and price to the return list
    for crypto in prices:
        return_list.append((crypto.title(), prices[crypto]["usd"]))

    return return_list

# Define function to read list of stock tickers, amazon items, and cryptos from a JSON file 
# and return the parsed content
def read_data(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"amazon_items": [], "stocks": [], "cryptocurrencies": ""}

#store individual components of JSON file to separate variables
data = read_data('trackitems.json')
amazon_item_list = data['amazon_items']
stock_tickers = data['stocks']
cryptos = data['cryptocurrencies']

# Define function to update prices in the database and send email alerts if prices hit new lows
def update_prices():

    # Create connection object to database and record current time
    con = sqlite3.connect('prices.db')
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get current prices for amazon items, stocks, and cryptocurrencies
    amazon_list = return_price(amazon_item_list)
    stock_list = return_stock_prices(stock_tickers)
    crypto_list = return_crypto_prices(cryptos)

    # Define empty list of items at new price lows
    low_price_list = []

    # Insert amazon item, stock, and cryptocurrency prices into the database and append items 
    # at new low prices to the low price list
    for stock in stock_list:
        db.insert_stock(con, stock[0], stock[1], current_time)
        if float(stock[1]) < check_lowest_price(con, stock[0], "stocks", "stock_symbol"):
            low_price_list.append(stock[0])
            
    for item in amazon_list:
        db.insert_amazon_item(con, item[0], item[1], current_time)
        if float(item[1].replace(',', ''))  < check_lowest_price(con, item[0], "amazon_items", "item_name"):
            low_price_list.append(item[0])
            
    for crypto in crypto_list:
        db.insert_cryptocurrency(con, crypto[0], crypto[1], current_time)
        if float(crypto[1]) < check_lowest_price(con, crypto[0], "cryptocurrencies", "crypto_name"):
            low_price_list.append(crypto[0])

    # Close connection object
    con.close()

    # Send myself an email about items at their lowest price in the last two weeks
    subject = "Low Price"
    body = f"The prices of {low_price_list} are at their lowest in the last two weeks"
    to_email = "shaurya.jeloka@gmail.com"
    from_email = "shaurya.jeloka@gmail.com"
    password = "ngwtpvqaqctoxdzq" 
    send_email(subject, body, to_email, from_email, password)

    return low_price_list

# Define function to check the lowest price of an item in the last 
# two weeks from the database
def check_lowest_price(con, item, table, column):

    # Create cursor from connection object
    cursor = con.cursor()

    # Define SQL query to check the lowest price in the last 14 days 
    # for a given item
    query = f'''
    SELECT MIN(price) AS lowest_price
    FROM {table}
    WHERE {column} = ?
    AND timestamp >= datetime('now', '-14 days');
    '''

    # Execute the query with the item as the parameter and store the result
    cursor.execute(query, (item,))
    result = cursor.fetchone()

    # Close the cursor
    cursor.close()

    # Return the lowest price as a float
    if isinstance(result[0], float):
        return result[0]
    else:
        return float(result[0].replace(',', ''))

# Define function to send email notifications to users
def send_email(subject, body, to_email, from_email, password):
    try:
        # Begin creating the email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the email's main body
        msg.attach(MIMEText(body, 'plain'))

        # Setup the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login to the server
        server.login(from_email, password)

        # Send the email and quit the server
        server.send_message(msg)
        server.quit()

        print("Email sent successfully!")

    # In case of an authentication error when logging in, print the 
    # authentication error
    except smtplib.SMTPAuthenticationError as e:
        print("SMTPAuthenticationError: Unable to log in. Check your \
              email and password.")
        print(f"Error details: {e}")

    # Print any other general errors
    except Exception as e:
        print(f"An error occurred: {e}")