TICKERS = ["AAPL"]#, "MSFT", "GOOGL", "AMZN", "TSLA"]
# History length for evaluating stock data
HISTORY_LENGTH = 7  # Adjusted to 7 days to match yfinance's 1-minute data limit

import yfinance as yf
import time
from sklearn.metrics import r2_score

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
    return slope

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

# Main function to run the real-time simulation
def run_real_time_simulation(tickers, initial_investment, interval=60):
    cash = initial_investment
    stock_holdings_info = {ticker: {'quantity': 0, 'average_cost': 0} for ticker in tickers}
    portfolio_value_over_time = []
    historical_data = {ticker: fetch_real_time_stock_data(ticker, period=f"{HISTORY_LENGTH}d") for ticker in tickers}
    last_historical_timestamp = historical_data.index[-1].strftime("%m/%d/%Y %H:%M:%S")
    try:
        while True:
            current_time = time.perf_counter()
            new_stock_data_dict = {ticker: fetch_real_time_stock_data(ticker, period=f"{HISTORY_LENGTH}d") for ticker in tickers}
           
            print(stock_data_dict)
            
            live_stats = {}
            for ticker, stock_data in new_stock_data_dict.items():
                # Get the latest price and time
                latest_price = stock_data['Close'].iloc[-1]
                previous_data = stock_data['Close'].tail(10).tolist()
                latest_timestamp = stock_data.index[-1].strftime("%m/%d/%Y %H:%M:%S")
                #Check if stock is updated
                if latest_time == last_historical_timestamp:
                    print("Stock %s has not been updated, latest time was %s" %( ticker, latest_timestamp))
                else:
                    print("Stock %s updated." %(ticker))
                    gradient,intercept = linear_regression(previous_data)
                    risk_score = assess_risk(previous_data, gradient, intercept)
                    live_stats[ticker] = {"gradient":gradient, "risk": risk_score}

            sorted_data = dict(sorted(live_stats.items(), key=lambda x: x[1]['gradient'], reverse=True))

            for ticker, (gradient, risk_score) in sorted_data.items():
                if gradient > 0:
                    investment_amount = determine_investment_amount(cash, risk_score)

                    quantity, remaining_cash, stock_holdings_info = buy_stock(ticker, cash, price, investment_amount, risk_score, stock_holdings_info)
                
            # # Calculate current portfolio value and profit/loss
            # current_value = cash + calculate_profit_or_loss(stock_holdings_info, stock_data_dict)
            # portfolio_value_over_time.append(current_value)
            # print(f"Current portfolio value: ${current_value:.2f}")

            time.sleep(interval)
            break

    except KeyboardInterrupt:
        print("Simulation stopped.")
        return portfolio_value_over_time



portfolio_value = run_real_time_simulation(TICKERS, initial_investment, interval)
