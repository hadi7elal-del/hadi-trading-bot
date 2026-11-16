 import os
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

client = Client(api_key, api_secret)

QUOTE_ASSET = 'USDT'
CHECK_INTERVAL = 60
PROFIT_TARGET_PCT = 2.0

# قاموس لتخزين أسعار البداية لكل عملة يتم اكتشافها في المحفظة
baseline_prices = {}

def get_account_balances():
    try:
        account = client.get_account()
        balances = account.get('balances', [])
        active_assets = []
        for b in balances:
            asset = b['asset']
            free = float(b['free'])
            # نستثني عملات الكاش الأساسية ونبحث عن العملات الرقمية التي تمتلكها
            if asset != QUOTE_ASSET and free > 0:
                active_assets.append((asset, free))
        return active_assets
    except Exception as e:
        print(f"Error fetching account balances: {e}")
        return []

def get_current_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        return None

def execute_portfolio_strategy():
    print("\nScanning portfolio for active assets...")
    assets = get_account_balances()
    
    if not assets:
        print("No active digital assets found in wallet (only USDT or empty).")
        return

    for asset, free_balance in assets:
        symbol = f"{asset}{QUOTE_ASSET}"
        current_price = get_current_price(symbol)
        
        if not current_price:
            # ربما الزوج غير متوفر للتداول المباشر مع USDT
            continue

        print(f"Asset: {asset} | Balance: {free_balance} | Current Price: {current_price}")

        # إذا كانت المرة الأولى التي نرى فيها هذه العملة، نثبت سعر البداية لها
        if asset not in baseline_prices:
            baseline_prices[asset] = current_price
            print(f"Baseline price set for {asset}: {baseline_prices[asset]}")
            continue

        baseline = baseline_prices[asset]
        price_change_pct = ((current_price - baseline) / baseline) * 100
        print(f"-> {asset} change: {price_change_pct:.2f}% (Target: +{PROFIT_TARGET_PCT}%)")

        # التحقق من تحقيق نسبة الربح المستهدفة
        if price_change_pct >= PROFIT_TARGET_PCT:
            print(f"Profit target reached for {asset}! Attempting to sell...")
            try:
                # التأكد من الحد الأدنى للكمية أو القيمة حسب قواعد بينانس
                order = client.order_market_sell(
                    symbol=symbol,
                    quantity=round(free_balance, 2)
                )
                print(f"Successfully sold {asset}! Order details: {order}")
                # تحديث سعر البداية بعد البيع الناجح
                baseline_prices[asset] = current_price
            except BinanceAPIException as e:
                print(f"Order failed for {asset}: {e}")

if __name__ == "__main__":
    print("--- Multi-Asset Automated Portfolio Bot Started ---")
    while True:
        try:
            execute_portfolio_strategy()
        except Exception as e:
            print(f"General error occurred: {e}")
        time.sleep(CHECK_INTERVAL)
