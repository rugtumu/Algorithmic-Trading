import pandas as pd
import numpy as np
from hmmlearn import hmm # pip install hmmlearn
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import time

# Hidden Markov Model for training

print("Starting Bitcoin HMM analysis...")

# Load and preprocess data
def load_and_preprocess_data(file_path):
    print(f"Loading data from {file_path}...")

    # Read CSV and reverse the DataFrame to chronological order
    df = pd.read_csv(file_path)

    # Parse 'Start' as datetime and set as index
    print("Creating datetime index...")
    df.index = pd.date_range(start='2018-01-28', periods=len(df), freq='h')

    print("Calculating returns and volatility...")
    df['Returns'] = df['Close'].pct_change()
    df['Volatility'] = df['Returns'].rolling(window=24).std()

    print("Calculating volume change...")
    df['Volume_Change'] = df['Volume'].pct_change()

    print("Dropping NaN values...")
    df.dropna(inplace=True)

    print(f"Data preprocessed. Shape: {df.shape}")
    return df

# Train HMM
def train_hmm(data, n_components=3):
    print(f"Training HMM with {n_components} components...")
    features=['Returns', 'Volatility', 'Volume_Change']
    X = data[features].values

    print("Normalizing features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Fitting Hmm model...")
    model = hmm.GaussianHMM(n_components=n_components, covariance_type="full", n_iter=100, random_state=42)
    model.fit(X_scaled)

    print("HMM training completed")
    return model, scaler

# Predict states
def predict_states(model, data, scaler):
    print("Predicting states...")
    features=['Returns', 'Volatility', 'Volume_Change']

    X = data[features].values
    X_scaled = scaler.transform(X)
    states = model.predict(X_scaled)

    print(f"States predicted. Unique states: {np.unique(states)}")
    return states

# Analyze states
def analyzes_states(data, states):
    print("Analyzing states...")
    df_analysis = data.copy()
    df_analysis['State'] = states

    for state in range(model.n_components):
        print(f"\nAnalyzing State {state}:")
        state_data = df_analysis[df_analysis['State'] == state]
        print(state_data[['Returns', 'Volatility', 'Volume_Change']].describe())
        print(f"Number of periods in State {state}: {len(state_data)}")

# Plot results
def plot_results(data, states):
    print("Plotting results...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)

    ax1.plot(data.index, data['Close'])
    ax1.set_title('Bitcoin Price and HMM States')
    ax1.set_ylabel('Price')

    print(f"Length of data index: {len(data.index)}")
    print(f"Length of states: {len(states)}")

    for state in range(model.n_components):
        mask = (states == state)
        ax1.fill_between(data.index, data['Close'].min(), data['Close'].max(),
                         where=mask, alpha=0.3, label=f'State {state}')
    
    ax1.legend()

    ax2.plot(data.index, data['Returns'])
    ax2.set_title('Bitcoin Returns')
    ax2.set_ylabel('Returns')
    ax2.set_xlabel('Date')

    plt.tight_layout()
    print("Showing plot...")
    plt.show()

# Main execution
print("Starting main execution...")
file_path = '/home/umut/trade/data/modified_bitcoin_data_hourly.csv'
data = load_and_preprocess_data(file_path)

# Passing in the above data to a training HMM model
print("Training HMM model...")
model, scaler = train_hmm(data)

print("Predicting states...")
states = predict_states(model, data, scaler)
time.sleep(124781)

print("Analyzing states...")
analyzes_states(data, states)

print("Plotting results...")
plot_results(data, states)

print("Printing transition matrix...")
print("Transition Matrix:")
print(model.transmat_)

print("\nPrinting means and covariances of each state...")
for i in range(model.n_components):
    print(f"State {i}:")
    print("Mean:", model.means_[i])
    print("Covariance:", model.covars_[i])
    print()

print("Bitcoin HMM analysis completed.")
