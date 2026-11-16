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
DIP_BUY_PCT = -2.0  # نسبة النزول لاعتبار العملة فرصة شراء (القاع)
TRADE_AMOUNT_USDT = 15.0  # الحد الأدنى أو القيمة لكل صفقة شراء بالـ USDT

baseline_prices = {}

# قائمة العملات المقترحة للمراقبة واقتناص الهبوط
WATCH_SYMBOLS = ['XRPUSDT', 'DOGEUSDT', 'UNIUSDT', 'BTCUSDT', 'ETHUSDT', 'SOLUSDT']

def get_account_balance(asset):
    try:
        balance = client.get_asset_balance(asset=asset)
        return float(balance['free']) if balance else 0.0
    except Exception as e:
        print(f"Error fetching balance for {asset}: {e}")
        return 0.0

def get_current_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        return None

def execute_smart_strategy():
    print("\n--- Running Smart Portfolio & Market Strategy ---")
    
    # 1. فحص المحفظة الحالية لجني الأرباح (بيع العملات المرتفعة >= 2%)
    account_info = client.get_account()
    for b in account_info.get('balances', []):
        asset = b['asset']
        free_balance = float(b['free'])
        
        if asset != QUOTE_ASSET and free_balance > 0:
            symbol = f"{asset}{QUOTE_ASSET}"
            current_price = get_current_price(symbol)
            if not current_price:
                continue

            if asset not in baseline_prices:
                baseline_prices[asset] = current_price
                continue

            baseline = baseline_prices[asset]
            price_change_pct = ((current_price - baseline) / baseline) * 100
            print(f"Holding -> {asset} change: {price_change_pct:.2f}% (Target: +{PROFIT_TARGET_PCT}%)")

            if price_change_pct >= PROFIT_TARGET_PCT:
                print(f"Profit target reached for {asset}! Executing market sell to USDT...")
                try:
                    order = client.order_market_sell(
                        symbol=symbol,
                        quantity=free_balance
                    )
                    print(f"SUCCESS! Sold {asset}. Order: {order}")
                    baseline_prices[asset] = current_price
                except BinanceAPIException as e:
                    print(f"Binance API error selling {asset}: {e}")

    # 2. مسح السوق واقتناص الهبوط (شراء العملات النازلة باستخدام USDT المتاح)
    usdt_balance = get_account_balance(QUOTE_ASSET)
    print(f"Available USDT Balance: {usdt_balance}")

    if usdt_balance >= TRADE_AMOUNT_USDT:
        for symbol in WATCH_SYMBOLS:
            current_price = get_current_price(symbol)
            if not current_price:
                continue

            base_asset = symbol.replace(QUOTE_ASSET, '')

            if base_asset not in baseline_prices:
                baseline_prices[base_asset] = current_price
                continue

            baseline = baseline_prices[base_asset]
            price_change_pct = ((current_price - baseline) / baseline) * 100
            print(f"Market Watch -> {symbol} change: {price_change_pct:.2f}% (Dip Target: {DIP_BUY_PCT}%)")

            # إذا هبطت العملة بالنسب المحدد (القاع)، نقوم بشرائها لاستغلال الـ USDT
            if price_change_pct <= DIP_BUY_PCT:
                print(f"Dip detected for {symbol}! Executing buy order...")
                try:
                    # حساب الكمية المطلوبة للشراء بناءً على المبلغ المخصص لكل صفقة
                    quantity = round(TRADE_AMOUNT_USDT / current_price, 2)
                    order = client.order_market_buy(
                        symbol=symbol,
                        quantity=quantity
                    )
                    print(f"SUCCESS! Bought {symbol}. Order: {order}")
                    baseline_prices[base_asset] = current_price
                    break  # شراء عملة واحدة في كل دورة حفاظاً على السيولة
                except BinanceAPIException as e:
                    print(f"Binance API error buying {symbol}: {e}")

if __name__ == "__main__":
    print("--- Smart Trading Bot Started (Sell High & Buy Dip) ---")
    while True:
        try:
            execute_smart_strategy()
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(CHECK_INTERVAL)
