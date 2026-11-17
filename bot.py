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
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        logging.error("Binance API credentials not found in environment variables!")
        return

    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })

    symbol = 'XRP/USDT'
    base_trade_amount = 15     
    profit_target_pct = 1.5    
    dip_trigger_pct = 2.0      
    
    logging.info(f"Starting deep dip accumulation and profit-taking bot for {symbol}...")
    
    ticker = exchange.fetch_ticker(symbol)
    reference_price = ticker['last']
    logging.info(f"Initial Reference Price set to: {reference_price}")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            price_change = ((current_price - reference_price) / reference_price) * 100
            logging.info(f"Current Price: {current_price} | Ref Price: {reference_price} | Change: {price_change:.2f}%")

            if price_change >= profit_target_pct:
                logging.info(f"Price surged by {price_change:.2f}%. Executing SELL order to collect USDT...")
                
                balance = exchange.fetch_free_balance()
                base_currency = symbol.split('/')[0]
                coin_balance = balance.get(base_currency, 0)
                
                if coin_balance * current_price >= 10:
                    # order = exchange.create_market_sell_order(symbol, coin_balance)
                    # logging.info(f"SELL order executed successfully: {order['id']}")
                    reference_price = current_price
                else:
                    logging.warning(f"Insufficient {base_currency} balance for selling.")

            elif price_change <= -dip_trigger_pct:
                logging.info(f"Deep dip detected ({price_change:.2f}%). Executing aggressive BUY/ACCUMULATION order...")
                
                balance = exchange.fetch_free_balance()
                usdt_balance = balance.get('USDT', 0)
                
                multiplier = abs(int(price_change / dip_trigger_pct))
                effective_buy_amount = base_trade_amount * max(1, multiplier)
                
                if usdt_balance >= effective_buy_amount:
                    amount_to_buy = effective_buy_amount / current_price
                    # order = exchange.create_market_buy_order(symbol, amount_to_buy)
                    # logging.info(f"ACCUMULATION BUY order executed: {order['id']}")
                    reference_price = current_price
                else:
                    logging.warning("Insufficient USDT balance for deep dip accumulation.")

            else:
                logging.info("Market stabilizing, waiting for significant movement...")

            time.sleep(60)

        except Exception as e:
            logging.error(f"An error occurred in trading loop: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
