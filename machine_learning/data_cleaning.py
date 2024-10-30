import pandas as pd
import time

# Load the CSV file
#data = pd.read_csv('/home/umut/trade/data/bitcoin_2018-01-28_2024-10-28.csv')
data = pd.read_csv('/home/umut/trade/data/Bitstamp_BTCUSD_1h.csv')

# Drop unnecessary columns
#data = data.drop(columns=['End', 'Market_Cap'])
data = data.drop(columns=['unix', 'symbol', 'Volume BTC'])

# Reverse the rows of the DataFrame
data = data.iloc[::-1].reset_index(drop=True)

# Round the numeric columns to two decimal places
#data[['Open', 'High', 'Low', 'Close', 'Volume']] = data[['Open', 'High', 'Low', 'Close', 'Volume']].round(2)
data[['open', 'high', 'low', 'close', 'volume']] = data[['open', 'high', 'low', 'close', 'volume']].round(2)

# Save the modified dataframe to a new CSV file
data.to_csv('/home/umut/trade/data/modified_bitcoin_data_hourly_1.csv', index=False)

# Display
print("Data has been saved to 'modified_bitcoin_data_hourly_1.csv'.")