import time

def check_sma_strategy(client, symbol):
    """
    Fetches historical klines for 15-minute intervals,
    calculates SMA-20, and handles rate limits safely.
    """
    try:
        klines = client.get_historical_klines(
            symbol, 
            client.KLINE_INTERVAL_15MINUTE, 
            "2 hours ago UTC"
        )
        
        if not klines or len(klines) < 20:
            print(f"Not enough data for {symbol}")
            return None

        closes = [float(entry[4]) for entry in klines]
        sma_20 = sum(closes[-20:]) / 20
        current_price = closes[-1]
        
        print(f"[{symbol}] Current Price: {current_price}, SMA-20: {sma_20:.4f}")
        time.sleep(3)
        
        return {"symbol": symbol, "price": current_price, "sma_20": sma_20}
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
