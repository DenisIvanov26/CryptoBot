import ccxt
import config


#MAKE SURE TO SYNC WINDOWS TIME
exchange = ccxt.binance({
    'apiKey': config.BINANCE_API_KEY,
    'secret': config.BINANCE_SECRET_KEY,
})

balance = exchange.fetch_balance()
print(balance)

#get all coin and market pairings
#markets = exchange.load_markets()
#for market in markets:
#    print(market)

ticker = exchange.fetch_ticker('ETH/USDT')
ohlcv = exchange.fetch_ohlcv('ETH/USDT',timeframe = '5m', limit = 10)

#for candle in ohlcv:
#    print(candle)

#orderbook = exchange.fetch_order_book('ETH/USDT')
#print(orderbook)

#copied from ccxt page for refernce
#exchange_id = 'binance'
#exchange_class = getattr(ccxt, exchange_id)
#exchange = exchange_class({
#   'apiKey': 'YOUR_API_KEY',
#    'secret': 'YOUR_SECRET',
#})
