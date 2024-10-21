import numpy as np
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
import warnings
import pandas_ta as ta
import matplotlib.pyplot as plt

warnings.simplefilter(action='ignore')

# Function to calculate RSI and apply Inverse Fisher Transform (IFT) on RSI
def calculate_rsi_ift(data, rsi_length=5, smoothing_length=9):
    data['RSI'] = ta.rsi(data['close'], length=rsi_length)
    v1 = 0.1 * (data['RSI'] - 50)
    v2 = ta.ema(v1, length=smoothing_length)
    data['IFT_RSI'] = (np.exp(2 * v2) - 1) / (np.exp(2 * v2) + 1)
    return data

# Initialize the data feed
tv = TvDatafeed()

# Define the list of cryptocurrencies to analyze
cryptos = ['BINANCE:BTCUSDT','BINANCE:ETHUSDT','BINANCE:LTCUSDT',
           'BINANCE:SOLUSDT','BINANCE:BNBUSDT','BINANCE:TAOUSDT',
           'BINANCE:MANAUSDT','BINANCE:AVAXUSDT','BINANCE:SUIUSDT',
           'BINANCE:IMXUSDT','BINANCE:FTMUSDT','BINANCE:FLOWUSDT',
           'BINANCE:FLOKIUSDT','BINANCE:BONKUSDT','BINANCE:PORTALUSDT',
           'BINANCE:PEPEUSDT','BINANCE:SHIBUSDT','BINANCE:DOGEUSDT',
           'BINANCE:RENDERUSDT','BINANCE:PYTHUSDT','BINANCE:ARBUSDT',
           'BINANCE:VETUSDT','BINANCE:ETHFIUSDT','BINANCE:XRPUSDT',
           'BINANCE:FETUSDT','BINANCE:ICPUSDT','BINANCE:NEARUSDT',
           'BINANCE:DOTUSDT','BINANCE:ADAUSDT','BINANCE:SXPUSDT',
           'BINANCE:AXSUSDT','BINANCE:ROSEUSDT','BINANCE:ARKUSDT',
           'BINANCE:APTUSDT','BINANCE:ALTUSDT','BINANCE:TRXUSDT',
           'BINANCE:LINKUSDT','BINANCE:BCHUSDT','BINANCE:UNIUSDT',
           'BINANCE:ETCUSDT','BINANCE:WIFUSDT','BINANCE:OPUSDT',
           'BINANCE:FILUSDT','BINANCE:INJUSDT','BINANCE:ATOMUSDT',
           'BINANCE:SEIUSDT','BINANCE:RUNEUSDT','BINANCE:RAYUSDT']

# DataFrame to store signals
df_signals = pd.DataFrame(columns=['Crypto Symbol', 'Last Price', 'IFT Signal'])

# User input to choose the range of IFT_RSI to scan
print("Select the range of IFT RSI to scan:")
print("1. Less than -0.5")
print("2. Between -0.5 and +0.5")
choice = input("Enter choice (1 or 2): ")

# Validate user input
if choice not in ['1', '2']:
    raise ValueError("Invalid choice. Please enter 1 or 2.")

# Main loop to process each cryptocurrency
for crypto in cryptos:
    try:
        data = tv.get_hist(symbol=crypto, exchange='BINANCE', interval=Interval.in_daily, n_bars=1000)
        data = data.reset_index()
        data = calculate_rsi_ift(data, rsi_length=5, smoothing_length=9)
        data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        data.set_index('datetime', inplace=True)
        data.dropna(subset=['IFT_RSI'], inplace=True)

        Signals = data.tail(1).reset_index()
        IFT_RSI_value = Signals.loc[0, 'IFT_RSI']
        if choice == '1':
            Entry = IFT_RSI_value <= -0.5
        else:  # choice == '2'
            Entry = -0.5 <= IFT_RSI_value <= 0.5

        Last_Price = float(Signals.loc[0, 'Close'])
        df_signals.loc[len(df_signals)] = [crypto, Last_Price, bool(Entry)]
    except Exception as e:
        print(f"Error processing {crypto}: {e}")

# Filter and display cryptocurrencies with the signal
df_True = df_signals[df_signals['IFT Signal'] == True]
print("\nSelected Cryptocurrencies:")
print(df_True)
