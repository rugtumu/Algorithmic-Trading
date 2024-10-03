# Import required libraries
import numpy as np
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from tradingview_screener import get_all_symbols
import warnings

# Ignore warnings to keep the output clean
warnings.simplefilter(action='ignore')

# Define Simple Moving Average (SMA) function
def sma(series, length):
    """
    Calculate the Simple Moving Average (SMA) for a given series.

    Parameters:
    - series: The data series (e.g., close prices) to calculate the SMA on.
    - length: The number of periods over which to calculate the SMA.

    Returns:
    - A Pandas Series representing the SMA of the input series.
    """
    return series.rolling(window=length).mean()

# Define Exponential Moving Average (EMA) function
def ema(series, length):
    """
    Calculate the Exponential Moving Average (EMA) for a given series.

    Parameters:
    - series: The data series to calculate the EMA on.
    - length: The span of the EMA.

    Returns:
    - A Pandas Series representing the EMA of the input series.
    """
    return series.ewm(span=length, adjust=False).mean()

def Bankery(data):
    """
    Compute custom indicators and generate entry signals based on the provided data.

    Parameters:
    - data: A DataFrame containing stock data with columns 'open', 'high', 'low', 'close', 'volume'.

    Returns:
    - A DataFrame with an added 'Entry' column indicating potential buy signals.
    """
    # Create a copy of the data to avoid modifying the original DataFrame
    df = data.copy()

    # Calculate the difference between the current close and the rolling minimum low over 27 periods
    close_minus_rolling_min = data['close'] - data['low'].rolling(window=27).min()
    
    # Calculate the range between the rolling maximum high and rolling minimum low over 27 periods
    rolling_range = data['high'].rolling(window=27).max() - data['low'].rolling(window=27).min()
    
    # Compute the percentage change within the rolling range
    percentage_change = (close_minus_rolling_min / rolling_range) * 100

    # Calculate two SMAs of the percentage change
    sma1 = sma(percentage_change, 5)
    sma2 = sma(sma1, 3)

    # Compute the 'fundtrend' indicator using a weighted formula
    fundtrend = (3 * sma1 - 2 * sma2 - 50) * 1.032 + 50

    # Calculate the typical price
    typ = (2 * data['close'] + data['high'] + data['low'] + data['open']) / 5
    
    # Calculate the lowest low and highest high over a 34-period window
    lol = data['low'].rolling(window=34).min()
    hoh = data['high'].rolling(window=34).max()
    
    # Compute the 'bullbearline' indicator using EMA
    bullbearline = ema(((typ - lol) / (hoh - lol) * 100), 13)

    # Determine the 'bankerentry' signal based on the fundtrend and bullbearline
    bankerentry = (fundtrend > bullbearline) & (bullbearline < 25)

    # Add the 'Entry' signal to the DataFrame
    df['Entry'] = bankerentry

    return df

# Initialize the data feed from TradingView
tv = TvDatafeed()

# Get the list of all symbols in the Turkish market
Hisseler = get_all_symbols(market='turkey')

# Remove the 'BIST:' prefix from symbols and sort the list
Hisseler = [symbol.replace('BIST:', '') for symbol in Hisseler]
Hisseler = sorted(Hisseler)

# Define the columns for the signals DataFrame (translated from Turkish)
Titles = ['Stock Name', 'Last Price', 'Bottom Signal']
df_signals = pd.DataFrame(columns=Titles)

# Loop through each stock symbol
for hisse in Hisseler:
    try:
        # Fetch historical data for the stock
        data = tv.get_hist(
            symbol=hisse,
            exchange='BIST',
            interval=Interval.in_daily,
            n_bars=100  # Number of periods to fetch
        )
        # Reset index to make 'datetime' a column
        data = data.reset_index()

        # Apply the 'Bankery' function to compute indicators and signals
        Banker = Bankery(data)

        # Rename columns to standardize them
        Banker.rename(
            columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            },
            inplace=True
        )
        # Set 'datetime' as the index
        Banker.set_index('datetime', inplace=True)

        # Get the last two data points to check for signal changes
        Signals = Banker.tail(2).reset_index()

        # Determine if an 'Entry' signal occurred (transition from False to True)
        Entry = (Signals.loc[0, 'Entry'] == False) & (Signals.loc[1, 'Entry'] == True)
        Entry = bool(Entry)

        # Get the last closing price
        Last_Price = float(Signals.loc[1, 'Close'])

        # Create a list of the stock symbol, last price, and entry signal
        L1 = [hisse, Last_Price, Entry]

        # Append the data to the signals DataFrame
        df_signals.loc[len(df_signals)] = L1

        # Print the result for the current stock
        print(L1)
    except Exception as e:
        # If there's an error, print it and continue with the next stock
        print(f"Error processing {hisse}: {e}")
        pass

# Filter and display stocks with a buy signal ('Bottom Signal' is True)
df_True = df_signals[df_signals['Bottom Signal'] == True]
print("\nStocks with 'Bottom Signal':")
print(df_True)
