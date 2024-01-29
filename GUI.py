import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import numpy as np
import time
import yfinance as yf
import time
from sklearn.metrics import r2_score
import numpy as np 
import sys
import time
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import warnings
import os
import csv 
import json

warnings.filterwarnings("ignore")
from fitting import *
from graphing import *

TICKERS = ["AAPL"]#, "MSFT", "GOOGL", "AMZN", "TSLA"]
TICKER_DICT = {ticker:i for i,ticker in enumerate(TICKERS)}
# History length for evaluating stock data
HISTORY_LENGTH = 7  # Adjusted to 7 days to match yfinance's 1-minute data limit
MOVING_AVG_NUM=10

def next_full_minute(current_time):
    # Get the current time

    # Add one minute to the current time
    next_minute = current_time + timedelta(minutes=1)

    # Reset seconds and microseconds to zero
    next_full_minute = next_minute.replace(second=0, microsecond=0)

    return next_full_minute

# Function to fetch real-time stock data
def fetch_real_time_stock_data(ticker, period='7d', interval='1m'):
    stock_data = yf.download(ticker, period=period, interval=interval)
    return stock_data

def buy_sell_logic(latest_price,avg, gradient,d2y, a_values, a_grad):
    if latest_price <avg and a_grad>0:
        return "buy"
    if latest_price>avg and a_grad<0:
        return "sell"

class App:
    def __init__(self, root):
        self.root = root
        self.cash = 10000

        self.root.title("Dynamic Plots")

        self.tab_control = ttk.Notebook(root)

        # Tab 1
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text='Live Price')
        n = len(TICKERS)+1

        self.fig1, self.axes1 = plt.subplots(n, 1, figsize=(8, n * 3))    # Initialize a line object on the axes
        # Check if only one subplot is created (which is not a list), and convert it to a list
        if n == 1:
            self.axes1 = [self.axes1]
        self.line_plots = [ax.plot([], [], label=f'Line {i+1}')[0] for i, ax in enumerate(self.axes1)]

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tab1)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # # Tab 2
        # self.tab2 = ttk.Frame(self.tab_control)
        # self.tab_control.add(self.tab2, text='Plot 2')
        # self.fig2, self.ax2 = plt.subplots()
        # self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.tab2)
        # self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        self.tab_control.pack(expand=1, fill="both")

        self.start_sim_button = tk.Button(root, text= "Start Simulation", command = self.start_running_sim)
        self.start_sim_button.pack()


    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
