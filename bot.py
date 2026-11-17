import time
import logging
import ccxt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'urls': {
            'api': {
                'public': 'https://testnet.binance.vision/api/v3',
            }
        }
    })
    
    symbols = ['XRPUSDT', 'DOGEUSDT', 'UNIUSDT']
    logging.info(f"Starting public market data bot for symbols: {symbols}")

    while True:
        try:
            for symbol in symbols:
                ticker = exchange.fetch_ticker(symbol)
                last_price = ticker['last']
                logging.info(f"Symbol: {symbol} | Current Price: {last_price}")
                
            time.sleep(90)

        except Exception as e:
            logging.error(f"An error occurred while fetching market data: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
