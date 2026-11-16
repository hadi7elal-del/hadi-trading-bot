import time
from binance.client import Client
from binance.exceptions import BinanceAPIException

def main():
    client = None
    
    while client is None:
        try:
            client = Client()
        except BinanceAPIException as e:
            time.sleep(60)
        except Exception as e:
            time.sleep(60)

    while True:
        try:
            ticker = client.get_symbol_ticker(symbol="BTCUSDT")
            print(f"Current Bitcoin Price: {ticker['price']}")
            time.sleep(60)
        except BinanceAPIException as e:
            time.sleep(60)
        except Exception as e:
            time.sleep(60)

if __name__ == "__main__":
    main()
