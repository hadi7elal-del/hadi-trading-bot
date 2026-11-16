import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from binance.client import Client
from binance.exceptions import BinanceAPIException

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hadi's Binance Trading Bot is Live and Running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def check_wallet_and_market():
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET_KEY')
    
    client = Client(api_key, api_secret)
    
    try:
        print("\n========================================")
        print(" Scanning spot wallet and markets now...")
        print("========================================")
        
        account = client.get_account()
        balances = account['balances']
        
        for asset in balances:
            currency = asset['asset']
            free_balance = float(asset['free'])
            
            if currency in ['USDT', 'USDC', 'FDUSD'] or free_balance <= 0:
                continue
                
            trading_pair = f"{currency}USDT"
            
            try:
                ticker = client.get_symbol_ticker(symbol=trading_pair)
                current_price = float(ticker['price'])
                print(f" Asset: {currency} | Balance: {free_balance} | Current Price: {current_price} USDT")
            except BinanceAPIException:
                continue
                
        print("----------------------------------------")
    except Exception as e:
        print(f" Binance API Error: {e}")

def background_bot_loop():
    while True:
        try:
            check_wallet_and_market()
        except Exception as e:
            print(f" Loop Error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("Web server started successfully.")

    print("Starting Binance Trading Bot loop...")
    background_bot_loop()
