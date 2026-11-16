import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from binance.client import Client
from strategy import analyze_market_and_decide
from trader import execute_buy_order, execute_sell_order

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hadi's Modular Trading Bot is Live and Executing!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def bot_trading_loop():
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET_KEY')
    
    client = Client(api_key, api_secret)
    
    while True:
        try:
            print("\n========================================")
            print(" Scanning wallet assets and markets...")
            print("========================================")
            
            account = client.get_account()
            balances = account['balances']
            
            for asset in balances:
                currency = asset['asset']
                free_balance = float(asset['free'])
                
                # Skip stablecoins and zero balances
                if currency in ['USDT', 'USDC', 'FDUSD'] or free_balance <= 0:
                    continue
                    
                trading_pair = f"{currency}USDT"
                
                # Analyze market and get signal from strategy module
                action, price = analyze_market_and_decide(client, symbol=trading_pair)
                print(f" Asset: {currency} | Signal: {action} | Price: {price}")
                
                # Execute orders automatically based on signal via trader module
                if action == "BUY":
                    print(f" BUY signal triggered for {trading_pair}!")
                    # execute_buy_order(client, trading_pair, quantity=1.0)
                elif action == "SELL":
                    print(f" SELL signal triggered for {trading_pair}!")
                    # execute_sell_order(client, trading_pair, quantity=1.0)
                    
            print("----------------------------------------")
        except Exception as e:
            print(f" Bot Loop Error: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    # Start background web server for Render
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("Web server started successfully.")

    # Start main bot loop
    print("Starting Modular Trading Bot loop...")
    bot_trading_loop()
