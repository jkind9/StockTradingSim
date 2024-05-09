
import requests

# Your Polygon.io API key
api_key = "nfak2zW9PQJVjYSkqCS07Oc9dvEGFp9O"

# Parameters for the options query
ticker = "AAPL"
from_date = "2024-09-05"
to_date = "2023-01-31"

# URL for historical options data (example: Apple options)
url = f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker="+ticker+"&as_of="+from_date+"&limit=520&apiKey=nfak2zW9PQJVjYSkqCS07Oc9dvEGFp9O"
# url = "https://api.polygon.io/v2/aggs/ticker/O:SPY251219C00650000/range/1/day/2023-01-01/2023-01-31?adjusted=true&sort=asc&apiKey=nfak2zW9PQJVjYSkqCS07Oc9dvEGFp9O"
# Make the request to Polygon.io
response = requests.get(url)
data = response.json()
# print(data)
# Extract and print specific fields like strike price, expiry date
if 'results' in data:
    for option in data['results']:
        print(option)
        break
else:
    print(f"No options data found for {ticker} within {from_date} to {to_date}.")