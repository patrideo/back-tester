import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from tester_algos import momentAlgo
from tabulate import tabulate 

def main():
    # Defines the risk-free rate.
    rfr=0.045
    # Retrieves the users stock of choice.
    ticker_sym = input("Please input your chosen stock. Use their ticker: ").upper()

    # Processes data.
    data, timeframe = getStockData(ticker_sym)
    timeframe=int(timeframe.replace('y',''))
    data = calculateReturns(data)

    data = momentAlgo(data)   # Choose an algorithm you want to test here. Make sure to import the function at the top of the file.
    data = calculateStrat(data)

    data, max_drawdown=calculate_drawdown(data)

    # Error checker
    if data is None or data.empty:
        print("Error: Data is empty after processing.")
        return
    
    stock_return, strat_return, ann_vol, sharpe_ratio, stock_vol = calculateStats(data, rfr, timeframe)
    output(stock_return, strat_return, ann_vol, sharpe_ratio, max_drawdown, timeframe, stock_vol)
    plotResults(data)


def getStockData(ticker_sym):
    ticker = yf.Ticker(ticker_sym)
    timeframe=str(input("How long would you like to backtest this strategy over? Options are: 1y, 2y, 5y, 10y."))
    historical_data = ticker.history(period=timeframe)
    if historical_data.empty or historical_data is None:
        print(f"No historical data found for ticker: {ticker_sym}")
        return None
    return historical_data[['Open', 'High', 'Low', 'Close']], timeframe


# Adds the daily proportional returns and the strategy returns to the dataframe.
def calculateReturns(data):
    data['Returns'] = np.log(data['Close'] / data['Close'].shift(1))
    data.dropna(inplace=True)
    return data

def calculateStrat(data):
    data['Strat'] = data['Position'].shift(1) * data['Returns']
    data.dropna(inplace=True)
    return data
# Calculates relevant statistics.
def calculateStats(data, rfr, timeframe):
    strat = data['Strat'].values
    returns = data['Returns'].values

    if len(strat) == 0 or len(returns) == 0:
        print("Error: No valid data for returns or strategy.")

    stock_return = np.exp(returns.sum())-1
    strat_return = np.exp(strat.sum())-1
    ann_vol = strat.std() * np.sqrt(252)
    stock_vol = returns.std() * np.sqrt(252)
    sharpe_ratio = (strat_return/timeframe - rfr) / ann_vol
    return stock_return, strat_return, ann_vol, sharpe_ratio, stock_vol

def calculate_drawdown(data):
    # Calculate cumulative returns
    data['Cumulative_Returns'] = (1 + data['Strat']).cumprod()
    
    # Calculate running maximum
    data['Running_Max'] = data['Cumulative_Returns'].cummax()
    
    # Calculate drawdown
    data['Drawdown'] = (data['Cumulative_Returns'] - data['Running_Max']) / data['Running_Max']
    
    # Calculate maximum drawdown
    max_drawdown = max(abs(data['Drawdown']))
    
    print(type(max_drawdown))
    return data, max_drawdown


# Plots the cumulative stock and strategy returns.
def plotResults(data):
    plt.figure(figsize=(10,6))
    plt.plot(data['Returns'].cumsum().apply(np.exp), label='Stock Returns')
    plt.plot(data['Strat'].cumsum().apply(np.exp), label='Strategy Returns')
    plt.legend(loc=0)
    plt.show()


def output(stock_return, strat_return, ann_vol, sharpe_ratio, max_drawdown, timeframe, stock_vol):
    stock_data = [
        ["Annual return", f"{round(stock_return * 100 / timeframe, 3)}%"],
        ["Total return", f"{round(stock_return * 100, 3)}%"],
        ["Annual volatility", f"{round(stock_vol * 100, 3)}%"],
    ]

    strategy_data = [
        ["Annual Return", f"{round(strat_return * 100 / timeframe, 3)}%"],
        ["Total Return", f"{round(strat_return * 100, 3)}%"],
        ["Annual volatility", f"{round(ann_vol * 100, 3)}%"],
        ["Max Drawdown", f"{round(max_drawdown * 100, 3)}%"],
        ["Sharpe Ratio", f"{sharpe_ratio}"]
    ]

    print("Stock Data:")
    print(tabulate(stock_data, headers=["Metric", "Value"], tablefmt="pretty"))

    print("\nStrategy Data:")
    print(tabulate(strategy_data, headers=["Metric", "Value"], tablefmt="pretty"))


if __name__ == "__main__":
    main()