# Import required libraries
import numpy as np
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from tradingview_screener import get_all_symbols
import warnings
import pandas_ta as ta

# Suppress warnings to keep the output clean
warnings.simplefilter(action='ignore')

# Function to calculate RSI
def calculate_rsi(data, length=14):
    """
    Calculate the Relative Strength Index (RSI) for the given data.

    Parameters:
    - data: DataFrame containing stock data with a 'close' price column.
    - length: The period over which to calculate the RSI.

    Returns:
    - The DataFrame with an added 'RSI' column.
    """
    # Use pandas_ta to calculate RSI
    data['RSI'] = ta.rsi(data['close'], length=length)
    return data

# Initialize the data feed from TradingView
tv = TvDatafeed()

# Define the list of stocks to analyze
# Get all symbols from the American market
symbols = get_all_symbols(market='america')

# Remove the 'NASDAQ:' prefix from symbols (if present)
symbols = [symbol.replace('NASDAQ:', '') for symbol in symbols]

# Sort the list of symbols alphabetically
symbols = sorted(symbols)

# DataFrame to store signals
columns = ['Stock Name', 'Last Price', 'RSI Buy Signal']
df_signals = pd.DataFrame(columns=columns)

# Main loop to process each stock symbol
for symbol in symbols:
    try:
        # Fetch historical data for the stock symbol
        data = tv.get_hist(
            symbol=symbol,
            exchange='NASDAQ',
            interval=Interval.in_daily,
            n_bars=100  # Fetch the last 100 daily data points
        )
        # Check if data is returned
        if data is None or data.empty:
            print(f"No data for {symbol}")
            continue

        # Reset index to make 'datetime' a column
        data = data.reset_index()

        # Calculate RSI and add it to the DataFrame
        data = calculate_rsi(data)

        # Rename columns to standard format for consistency
        data.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)

        # Set 'datetime' as the index
        data.set_index('datetime', inplace=True)

        # Remove rows with NaN values in 'RSI' (usually the first few rows)
        data.dropna(subset=['RSI'], inplace=True)

        # Ensure we have at least two data points after dropping NaNs
        if len(data) < 2:
            print(f"Not enough data for {symbol} after dropping NaNs")
            continue

        # Extract the last two data points to check for RSI crossing above 30
        Signals = data.tail(2).reset_index()

        # Define the buy signal logic for RSI
        # Signal when RSI crosses above 30 (from oversold territory)
        Entry = (Signals.loc[0, 'RSI'] < 30) and (Signals.loc[1, 'RSI'] >= 30)
        Entry = bool(Entry)

        # Get the last closing price and convert to float
        Last_Price = float(Signals.loc[1, 'Close'])

        # Append the results to the DataFrame
        row = [symbol, Last_Price, Entry]
        df_signals.loc[len(df_signals)] = row

        # Print the result for the current stock
        print(row)
    except Exception as e:
        # If an error occurs, print it and continue with the next symbol
        print(f"Error processing {symbol}: {e}")
        pass

# Filter and display stocks with a buy signal
df_true = df_signals[df_signals['RSI Buy Signal'] == True]

print("\nStocks with RSI Buy Signal:")
print(df_true)
