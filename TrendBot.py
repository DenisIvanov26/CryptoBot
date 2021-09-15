#pip install these
from logging import PercentStyle
import ccxt
import numpy as np
import schedule
import pandas as pd
pd.set_option('display.max_rows', None) #to see all rows requested without having ...
import numpy as np
from datetime import datetime
import time

#extra file containing config for exchanges and api keys
import config

import warnings
warnings.filterwarnings('ignore')

#MAKE SURE TO SYNC WINDOWS TIME
exchange = ccxt.binance({
    'apiKey': config.BINANCE_API_KEY,
    'secret': config.BINANCE_SECRET_KEY,
    'options': {
        'defaultType': 'future'#enables futures market
    },
    'marginType': 'ISOLATED'
})
###########COIN PARING TO TRADE############
coin = 'XTZ'
pairing = coin + '/USDT'
#############ADJUST LEVERAGE###############
leverage = 5
exchange.set_leverage(leverage,pairing)
####POSITION SIZING RELATIVE TO BALANCE####
balances = exchange.fetch_balance()
usdtbalance = balances['USDT']['total']
usdtpossize  = usdtbalance / 5
coinprice = exchange.fetch_ticker(pairing)
print('CURRENT USDT POS SIZE:' + str(usdtpossize) + " LEVERAGE: " + str(leverage) + " COIN: " + pairing)
#print(coinprice['last'])
coinpossize = (usdtpossize / (coinprice['last'])) * leverage
#print(coinpossize)


#https://www.investopedia.com/terms/a/atr.asp to read about Average True Range

def getTrueRange(df):
    df['prev_close'] = df['close'].shift(1)
    df['high-low'] = df['high'] - df['low']
    df['high-prev_close'] = abs(df['high'] - df['prev_close'])
    df['low-prev_close'] = abs(df['low'] - df['prev_close'])
    true_range = df[['high-low', 'high-prev_close', 'low-prev_close']].max(axis=1)
    return true_range

#numbars = parameter to specify when calling, 12 is default since 5m bars = 60m = 1h
def getAverageTrueRange(df, numbars = 7):
    df['true_range'] = getTrueRange(df)
    avg_true_range= df["true_range"].rolling(numbars).mean()
    return avg_true_range

#UPPERBAND = ((high + low) / 2) + (multiplier * atr) 
#LOWERBAND = ((high + low) / 2) - (multiplier * atr) 
def trend(df, numbars = 7, multi = 3):
    df['avg_true_range'] = getAverageTrueRange(df, numbars)
    df['upperband'] = ((df['high'] + df['low']) / 2) + (multi * df['avg_true_range'])
    df['lowerband'] = ((df['high'] + df['low']) / 2) - (multi * df['avg_true_range'])
    df['Bullish'] = True
    #Loop through all rows in dataframe
    for curr in range(1, len(df.index)):
        prev = curr - 1
        #Defines if we are in an uptrend 
        if df['close'][curr] > df['upperband'][prev]:
            df['Bullish'][curr] = True
        else:
            #Defines in we are in downtrend
            if df['close'][curr] < df['lowerband'][prev]:
                df['Bullish'][curr] = False
            else:
                #If trend hasnt changed keep previous trend
                df['Bullish'][curr] = df['Bullish'][prev]
                #flattens lowerband if we have lower lows to maintain highest point in lowerband
                if df['Bullish'][curr] and df['lowerband'][curr] < df['lowerband'][prev]:
                    df['lowerband'][curr] = df['lowerband'][prev]
                #flattens upperband if we have higher highs to maintain lowest point in upperband
                if not df['Bullish'][curr] and df['upperband'][curr] > df['upperband'][prev]:
                    df['upperband'][curr] = df['upperband'][prev]
    return df

starting = True
long = False

#checks for signals to buy or sell
def Signal(df):
    global long
    global starting
    print(df.tail(1))
    print("\n\nLOOKING FOR TRADE...\n\n")
    lastrow = len(df.index) - 1
    prevrow = lastrow - 1
    #if trend switches to bullish
    if not df['Bullish'][prevrow] and df['Bullish'][lastrow]:
        if starting:
            print("#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY####")
            starting = False
            long = True
            order = exchange.create_market_buy_order(pairing, coinpossize)
            print(f"{pd.to_datetime(order['info']['updateTime'], unit = 'ms').round('1s')} ID: " + order['info']['orderId'] + " Type: " + pairing + " Price: " + str(round(float(order['info']['avgPrice']),2)) + " QTY: " + order['info']['origQty'] + " CostWithLeverage: " + str(round(order['cost'],2)) + "$ Cost: " + str(round((order['cost']/leverage),2)) + "$")
            print("#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY####\n\n")
        elif not long:
            print("#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY####")
            order = exchange.create_market_buy_order(pairing, coinpossize * 2)
            print(f"{pd.to_datetime(order['info']['updateTime'], unit = 'ms').round('1s')} ID: " + order['info']['orderId'] + " Type: " + pairing + " Price: " + str(round(float(order['info']['avgPrice']),2)) + " QTY: " + order['info']['origQty'] + " CostWithLeverage: " + str(round(order['cost'],2)) + "$ Cost: " + str(round((order['cost']/leverage),2)) + "$")
            long = True
            print("#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY#####BUY####\n\n")
        else:
            print('WARNING: ALREADY LONG\n\n')
    #trend is bearish
    if df['Bullish'][prevrow] and not df['Bullish'][lastrow]:
        if starting:
            print("#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####")
            starting = False
            long = False
            order = exchange.create_market_sell_order(pairing, coinpossize)
            print(f"{pd.to_datetime(order['info']['updateTime'], unit = 'ms').round('1s')} ID: " + order['info']['orderId'] + " Type: " + pairing + " Price: " + str(round(float(order['info']['avgPrice']),2)) + " QTY: " + order['info']['origQty'] + " CostWithLeverage: " + str(round(order['cost'],2)) + "$ Cost: " + str(round((order['cost']/leverage),2)) + "$")
            print("#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####\n\n")
        elif long:
            print("#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####")
            order = exchange.create_market_sell_order(pairing, coinpossize * 2)
            print(f"{pd.to_datetime(order['info']['updateTime'], unit = 'ms').round('1s')}  ID: " + order['info']['orderId'] + " Type: " + pairing + " Price: " + str(round(float(order['info']['avgPrice']),2)) + " QTY: " + order['info']['origQty'] + " CostWithLeverage: " + str(round(order['cost'],2)) + "$ Cost: " + str(round((order['cost']/leverage),2)) + "$")
            long = False
            print("#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####SELL#####\n\n")
        else:
            print('WARNING: ALREADY SHORT\n\n')

def run():
    #print(f"Bar at: {datetime.now().isoformat()}")
    #limit = how many to appear, timeframe = candlesticks time
    bars = exchange.fetch_ohlcv(pairing, timeframe = '1m', limit = 100)
    df = pd.DataFrame(bars[:-1], columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit = 'ms')
    #print(df)
    trend_data = trend(df)
    Signal(trend_data)

schedule.every(1).minute.do(run)
#get last 3 bars determine combo
#rating scale? -1 bearish 0 neutral 1 bullish
#jcandles = exchange.fe
#IN NEXT VERSION

while(True):
    schedule.run_pending()
    time.sleep(1)


