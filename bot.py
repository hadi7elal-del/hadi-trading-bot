import time
from binance.client import Client

# Initialize Binance Client
client = Client()

def main():
    while True:
        try:
            # Fetch Bitcoin ticker price
            ticker = client.get_symbol_ticker(symbol="BTCUSDT")
            print(f"Current Bitcoin Price: {ticker['price']}")
        except Exception as e:
            print(f"Error connecting to Binance: {e}")
        
        # 60 seconds sleep to prevent hitting API rate limits and IP ban
        time.sleep(60)

if __name__ == "__main__":
    main()
