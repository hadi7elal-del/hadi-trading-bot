import time
from binance.exceptions import BinanceAPIException

def execute_trade_logic(client, symbol, current_price, sma_20):
    try:
        base_asset = symbol.replace("USDT", "")
        
        account = client.get_account()
        balances = {item['asset']: float(item['free']) for item in account['balances']}
        
        usdt_balance = balances.get("USDT", 0.0)
        asset_balance = balances.get(base_asset, 0.0)
        
        print(f"[{symbol}] Balances -> USDT: {usdt_balance:.2f}, {base_asset}: {asset_balance:.4f}", flush=True)

        exchange_info = client.get_symbol_info(symbol)
        step_size = 1.0
        min_notional = 10.0
        
        if exchange_info:
            for filt in exchange_info['filters']:
                if filt['filterType'] == 'LOT_SIZE':
                    step_size = float(filt['stepSize'])
                elif filt['filterType'] in ['NOTIONAL', 'MIN_NOTIONAL']:
                    min_notional = float(filt.get('minNotional', 10.0))

        # Strategy Buy Condition: Price <= SMA_20
        if current_price <= sma_20:
            print(f"[{symbol}] Signal: Price ({current_price}) <= SMA ({sma_20:.4f}) -> Dip! BUY...", flush=True)
            target_usdt_to_spend = 11.0 
            
            if usdt_balance >= target_usdt_to_spend:
                raw_qty = target_usdt_to_spend / current_price
                precision = 0
                if step_size < 1:
                    precision = len(str(step_size).split('.')[1].rstrip('0'))
                quantity = round(raw_qty, precision)
                
                if (quantity * current_price) >= min_notional:
                    print(f"[{symbol}] Placing MARKET BUY order for {quantity} {base_asset}...", flush=True)
                    order = client.order_market_buy(symbol=symbol, quantity=quantity)
                    print(f"[{symbol}] BUY Success: {order}", flush=True)
                else:
                    print(f"[{symbol}] Order value below minimum notional ({min_notional} USDT).", flush=True)
            else:
                print(f"[{symbol}] Not enough USDT balance.", flush=True)

        # Strategy Sell Condition: Price > SMA_20
        elif current_price > sma_20:
            print(f"[{symbol}] Signal: Price ({current_price}) > SMA ({sma_20:.4f}) -> Take Profit! SELL...", flush=True)
            
            if asset_balance > 0:
                precision = 0
                if step_size < 1:
                    precision = len(str(step_size).split('.')[1].rstrip('0'))
                quantity = round(asset_balance, precision)
                
                if (quantity * current_price) >= min_notional:
                    print(f"[{symbol}] Placing MARKET SELL order for {quantity} {base_asset}...", flush=True)
                    order = client.order_market_sell(symbol=symbol, quantity=quantity)
                    print(f"[{symbol}]$ SELL Success: {order}", flush=True)
                else:
                    print(f"[{symbol}] Asset value below minimum notional.", flush=True)
            else:
                print(f"[{symbol}] No {base_asset} balance to sell.", flush=True)

    except BinanceAPIException as e:
        print(f"[{symbol}] Binance API Error: {e}", flush=True)
    except Exception as e:
        print(f"[{symbol}] General Error: {e}", flush=True)

def check_sma_strategy(client, symbol):
    try:
        time.sleep(5)

        klines = client.get_historical_klines(
            symbol,
            client.KLINE_INTERVAL_15MINUTE,
            "1 hour ago UTC"
        )

        if not klines or len(klines) < 20:
            print(f"Not enough data for {symbol}", flush=True)
            return None

        closes = [float(entry[4]) for entry in klines]
        sma_20 = sum(closes[-20:]) / 20
        current_price = closes[-1]

        print(f"[{symbol}] Current Price: {current_price}, SMA-20: {sma_20:.4f}", flush=True)
        execute_trade_logic(client, symbol, current_price, sma_20)

        return {"symbol": symbol, "price": current_price, "sma_20": sma_20}

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}", flush=True)
        time.sleep(15)
        return None
