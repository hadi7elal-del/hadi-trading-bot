import os
import time
from binance.client import Client
from strategy import check_sma_strategy

def run_trading_bot():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET_KEY")
    
    if not api_key or not api_secret:
        print("API keys are missing! Please check environment variables.")
        return

    # Initialize Binance Client with connection parameters
    client = Client(api_key, api_secret)
    symbols = ["XRPUSDT", "DOGEUSDT", "UNIUSDT"]
    
    print("Hadi Trading Bot initialized successfully. Starting main loop...")
    
    while True:
        try:
            print("\n--- Starting new market check cycle ---")
            for symbol in symbols:
                check_sma_strategy(client, symbol)
            
            # Safe sleep between full cycles to avoid rate limits
            print("Cycle completed. Waiting 120 seconds before next check...")
            time.sleep(120)
            
        except Exception as e:
            print(f"An error occurred in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_trading_bot()
