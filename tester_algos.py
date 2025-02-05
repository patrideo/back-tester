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
    weights = [5, -3, -1,] # By experimenting with the weights, you can change the type of strategy acts as, e.g. Momentum or Mean-reversion.

    for ticker in data.columns.levels[0]:
        data[ticker, 'lag_sum'] = np.zeros_like(data[ticker, 'Returns'])

        for lag in range(1, lags + 1):
            data[ticker, 'lag_sum'] += data[ticker, 'Returns'].shift(lag) * (weights[lag - 1] / sum(weights))
        
        # Determine the position
        data[ticker, 'Position'] = np.where(data[ticker, 'lag_sum'] > 0, 1, -1)
    
    return data

def rsiAlgo(data, period=14, lower_threshold=200, upper_threshold=240):
    for ticker in data.columns.levels[0]:

        delta = data[(ticker, 'Close')].diff()
        delta = delta[1:]  # Remove the first NaN

        gain = delta.copy()
        loss = delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        loss = loss.abs()

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        data[(ticker, 'RSI')] = rsi

        data[(ticker, 'Position')] = 0
        data[(ticker, 'Position')] = np.where(data[(ticker, 'RSI')] < lower_threshold, 1, data[(ticker, 'Position')])
        data[(ticker, 'Position')] = np.where(data[(ticker, 'RSI')] > upper_threshold, -1, data[(ticker, 'Position')])

        data[(ticker, 'Position')].fillna(method='ffill', inplace=True)

    return data

def macdAlgo(data, fast_period=12, slow_period=26, signal_period=9):
    for ticker in data.columns.levels[0]:
        # Calculate the fast and slow exponential moving averages (EMAs)
        data[(ticker, 'EMA_fast')] = data[(ticker, 'Close')].ewm(span=fast_period, adjust=False).mean()
        data[(ticker, 'EMA_slow')] = data[(ticker, 'Close')].ewm(span=slow_period, adjust=False).mean()

        # Calculate MACD line and signal line
        data[(ticker, 'MACD')] = data[(ticker, 'EMA_fast')] - data[(ticker, 'EMA_slow')]
        data[(ticker, 'Signal_Line')] = data[(ticker, 'MACD')].ewm(span=signal_period, adjust=False).mean()

        # Generate signals
        data[(ticker, 'Position')] = 0
        data[(ticker, 'Position')] = np.where(data[(ticker, 'MACD')] > data[(ticker, 'Signal_Line')], 1, -1)

        # Forward fill positions to hold until next signal
        data[(ticker, 'Position')].fillna(method='ffill', inplace=True)
    return data
