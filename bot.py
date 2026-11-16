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
        self.wfile.write(b"Hadi's Integrated Trading Bot is Live and Executing!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def analyze_market_and_decide(client, symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE, limit=50)
        closes = [float(entry[4]) for entry in klines]
        
        current_price = closes[-1]
        sma_20 = sum(closes[-20:]) / 20
        
        print(f"[Strategy] Symbol: {symbol} | Price: {current_price} | SMA20: {sma_20}")
        
        if current_price > sma_20 * 1.002:
            return "BUY", current_price
        elif current_price < sma_20 * 0.998:
            return "SELL", current_price
        else:
            return "HOLD", current_price
            
    except Exception as e:
        print(f"[Strategy] Analysis Error for {symbol}: {e}")
        return "HOLD", 0.0

def execute_trade_order(client, symbol, side, quantity=1.0):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        print(f"[Trader] Successfully executed {side} for {symbol}! Order ID: {order['orderId']}")
        return order
    except BinanceAPIException as e:
        print(f"[Trader] Binance API Error during {side} for {symbol}: {e}")
    except Exception as e:
        print(f"[Trader] General Error during {side}: {e}")
    return None

def bot_trading_loop():
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET_KEY')
    
    client = Client(api_key, api_secret)
    
    target_symbols = ['XRPUSDT', 'DOGEUSDT', 'UNIUSDT']
    
    while True:
        try:
            print("\n========================================")
            print(" Scanning target markets...")
            print("========================================")
            
            for symbol in target_symbols:
                action, price = analyze_market_and_decide(client, symbol=symbol)
                print(f" Asset: {symbol} | Signal: {action} | Price: {price}")
                
                if action == "BUY":
                    print(f" BUY signal triggered for {symbol}!")
                    # execute_trade_order(client, symbol, 'BUY', quantity=10.0)
                elif action == "SELL":
                    print(f" SELL signal triggered for {symbol}!")
                    # execute_trade_order(client, symbol, 'SELL', quantity=10.0)
                
                time.sleep(5)
                    
            print("----------------------------------------")
        except Exception as e:
            print(f" Bot Loop Error: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("Web server started successfully.")

    print("Starting Integrated Trading Bot loop...")
    bot_trading_loop()
