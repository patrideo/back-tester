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
def lagAlgo(data):
    lags = 3
    weights = [-2, 4, -1,] # By experimenting with the weights, you can change the type of strategy acts as, e.g. Momentum or Mean-reversion.

    for ticker in data.columns.levels[0]:
        data[ticker, 'lag_sum'] = np.zeros_like(data[ticker, 'Returns'])

        for lag in range(1, lags + 1):
            data[ticker, 'lag_sum'] += data[ticker, 'Returns'].shift(lag) * (weights[lag - 1] / sum(weights))
        
        # Determine the position
        data[ticker, 'Position'] = np.where(data[ticker, 'lag_sum'] > 0, 1, -1)
    
    return data
