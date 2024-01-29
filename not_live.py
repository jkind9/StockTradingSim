TICKERS = ["AAPL"]#, "MSFT", "GOOGL", "AMZN", "TSLA"]
TICKER_DICT = {ticker:i for i,ticker in enumerate(TICKERS)}
# History length for evaluating stock data
HISTORY_LENGTH = 7  # Adjusted to 7 days to match yfinance's 1-minute data limit
MOVING_AVG_NUM=10

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

# Function to fetch real-time stock data
def fetch_real_time_stock_data(ticker, period='7d', interval='1m'):
    stock_data = yf.download(ticker, period=period, interval=interval)
    return stock_data

# Pseudo function for buying stocks
def buy_stock(ticker, cash, price, investment_amount, stock_holdings_info):
    quantity = int(investment_amount // price)

    remaining_cash = cash - quantity*price
    print(f"Bought {quantity} shares of {ticker} at ${price} each. Investment amount: ${investment_amount}, Risk score: {risk_score:.2f}.")
    if ticker in stock_holdings_info:
        stock_holdings_info[ticker]['quantity'] += quantity
        total_cost = stock_holdings_info[ticker]['average_cost'] * stock_holdings_info[ticker]['quantity']
        stock_holdings_info[ticker]['average_cost'] = (total_cost + investment_amount) / stock_holdings_info[ticker]['quantity']
    else:
        stock_holdings_info[ticker] = {'quantity': quantity, 'average_cost': price}
    return quantity, remaining_cash, stock_holdings_info

# Pseudo function for selling stocks
def sell_stock(ticker, quantity, price, stock_holdings_info):
    cash = quantity * price
    print(f"Sold {quantity} shares of {ticker} at ${price} each.")
    stock_holdings_info[ticker]['quantity'] -= quantity
    if stock_holdings_info[ticker]['quantity'] == 0:
        stock_holdings_info[ticker]['average_cost'] = 0
    return cash

# Function to assess risk based on recent price volatility
def assess_risk(data, slope,intercept):
    #find the std of the stock compared to the historical data
    actual_vals = data
    predicted_vals = [slope*i + intercept for i in data]
    return r2_score(actual_vals, predicted_vals)


# Function to determine investment amount based on risk
def determine_investment_amount(cash, risk_score, max_percent=0.25):

    max_investment = cash * max_percent
    return max_investment * risk_score**3


def next_full_minute(current_time):
    # Get the current time

    # Add one minute to the current time
    next_minute = current_time + timedelta(minutes=1)

    # Reset seconds and microseconds to zero
    next_full_minute = next_minute.replace(second=0, microsecond=0)

    return next_full_minute

def buy_sell_logic(latest_price, moving_average, gradient, second_derivative, a_vals, a_grad):
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
    if a_grad >0.00025 or second_derivative>0.002:
        return "buy"
    elif a_grad<-0.00025:
        return "sell"


# Main function to run the real-time simulation
def run_real_time_simulation(initial_investment, interval=60):
    cash = initial_investment
    # read latest csv line

    stock_holdings_info = {ticker: {'quantity': 0, 'average_cost': 0} for ticker in TICKERS}
    portfolio_value_over_time = []
    all_data = {ticker: pd.read_excel("Data.xlsx", index_col=0) for ticker in TICKERS}
    metrics = ["latest_price", "gradient", "d2y", "avg", "a_grad", "total_value"]
    out_data_dict ={metric:[] for metric in metrics}

    first_timestamp = all_data["AAPL"].index[0]

    # Initialize a figure
    n = len(TICKERS)+1
    plt.ion()
    fig, axes = plt.subplots(n, 1, figsize=(8, n * 3))    # Initialize a line object on the axes

    # Check if only one subplot is created (which is not a list), and convert it to a list
    if n == 1:
        axes = [axes]

    # Initialize lines, one for each subplot
    lines = [ax.plot([], [], label=f'Line {i+1}')[0] for i, ax in enumerate(axes)]

    # Set limits and labels for each axis
    for ax in axes[:-1]:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.legend()

    try:
        print("Launching Sim|", len(axes), "graphs")
        loop_idx=0
        vline_dict = {}
        straight_line_dict ={}
        text_dict={}

        for ticker in TICKERS:
            vline = ax.axvline(x=0, color='blue', linestyle='--', label='Current Position')
            vline_dict[ticker] = vline

        gradients = []
        a_values=[]


        # This is where the sim loop begins. The first section of the loop is about collecting stats, metrics and infering models.
        # The second section is separate so we can sort tickers by their metrics before running the buy/sell functionality.

        while loop_idx<len(all_data[TICKERS[0]].index):
            new_stock_data_dict ={}
            for ticker in TICKERS:
                idx = all_data[ticker].index.get_loc(first_timestamp)+1000+loop_idx
                new_stock_data_dict[ticker]= all_data[ticker].iloc[:idx]

            # This loop iterates through the new_stock_data_dict and finds ticker specific information. The information is then stored in live stats.
            # This ensures the number of stocks watched at one time is dynamic.
            
            live_stats = {}
            for i, (ticker, stock_data) in enumerate(new_stock_data_dict.items()):
                # Get the latest price and time
                latest_price = stock_data['Close'].iloc[-1]
                previous_data = stock_data['Close'].tail(MOVING_AVG_NUM).tolist()
                # print("Ticker:", ticker, "| i:", i, "| Latest Price:", latest_price)

                # Update graphs, using the index for finding the correct axis, moving blue line, line of best fit etc.
                ax = axes[i]
                line = lines[i]  
                vline = vline_dict[ticker]              
                update_graph(ax, line, [loop_idx, latest_price])

                # Linear Regression
                gradient,intercept = linear_regression(x= range(loop_idx-MOVING_AVG_NUM, loop_idx), y = previous_data)
                #Polynomial Regression
                coefficients = fit_quadratic_polynomial(range(loop_idx-MOVING_AVG_NUM, loop_idx), previous_data)

                a_values.extend([coefficients[0]])
                gradients.extend([gradient])

                # ensure enough loops have run to get the previous data required for trends
                if loop_idx>= MOVING_AVG_NUM:
                    d2y,__ = linear_regression(x= range(MOVING_AVG_NUM), y = gradients[-MOVING_AVG_NUM:])
                    a_grad,__ = linear_regression(x= range(MOVING_AVG_NUM), y = a_values[-MOVING_AVG_NUM:])
                    
                    # handle linear regression  plots
                    x_start, x_end = loop_idx - MOVING_AVG_NUM, loop_idx+1  # X-values between which the line is drawn
                    y_start = gradient * x_start + intercept
                    y_end = gradient * x_end + intercept
                    vline.set_xdata(loop_idx - MOVING_AVG_NUM)

                    # handle polynomial regression plots
                    x_values = np.linspace(x_start, x_end, 500)
                    y_values = np.polyval(coefficients, x_values)

                    plt.draw()  

                    avg =sum(previous_data)/len(previous_data)

                    # append metrics to storage for later exporting
                    out_data_dict["gradient"].extend([gradient])
                    out_data_dict["d2y"].extend([d2y])
                    out_data_dict["latest_price"].extend([latest_price])
                    out_data_dict["avg"].extend([avg])
                    out_data_dict["a_grad"].extend([a_grad])
                    

                    #update the live stats and metrics ready for the buy/sell functionality
                    live_stats[ticker] = {"gradient":gradient,
                                        "d2y": d2y,
                                        "latest_price": latest_price,
                                        "previous_prices":previous_data,
                                        "avg":avg,
                                        "poly_a":a_values[-MOVING_AVG_NUM:],
                                        "a_grad":a_grad
                                        }
                else:
                    live_stats[ticker] = {}


            # approx structure of how tracking different methods will work. Each method should have its own associated cash and stock tracker
            # methods =["averages", "GPT", "gradient"]
            # method_values = {key: [initial_investment, stockInfoDict] for key in methods} configure to work with different methods later

            total_stock_val = 0
            for ticker in TICKERS:
                if live_stats[ticker]=={}:
                    continue
                
                #get data and metrics from live_stats
                gradient = live_stats[ticker]["gradient"]
                d2y = live_stats[ticker]["d2y"]
                latest_price = live_stats[ticker]["latest_price"]
                previous_prices = live_stats[ticker]["previous_prices"]
                avg = live_stats[ticker]["avg"]
                a_values = live_stats[ticker]["poly_a"]
                a_grad = live_stats[ticker]["a_grad"]

                ax = axes[TICKER_DICT[ticker]]
                text_dict[ticker].set_text('a_grad:'+str(round(a_grad,5)))

                quantity_held = stock_holdings_info[ticker]["quantity"]

                # All logic to decide if any ticker is being bought or sold should go here 
                
                var = buy_sell_logic(latest_price,avg, gradient,d2y, a_values, a_grad)
                # var2 = buy_sell_logic_2(latest_price,avg, gradient,d2y, a_values, a_grad)

                if var=="buy" and quantity_held == 0:
                    investment_amount = 1000 #determine_investment_amount(cash, risk_score)
                    quantity, remaining_cash, stock_holdings_info = buy_stock(ticker, cash, latest_price, investment_amount, stock_holdings_info)
                    cash = remaining_cash
                    add_vertical_line(ax, x=loop_idx, color='green')
                    plt.draw()  
                
                elif var=="sell" and quantity_held>0:
                    sale_cash = sell_stock(ticker,quantity_held, latest_price, stock_holdings_info)
                    cash+=sale_cash
                    add_vertical_line(ax, x=loop_idx, color='red')
                    plt.draw()

                current_stock_val = stock_holdings_info[ticker]["quantity"]*latest_price
                total_stock_val+=current_stock_val          
            
            total_value = cash
            total_value += total_stock_val
            out_data_dict["total_value"].extend([total_value])

            print("Cash:", cash, "| Stock worth:", total_stock_val, "|Portfolio worth:: ", total_value )
            
            # Handle total_value plot and ensure updates
            ax = axes[n-1]
            ax.set_xlim(0, max(out_data_dict["total_value"]))
            ax.set_ylim(0, max(out_data_dict["total_value"]))
            line = lines[n-1]
            update_graph(ax, line, [loop_idx, total_value])

            # Calculate current portfolio value and profit/loss
            # current_value = cash + calculate_profit_or_loss()
            # portfolio_value_over_time.append(current_value)
            # print(f"Current portfolio value: ${current_value:.2f}")

            loop_idx+=1
            plt.savefig("Data.jpg")

    except KeyboardInterrupt:
        print("Simulation stopped.")

        out_df = pd.DataFrame.from_dict(out_data_dict)
        output_graph(out_df)
        out_df.to_excel("Output.xlsx")
        return portfolio_value_over_time



portfolio_value = run_real_time_simulation(TICKERS, 10000)
