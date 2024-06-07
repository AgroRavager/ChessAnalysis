import requests
from bs4 import BeautifulSoup
from lxml import etree as et
import datetime
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import yfinance as yf
from pycoingecko import CoinGeckoAPI

import db
import sqlite3

# Set Chrome optionsm to run headless
chrome_options = Options()
chrome_options.add_argument("--headless") 

def return_price(url_list):
    # Initialize WebDriver using ChromeDriver Manager
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)  
    return_list = []
    
    for url in url_list:
        driver.get(url)
        
        # Extract the HTML page source
        page_content = driver.page_source
        
        # use BeautifulSoup for parsing
        soup = BeautifulSoup(page_content, 'html.parser')
    
        #find the name and price of the item by the class/id elements
        price_int = soup.find('span', class_="a-price-whole")
        price_decimal = soup.find('span', class_='a-price-fraction')
        price_total = price_int.get_text() + price_decimal.get_text()
        product_name = soup.find(id = 'productTitle').get_text().strip()

        return_list.append((product_name, price_total))
        
    
    # Close the browser
    driver.quit()
    
    return return_list

# Define function to get the current stock price
def fetch_current_price(ticker):
    stock = yf.Ticker(ticker)
    current_price = stock.history(period='1d')['Close'].iloc[0]
    return current_price

def return_stock_prices(stock_tickers):
    return_list = []
    for ticker in stock_tickers:
        stock = yf.Ticker(ticker)
        current_price = stock.history(period='1d')['Close'].iloc[0]
        return_list.append((ticker, round(current_price, 2)))
    return return_list

def return_crypto_prices(crypto_currency):
    destination_currency = 'usd'
    cg_client = CoinGeckoAPI()
    prices = cg_client.get_price(ids = crypto_currency,
                                 vs_currencies = destination_currency)
    return_list = []
    for crypto in prices:
        # print(f'Current price of {crypto.title()}: ${prices[crypto]["usd"]}')
        return_list.append((crypto.title(), prices[crypto]["usd"]))

    return return_list

#Define amazon item list
amazon_item_list = ['https://www.amazon.com/Apple-MacBook-Laptop-12%E2%80%91core-19%E2%80%91core/dp/B0BSHDJG9T/ref=pd_ci_mcx_mh_mcx_views_0?pd_rd_w=wm3h2&content-id=amzn1.sym.8b590b55-908d-4829-9f90-4c8752768e8b%3Aamzn1.symc.40e6a10e-cbc4-4fa5-81e3-4435ff64d03b&pf_rd_p=8b590b55-908d-4829-9f90-4c8752768e8b&pf_rd_r=Z8ECMH9ABJ02EA0R5K46&pd_rd_wg=0SYTs&pd_rd_r=2b721d28-423e-4783-8caa-098bb631bd20&pd_rd_i=B0BSHDJG9T', 
                    'https://www.amazon.com/Harvard-16-oz-Ceramic-Mug/dp/B0B2ZB4XMZ/?_encoding=UTF8&pd_rd_w=LHfmo&content-id=amzn1.sym.3c3990c3-513c-4686-8d92-a42b4095cecb%3Aamzn1.symc.8b620bc3-61d8-46b3-abd9-110539785634&pf_rd_p=3c3990c3-513c-4686-8d92-a42b4095cecb&pf_rd_r=0RZA1NMRJ8SH5MJTYVQM&pd_rd_wg=RMfzY&pd_rd_r=23ac4591-73f2-48fa-b640-a781197701ba&ref_=pd_hp_d_btf_ci_mcx_mr_hp_d&th=1']

# Define stock tickers
stock_tickers = ['AAPL', 'GOOGL', 'TSLA', 'NVDA']

#Define cryptocurrencies
cryptos = 'bitcoin, ethereum'

def update_prices():
    con = sqlite3.connect('prices.db')
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    amazon_list = return_price(amazon_item_list)
    stock_list = return_stock_prices(stock_tickers)
    crypto_list = return_crypto_prices(cryptos)
    low_price_list = []

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
            
    con.close()
    return low_price_list

def check_lowest_price(con, item, table, column):
    cursor = con.cursor()
    query = f'''
    SELECT MIN(price) AS lowest_price
    FROM {table}
    WHERE {column} = ?
    AND timestamp >= datetime('now', '-14 days');
    '''
    cursor.execute(query, (item,))
    result = cursor.fetchone()
    cursor.close()
    
    if isinstance(result[0], float):
        return result[0]
    else:
        return float(result[0].replace(',', ''))
