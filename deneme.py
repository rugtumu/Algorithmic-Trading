"""
This code scans cryptocurrencies based on user selection:
[1] IFT RSI less than -0.5
[2] IFT RSI between -0.5 and 0.5
"""

# Import required libraries
import numpy as np
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
import warnings
import pandas_ta as ta

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
cryptos = ['BINANCE:BTCUSDT', 'BINANCE:ETHUSDT', 'BINANCE:LTCUSDT', 'BINANCE:SOLUSDT', 'BINANCE:BNBUSDT',
           'BINANCE:MANAUSDT', 'BINANCE:AVAXUSDT', 'BINANCE:SUIUSDT', 'BINANCE:FLOKIUSDT', 'BINANCE:IMXUSDT',
           'BINANCE:FTMUSDT', 'BINANCE:FLOWUSDT', 'BINANCE:BONKUSDT', 'BINANCE:PORTALUSDT', 'BINANCE:PYTHUSDT',
           'BINANCE:ARBUSDT', 'BINANCE:XRPUSDT', 'BINANCE:VETUSDT', 'BINANCE:RENDERUSDT', 'BINANCE:PEPEUSDT',
           'BINANCE:FETUSDT', 'BINANCE:ICPUSDT', 'BINANCE:NEARUSDT', 'BINANCE:DOTUSDT', 'BINANCE:ADAUSDT',
           'BINANCE:DOGEUSDT', 'BINANCE:SXPUSDT', 'BINANCE:AXSUSDT', 'BINANCE:ROSEUSDT', 'BINANCE:ARKUSDT',
           'BINANCE:APTUSDT', 'BINANCE:ALTUSDT', 'BINANCE:ETHFIUSDT', 'BINANCE:TRXUSDT', 'BINANCE:SHIBUSDT',
           'BINANCE:LINKUSDT', 'BINANCE:BCHUSDT', 'BINANCE:UNIUSDT', 'BINANCE:TAOUSDT', 'BINANCE:ETCUSDT',
           'BINANCE:WIFUSDT', 'BINANCE:OPUSDT', 'BINANCE:FILUSDT', 'BINANCE:INJUSDT', 'BINANCE:ATOMUSDT',
           'BINANCE:SEIUSDT', 'BINANCE:RUNEUSDT']

# DataFrame to store signals
Titles = ['Crypto Symbol', 'Last Price', 'IFT_RSI']
df_signals = pd.DataFrame(columns=Titles)

# Prompt the user for their choice
print("Please select an option:")
print("[1] List cryptocurrencies with IFT RSI less than -0.5")
print("[2] List cryptocurrencies with IFT RSI between -0.5 and 0.5")
choice = input("Enter 1 or 2: ").strip()  # Added strip()

# Validate user input
while choice not in ['1', '2']:
    choice = input("Invalid input. Please enter 1 or 2: ").strip()  # Added strip()

# **Ensure that the following code is not indented under the while loop**

# Main loop to process each cryptocurrency
for crypto in cryptos:
    try:
        # Fetch historical data
        data = tv.get_hist(symbol=crypto, exchange='BINANCE', interval=Interval.in_daily, n_bars=1000)
        data = data.reset_index()

        # Calculate IFT RSI
        data = calculate_rsi_ift(data, rsi_length=5, smoothing_length=9)

        # Prepare the data
        data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        data.set_index('datetime', inplace=True)

        # Remove rows with NaN values in IFT_RSI
        data.dropna(subset=['IFT_RSI'], inplace=True)

        # Extract the last data point
        Signals = data.tail(1).reset_index()

        # Get the last IFT_RSI value
        IFT_RSI_value = Signals.loc[0, 'IFT_RSI']

        # Determine if the cryptocurrency meets the selected criteria
        if choice == '1':
            # Option 1: IFT RSI less than -0.5
            Signal = IFT_RSI_value < -0.5
        elif choice == '2':
            # Option 2: IFT RSI between -0.5 and 0.5
            Signal = -0.5 <= IFT_RSI_value <= 0.5

        # If the signal is True, add it to the DataFrame
        if Signal:
            Last_Price = float(Signals.loc[0, 'Close'])
            L1 = [crypto, Last_Price, IFT_RSI_value]
            df_signals.loc[len(df_signals)] = L1
            print(f"{crypto} meets the criteria with IFT_RSI: {IFT_RSI_value}")
    except Exception as e:
        print(f"Error processing {crypto}: {e}")
        pass

# Ensure all rows are shown in the output
pd.set_option('display.max_rows', None)

# Display the results
if choice == '1':
    print("\nCryptocurrencies with IFT RSI less than -0.5:")
elif choice == '2':
    print("\nCryptocurrencies with IFT RSI between -0.5 and 0.5:")

print(df_signals)
