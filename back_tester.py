import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tester_algos import smaAlgo
from tester_algos import randAlgo
import tkinter as tk

# Function dictionary for strategies
strategy_functions = {
    "smaAlgo": smaAlgo,
    "randAlgo": randAlgo,
    # Add other strategies here
    # "anotherAlgo": anotherAlgo,
}

def main(tickers, timeframe, rfr, strategy, output_text, plot_frame, tree):
    # Defines the risk-free rate.
    # Retrieves the users stock of choice.
    tickers=tickers.upper()

    # Processes data.
    data = getMultiStockData(tickers, timeframe)
    timeframe=int(timeframe.replace('y',''))
    data = calculateReturns(data)


    
    data = calculateStrat(data, strategy)

    # Error checker
    if data is None or data.empty:
        print("Error: Data is empty after processing.")
        return
    

    stats, data = calculateStats(data, rfr, timeframe)
    data = combineStrategyReturns(data)


    output(stats, timeframe, output_text, tree)
    plotResults(data, plot_frame)


def getMultiStockData(tickers, timeframe):
    data = {}
    tickers = tickers.split(", ")
    
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
    return data


# Adds the daily proportional returns and the strategy returns to the dataframe.
def calculateReturns(data):
    for ticker in data.columns.levels[0]:
        data[(ticker, 'Returns')] = np.log(data[(ticker, 'Close')] / data[(ticker, 'Close')].shift(1))
    data.dropna(inplace=True)
    return data


def calculateStrat(data, strategy):
    strategy_function = strategy_functions.get(strategy)
    if strategy_function is None:
        raise ValueError(f"Strategy '{strategy}' not found.")
    data = strategy_function(data)
    for ticker in data.columns.levels[0]:
        data[(ticker, 'Strat')] = data[(ticker, 'Position')] * data[(ticker, 'Returns')]
    data.dropna(inplace=True)
    return data


def calculateStats(data, rfr, timeframe):
    stats = []

    # Calculate individual stats for each ticker
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

    # # Calculate combined stats for all stocks in the strategy
    # combined_strat = data.xs('Strat', level=1, axis=1).sum(axis=1)      #FIX THIS BULLSHIT
    # combined_returns = data.xs('Returns', level=1, axis=1).sum(axis=1)

    # combined_stock_return = np.exp(combined_returns.sum()) - 1
    # combined_strat_return = np.exp(combined_strat.sum()) - 1
    # combined_ann_vol = combined_strat.std() * np.sqrt(252)
    # combined_stock_vol = combined_returns.std() * np.sqrt(252)
    # combined_sharpe_ratio = (combined_strat_return / timeframe - rfr) / combined_ann_vol

    # # Calculate drawdown for the combined strategy
    # combined_cumulative_returns = (1 + combined_strat).cumprod()
    # combined_running_max = combined_cumulative_returns.cummax()
    # combined_drawdown = (combined_cumulative_returns - combined_running_max) / combined_running_max
    # combined_max_drawdown = combined_drawdown.min()

    # stats.append(['Strategy', combined_stock_return, combined_strat_return, combined_ann_vol, combined_sharpe_ratio, combined_stock_vol, combined_max_drawdown])

    return stats, data



def combineStrategyReturns(data):
    # Check if 'Strat' column exists
    if 'Strat' not in data.columns.get_level_values(1):
        raise ValueError("The 'Strat' column is not found in the DataFrame.")

    # Create a column 'Combined_Strategy' which is the sum of strategy returns across all stocks
    combined_strategy = data.xs('Strat', level=1, axis=1).sum(axis=1)
    data[('Combined', 'Strategy')] = combined_strategy

    # Create additional columns if needed (e.g., cumulative returns)
    data[('Combined', 'Cumulative_Returns')] = (1 + data[('Combined', 'Strategy')]).cumprod()

    return data




# Plots the cumulative stock and strategy returns.
def plotResults(data, plot_frame):
    fig, ax = plt.subplots(figsize=(12, 6))
    for ticker in data.columns.levels[0]:
        if ticker == 'Combined':
            continue
        ax.plot(data[ticker, 'Returns'].cumsum().apply(np.exp), label=f"{ticker} Returns", linewidth=0.5)

    # Plot the combined strategy cumulative returns if it exists
    if ('Combined', 'Cumulative_Returns') in data.columns:
        ax.plot(data[('Combined', 'Cumulative_Returns')], label='Combined Strategy Returns')

    ax.legend(loc='upper left')
    ax.set_title("Stock and Strategy Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Returns")
    ax.grid(True)

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)



def output(stats, timeframe, output_text, tree):
    headers = ["Ticker", "Annual Stock Return (%)", "Annual Strategy Return (%)", "Annual Volatility (%)", "Sharpe Ratio", "Volatility (%)", "Max Drawdown (%)"]
    formatted_stats = [
        [ticker,
         f"{stock_return * 100/timeframe:.2f}",
         f"{strat_return * 100/timeframe:.2f}",
         f"{ann_vol * 100:.2f}",
         f"{sharpe_ratio:.2f}",
         f"{stock_vol * 100:.2f}",
         f"{max_drawdown * 100:.2f}"]
        for ticker, stock_return, strat_return, ann_vol, sharpe_ratio, stock_vol, max_drawdown in stats
    ]

        # Clear the existing rows in the tree
    for row in tree.get_children():
        tree.delete(row)
    
    # Insert the formatted stats into the Treeview
    for stat in formatted_stats:
        tree.insert("", "end", values=(stat[0], stat[1]))



if __name__ == "__main__":
    main()