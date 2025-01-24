import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def main():
    # Defines the risk-free rate.
    rfr=0.045
    # Retrieves the users stock of choice.
    ticker_sym = input("Please input your chosen stock. Use their ticker: ").upper()

    # Processes data.
    data = getStockData(ticker_sym)
    data = positionAlgorithm(data)
    data = calculateReturns(data)

    # Error checker
    if data is None or data.empty:
        print("Error: Data is empty after processing.")
        return
    
    stock_return, ann_return, ann_vol, sharpe_ratio = calculateStats(data, rfr)
    output(stock_return, ann_return, ann_vol, sharpe_ratio)
    plotResults(data)


def getStockData(ticker_sym):
    ticker = yf.Ticker(ticker_sym)
    timeframe=str(input("How long would you like to backtest this strategy over? E.g. 1d, 2w, 3m, 4y"))
    historical_data = ticker.history(period=timeframe)
    if historical_data.empty or historical_data is None:
        print(f"No historical data found for ticker: {ticker_sym}")
        return None
    return historical_data[['Open', 'High', 'Low', 'Close']]


# Adds the daily proportional returns and the strategy returns to the dataframe.
def calculateReturns(data):
    data['Returns'] = np.log(data['Close'] / data['Close'].shift(1))
    data['Strat'] = data['Position'].shift(1) * data['Returns']
    data.dropna(inplace=True)

    return data


# Calculates relevant statistics.
def calculateStats(data, rfr):
    strat = data['Strat'].values
    returns = data['Returns'].values

    if len(strat) == 0 or len(returns) == 0:
        print("Error: No valid data for returns or strategy.")

    stock_return = np.exp(returns.sum())-1
    ann_return = np.exp(strat.sum())-1
    ann_vol = strat.std() * np.sqrt(len(data))

    if ann_vol == 0:
        print("Error: Annual volatility is zero.")
        sharpe_ratio = np.nan
    else:
        sharpe_ratio = (ann_return - rfr) / ann_vol

    return stock_return, ann_return, ann_vol, sharpe_ratio


# Plots the cumulative stock and strategy returns.
def plotResults(data):
    plt.figure(figsize=(10,6))
    plt.plot(data['Returns'].cumsum().apply(np.exp), label='Stock Returns')
    plt.plot(data['Strat'].cumsum().apply(np.exp), label='Strategy Returns')
    plt.plot(data['SMA1']/data['Close'].iloc[0], label='SMA1')
    plt.plot(data['SMA2']/data['Close'].iloc[0], label='SMA2')
    plt.legend(loc=0)
    plt.show()


# Output statistics.
def output(stock_return, ann_return, ann_vol, sharpe_ratio):
    print(f'Annual stock return: {np.round(stock_return, 3)*100}%')
    print(f'Annual volatility: {np.round(ann_vol, 3)*100}%')
    print(f'Annual Return: {np.round(ann_return, 3)*100}%')
    print(f'Sharpe: {sharpe_ratio}')


# Function that defines what positions to take.
def positionAlgorithm(data):
    data.dropna(inplace=True)

    SMA1=42
    SMA2=252

    data['SMA1']=data['Close'].rolling(SMA1).mean()
    data['SMA2']=data['Close'].rolling(SMA2).mean()
    data['Position'] = np.where(data['SMA1']>data['SMA2'], 1, -1)

    data.dropna(inplace=True)
    return data



if __name__ == "__main__":
    main()