"""
This code scans cryptocurrencies where Inverse Fisher Transform (IFT) on RSI is between -0.5 and +0.5.
"""

# Import required libraries
import numpy as np
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
import warnings
import pandas_ta as ta
import matplotlib.pyplot as plt

warnings.simplefilter(action='ignore')

# Function to calculate RSI and apply Inverse Fisher Transform (IFT) on RSI with adjustable parameters
def calculate_rsi_ift(data, rsi_length=5, smoothing_length=9):
    """
    Calculate the RSI and apply the Inverse Fisher Transform (IFT) on RSI with adjustable RSI and smoothing lengths.
    """
    # Calculate RSI
    data['RSI'] = ta.rsi(data['close'], length=rsi_length)
    
    # Normalize RSI
    v1 = 0.1 * (data['RSI'] - 50)
    
    # Smooth v1 using an Exponential Moving Average (EMA)
    v2 = ta.ema(v1, length=smoothing_length)
    
    # Apply the Inverse Fisher Transform
    data['IFT_RSI'] = (np.exp(2 * v2) - 1) / (np.exp(2 * v2) + 1)
    
    return data

# Initialize the data feed
tv = TvDatafeed()

# Define the list of cryptocurrencies to analyze
cryptos = ['BINANCE:BTCUSDT','BINANCE:ETHUSDT','BINANCE:LTCUSDT','BINANCE:SOLUSDT','BINANCE:BNBUSDT',
           'BINANCE:MANAUSDT','BINANCE:AVAXUSDT','BINANCE:SUIUSDT','BINANCE:FLOKIUSDT','BINANCE:IMXUSDT',
           'BINANCE:FTMUSDT','BINANCE:FLOWUSDT','BINANCE:BONKUSDT','BINANCE:PORTALUSDT','BINANCE:PYTHUSDT',
           'BINANCE:ARBUSDT','BINANCE:XRPUSDT','BINANCE:VETUSDT','BINANCE:RENDERUSDT','BINANCE:PEPEUSDT',
           'BINANCE:FETUSDT','BINANCE:ICPUSDT','BINANCE:NEARUSDT','BINANCE:DOTUSDT','BINANCE:ADAUSDT',
           'BINANCE:DOGEUSDT','BINANCE:SXPUSDT','BINANCE:AXSUSDT','BINANCE:ROSEUSDT','BINANCE:ARKUSDT',
           'BINANCE:APTUSDT','BINANCE:ALTUSDT','BINANCE:ETHFIUSDT','BINANCE:TRXUSDT','BINANCE:SHIBUSDT',
           'BINANCE:LINKUSDT','BINANCE:BCHUSDT','BINANCE:UNIUSDT','BINANCE:TAOUSDT','BINANCE:ETCUSDT',
           'BINANCE:WIFUSDT','BINANCE:OPUSDT','BINANCE:FILUSDT','BINANCE:INJUSDT','BINANCE:ATOMUSDT',
           'BINANCE:SEIUSDT','BINANCE:RUNEUSDT']

# DataFrame to store signals
Titles = ['Crypto Symbol', 'Last Price', 'IFT Signal']
df_signals = pd.DataFrame(columns=Titles)

# Main loop to process each cryptocurrency
for crypto in cryptos:
    try:
        # Fetch historical data
        data = tv.get_hist(symbol=crypto, exchange='BINANCE', interval=Interval.in_daily, n_bars=1000)
        data = data.reset_index()

        # Customize RSI length and smoothing length for different timeframes
        data = calculate_rsi_ift(data, rsi_length=5, smoothing_length=9)

        # Prepare the data
        data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        data.set_index('datetime', inplace=True)

        # Remove rows with NaN values in IFT_RSI
        data.dropna(subset=['IFT_RSI'], inplace=True)

        # Extract the last data point
        Signals = data.tail(1).reset_index()

        # Define the signal logic based on IFT of RSI being between -0.5 and +0.5
        IFT_RSI_value = Signals.loc[0, 'IFT_RSI']
        Entry = (-0.5 <= IFT_RSI_value <= 0.5)
        Entry = bool(Entry)  # Convert to boolean

        # Get the last closing price and convert to float
        Last_Price = float(Signals.loc[0, 'Close'])

        # Append the results to the DataFrame
        L1 = [crypto, Last_Price, Entry]
        df_signals.loc[len(df_signals)] = L1
        print(L1)
    except Exception as e:
        print(f"Error processing {crypto}: {e}")
        pass

# Filter and display cryptocurrencies with the signal
df_True = df_signals[df_signals['IFT Signal'] == True]

# Ensure all rows are shown in the output
pd.set_option('display.max_rows', None)

print("\nCryptocurrencies with IFT RSI between -0.5 and +0.5:")
print(df_True)
