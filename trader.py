from binance.client import Client
from binance.exceptions import BinanceAPIException

def execute_buy_order(client, symbol, quantity=1.0):
    """
    Executes a real MARKET buy order on Binance Spot.
    """
    try:
        order = client.create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )
        print(f"[Trader] Successfully executed BUY for {symbol}! Order ID: {order['orderId']}")
        return order
    except BinanceAPIException as e:
        print(f"[Trader] Binance API Error during BUY for {symbol}: {e}")
    except Exception as e:
        print(f"[Trader] General Error during BUY: {e}")
    return None

def execute_sell_order(client, symbol, quantity=1.0):
    """
    Executes a real MARKET sell order on Binance Spot.
    """
    try:
        order = client.create_order(
            symbol=symbol,
            side='SELL',
            type='MARKET',
            quantity=quantity
        )
        print(f"[Trader] Successfully executed SELL for {symbol}! Order ID: {order['orderId']}")
        return order
    except BinanceAPIException as e:
        print(f"[Trader] Binance API Error during SELL for {symbol}: {e}")
    except Exception as e:
        print(f"[Trader] General Error during SELL: {e}")
    return None
