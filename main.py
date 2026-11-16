import os
import time
from binance.client import Client

api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

client = Client(api_key, api_secret)

def main():
    print("Bot started successfully...")
    
    try:
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        print(f"Current Bitcoin price: {ticker['price']}")
    except Exception as e:
        print(f"Error connecting or fetching data: {e}")

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
