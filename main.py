import os, time, hmac, hashlib, argparse
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY", "").strip()
API_SECRET = os.getenv("BINANCE_API_SECRET", "").strip()
BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com").rstrip("/")
LIVE_TRADING = os.getenv("LIVE_TRADING", "false").lower() == "true"
MAX_BUY_USD = float(os.getenv("MAX_BUY_USD", "20"))
TIMEOUT = 10

session = requests.Session()
if API_KEY:
    session.headers.update({"X-MBX-APIKEY": API_KEY})

def public_get(path, params=None):
    r = session.get(BASE_URL + path, params=params or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def signed_request(method, path, params=None):
    if not API_KEY or not API_SECRET:
        raise RuntimeError("API keys not set.")
    params = params or {}
    params["timestamp"] = int(time.time() * 1000)
    query_string = urlencode(params)
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    params["signature"] = signature
    url = BASE_URL + path
    if method == "GET":
        r = session.get(url, params=params, timeout=TIMEOUT)
    elif method == "POST":
        r = session.post(url, data=params, timeout=TIMEOUT)
    elif method == "DELETE":
        r = session.delete(url, params=params, timeout=TIMEOUT)
    else:
        raise ValueError(f"Unsupported method: {method}")
    r.raise_for_status()
    return r.json()

def get_account_balance():
    data = signed_request("GET", "/api/v3/account")
    balances = data.get("balances", [])
    result = {}
    for b in balances:
        free = float(b["free"])
        locked = float(b["locked"])
        if free > 0 or locked > 0:
            result[b["asset"]] = {"free": free, "locked": locked}
    return result

def get_ticker_price(symbol):
    data = public_get("/api/v3/ticker/price", {"symbol": symbol})
    return float(data["price"])

def market_buy(symbol, quote_order_qty):
    if not LIVE_TRADING:
        print(f"[TEST MODE] Simulated MARKET BUY for {symbol} with {quote_order_qty} USDT")
        return {"simulated": True, "symbol": symbol, "quoteOrderQty": quote_order_qty}
    return signed_request("POST", "/api/v3/order", {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": quote_order_qty
    })

def market_sell(symbol, quantity):
    if not LIVE_TRADING:
        print(f"[TEST MODE] Simulated MARKET SELL for {symbol} with quantity {quantity}")
        return {"simulated": True, "symbol": symbol, "quantity": quantity}
    return signed_request("POST", "/api/v3/order", {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": quantity
    })

def run_bot(symbol):
    print(f"Starting Hadi Trading Bot for {symbol} (Live Trading: {LIVE_TRADING})")
    while True:
        try:
            price = get_ticker_price(symbol)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {symbol} Current Price: {price}")
            
            balances = get_account_balance()
            usdt_balance = balances.get("USDT", {}).get("free", 0.0)
            print(f"Available USDT Balance: {usdt_balance}")
            
            if usdt_balance >= MAX_BUY_USD and LIVE_TRADING:
                print(f"Balance is sufficient. Executing buy order...")
                # Calculate quantity based on max buy amount and current price
                # Safe fallback logic can be adjusted per strategy
                pass
            
        except Exception as e:
            print(f"Error in loop: {e}")
        
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hadi Trading Bot")
    parser.add_argument("--symbol", type=str, default="BTCUSDT", help="Trading symbol (e.g., BTCUSDT)")
    args = parser.parse_args()
    run_bot(args.symbol)
