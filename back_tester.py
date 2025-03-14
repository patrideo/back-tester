import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tester_algos import smaAlgo,randAlgo, lagAlgo, rsiAlgo, macdAlgo, arimaModel
import tkinter as tk
from datetime import datetime

# Function dictionary for strategies
strategy_functions = {
    "smaAlgo": smaAlgo,
    "randAlgo": randAlgo,
    "lagAlgo": lagAlgo,
    "rsiAlgo": rsiAlgo,
    "macdAlgo": macdAlgo,
    "arimaModel": arimaModel,
    # Add other strategies here
}

def main(tickers, starter, ender, rfr, strategy, plot_frame, tree, interval):
    tickers=tickers.upper()
    timeframe=convert_to_timeframe(starter, ender)
    #timeframe2=convert_to_years(timeframe)

    # Processes data.
    data = getMultiStockData(tickers, starter, ender, interval)
    tickers=tickers.split(" ")
    data = calculateReturns(data)


    
    data = calculateStrat(data, strategy)

    # Error checker
    if data is None or data.empty:
        print("Error: Data is empty after processing.")
        return
    
    data, combined_strat  = combineStrategyReturns(data)

    stats, data = calculateStats(data, rfr, timeframe, combined_strat)
    output(stats, tree, timeframe, starter, ender)

    plotResults(data, plot_frame)

def convert_to_timeframe(starter, ender):
    d1 = datetime.strptime(starter, "%Y-%m-%d")
    d2 = datetime.strptime(ender, "%Y-%m-%d")
    
    days_diff = (d2 - d1).days
    
    years_diff = days_diff / 365.25  # Considering leap years
    
    return years_diff



def convert_to_years(timeframe):
    total_years = 0.0
    value=0
    unit=""
    for char in timeframe:
        if char.isdigit():
            value += int(char)
        if char.isalpha():
            unit += char
        
    
    if unit=='y':
        total_years+=value
    elif unit=='m':
        total_years+=value/525600
    elif unit=='h':
        total_years+=value/8760
    elif unit=='mo':
        total_years+=value/12
    elif unit=='d':
        total_years+=value/365.25
    elif unit=='wk':
        total_years+=value/52.1429
    return total_years



def getMultiStockData(tickers, starter, ender, interval):
    # data = {}
    # tickers = tickers.split(", ")
    
    # for tick in tickers:
    #     ticker = yf.Ticker(tick)
    #     historical_data = ticker.history(period=timeframe)
    #     if historical_data.empty or historical_data is None:
    #         print(f"No historical data found for {tick}")
    #     else:
    #         data[tick] = historical_data[['Open', 'High', 'Low', 'Close']]
    
    data=yf.download(tickers, start=starter, end=ender, group_by='tickers', interval=interval)

    if data.empty:
        raise ValueError("No valid data retrieved for any ticker.")
    
    #data = pd.concat(data, axis=1, keys=data.keys())
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


def calculateStats(data, rfr, timeframe, combined_strat):
    stats = []

    for ticker in data.columns.levels[0]:
        if ticker!='Combined':
            strat = data[(ticker, 'Strat')].values
            returns = data[(ticker, 'Returns')].values
            if len(strat) == 0 or len(returns) == 0:
                print(f"No valid data for returns or strategy for {ticker}.")
                continue

            stock_return = np.exp(returns.sum()) - 1
            strat_return = np.exp(strat.sum()) - 1
            timeframe_vol = strat.std() * np.sqrt(252*timeframe)
            stock_vol = returns.std() * np.sqrt(252)
            sharpe_ratio = (strat_return - rfr*timeframe) / timeframe_vol

            # Calculate drawdown
            data[(ticker, 'Cumulative_Returns')] = (1 + data[(ticker, 'Strat')]).cumprod()
            data[(ticker, 'Running_Max')] = data[(ticker, 'Cumulative_Returns')].cummax()
            data[(ticker, 'Drawdown')] = (data[(ticker, 'Cumulative_Returns')] - data[(ticker, 'Running_Max')]) / data[(ticker, 'Running_Max')]
            max_drawdown = data[(ticker, 'Drawdown')].min()

        stats.append([ticker, stock_return, strat_return, timeframe_vol, sharpe_ratio, stock_vol, max_drawdown])

    # Combined strategy stats


    combined_stock_return = np.exp(combined_strat.sum()) - 1
    combined_strat_return = np.exp(combined_strat.sum()) - 1
    combined_timeframe_vol = combined_strat.std() * np.sqrt(252*timeframe)
    combined_annual_vol = combined_strat.std() * np.sqrt(252)
    combined_sharpe_ratio = (combined_strat_return/timeframe - rfr) / combined_annual_vol

    combined_cumulative_returns = (1 + combined_strat).cumprod()
    combined_running_max = combined_cumulative_returns.cummax()
    combined_drawdown = (combined_cumulative_returns - combined_running_max) / combined_running_max
    combined_max_drawdown = combined_drawdown.min()
    combined_avg_drawdown = combined_drawdown.mean()

    stats.append(['Strategy', combined_stock_return, combined_strat_return, combined_timeframe_vol, combined_sharpe_ratio, combined_max_drawdown, combined_avg_drawdown])

    return stats, data






