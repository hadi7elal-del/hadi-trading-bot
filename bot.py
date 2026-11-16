import time
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException

def main():
    client = None
    
    # محاولة الاتصال وتجاوز الحظر المؤقت إن وجد
    while client is None:
        try:
            print("Trying to connect to Binance...")
            client = Client()
        except BinanceAPIException as e:
            print(f"IP is still banned or connection failed: {e}. Waiting 60 seconds...")
            time.sleep(60)
        except Exception as e:
            print(f"Unexpected error: {e}. Waiting 60 seconds...")
            time.sleep(60)

    # التشغيل الطبيعي بعد نجاح الاتصال
    while True:
        try:
            ticker = client.get_symbol_ticker(symbol="BTCUSDT")
            print(f"Current Bitcoin Price: {ticker['price']}")
            time.sleep(60)
        except BinanceAPIException as e:
            print(f"Binance API error during execution: {e}")
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
