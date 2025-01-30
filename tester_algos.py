import numpy as np
import pandas as pd


# A Simple Moving Average Strategy
def smaAlgo(data):     
    data.dropna(inplace=True)

    SMA1=40
    SMA2=100

    for ticker in data.columns.levels[0]:
        data[ticker, 'SMA1']=data[ticker, 'Close'].rolling(SMA1).mean()
        data[ticker, 'SMA2']=data[ticker, 'Close'].rolling(SMA2).mean()
        data[ticker, 'Position'] = np.where(data[ticker, 'SMA1']>data[ticker, 'SMA2'], 1, -1)
    data.dropna(inplace=True)
    return data


# Randomly go long or short each day.
def randAlgo(data):
    for ticker in data.columns.levels[0]:
        data[ticker, 'Position']=np.random.choice([1, -1], size=len(data))
    return data


# Simple lag-based algorithm.
def momentAlgo(data):
    lags = 3
    weights = [5, -2, 1,] # By experimenting with the weights, you can change the type of strategy acts as, e.g. Momentum or Mean-reversion.

    data['lag_sum'] = np.zeros_like(data['Returns'])
    # Initialize 'lag_sum' column with zeros

    # Calculate weighted sum of lagged returns
    for lag in range(1, lags + 1):
        data['lag_sum'] += data['Returns'].shift(lag) * (weights[lag - 1] / sum(weights))
    
    # Determine the position
    data['Position'] = np.where(data['lag_sum'] > 0, 1, -1)
    
    return data

