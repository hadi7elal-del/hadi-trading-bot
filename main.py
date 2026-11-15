 import os, time, hmac, hashlib, argparse
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY", "").strip()
API_SECRET = os.getenv("BINANCE_API_SECRET", "").strip()
BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com").rstrip("/")
LIVE_TRADING = os.getenv("LIVE_TRADING", "false").lower() == "true"
MAX_BUY_USDT = float(os.getenv("MAX_BUY_USDT", "20"))
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
        raise RuntimeError("أضف مفاتيح API في ملف .env أولاً.")
    p = dict(params or {})
    p["timestamp"] = int(time.time() * 1000)
    p["recvWindow"] = 5000
    query = urlencode(p)
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"{BASE_URL}{path}?{query}&signature={signature}"
    r = session.request(method, url, timeout=TIMEOUT)
    if not r.ok:
        raise RuntimeError(f"Binance API error {r.status_code}: {r.text}")
    return r.json()

def price(symbol):
    data = public_get("/api/v3/ticker/price", {"symbol": symbol.upper()})
    print(f'{data["symbol"]}: {data["price"]} USDT تقريباً (حسب زوج التداول)')

def account():
    data = signed_request("GET", "/api/v3/account")
    print("حالة الاتصال: ناجح")
    print("الأرصدة غير الصفرية:")
    found = False
    for b in data.get("balances", []):
        free, locked = float(b["free"]), float(b["locked"])
        if free or locked:
            found = True
            print(f'  {b["asset"]}: متاح {free:g} | محجوز {locked:g}')
    if not found:
        print("لا توجد أرصدة غير صفرية ظاهرة.")

def buy(symbol, quote_qty, confirm):
    symbol = symbol.upper()
    if quote_qty <= 0 or quote_qty > MAX_BUY_USDT:
        raise ValueError(f"قيمة الشراء يجب أن تكون بين 0 و {MAX_BUY_USDT} USDT.")
    if not LIVE_TRADING or not confirm:
        print("معاينة فقط — لم يتم إرسال أي أمر حقيقي.")
        print(f"شراء سوقي: {symbol} بقيمة {quote_qty} من عملة التسعير.")
        print("للتنفيذ الحقيقي: LIVE_TRADING=true مع --confirm-live.")
        return
    print("إرسال أمر شراء حقيقي...")
    result = signed_request("POST", "/api/v3/order", {
        "symbol": symbol, "side": "BUY", "type": "MARKET",
        "quoteOrderQty": f"{quote_qty:.8f}", "newOrderRespType": "FULL"
    })
    print("استجابة Binance:")
    print(result)

def sell(symbol, quantity, confirm):
    symbol = symbol.upper()
    if quantity <= 0:
        raise ValueError("الكمية يجب أن تكون أكبر من صفر.")
    if not LIVE_TRADING or not confirm:
        print("معاينة فقط — لم يتم إرسال أي أمر حقيقي.")
        print(f"بيع سوقي: {quantity} من {symbol}.")
        print("للتنفيذ الحقيقي: LIVE_TRADING=true مع --confirm-live.")
        return
    print("تنبيه: أمر بيع سوقي حقيقي قد ينفذ بسعر متغير.")
    result = signed_request("POST", "/api/v3/order", {
        "symbol": symbol, "side": "SELL", "type": "MARKET",
        "quantity": f"{quantity:.8f}", "newOrderRespType": "FULL"
    })
    print("استجابة Binance:")
    print(result)

def main():
    parser = argparse.ArgumentParser(description="Hadi Trading Bot — Binance Spot")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("account", help="قراءة رصيد Spot")
    p = sub.add_parser("price", help="قراءة السعر")
    p.add_argument("symbol")
    b = sub.add_parser("buy", help="معاينة/شراء سوقي محدود")
    b.add_argument("symbol")
    b.add_argument("quote_qty", type=float, help="قيمة الشراء بعملة التسعير، غالباً USDT")
    b.add_argument("--confirm-live", action="store_true")
    s = sub.add_parser("sell", help="معاينة/بيع سوقي")
    s.add_argument("symbol")
    s.add_argument("quantity", type=float)
    s.add_argument("--confirm-live", action="store_true")
    args = parser.parse_args()

    try:
        if args.cmd == "account": account()
        elif args.cmd == "price": price(args.symbol)
        elif args.cmd == "buy": buy(args.symbol, args.quote_qty, args.confirm_live)
        elif args.cmd == "sell": sell(args.symbol, args.quantity, args.confirm_live)
    except Exception as e:
        print("تعذر إكمال العملية:", e)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
