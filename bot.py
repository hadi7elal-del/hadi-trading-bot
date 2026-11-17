import time
import logging
import os
import ccxt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():
    api_key = os.getenv('BINANCE_API_KEY') or os.getenv('API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET') or os.getenv('API_SECRET')
    
    if not api_key or not api_secret:
        logging.error("Binance API credentials not found in environment variables!")
        return

    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })

    base_trade_amount = 15     
    profit_target_pct = 1.5    
    dip_trigger_pct = 2.0      
    
    logging.info("Starting Dynamic Multi-Asset Portfolio Bot (Live Execution Mode)...")
    
    reference_prices = {}

    while True:
        try:
            balance = exchange.fetch_free_balance()
            
            active_coins = []
            for coin, amt in balance.items():
                if amt > 0 and coin not in ['USDT', 'FDUSD']:
                    symbol = f"{coin}/USDT"
                    try:
                        exchange.load_markets()
                        if symbol in exchange.markets:
                            active_coins.append(symbol)
                    except Exception:
                        pass

            if not active_coins:
                logging.warning("No active trading coins with positive balance found. Retrying in 60 seconds...")
                time.sleep(60)
                continue

            logging.info(f"Monitoring active portfolio coins: {active_coins}")

            for symbol in active_coins:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    
                    if symbol not in reference_prices:
                        reference_prices[symbol] = current_price
                        logging.info(f"[{symbol}] Initial Reference Price set to: {current_price}")
                        continue
                    
                    ref_price = reference_prices[symbol]
                    price_change = ((current_price - ref_price) / ref_price) * 100
                    logging.info(f"[{symbol}] Current: {current_price} | Ref: {ref_price} | Change: {price_change:.2f}%")

                    base_currency = symbol.split('/')[0]
                    coin_balance = balance.get(base_currency, 0)

                    if price_change >= profit_target_pct:
                        logging.info(f"[{symbol}] Price surged by {price_change:.2f}%. Executing SELL order...")
                        if coin_balance * current_price >= 10:
                            order = exchange.create_market_sell_order(symbol, coin_balance)
                            logging.info(f"[{symbol}] SELL order executed successfully: {order['id']}")
                            reference_prices[symbol] = current_price
                        else:
                            logging.warning(f"[{symbol}] Insufficient balance for selling.")

                    elif price_change <= -dip_trigger_pct:
                        logging.info(f"[{symbol}] Deep dip detected ({price_change:.2f}%). Executing BUY order...")
                        usdt_balance = balance.get('USDT', 0)
                        
                        multiplier = abs(int(price_change / dip_trigger_pct))
                        effective_buy_amount = base_trade_amount * max(1, multiplier)
                        
                        if usdt_balance >= effective_buy_amount:
                            amount_to_buy = effective_buy_amount / current_price
                            order = exchange.create_market_buy_order(symbol, amount_to_buy)
                            logging.info(f"[{symbol}] BUY order executed successfully: {order['id']}")
                            reference_prices[symbol] = current_price
                        else:
                            logging.warning(f"[{symbol}] Insufficient USDT balance for dip accumulation.")

                except Exception as inner_e:
                    logging.
