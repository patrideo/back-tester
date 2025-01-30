import tkinter as tk
from tkinter import ttk, Text, Scrollbar, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from back_tester import main

# Available strategies
strategies = {
    "Simple Moving Average": "smaAlgo",
    "Random Daily Position": "randAlgo",
    # Add other strategies here
    # "Another Strategy": "anotherAlgo",
}

def start_backtest():
    tickers = tickers_entry.get()
    timeframe = timeframe_entry.get()
    selected_strategy = strategy_var.get()
    rfr = 0.045

    try:
        # Get the strategy function name
        strategy_function_name = strategies.get(selected_strategy)
        if strategy_function_name is None:
            raise ValueError("Selected strategy not found.")

        # Clear the output screen
        output_text.delete(1.0, tk.END)
        
        # Clear the previous plot
        for widget in plot_frame.winfo_children():
            widget.destroy()
        
        # Call the backtest with the selected strategy
        main(tickers, timeframe, rfr, strategy_function_name, output_text, plot_frame, tree)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = tk.Tk()
root.title("Algotrading Backtester")

# Create a frame for the input fields and buttons
input_frame = tk.Frame(root)
input_frame.pack(expand=True, pady=10)

# Create and place the input fields and buttons in the input_frame
tk.Label(input_frame, text="Tickers:").grid(row=0, column=0, padx=5, pady=5)
tickers_entry = tk.Entry(input_frame)
tickers_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Timeframe:").grid(row=1, column=0, padx=5, pady=5)
timeframe_entry = tk.Entry(input_frame)
timeframe_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Strategy:").grid(row=2, column=0, padx=5, pady=5)
strategy_var = tk.StringVar()
strategy_dropdown = ttk.Combobox(input_frame, textvariable=strategy_var, values=list(strategies.keys()))
strategy_dropdown.grid(row=2, column=1, padx=5, pady=5)
strategy_dropdown.current(0)  # Set default value

start_button = tk.Button(input_frame, text="Start Backtest", command=start_backtest)
start_button.grid(row=3, columnspan=2, pady=10)

# Create a Text widget for output display
output_text = Text(root, wrap='word', height=5, width=80)
output_text.pack(expand=True, pady=10)

# Add a scrollbar to the Text widget
scrollbar = Scrollbar(root, command=output_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_text['yscrollcommand'] = scrollbar.set

# Create a Treeview widget for tabular output
tree = ttk.Treeview(root, columns=("Metric", "Value"), show="headings", height=5)
tree.heading("Metric", text="Metric")
tree.heading("Value", text="Value")
tree.column("Metric", width=300)
tree.column("Value", width=300)
tree.pack(expand=True, pady=10)

# Add a scrollbar to the Treeview
tree_scrollbar = Scrollbar(root, orient="vertical", command=tree.yview)
tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=tree_scrollbar.set)

# Create a frame for the plot
plot_frame = tk.Frame(root)
plot_frame.pack(expand=True, pady=10)

# Run the GUI loop
root.mainloop()