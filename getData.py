
import requests
from datetime import datetime, timedelta
import time
import json 
from alpaca.data import StockHistoricalDataClient, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading import TradingClient, GetAssetsRequest, GetOptionContractsRequest
from alpaca.trading import AssetStatus
import os
import pandas as pd

def get_stock_data(ticker, start_date, end_date):
    # # Set your API credentials
    os.environ["APCA_API_KEY_ID"] = "AKK5FQDZ5FISNOV08S2M"
    os.environ["APCA_API_SECRET_KEY"] = "Cmpx70xStHoT4gpWNoTkfkeVZMu5va8c9xhyjXFm"

    # Initialize the Alpaca client
    client = StockHistoricalDataClient(os.getenv("APCA_API_KEY_ID"),os.getenv("APCA_API_SECRET_KEY"))

    # Request historical data for Apple (AAPL)
    request_params = StockBarsRequest(
        symbol_or_symbols=[ticker],
        timeframe=TimeFrame.Day,
        start=start_date,
        end=end_date
    )
    # Fetch the data
    bars = client.get_stock_bars(request_params).df
    bars = bars.reset_index(inplace=False)
    # print(bars)
    bars['timestamp'] = bars['timestamp'].dt.tz_localize(None)
    bars['timestamp'] = bars['timestamp'].astype(str)
    return bars

def get_option_data(ticker, start_date_str, end_date_str, wait=False):
    # Your Polygon.io API key
    api_key = "nfak2zW9PQJVjYSkqCS07Oc9dvEGFp9O"

    # Parse the dates into `datetime` objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Initialize a list to hold the date strings
    date_list = []

    # Loop to generate the dates
    current_date = start_date
    while current_date <= end_date:
        # Append the date string in the desired format
        date_list.append(current_date.strftime("%Y-%m-%d"))
        # Increment by one day
        current_date += timedelta(days=1)


    # URL for historical options data (example: Apple options)
    # url = f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker="+ticker+"&as_of="+from_date+"&limit=520&apiKey=nfak2zW9PQJVjYSkqCS07Oc9dvEGFp9O"

    # Print or use the date strings
    output_data = {}
    import tqdm
    count = 0
    for date in tqdm.tqdm(date_list):
        print(date)
        url = "https://api.polygon.io/v3/reference/options/contracts?underlying_ticker=+"+ticker+"&as_of="+date+"&limit=10&apiKey="+api_key
        
        # count to avoid API call issues (5 API calls per minute)
        if (count % 5 == 0) and wait:
            time.sleep(60)
            print("Waiting for 1 minute...")
        
        response = requests.get(url)
        data = response.json()
        count += 1
        # print(data)
        # Extract and print specific fields like strike price, expiry date
        if 'results' in data:
            output_data[date]=data["results"]
    return output_data

def get_both_data(ticker, startdate, enddate):
    stock_df = get_stock_data(ticker,startdate,enddate)
    options_dict = get_option_data(ticker, startdate,enddate)
    output={}
    output["options"]=options_dict
    output["stocks"]=stock_df.to_dict()
    return output


# example usage
# all_data = get_both_data("AAPL", "2023-01-01", "2023-01-31")
# print(all_data)
# with open("cf.json", "w+") as file:
#     file.write(json.dumps(all_data))
