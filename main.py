 import os
import time
from binance.client import Client

# Fetch API keys from Render environment variables
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

# Initialize Binance client for Spot trading
client = Client(api_key, api_secret)

# Trading configuration
SYMBOL = 'BTCUSDT'
CHECK_INTERVAL = 60

def check_balance():
    try:
        balance = client.get_asset_balance(asset='USDT')
        print(f"Available USDT Balance: {balance['free']}")
        return float(balance['free'])
    except Exception as e:
        print(f"Error reading balance: {e}")
        return 0.0

def get_current_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def execute_trade():
    print(f"Checking market for {SYMBOL}...")
    price = get_current_price(SYMBOL)
    if price:
        print(f"Current price of {SYMBOL} is: {price}")
        check_balance()

if __name__ == "__main__":
    print("--- Spot Trading Bot Started ---")
    while True:
        try:
            execute_trade()
        except Exception as e:
            print(f"General error occurred: {e}")
        time.sleep(CHECK_INTERVAL)
