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
warnings.filterwarnings("ignore")
from fitting import *
from graphing import *

import threading
import time
import os
import json 

TICKERS = ["AAPL"]#, "MSFT", "GOOGL", "AMZN", "TSLA"]
MOVING_AVG_NUM = 10 
ATTRIBUTES = ["gradient", "d2y", "latest_price", "avg", "poly_a", "a_grad"]

class Simulation:
    def __init__(self, starting_cash, file_path=None):
        self.running = False
        self.thread = None
        self.cash = starting_cash
        self.file_path = file_path
        

    def load_data(self):
        if "sim_data/stock_holdings.json" in os.listdir("sim_data"):
            with open("sim_data/stock_holdings.json", 'r') as file:
                self.stock_holdings_info = json.load(file)
        else:
            self.stock_holdings_info = {ticker: {'quantity': 0, 'average_cost': 0} for ticker in TICKERS}
        if "sim_data/all_data.json" in os.listdir("sim_data"):
            with open("sim_data/all_data.json", 'r') as file:
                self.all_data = json.load(file)
        else:
            self.all_data = {ticker: {'Datetime': [], 'Open': [], 'High':[], 'Low':[], 'Close':[], 'Adj Close':[], 'Volume':[]} for ticker in TICKERS}

        self.out_data_dict = {ticker:{} for ticker in TICKERS}
        for ticker in TICKERS:
            self.out_data_dict[ticker] = {metric:[] for metric in ATTRIBUTES}
            self.out_data_dict[ticker]["total_value"] = []
    
    def start_simulation(self):
        """Start the simulation in a separate thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_simulation)
            self.thread.start()

    def run_simulation(self):
        self.a_values = []
        self.gradients = []
        self.averages = []

        if self.file_path:
            self.load_data()
            self.run_not_live_sim()
        else:
            self.run_live_sim()

    def run_not_live_sim(self):
        """The main loop of the simulation."""
        self.input_data = {ticker: pd.read_excel(self.file_path, index_col=0) for ticker in TICKERS}
        
        self.loop_idx=MOVING_AVG_NUM
        while self.running and self.loop_idx<len(self.input_data[TICKERS[0]].index):

            new_stock_data_dict ={}
            for ticker in TICKERS:
                idx = 100
                new_stock_data_dict[ticker]= self.input_data[ticker].iloc[:idx+self.loop_idx]

            # This loop iterates through the new_stock_data_dict and finds ticker specific information. The information is then stored in live stats.
            # This ensures the number of stocks watched at one time is dynamic.

            progress = self.get_live_stats(new_stock_data_dict)
            if progress == "progress":
                self.process_live_stats()
            time.sleep(1)
            self.loop_idx+=1

    def run_live_sim(self):
        pass

    def append_to_output(self, live_stats):
        # append metrics to storage for later exporting
        for ticker in TICKERS:
            for attribute in ATTRIBUTES:
                self.out_data_dict[ticker][attribute].extend([live_stats[ticker][attribute]])

    
    def get_live_stats(self, new_stock_data_dict):
        self.live_stats = {ticker:{} for ticker in TICKERS}
        for i, (ticker, stock_data) in enumerate(new_stock_data_dict.items()):
            # Get the latest price and time
            latest_price = stock_data['Close'].iloc[-1]
            previous_data = stock_data['Close'].tail(MOVING_AVG_NUM).tolist()

            # Linear Regression


            x_data = np.array(list(range(self.loop_idx-MOVING_AVG_NUM, self.loop_idx)))
            y_data = np.array(previous_data)

            gradient,intercept = linear_regression(x= x_data, y = y_data)
            self.gradients.extend([gradient])
            #Polynomial Regression
            coefficients = fit_quadratic_polynomial(x = x_data, y = y_data)
            self.a_values.extend([coefficients[0]])
            # ensure enough loops have run to get the previous data required for trends
            if len(self.gradients)<=MOVING_AVG_NUM:
                return "wait"

            d2y,__ = linear_regression(x= x_data, y = self.gradients[-MOVING_AVG_NUM:])
            a_grad,__ = linear_regression(x= x_data, y = self.a_values[-MOVING_AVG_NUM:])

            avg =sum(previous_data)/len(previous_data)           

            #update the live stats and metrics ready for the buy/sell functionality
            self.live_stats[ticker] = {"gradient":gradient,
                                "d2y": d2y,
                                "latest_price": latest_price,
                                "previous_prices":previous_data,
                                "avg":avg,
                                "poly_a":self.a_values[-MOVING_AVG_NUM:],
                                "a_grad":a_grad
                                }
            return "progress"


    def process_live_stats(self):
        total_stock_val = 0
        for ticker in TICKERS:
            # All logic to decide if any ticker is being bought or sold should go here 
            
            var = self.buy_sell_logic(ticker)
            quantity_held  = self.stock_holdings_info[ticker]["quantity"]
            latest_price = self.live_stats[ticker]["latest_price"]

            if var=="buy" and quantity_held == 0:
                investment_amount = 1000 
                self.buy_stock(ticker, investment_amount, latest_price)
            
            elif var=="sell" and quantity_held>0:
                self.sell_stock(ticker, quantity_held, latest_price)

            current_stock_val = self.stock_holdings_info[ticker]["quantity"]*latest_price
            total_stock_val+=current_stock_val          
        
        self.total_value = self.cash
        self.total_value += total_stock_val
        self.out_data_dict[ticker]["total_value"].extend([self.total_value])

        print("Cash:", self.cash, "| Stock worth:", total_stock_val, "| Portfolio worth:: ", self.total_value )


    def buy_sell_logic(self, ticker):
        
        """
        Determine buy, sell, or hold based on the latest price, moving average,
        gradient (first derivative), and second derivative.

        :param latest_price: The most recent stock price.
        :param moving_average: The current moving average of the stock price.
        :param gradient: The first derivative of the stock price.
        :param second_derivative: The second derivative of the stock price.
        :return: A string indicating 'buy', 'sell', or 'hold'.
        """

        # gradient of >0 meands a is increasing leading to spike in stock val
        # gradient <0 either means stock increase is slowing down or about to heavily decrease
        if self.live_stats[ticker]["a_grad"] >0.00025 or self.live_stats[ticker]["d2y"]>0.002:
            return "buy"
        elif self.live_stats[ticker]["a_grad"]<-0.00025:
            return "sell"

    def stop_simulation(self):
        """Stop the simulation."""
        self.running = False
        if self.thread:
            self.thread.join()

    def is_running(self):
        """Check if the simulation is currently running."""
        return self.running

    # Pseudo function for selling stocks
    def sell_stock(self, ticker, quantity, price):
        sale_cash = quantity * price
        print(f"Sold {quantity} shares of {ticker} at ${price} each.")
        self.stock_holdings_info[ticker]['quantity'] -= quantity
        if self.stock_holdings_info[ticker]['quantity'] == 0:
            self.stock_holdings_info[ticker]['average_cost'] = 0
        self.cash += sale_cash
    
    def buy_stock(self, ticker, investment_amount, price):
        quantity = int(investment_amount // price)

        self.cash -= quantity*price
        if ticker in self.stock_holdings_info:
            self.stock_holdings_info[ticker]['quantity'] += quantity
            total_cost = self.stock_holdings_info[ticker]['average_cost'] * self.stock_holdings_info[ticker]['quantity']
            self.stock_holdings_info[ticker]['average_cost'] = (total_cost + investment_amount) / self.stock_holdings_info[ticker]['quantity']
        else:
            self.stock_holdings_info[ticker] = {'quantity': quantity, 'average_cost': price}


# file_path = "Data.xlsx"
# # Example usage
# sim = Simulation(starting_cash=10000, file_path = file_path)
# sim.start_simulation()
# time.sleep(5)  # Let the simulation run for 5
