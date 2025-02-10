# Backtester

## Description

This is a Python project designed to simulate and evaluate the performance of trading strategies using historical market data. This project allows users to back-test multiple strategies on various stock tickers and evaluate their performance based on key metrics.

## Features

* Load Historical Data: Supports importing data from Yahoo Finance.

* Strategy Implementation: Allows users to implement and test custom trading strategies.

* Performance Metrics: Calculates key performance indicators such as total return, Sharpe ratio, and maximum drawdown.

* Visualization: Generates plots to visualize strategy performance over time.

* GUI Integration: Integrates with Tkinter for a graphical user interface.

## Usage 

* Load Data: Import your historical market data from Yahoo Finance using the specified tickers, start date, end date, and interval.

* Define Strategy: Implement your trading strategy in the tester_algos.py file and add it to the strategy_functions dictionary in the main script.

* Run Back-Test: Execute the back-testing script using the following command:
