import time

def check_sma_strategy(client, symbol):
    """
    Fetches historical klines safely with expanded delays 
    to completely avoid Binance rate limits and IP bans (-1003).
    """
    try:
        # Add a mandatory buffer before fetching each symbol
        time.sleep(5)
        
        klines = client.get_historical_klines(
            symbol, 
            client.KLINE_INTERVAL_15MINUTE, 
            "1 hour ago UTC"
        )
        
        if not klines or len(klines) < 20:
            print(f"Not enough data for {symbol}")
            return None

        closes = [float(entry[4]) for entry in klines]
        sma_20 = sum(closes[-20:]) / 20
        current_price = closes[-1]
        
        print(f"[{symbol}] Current Price: {current_price}, SMA-20: {sma_20:.4f}")
        
        return {"symbol": symbol, "price": current_price, "sma_20": sma_20}
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        # Sleep longer if an error occurs to let the IP ban lift
        time.sleep(10)
        return None
