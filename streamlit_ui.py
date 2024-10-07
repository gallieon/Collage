import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Simulated historical price data
data = {
    'Date': pd.date_range(start='2010-01-01', periods=1000),
    'Open': np.random.uniform(100, 200, 1000),
    'High': np.random.uniform(200, 250, 1000),
    'Low': np.random.uniform(80, 150, 1000),
    'Close': np.random.uniform(120, 180, 1000),
    'Volume': np.random.randint(10000, 50000, 1000)
}

df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# Simple Moving Average Strategy
def simple_moving_average_strategy(data, short_window, long_window):
    signals = pd.DataFrame(index=data.index)
    signals['Signal'] = 0.0

    signals['Short_MA'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['Long_MA'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()

    signals['Signal'][short_window:] = np.where(
        signals['Short_MA'][short_window:] > signals['Long_MA'][short_window:], 1.0, 0.0
    )

    signals['Positions'] = signals['Signal'].diff()
    return signals

st.title('Algorithmic Trading Simulation')

# User inputs
short_window = st.number_input('Short Window', min_value=1, max_value=100, value=10)
long_window = st.number_input('Long Window', min_value=1, max_value=200, value=50)
risk_per_trade = st.number_input('Risk per Trade (%)', min_value=0.01, max_value=1.0, value=0.02) / 100

# Apply strategy
signals = simple_moving_average_strategy(df, short_window, long_window)

# Trading simulation
initial_portfolio_value = 100000
position = 0
portfolio_value = []

for index, row in signals.iterrows():
    if row['Positions'] == 1:
        max_position_size = (risk_per_trade * initial_portfolio_value) / (row['Close'] - row['Low'])
        position = min(max_position_size, initial_portfolio_value / row['Close'])
        initial_portfolio_value -= position * row['Close']
    elif row['Positions'] == -1:
        initial_portfolio_value += position * row['Close']
        position = 0
    portfolio_value.append(initial_portfolio_value + position * row['Close'])

signals['PortfolioValue'] = portfolio_value

# Plotting
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

ax[0].plot(df.index, df['Close'], label='Close Price')
ax[0].plot(signals.index, signals['Short_MA'], label='Short MA')
ax[0].plot(signals.index, signals['Long_MA'], label='Long MA')
ax[0].legend()
ax[0].set_title('Price and Moving Averages')

ax[1].plot(signals.index, signals['PortfolioValue'], label='Portfolio Value', color='green')
ax[1].set_title('Portfolio Value Over Time')
ax[1].legend()

st.pyplot(fig)

st.write(signals)
