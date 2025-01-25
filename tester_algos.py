import numpy as np
import pandas as pd


# A Simple Moving Average Strategy
def smaAlgo(data):     
    data.dropna(inplace=True)

    SMA1=42
    SMA2=252


    data['SMA1']=data['Close'].rolling(SMA1).mean()
    data['SMA2']=data['Close'].rolling(SMA2).mean()
    data['Position'] = np.where(data['SMA1']>data['SMA2'], 1, -1)

    data.dropna(inplace=True)
    return data


# Randomly go long or short each day.
def randAlgo(data):
    data['Position']=np.random.choice([1, -1], size=len(data))
    return data


# Simple momentum-based algorithm.
def momentAlgo(data):
    lags = 3  
    weights = [10, 2, 1] 

    # Initialize 'lag_sum' column with zeros
    data['lag_sum'] = np.zeros_like(data['Returns'])

    # Calculate weighted sum of lagged returns
    for lag in range(1, lags + 1):
        data['lag_sum'] += data['Returns'].shift(lag) * (weights[lag - 1] / sum(weights))
    
    # Determine the position
    data['Position'] = np.where(data['lag_sum'] > 0, 1, -1)
    
    return data
