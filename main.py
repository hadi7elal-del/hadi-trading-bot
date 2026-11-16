 import os
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Fetch API keys from Render environment variables
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

# Initialize Binance client for Spot trading
client = Client(api_key, api_secret)

# Trading configuration
SYMBOL = 'BTCUSDT'       # زوج التداول
BASE_ASSET = 'BTC'       # العملة المراد بيعها عند الربح
QUOTE_ASSET = 'USDT'     # العملة المستلمة
CHECK_INTERVAL = 60      # الفحص كل 60 ثانية
PROFIT_TARGET_PCT = 2.0  # نسبة الربح المستهدفة للبيع (2%)

# Variable to track baseline purchase price
baseline_price = None

def check_balances():
    try:
        base_bal = client.get_asset_balance(asset=BASE_ASSET)
        quote_bal = client.get_asset_balance(asset=QUOTE_ASSET)
        return float(base_bal['free']), float(quote_bal['free'])
    except Exception as e:
        print(f"Error reading balances: {e}")
        return 0.0, 0.0

def get_current_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def execute_strategy():
    global baseline_price
    print(f"Checking market for {SYMBOL}...")
    
    current_price = get_current_price(SYMBOL)
    if not current_price:
        return

    base_free, quote_free = check_balances()
    print(f"Current Price: {current_price} | Balance {BASE_ASSET}: {base_free}")

    # Set baseline price on first run
    if baseline_price is None:
        baseline_price = current_price
        print(f"Baseline price set to: {baseline_price}")
        return

    # Calculate price change percentage
    price_change_pct = ((current_price - baseline_price) / baseline_price) * 100
    print(f"Price change since start: {price_change_pct:.2f}% (Target: +{PROFIT_TARGET_PCT}%)")

    # Check if profit target is reached and we have enough balance to sell
    if price_change_pct >= PROFIT_TARGET_PCT and base_free > 0.0001:
        print(f"Profit target reached! Attempting to sell {BASE_ASSET}...")
        try:
            order = client.order_market_sell(
                symbol=SYMBOL,
                quantity=round(base_free, 5) # تعديل الكمية بدقة
            )
            print(f"Successfully sold! Order details: {order}")
            # Reset baseline after successful sell
            baseline_price = current_price
        except BinanceAPIException as e:
            print(f"Order failed: {e}")

if __name__ == "__main__":
    print("--- Automated Profit-Taking Trading Bot Started ---")
    while True:
        try:
            execute_strategy()
        except Exception as e:
            print(f"General error occurred: {e}")
        time.sleep(CHECK_INTERVAL)
