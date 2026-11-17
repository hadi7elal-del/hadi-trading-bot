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
        self.wfile.write(b"Hadi's Integrated Trading Bot is running successfully!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def analyze_market_and_decide(client, symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MIN, limit=25)
        closes = [float(entry[4]) for entry in klines]
        
        current_price = closes[-1]
        sma_20 = sum(closes[-20:]) / 20
        
        print(f"[Strategy] Symbol: {symbol} | Price: {current_price} | SMA-20: {sma_20:.4f}")
        
        if current_price > sma_20 * 1.002:
            return "BUY", current_price
        elif current_price < sma_20 * 0.998:
            return "SELL", current_price
        else:
            return "HOLD", current_price
            
    except Exception as e:
        print(f"[Strategy] Analysis Error for {symbol}: {e}")
        return "HOLD", 0.0

def bot_trading_loop():
    print("Waiting 20 seconds for network stabilization...")
    time.sleep(20)

    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET_KEY')
    
    if not api_key or not api_secret:
        print("[Error] API keys not found in environment variables!")
        return

    client = Client(api_key, api_secret, {"verify": True, "timeout": 20})
    
    target_symbols = ['XRPUSDT', 'DOGEUSDT', 'UNIUSDT']
    
    while True:
        try:
            print("\n" + "="*50)
            print(" Scanning target markets...")
            print("="*50)
            
            for symbol in target_symbols:
                action, price = analyze_market_and_decide(client, symbol)
                print(f" Asset: {symbol} | Signal: {action} | Price: {price}")
                
                if action == "BUY":
                    print(f" BUY signal triggered for {symbol}")
                elif action == "SELL":
                    print(f" SELL signal triggered for {symbol}")
                    
                time.sleep(5)
                
            print("-" * 50)
        except Exception as e:
            print(f"Bot Loop Error: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("Web server started successfully.")
    
    print("Starting Integrated Trading Bot loop...")
    bot_trading_loop()
