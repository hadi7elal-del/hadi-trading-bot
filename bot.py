import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from binance.client import Client
from binance.exceptions import BinanceAPIException

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("Web server started on port 10000 to keep Render happy.")

    print("Starting Binance Bot...")
    client = None
    
    while client is None:
        try:
            client = Client()
            print("Successfully connected to Binance!")
        except BinanceAPIException as e:
            print(f"Connection blocked, retrying in 60s: {e}")
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

    while True:
        try:
            ticker = client.get_symbol_ticker(symbol="BTCUSDT")
            print(f"Current Bitcoin Price: {ticker['price']}")
            time.sleep(60)
        except BinanceAPIException as e:
            print(f"API Error: {e}")
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
