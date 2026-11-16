from binance.client import Client
from binance.exceptions import BinanceAPIException

def analyze_market_and_decide(client, symbol="BTCUSDT"):
    """
    Analyzes market data based on historical candles and Simple Moving Average (SMA)
    to generate trading signals (BUY, SELL, HOLD).
    """
    try:
        # Fetch last 50 candles on 15-minute timeframe
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE, limit=50)
        closes = [float(entry[4]) for entry in klines]
        
        current_price = closes[-1]
        sma_20 = sum(closes[-20:]) / 20
        
        print(f"[Strategy] Symbol: {symbol} | Price: {current_price} | SMA20: {sma_20}")
        
        # Simple scalping strategy logic
        if current_price > sma_20 * 1.002:
            return "BUY", current_price
        elif current_price < sma_20 * 0.998:
            return "SELL", current_price
        else:
            return "HOLD", current_price
            
    except Exception as e:
        print(f"[Strategy] Analysis Error for {symbol}: {e}")
        return "HOLD", 0.0

def execute_trade_order(client, symbol, side, quantity=0.001):
    """
    Executes a real MARKET buy or sell order on Binance Spot.
    """
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        print(f"[Trade] Successfully executed {side} for {symbol}! Order ID: {order['orderId']}")
        return order
    except BinanceAPIException as e:
        print(f"[Trade] Binance API Error during {side}: {e}")
    except Exception as e:
        print(f"[Trade] General Error: {e}")
    return None