def combineStrategyReturns(data):
    # Check if 'Strat' column exists
    if 'Strat' not in data.columns.get_level_values(1):
        raise ValueError("The 'Strat' column is not found in the DataFrame.")

    # Create a column 'Combined_Strategy' which is the sum of strategy returns across all stocks
    combined_strat = data.xs('Strat', level=1, axis=1).sum(axis=1)
    data[('Combined', 'Strategy')] = combined_strat

    # Create additional columns if needed (e.g., cumulative returns)
    data[('Combined', 'Cumulative_Returns')] = np.exp(data[('Combined', 'Strategy')].cumsum())

    return data, combined_strat




# Plots the cumulative stock and strategy returns.
def plotResults(data, plot_frame):
    plt.close()
    fig, ax = plt.subplots(figsize=(10, 6))
    for ticker in data.columns.levels[0]:
        if ticker == 'Combined':
            continue
        ax.plot(data[ticker, 'Returns'].cumsum().apply(np.exp), label=f"{ticker} Closing Price", linewidth=0.5)

    # Plot the combined strategy cumulative returns if it exists
    if ('Combined', 'Cumulative_Returns') in data.columns:
        ax.plot(data[('Combined', 'Cumulative_Returns')], label='Combined Strategy Returns')

    #ax.plot(data[('AAPL', 'MACD')], linewidth=0.5, label='MACD')

    ax.legend(loc='upper left')
    ax.set_title("Stock and Strategy Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Returns")
    ax.grid(True)

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)



def output(stats,tree, timeframe, starter, ender):
    # Clear the existing rows in the tree
    for row in tree.get_children():
        tree.delete(row)

    # Add stats for each stock
    for stat in stats[:-2]:  # Exclude the last entry (combined strategy stats)
        ticker = stat[0]
        stock_return = stat[1]
        strat_return = stat[2]
        timeframe_vol = stat[3]
        sharpe_ratio = stat[4]
        stock_vol = stat[5]
        max_drawdown = stat[6]

        # Add a subheading for the ticker
        ticker_id = tree.insert('', 'end', text=f"Stock: {ticker}", open=True)

        # Insert stats under the ticker subheading
        tree.insert(ticker_id, 'end', values=(f"Stock Return between {starter} and {ender}(%)", f"{stock_return * 100:.2f}"))
        tree.insert(ticker_id, 'end', values=("Stock Volatility (%)", f"{stock_vol * 100:.2f}"))
        tree.insert(ticker_id, 'end', values=(f"Strategy Return on Stock between {starter} and {ender} (%)", f"{strat_return * 100:.2f}"))
        tree.insert(ticker_id, 'end', values=(f"Strategy Volatility between {starter} and {ender} (%)", f"{timeframe_vol * 100:.2f}"))
        tree.insert(ticker_id, 'end', values=("Sharpe Ratio", f"{sharpe_ratio:.2f}"))
        tree.insert(ticker_id, 'end', values=("Max Drawdown (%)", f"{max_drawdown * 100:.2f}"))

    # Add combined strategy stats
    combined_stats = stats[-1]
    combined_stock_return = combined_stats[1]
    combined_strat_return = combined_stats[2]
    combined_timeframe_vol = combined_stats[3]
    combined_sharpe_ratio = combined_stats[4]
    combined_max_drawdown = combined_stats[5]
    combined_avg_drawdown = combined_stats[6] if len(combined_stats) > 6 else None  # Adjust if average drawdown is included

    # Add a subheading for the combined strategy
    strategy_id = tree.insert('', 'end', text="Combined Strategy", open=True)

    # Insert combined stats under the strategy subheading
    tree.insert(strategy_id, 'end', values=(f"Combined Strategy Return between {starter} and {ender} (%)", f"{combined_strat_return * 100:.2f}"))
    tree.insert(strategy_id, 'end', values=(f"Strategy Volatility between {starter} and {ender}(%)", f"{combined_timeframe_vol * 100:.2f}"))
    tree.insert(strategy_id, 'end', values=("Sharpe Ratio", f"{combined_sharpe_ratio:.2f}"))
    tree.insert(strategy_id, 'end', values=("Max Drawdown (%)", f"{combined_max_drawdown * 100:.2f}"))
    if combined_avg_drawdown is not None:
        tree.insert(strategy_id, 'end', values=("Average Drawdown (%)", f"{combined_avg_drawdown * 100:.2f}"))

