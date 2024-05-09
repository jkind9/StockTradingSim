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
import buy_sell_logic
import threading
import time
import os
import json 

TICKERS = ["AAPL", "MSFT"]#, "GOOGL", "AMZN", "TSLA"]
MOVING_AVG_NUM = 10 
ATTRIBUTES = [ "price", "gradient", "d2y", "avg", "poly_a", "a_grad"]

class Simulation:
    def __init__(self, starting_cash=10000, file_path=None, tickers = TICKERS, logic = buy_sell_logic.a_grad, graphing=False):
        self.chosen_func = logic
        self.running = False
        self.thread = None
        self.cash = starting_cash
        self.file_path = file_path
        self.tickers = tickers
        self.graphing = graphing
        self.total_stock_val = 0
        self.total_value = starting_cash
        self.starting_cash = starting_cash

        self.results = {"TotalValue":[starting_cash], "ProfitOverTime":[0], "PositiveTradeRatio":[0]}
        print("SIM TICKERS:: ", tickers)
        self.ticker_dict ={ticker: i for i,ticker in enumerate(TICKERS)}
        if graphing:
            fig, axs = plt.subplots(2, 2, figsize=(10, 8))
            
    def load_data(self):
        if "sim_data/stock_holdings.json" in os.listdir("sim_data"):
            with open("sim_data/stock_holdings.json", 'r') as file:
                self.stock_holdings_info = json.load(file)
                for ticker in TICKERS:
                    if ticker not in self.stock_holdings_info.keys():
                        self.stock_holdings_info[ticker] = {'quantity': 0, 'average_cost': 0}
        else:
            self.stock_holdings_info = {ticker: {'quantity': 0, 'average_cost': 0} for ticker in TICKERS}
        if "sim_data/all_data.json" in os.listdir("sim_data"):
            with open("sim_data/all_data.json", 'r') as file:
                self.all_data = json.load(file)
                for ticker in TICKERS:
                    if ticker not in self.all_data.keys():
                        self.all_data[ticker] = {'Datetime': [], 'Open': [], 'High':[], 'Low':[], 'Close':[], 'Adj Close':[], 'Volume':[]}
        else:
            self.all_data = {ticker: {'Datetime': [], 'Open': [], 'High':[], 'Low':[], 'Close':[], 'Adj Close':[], 'Volume':[]} for ticker in TICKERS}

        self.out_data_dict = {ticker:{} for ticker in TICKERS}
        for ticker in TICKERS:
            self.out_data_dict[ticker] = {metric:[] for metric in ATTRIBUTES}
            self.out_data_dict["total_value"] = []
    
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
                
                df =  new_stock_data_dict[ticker]
                # Get the last row of the DataFrame
                last_row = df.iloc[-1]
                # Iterate through columns and append values to the JSON structure
                for col in df.columns:
                    self.all_data[ticker][col].append(last_row[col])

            # This loop iterates through the new_stock_data_dict and finds ticker specific information. The information is then stored in live stats.
            # This ensures the number of stocks watched at one time is dynamic.
            if self.method == "stock":
                run = self.get_live_stats(new_stock_data_dict)
                if run: self.process_live_stats()
                self.loop_idx+=1

            elif self.method == "options":
                self.get_ticker_option_data(new_stock_data_dict)



    def run_live_sim(self):
        pass

    def append_to_output(self):
        # append metrics to storage for later exporting
        for ticker in TICKERS:
            for attribute in ATTRIBUTES:
                att = self.live_stats[ticker][attribute]
                
                self.out_data_dict[ticker][attribute].extend([att])

    def get_ticker_option_data(self, new_stock_data_dict, option_data):
        quantity = 5
        option_value, strike_price = option_data
        bought_options={}
        for ticker in TICKERS:
            var = self.chosen_func(new_stock_data_dict) # output is buycall, buyput, hold
            for command in var:
                if command=="buycall":
                    bought_options[ticker]+=quantity*option_value
            
    def get_live_stats(self, new_stock_data_dict):
        self.live_stats = {ticker:{} for ticker in TICKERS}
        run =[True]
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
                run.extend([False])
                continue

            d2y,__ = linear_regression(x= x_data, y = self.gradients[-MOVING_AVG_NUM:])
            a_grad,__ = linear_regression(x= x_data, y = self.a_values[-MOVING_AVG_NUM:])

            avg =sum(previous_data)/len(previous_data)           

            #update the live stats and metrics ready for the buy/sell functionality
            self.live_stats[ticker] = {"gradient":gradient,
                                "d2y": d2y,
                                "price": latest_price,
                                "previous_prices":previous_data,
                                "avg":avg,
                                "poly_a":self.a_values[-MOVING_AVG_NUM:],
                                "a_grad":a_grad
                                }
        var = all(run)
        if var: self.append_to_output()
        return var


    def process_live_stats(self):
        total_stock_val = 0
        for ticker in TICKERS:
            # All logic to decide if any ticker is being bought or sold should go here 
            
            var = self.chosen_func(ticker, self.live_stats)
            quantity_held  = self.stock_holdings_info[ticker]["quantity"]
            latest_price = self.live_stats[ticker]["price"]

            if var=="buy" and quantity_held == 0:
                investment_amount = 1000 
                self.buy_stock(ticker, investment_amount, latest_price)
            
            elif var=="sell" and quantity_held>0:
                self.sell_stock(ticker, quantity_held, latest_price)

            current_stock_val = self.stock_holdings_info[ticker]["quantity"]*latest_price
            total_stock_val+=current_stock_val          
        
        self.total_value = self.cash
        self.total_value += total_stock_val
        self.out_data_dict["total_value"].extend([self.total_value])
        self.total_stock_val = total_stock_val
        # print("Cash:", self.cash, "| Stock worth:", total_stock_val, "| Portfolio worth:: ", self.total_value )
        self.profit = self.total_value - self.starting_cash
        self.results["ProfitOverTime"].extend([self.profit])
        self.results["TotalValue"].extend([self.total_value])


       
    def stop_simulation(self):
        """Stop the simulation."""
        self.running = False

        with open("sim_data/stock_results.json", "w") as file:
            json.dump(self.out_data_dict, file, indent=4)

        with open("sim_data/stock_holdings.json", "w") as file:
            json.dump(self.stock_holdings_info, file, indent=4)

        with open("sim_data/all_data.json", "w") as file:
            json.dump(self.all_data, file, indent=4)

    def is_running(self):
        """Check if the simulation is currently running."""
        return self.running

    # Pseudo function for selling stocks
    def sell_stock(self, ticker, quantity, price):
        sale_cash = quantity * price
        # print(f"Sold {quantity} shares of {ticker} at ${price} each.")
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
# # # Example usage
# sim = Simulation(starting_cash=10000, file_path = file_path)
# sim2 = Simulation(starting_cash=5000, file_path = file_path)
# sim.start_simulation()
# sim2.start_simulation()
# time.sleep(1)  # Let the simulation run for 5
# sim.stop_simulation()
# sim2.stop_simulation()