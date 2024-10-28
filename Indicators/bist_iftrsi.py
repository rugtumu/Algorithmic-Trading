# This code scans for the stocks where Inverse Fisher Transform (IFT) on RSI is less than -0,5

# Import required libraries
import numpy as np
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from tradingview_screener import get_all_symbols
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
    
    # Normalize RSI to the range [-1, 1] for IFT
    normalized_rsi = 2 * (data['RSI'] - 50) / 100
    
    # Smooth the normalized RSI with a simple moving average (SMA)
    smoothed_rsi = ta.sma(normalized_rsi, length=smoothing_length)
    
    # Apply the Inverse Fisher Transform
    data['IFT_RSI'] = np.tanh(smoothed_rsi)
    
    return data

# Initialize the data feed
tv = TvDatafeed()

# Define the list of stocks to analyze (from the Turkish market)
Hisseler = get_all_symbols(market='turkey')
Hisseler = [symbol.replace('BIST:', '') for symbol in Hisseler]
Hisseler = sorted(Hisseler)

# DataFrame to store signals
Titles = ['Hisse Adı', 'Son Fiyat', 'IFT Buy Signal']
df_signals = pd.DataFrame(columns=Titles)

# Main loop to process each stock
for hisse in Hisseler:
    try:
        # Fetch historical data
        data = tv.get_hist(symbol=hisse, exchange='BIST', interval=Interval.in_daily, n_bars=1000)
        data = data.reset_index()

        # Customize RSI length and smoothing length for different timeframes
        # For daily charts, use RSI length = 5 and smoothing length = 9
        data = calculate_rsi_ift(data, rsi_length=5, smoothing_length=9)

        # Prepare the data
        data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        data.set_index('datetime', inplace=True)

        # Remove rows with NaN values in IFT_RSI
        data.dropna(subset=['IFT_RSI'], inplace=True)

        # Extract the last data point
        Signals = data.tail(1).reset_index()

        # Define the buy signal logic based on IFT of RSI being less than -0.5
        Entry = Signals.loc[0, 'IFT_RSI'] < -0.5
        Entry = bool(Entry)

        # Get the last closing price
        Last_Price = float(Signals.loc[0, 'Close'])

        # Append the results to the DataFrame
        L1 = [hisse, Last_Price, Entry]
        df_signals.loc[len(df_signals)] = L1
        print(L1)
    except Exception as e:
        print(f"Error processing {hisse}: {e}")
        pass

# Filter and display stocks with a buy signal
df_True = df_signals[df_signals['IFT Buy Signal'] == True]

# Ensure all rows are shown in the output
pd.set_option('display.max_rows', None)

print("\nStocks with IFT RSI below -0.5:")
print(df_True)
