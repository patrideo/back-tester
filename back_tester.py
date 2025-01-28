import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from tester_algos import randAlgo
from tabulate import tabulate 

def main():
    # Defines the risk-free rate.
    rfr=0.045
    # Retrieves the users stock of choice.
    tickers = input("Please input your chosen stocks. Input their ticket(s) separated by a comma: ").upper()

    # Processes data.
    data, timeframe = getMultiStockData(tickers)
    timeframe=int(timeframe.replace('y',''))
    data = calculateReturns(data)


    data = randAlgo(data)   # Choose an algorithm you want to test here. Make sure to import the function at the top of the file.
    
    data = calculateStrat(data)

    # Error checker
    if data is None or data.empty:
        print("Error: Data is empty after processing.")
        return
    

    stats = calculateStats(data, rfr, timeframe)

    output(stats)
    plotResults(data)

def getMultiStockData(tickers):
    data = {}
    tickers = tickers.split(", ")
    timeframe = str(input("How long would you like to backtest this strategy over? Options are: 1y, 2y, 5y, 10y."))
    
    for tick in tickers:
        ticker = yf.Ticker(tick)
        historical_data = ticker.history(period=timeframe)
        if historical_data.empty or historical_data is None:
            print(f"No historical data found for {tick}")
        else:
            data[tick] = historical_data[['Open', 'High', 'Low', 'Close']]
    
    if not data:
        raise ValueError("No valid data retrieved for any ticker.")
    
    data = pd.concat(data, axis=1, keys=data.keys())
    print(data.columns)
    return data, timeframe


# Adds the daily proportional returns and the strategy returns to the dataframe.
def calculateReturns(data):
    for ticker in data.columns.levels[0]:
        data[(ticker, 'Returns')] = np.log(data[(ticker, 'Close')] / data[(ticker, 'Close')].shift(1))
    data.dropna(inplace=True)
    return data


def calculateStrat(data):
    for ticker in data.columns.levels[0]:
        data[(ticker, 'Strat')] = data[(ticker, 'Position')].shift(1) * data[(ticker, 'Returns')]
    data.dropna(inplace=True)
    return data



def calculateStats(data, rfr, timeframe):
    stats = []
    for ticker in data.columns.levels[0]:
        strat = data[(ticker, 'Strat')].values
        returns = data[(ticker, 'Returns')].values
        if len(strat) == 0 or len(returns) == 0:
            print(f"No valid data for returns or strategy for {ticker}.")
            continue

        stock_return = np.exp(returns.sum()) - 1
        strat_return = np.exp(strat.sum()) - 1
        ann_vol = strat.std() * np.sqrt(252)
        stock_vol = returns.std() * np.sqrt(252)
        sharpe_ratio = (strat_return / timeframe - rfr) / ann_vol

        # Calculate drawdown
        data[(ticker, 'Cumulative_Returns')] = (1 + data[(ticker, 'Strat')]).cumprod()
        data[(ticker, 'Running_Max')] = data[(ticker, 'Cumulative_Returns')].cummax()
        data[(ticker, 'Drawdown')] = (data[(ticker, 'Cumulative_Returns')] - data[(ticker, 'Running_Max')]) / data[(ticker, 'Running_Max')]
        max_drawdown = data[(ticker, 'Drawdown')].min()

        stats.append([ticker, stock_return, strat_return, ann_vol, sharpe_ratio, stock_vol, max_drawdown])

    return stats





# Plots the cumulative stock and strategy returns.
def plotResults(data):
    plt.figure(figsize=(10,6))
    for ticker in data.columns.levels[0]:
        plt.plot(data[ticker, 'Returns'].cumsum().apply(np.exp), label=f'{ticker} Returns', linewidth=0.5 )
    plt.plot(data['AAPL', 'Strat'].cumsum().apply(np.exp), label='Strategy Returns')
    plt.legend(loc=0)
    plt.show()


def output(stats):
    headers = ["Ticker", "Stock Return (%)", "Strategy Return (%)", "Annual Volatility (%)", "Sharpe Ratio", "Stock Volatility (%)", "Max Drawdown (%)"]
    formatted_stats = [
        [ticker,
         f"{stock_return * 100:.2f}",
         f"{strat_return * 100:.2f}",
         f"{ann_vol * 100:.2f}",
         f"{sharpe_ratio:.2f}",
         f"{stock_vol * 100:.2f}",
         f"{max_drawdown * 100:.2f}"]
        for ticker, stock_return, strat_return, ann_vol, sharpe_ratio, stock_vol, max_drawdown in stats
    ]
    table = tabulate(formatted_stats, headers=headers, tablefmt="pretty")
    print(table)



if __name__ == "__main__":
    main()