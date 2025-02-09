import tkinter as tk
from tkinter import ttk, Text, Scrollbar, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from back_tester import main

# Set High-DPI awareness (for Windows)
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
    pass

# Available strategies
strategies = {
    "Simple Moving Average": "smaAlgo",
    "Random Daily Position": "randAlgo",
    "Lag Based Algorithm": "lagAlgo",
    "Relative Strength Index (RSI)": "rsiAlgo",
    "Moving Average Convergence Divergence (MACD)": "macdAlgo",
    # Add other strategies here
    # "Another Strategy": "anotherAlgo",
}

interval_opt = {
    "1 Minute": "1m",
    "2 Minutes": "2m",
    "5 Minutes": "5m",
    "15 Minutes": "15m",
    "30 Minutes": "30m",
    "60 Minutes": "60m",
    "90 Minutes": "90m",
    "1 Hour": "1h",
    "1 Day": "1d",
    "5 Days": "5d",
    "1 Week": "1wk",
    "1 Month": "1mo",
    "3 Months": "3mo",
}

def start_backtest():
    tickers = tickers_entry.get()
    starter = starter_entry.get()
    ender = ender_entry.get()
    selected_strategy = strategy_var.get()
    selected_interval = interval_var.get()

    rfr = 0.045
    interval_time=interval_opt.get(selected_interval)
    try:
        # Get the strategy function name
        strategy_function_name = strategies.get(selected_strategy)
        if strategy_function_name is None:
            raise ValueError("Selected strategy not found.")

        # # Clear the output screen
        # output_text.delete(1.0, tk.END)
        
        # Clear the previous plot
        for widget in plot_frame.winfo_children():
            widget.destroy()
        
        # Call the backtest with the selected strategy
        main(tickers, starter, ender, rfr, strategy_function_name, plot_frame, tree, interval_time)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = tk.Tk()
root.title("Algotrading Backtester")

# Set the window size (resolution)
window_width = 1500
window_height = 700
root.geometry(f"{window_width}x{window_height}")

# Create a style for the Treeview
style = ttk.Style()
style.configure("Treeview", rowheight=30)  # Set the desired row height

# Create a frame for the input fields and buttons
input_frame = tk.Frame(root)
input_frame.pack(expand=True, pady=10)

# Create and place the input fields and buttons in the input_frame
tk.Label(input_frame, text="Tickers:").grid(row=0, column=0, padx=5, pady=5)
tickers_entry = tk.Entry(input_frame)
tickers_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Starting Date (yyyy-mm-dd):").grid(row=1, column=0, padx=5, pady=5)
starter_entry = tk.Entry(input_frame)
starter_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Ending Date (yyyy-mm-dd):").grid(row=2, column=0, padx=5, pady=5)
ender_entry = tk.Entry(input_frame)
ender_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Strategy:").grid(row=4, column=0, padx=5, pady=5)
strategy_var = tk.StringVar()
strategy_dropdown = ttk.Combobox(input_frame, textvariable=strategy_var, values=list(strategies.keys()))
strategy_dropdown.grid(row=4, column=1, padx=5, pady=5)
strategy_dropdown.current(0)  # Set default value

tk.Label(input_frame, text="Interval:").grid(row=3, column=0, padx=5, pady=5)
interval_var = tk.StringVar()
strategy_dropdown = ttk.Combobox(input_frame, textvariable=interval_var, values=list(interval_opt.keys()))
strategy_dropdown.grid(row=3, column=1, padx=5, pady=5)
strategy_dropdown.current(8)  # Set default value

start_button = tk.Button(input_frame, text="Backtest", command=start_backtest)
start_button.grid(row=5, columnspan=2, pady=10)

# # Create a Text widget for output display
# output_text = Text(root, wrap='word', height=5, width=80)
# output_text.pack(expand=True, pady=10)

# # Add a scrollbar to the Text widget
# scrollbar = Scrollbar(root, command=output_text.yview)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# output_text['yscrollcommand'] = scrollbar.set

# Create a frame for the Treeview and its scrollbar
tree_frame = tk.Frame(root, width=1200, height=400)  # Fixed size for the frame
tree_frame.pack_propagate(False)  # Prevent frame from resizing
tree_frame.pack(pady=10)

# Create a Treeview widget for tabular output
tree = ttk.Treeview(tree_frame, columns=("Metric", "Value"), show="tree headings", height=10, style="Treeview")  # Fixed height for Treeview
tree.heading("#0", text="Ticker", anchor='w')
tree.column("#0", width=150, stretch=tk.YES)
tree.heading("Metric", text="Metric", anchor='w')
tree.heading("Value", text="Value", anchor='w')
tree.column("Metric", width=250, anchor='w')
tree.column("Value", width=150, anchor='w')
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a scrollbar to the Treeview
tree_scrollbar = Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=tree_scrollbar.set)


# Create a frame for the plot
plot_frame = tk.Frame(root)
plot_frame.pack(expand=True, pady=10)





# Run the GUI loop
root.mainloop()