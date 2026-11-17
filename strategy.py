import time
from binance.exceptions import BinanceAPIException

def execute_trade_logic(client, symbol, current_price, sma_20):
    """
    Executes real buy/sell orders based on SMA strategy.
    Buys when price is below/at SMA (buying the dip) and sells for USDT when price is above SMA.
    """
    try:
        # Determine asset base currency (e.g., XRP from XRPUSDT)
        base_asset = symbol.replace("USDT", "")
        
        # 1. Check account balances
        account = client.get_account()
        balances = {item['asset']: float(item['free']) for item in account['balances']}
        
        usdt_balance = balances.get("USDT", 0.0)
        asset_balance = balances.get(base_asset, 0.0)
        
        print(f"[{symbol}] Balances -> USDT: {usdt_balance:.2f}, {base_asset}: {asset_balance:.4f}", flush=True)

        # Get symbol precision and step size rules from Binance exchange info
        exchange_info = client.get_symbol_info(symbol)
        step_size = 1.0
        min_notional = 10.0 # Default minimum order value in USDT for Binance
        
        if exchange_info:
            for filt in exchange_info['filters']:
                if filt['filterType'] == 'LOT_SIZE':
                    step_size = float(filt['stepSize'])
                elif filt['filterType'] == 'NOTIONAL' or filt['filterType'] == 'MIN_NOTIONAL':
                    min_notional = float(filt.get('minNotional', 10.0))

        # 2. Strategy Buy Condition: Price <= SMA_20 (Buy from below using USDT)
        if current_price <= sma_20:
            print(f"[{symbol}] Signal: Price ({current_price}) <= SMA ({sma_20:.4f}) -> Bullish/Dip! Looking to BUY...", flush=True)
            
            # Allocate a safe amount of USDT per trade (e.g., 11 USDT or available balance if less)
            target_usdt_to_spend = 11.0 
            
            if usdt_balance >= target_usdt_to_spend:
                # Calculate quantity to buy
                raw_qty = target_usdt_to_spend / current_price
                
                # Format quantity according to step_size precision
                precision = 0
                if step_size < 1:
                    precision = len(str(step_size).split('.')[1].rstrip('0'))
                quantity = round(raw_qty, precision)
                
                if (quantity * current_price) >= min_notional:
                    print(f"[{symbol}] Placing MARKET BUY order for {quantity} {base_asset}...", flush=True)
                    order = client.order_market_buy(
                        symbol=symbol,
                        quantity=quantity
                    )
                    print(f"[{symbol}] BUY Order Executed Successfully: {order}", flush=True)
                else:
                    print(f"[{symbol}] Order value too small to meet Binance minimum notional ({min_notional} USDT).", flush=True)
            else:
                print(f"[{symbol}] Not enough USDT balance to execute buy order.", flush=True)

        # 3. Strategy Sell Condition: Price > SMA_20 (Sell asset to USDT from above)
        elif current_price > sma_20:
            print(f"[{symbol}] Signal: Price ({current_price}) > SMA ({sma_20:.4f}) -> Take Profit! Looking to SELL...", flush=True)
            
            if asset_balance > 0:
                # Format quantity according to step_size precision
                precision = 0
                if step_size < 1:
                    precision = len(str(step_size).split('.')[1].rstrip('0'))
                quantity = round(asset_balance, precision)
                
                if (quantity * current_price) >= min_notional:
                    print(f"[{symbol}] Placing MARKET SELL order for {quantity} {base_asset}...", flush=True)
                    order = client.order_market_sell(
                        symbol=symbol,
                        quantity=quantity
                    )
                    print(f"[{symbol}] SELL Order Executed Successfully: {order}", flush=True)
                else:
                    print(f"[{symbol}] Asset holding value too small to meet Binance minimum notional ({min_notional} USDT).", flush=True)
            else:
                print(f"[{symbol}] No {base_asset} balance available to sell.", flush=True)

    except BinanceAPIException as e:
        print(f"[{symbol}] Binance API Error during trade execution: {e}", flush=True)
    except Exception as e:
        print(f"[{symbol}] General Error during trade execution: {e}", flush=True)

def check_sma_strategy(client, symbol):
    """
    Fetches historical klines safely, calculates SMA-20, prints stats, 
    and triggers live trade execution logic.
    """
    try:
        # Add a mandatory buffer before fetching each symbol
        time.sleep(5)

        kines = client.get_historical_klines(
            symbol,
            client.KLINE_INTERVAL_15MINUTE,
            "1 hour ago UTC"
        )

        if not kines or len(kines) < 20:
            print(f"Not enough data for {symbol}", flush=True)
            return None

        closes = [float(entry[4]) for entry in kines]
        sma_20 = sum(closes[-20:]) / 20
        current_price = closes[-1]

        print(f"[{symbol}] Current Price: {current_price}, SMA-20: {sma_20:.4f}", flush=True)

        # Execute live trading based on strategy rules
        execute_trade_logic(client, symbol, current_price, sma_20)

        return {"symbol": symbol, "price": current_price, "sma_20": sma_20}

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}", flush=True)
        time.sleep(10)
        return None
