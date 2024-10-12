# This code uses Inverse Fisher Transform on RSI
import numpy as np
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from tradingview_screener import get_all_symbols
import warnings
import pandas_ta as ta
import matplotlib.pyplot as plt

warnings.simplefilter(action='ignore')

# Function to calculate RSI and apply Inverse Fisher Transform (IFT) on RSI
def calculate_rsi_ift(data, length=14):
    """
    Calculate the RSI and apply the Inverse Fisher Transform (IFT) on RSI.
    """
    data['RSI'] = ta.rsi(data['close'], length=length)
    
    # Normalize RSI to the range [-1, 1] for IFT
    normalized_rsi = 2 * (data['RSI'] - 50) / 100
    
    # Apply the Inverse Fisher Transform
    data['IFT_RSI'] = np.tanh(normalized_rsi)
    
    return data

# Initialize the data feed (use guest mode or provide credentials)
tv = TvDatafeed()  # For guest mode
# tv = TvDatafeed(username='your_username', password='your_password')  # For authenticated mode

# Define the list of stocks to analyze
Hisseler = ['NASDAQ:NVDA', 'NASDAQ:AMZN', 'NASDAQ:MSFT', 'NASDAQ:AMD', 'NASDAQ:MRVL',
            'NASDAQ:UAL', 'NASDAQ:COIN', 'NASDAQ:HEPS', 'NASDAQ:RIOT', 'NASDAQ:INTU',
            'NASDAQ:PANW', 'NASDAQ:MELI', 'NASDAQ:MDLZ', 'NASDAQ:SNPS', 'NASDAQ:META',
            'NASDAQ:CRWD', 'NASDAQ:GOOGL', 'NASDAQ:MU']
Hisseler = [symbol.replace('NASDAQ:', '') for symbol in Hisseler if symbol.startswith('NASDAQ:')]
Hisseler = sorted(Hisseler)

# DataFrame to store signals
Titles = ['Stock Symbol', 'Last Price', 'IFT Buy Signal']
df_signals = pd.DataFrame(columns=Titles)

# Main loop to process each stock
for hisse in Hisseler:
    try:
        # Fetch historical data
        data = tv.get_hist(symbol=hisse, exchange='NASDAQ', interval=Interval.in_daily, n_bars=1000)
        data = data.reset_index()
        
        # Calculate RSI and IFT on RSI
        data = calculate_rsi_ift(data)
        
        # Prepare the data
        data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        data.set_index('datetime', inplace=True)
        
        # Remove rows with NaN values in IFT_RSI
        data.dropna(subset=['IFT_RSI'], inplace=True)
        
        # Extract the last data point
        Signals = data.tail(1).reset_index()
        
        # Define the buy signal logic based on IFT of RSI being less than -0.5
        Entry = Signals.loc[0, 'IFT_RSI'] < -0.5
        
        # Get the last closing price and convert to float
        Last_Price = float(Signals.loc[0, 'Close'])

        # Convert Entry to a native boolean
        Entry = bool(Entry)
        
        # Append the results to the DataFrame
        L1 = [hisse, Last_Price, Entry]
        df_signals.loc[len(df_signals)] = L1
        print(L1)
    except Exception as e:
        print(f"Error processing {hisse}: {e}")
        pass

# Filter and display stocks with a buy signal
df_True = df_signals[df_signals['IFT Buy Signal'] == True]
print("\nStocks with IFT RSI below -0.5:")
print(df_True)
