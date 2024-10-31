import numpy as np
import pandas as pd
from hmmlearn import hmm

# Sample data: let's assume we have daily returns of a stock
data = pd.DataFrame({
    'returns': [0.01, -0.02, 0.03, -0.01, 0.02, -0.02, 0.04, -0.03, 0.01, -0.01]
})

# Reshape data for HMM
returns = data['returns'].values.reshape(-1, 1)

# Define the HMM model
model = hmm.GaussianHMM(n_components=3, covariance_type="diag", n_iter=1000)

# Fit the model
model.fit(returns)

# Predict the hidden states
hidden_states = model.predict(returns)

print("Hidden States:")
print(hidden_states)

# Model parameters
print("Transition matrix")
print(model.transmat_)
print("Means and vars of each hidden state")
for i in range(model.n_components):
    print(f"{i}: mean = {model.means_[i]} variance = {np.diag(model.covars_[i])}")

# Use the model to predict future states
future_returns = np.array([[0.02], [0.01], [-0.03], [0.04]])
future_hidden_states = model.predict(future_returns)
print("Future Hidden States:")
print(future_hidden_states)
