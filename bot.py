import sys
import os

# Force Python to flush stdout immediately so logs appear instantly on Render
sys.stdout.reconfigure(line_buffering=True)

import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from binance.client import Client
from strategy import check_sma_strategy

# Dummy HTTP server to satisfy Render's requirement for Web Services to bind a port
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hadi Trading Bot is running smoothly!")

def run_dummy_server():
    port = int(os.getenv("PORT", 10000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, DummyHandler)
    print(f"Dummy HTTP server started on port {port}")
    httpd.serve_forever()

def run_trading_bot():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET_KEY")
    
    if not api_key or not api_secret:
        print("API keys are missing! Please check environment variables.")
        return

    client = None
    
    # Try initializing the client safely with a loop to handle temporary bans smoothly
    while client is None:
        try:
            print("Attempting to connect to Binance safely...")
            client = Client(api_key, api_secret, {"timeout": 30})
            print("Binance client connected successfully.")
        except Exception as e:
            print(f"Initialization paused due to rate limit/ban: {e}")
            print("Waiting 60 seconds before retrying client initialization...")
            time.sleep(60)

    symbols = ["XRPUSDT", "DOGEUSDT", "UNIUSDT"]
    
    print("Hadi Trading Bot entering main loop...")
    
    while True:
        try:
            print("\n--- Starting new market check cycle ---")
            for symbol in symbols:
                check_sma_strategy(client, symbol)
                time.sleep(10)
            
            print("Cycle completed. Waiting 180 seconds before next check...")
            time.sleep(180)
            
        except Exception as e:
            print(f"An error occurred in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Start the dummy HTTP server in a background thread to keep Render happy
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    
    # Run the main trading bot loop
    run_trading_bot()
