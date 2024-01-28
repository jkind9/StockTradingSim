TICKERS = ["AAPL"]#, "MSFT", "GOOGL", "AMZN", "TSLA"]
# History length for evaluating stock data
HISTORY_LENGTH = 7  # Adjusted to 7 days to match yfinance's 1-minute data limit

import yfinance as yf
import time
from sklearn.metrics import r2_score
import numpy as np 
from sklearn.linear_model import LinearRegression
import sys
import time
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def linear_regression(y):
    x = np.array(range(len(y)))

    y = np.array(y)
    # Reshape the data (needed when you have a single feature)
    x = x.reshape(-1, 1)

    # Create a linear regression model
    model = LinearRegression()

    # Fit the model to the data
    model.fit(x, y)

    # Get the coefficients (slope and intercept)
    slope = model.coef_[0]
    intercept = model.intercept_
    return slope, intercept

# Function to fetch real-time stock data
def fetch_real_time_stock_data(ticker, period='7d', interval='1m'):
    stock_data = yf.download(ticker, period=period, interval=interval)

    return stock_data

# Pseudo function for buying stocks
def buy_stock(ticker, cash, price, investment_amount, risk_score, stock_holdings_info):
    quantity = investment_amount // price
    remaining_cash = cash - investment_amount
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

# Function to calculate profit or loss
def calculate_profit_or_loss(stock_holdings_info, stock_data_dict):
    total_profit_loss = 0
    for ticker, holding in stock_holdings_info.items():
        if holding['quantity'] > 0:
            current_price = stock_data_dict[ticker]['Adj Close'].iloc[-1]
            profit_loss = (current_price - holding['average_cost']) * holding['quantity']
            total_profit_loss += profit_loss
            print(f"{ticker} Profit/Loss: ${profit_loss:.2f}")
    print(f"Total Portfolio Profit/Loss: ${total_profit_loss:.2f}")
    return total_profit_loss

def update_graph(ax, line, new_data):
    """
    Updates the graph with new data and adjusts the axes limits to fit all data points.

    Parameters:
    ax (matplotlib.axes.Axes): The axis to update.
    line (matplotlib.lines.Line2D): The line object to update.
    new_data (tuple): A tuple (new_x, new_y) representing the new data point.
    """
    # Update the line data
    line.set_xdata(np.append(line.get_xdata(), new_data[0]))
    line.set_ydata(np.append(line.get_ydata(), new_data[1]))

    # Adjust the x and y limits to fit all data points
    ax.set_xlim(min(line.get_xdata()), max(line.get_xdata()))
    ax.set_ylim(min(line.get_ydata()), max(line.get_ydata()))

    # Redraw the figure to show the updated line and axes
    ax.relim()  # Recalculate limits
    ax.autoscale_view()  # Rescale the view
    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()


def update_or_add_line(ax, gradient, intercept, line_label='Updated Line'):
    """
    Updates or adds a line to a specified matplotlib axis (subplot) based on the gradient and y-intercept.
    Ensures only one line with the given label exists on the axis.

    Parameters:
    ax (matplotlib.axes.Axes): The axis to update/add the line to.
    gradient (float): The gradient (slope) of the line.
    intercept (float): The y-intercept of the line.
    line_label (str): Label for the line.
    """
    # Get the current x-limits of the axis to determine the range for plotting the line
    x_vals = np.array(ax.get_xlim())
    y_vals = intercept + gradient * x_vals

    # Check if a line with the given label already exists
    line_exists = False
    for line in ax.get_lines():
        if line.get_label() == line_label:
            # Update the existing line
            line.set_xdata(x_vals)
            line.set_ydata(y_vals)
            line_exists = True
            break

    # If the line doesn't exist, create a new one
    if not line_exists:
        ax.plot(x_vals, y_vals, label=line_label)

    # Redraw the axis to show the updated/new line
    ax.relim()  # Recalculate limits
    ax.autoscale_view()  # Rescale the view
    ax.legend()  # Update the legend

def next_full_minute(current_time):
    # Get the current time

    # Add one minute to the current time
    next_minute = current_time + timedelta(minutes=1)

    # Reset seconds and microseconds to zero
    next_full_minute = next_minute.replace(second=0, microsecond=0)

    return next_full_minute

# Main function to run the real-time simulation
def run_real_time_simulation(tickers, initial_investment, interval=60):
    cash = initial_investment
    stock_holdings_info = {ticker: {'quantity': 0, 'average_cost': 0} for ticker in tickers}
    portfolio_value_over_time = []
    historical_data = {ticker: fetch_real_time_stock_data(ticker, period=f"{HISTORY_LENGTH}d") for ticker in tickers}
    last_historical_timestamp = historical_data[tickers[0]].index[-1].strftime("%m/%d/%Y %H:%M:%S")

    # Initialize a figure
    n = len(TICKERS)
    plt.ion()
    fig, axes = plt.subplots(n, 1, figsize=(8, n * 3))    # Initialize a line object on the axes

    # Check if only one subplot is created (which is not a list), and convert it to a list
    if n == 1:
        axes = [axes]

    # Initialize lines, one for each subplot
    lines = [ax.plot([], [], label=f'Line {i+1}')[0] for i, ax in enumerate(axes)]

    # Set limits and labels for each axis
    for ax in axes:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.legend()

    try:
        print("Launching Sim")
        next_minute = next_full_minute(datetime.now())
        while True:
            current_time = datetime.now()
            if current_time <= next_minute:
                print(next_full_minute - current_time)
                continue
            next_minute = next_full_minute()
            new_stock_data_dict = {ticker: fetch_real_time_stock_data(ticker, period=f"{HISTORY_LENGTH}d") for ticker in tickers}
            # print(new_stock_data_dict)
            live_stats = {}
            for i, (ticker, stock_data) in enumerate(new_stock_data_dict.items()):


                # Get the latest price and time
                latest_price = stock_data['Close'].iloc[-1]
                previous_data = stock_data['Close'].tail(10).tolist()
                
                ax = axes[i]
                line = lines[i]                
                latest_timestamp = stock_data.index[-1].strftime("%m/%d/%Y %H:%M:%S")
                #Check if stock is updated
                if latest_timestamp == last_historical_timestamp:
                    print("Stock %s has not been updated, latest time was %s" %( ticker, latest_timestamp))
                else:
                    update_graph(ax, line, latest_price)
                    print("Stock %s updated." %(ticker))
                    gradient,intercept = linear_regression(previous_data)
                    update_or_add_line(ax, gradient=gradient, intercept=intercept, line_label="Trendline")
                    plt.draw()
                    # risk_score = assess_risk(previous_data, gradient, intercept)
                    # live_stats[ticker] = {"gradient":gradient, "risk": risk_score}

            # sorted_data = dict(sorted(live_stats.items(), key=lambda x: x[1]['gradient'], reverse=True))

            # for ticker, (gradient, risk_score) in sorted_data.items():
            #     if gradient > 0:
            #         investment_amount = determine_investment_amount(cash, risk_score)

            #         quantity, remaining_cash, stock_holdings_info = buy_stock(ticker, cash, latest_price, investment_amount, risk_score, stock_holdings_info)
                
            # # Calculate current portfolio value and profit/loss
            # current_value = cash + calculate_profit_or_loss(stock_holdings_info, stock_data_dict)
            # portfolio_value_over_time.append(current_value)
            # print(f"Current portfolio value: ${current_value:.2f}")

            # time.sleep(interval)
            # break

    except KeyboardInterrupt:
        print("Simulation stopped.")
        return portfolio_value_over_time



portfolio_value = run_real_time_simulation(TICKERS, 10000)
