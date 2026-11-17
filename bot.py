import time
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():
    symbols = ['XRPUSDT', 'DOGEUSDT', 'UNIUSDT']
    logging.info(f"Starting price fetcher for symbols: {symbols}")

    while True:
        try:
            for symbol in symbols:
                url = f"https://api1.binance.com/api/v3/ticker/price?symbol={symbol}"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if 'price' in data:
                    logging.info(f"Symbol: {symbol} | Current Price: {data['price']}")
                else:
                    logging.warning(f"Could not fetch price for {symbol}: {data}")
                
            time.sleep(60)

        except Exception as e:
            logging.error(f"An error occurred while fetching data: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
