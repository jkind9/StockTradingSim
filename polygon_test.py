
import requests
from datetime import datetime, timedelta
import json 

# Your Polygon.io API key
api_key = "nfak2zW9PQJVjYSkqCS07Oc9dvEGFp9O"

# Parameters for the options query
ticker = "SPY"
# Specify your start and end dates
start_date_str = "2023-01-01"
end_date_str = "2023-12-31"

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
for date in tqdm.tqdm(date_list):
    print(date)
    url = "https://api.polygon.io/v3/reference/options/contracts?underlying_ticker=AAPL&as_of="+date+"&limit=10&apiKey=nfak2zW9PQJVjYSkqCS07Oc9dvEGFp9O"
    # Make the request to Polygon.io
    response = requests.get(url)
    data = response.json()
    # print(data)
    # Extract and print specific fields like strike price, expiry date
    if 'results' in data:
        output_data[date]=data["results"]
        
            
with open("options_data.json","w+") as file:
    file.write(json.dumps(output_data))