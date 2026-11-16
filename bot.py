import os
import time
from flask import Flask
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Initialize Flask web server to keep the bot alive on Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Hadi's Binance Trading Bot is Live and Running!"

# Securely retrieve API keys from Render environment variables
api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_API_SECRET_KEY')

# Initialize Binance client for Spot trading
client = Client(api_key, api_secret)

# Trading Strategy Parameters
PROFIT_TARGET_PERCENT = 2.0   # Target profit percentage to sell
REBUY_DIP_PERCENT = 2.0       # Dip percentage to buy back

def check_wallet_and_market():
    try:
        print("\n========================================")
        print(" Scanning spot wallet and markets now...")
        print("========================================")
        
        # Fetch account details and spot balances
        account = client.get_account()
        balances = account['balances']
        
        for asset in balances:
            currency = asset['asset']
            free_balance = float(asset['free'])
            
            # Exclude stablecoins and zero balances
            if currency in ['USDT', 'USDC', 'FDUSD'] or free_balance <= 0:
                continue
                
            trading_pair = f"{currency}USDT"
            
            try:
                # Fetch current market price against USDT
                ticker = client.get_symbol_ticker(symbol=trading_pair)
                current_price = float(ticker['price'])
                
                print(f" Asset: {currency} | Balance: {free_balance} | Current Price: {current_price} USDT")
                
            except BinanceAPIException:
                # Some assets might not have a direct USDT trading pair
                continue
                
        print("----------------------------------------")
        
    except BinanceAPIException as e:
        print(f" Binance API Error: {e}")
    except Exception as e:
        print(f" Unexpected Error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    # Run initial scan on startup
    check_wallet_and_market()
    
    # Run the web server to keep the bot alive
    app.run(host='0.0.0.0', port=port)
