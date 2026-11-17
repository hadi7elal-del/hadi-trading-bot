import os
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
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')

    if not api_key or not secret_key:
        logging.error("API keys missing in environment variables!")
        return

    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': secret_key,
        'enableRateLimit': True,
    })

    # Enable sandbox mode for Testnet operations
    exchange.set_sandbox_mode(True)
    
    symbols = ['XRPUSDT', 'DOGEUSDT', 'UNIUSDT']
    logging.info(f"Starting trading bot for symbols: {symbols}")

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
