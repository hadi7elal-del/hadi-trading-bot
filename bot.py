import sys
import os

# Force Python to flush stdout immediately so logs appear instantly on Render
sys.stdout.reconfigure(line_buffering=True)

import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from binance.client import Client
from strategy import check_sma_strategy

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hadi Trading Bot is running smoothly!")

def run_dummy_server():
    port = int(os.getenv("PORT", 10000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, DummyHandler)
    print(f"Dummy HTTP server started on port {port}", flush=True)
    httpd.serve_forever()

def run_trading_bot():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET_KEY")
    
    if not api_key or not api_secret:
        print("API keys are missing! Please check environment variables.", flush=True)
        return

    client = None
    
    while client is None:
        try:
            print("Attempting to connect to Binance safely...", flush=True)
            client = Client(api_key, api_secret, {"timeout": 30})
            print("Binance client connected successfully.", flush=True)
        except Exception as e:
            print(f"Initialization paused due to rate limit/ban: {e}", flush=True)
            print("Waiting 90 seconds before retrying client initialization...", flush=True)
            time.sleep(90)

    symbols = ["XRPUSDT", "DOGEUSDT", "UNIUSDT"]
    
    print("Hadi Trading Bot entering main loop...", flush=True)
    
    while True:
        try:
            print("\n--- Starting new market check cycle ---", flush=True)
            for symbol in symbols:
                check_sma_strategy(client, symbol)
                # Increased buffer to 15 seconds between symbols to completely prevent IP rate limits (-1003)
                time.sleep(15)
            
            print("Cycle completed. Waiting 300 seconds (5 minutes) before next check...", flush=True)
            time.sleep(300)
            
        except Exception as e:
            print(f"An error occurred in main loop: {e}", flush=True)
            time.sleep(60)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    run_trading_bot()
