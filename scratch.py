import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Function to fetch real-time stock data
def fetch_real_time_stock_data(ticker, period='7d', interval='1m'):
    stock_data = yf.download(ticker, period=period, interval=interval)
    
    return stock_data
# data = fetch_real_time_stock_data("AAPL")
# # data.index = data.index.tz_localize(None)
# print(data)
# # data.to_excel("Data.xlsx")

def next_full_minute(current_time):
    # Get the current time

    # Add one minute to the current time
    next_minute = current_time + timedelta(minutes=1)

    # Reset seconds and microseconds to zero
    next_full_minute = next_minute.replace(second=0, microsecond=0)

    return next_full_minute
ticker="a"
all_data ={}
all_data[ticker]=pd.read_excel("Data.xlsx", index_col=0)
first_timestamp = all_data[ticker].index[0]

print(all_data[ticker].iloc[all_data[:ticker].index.get_loc(first_timestamp)+1000])