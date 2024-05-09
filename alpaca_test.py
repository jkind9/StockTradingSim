from alpaca.data import StockHistoricalDataClient, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading import TradingClient, GetAssetsRequest, GetOptionContractsRequest
from alpaca.trading import AssetStatus
import os

# # Set your API credentials
os.environ["APCA_API_KEY_ID"] = "AKK5FQDZ5FISNOV08S2M"
os.environ["APCA_API_SECRET_KEY"] = "Cmpx70xStHoT4gpWNoTkfkeVZMu5va8c9xhyjXFm"

# Initialize the Alpaca client
client = StockHistoricalDataClient(os.getenv("APCA_API_KEY_ID"),os.getenv("APCA_API_SECRET_KEY"))

# Request historical data for Apple (AAPL)
request_params = StockBarsRequest(
    symbol_or_symbols=["SPY"],
    timeframe=TimeFrame.Minute,
    start="2023-01-01",
    end="2023-01-31"
)
import pandas as pd
# Fetch the data
bars = client.get_stock_bars(request_params).df
bars = bars.reset_index(inplace=False)
# print(bars)
bars['timestamp'] = bars['timestamp'].dt.tz_localize(None)
# bars.to_excel("StockData.xlsx")

#### We use paper environment for this example ####
PAPER=True
TRADE_API_URL="https://api.alpaca.markets"
TRADE_API_WSS=None
DATA_API_URL=None
OPTION_STREAM_DATA_WSS=None

api_key = os.getenv("APCA_API_KEY_ID")
secret_key = os.getenv("APCA_API_SECRET_KEY")
paper = PAPER
trade_api_url = TRADE_API_URL

trade_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper, url_override=trade_api_url)

# acc = trade_client.get_account()
# acct_config = trade_client.get_account_configurations()
# req = GetAssetsRequest(
#   attributes = "options_enabled"  
# )
# assets = trade_client.get_all_assets(req)
# underlying_symbol = "SPY"

req = GetOptionContractsRequest(
    underlying_symbol=["SPY"],                 
# specify underlying symbol
    status=AssetStatus.ACTIVE,                           
# specify asset status: active (default)
    expiration_date=None,                                
# specify expiration date (specified date + 1 day range)
    expiration_date_gte=None,                            
# we can pass date object
    expiration_date_lte=None,                           
 # or string (YYYY-MM-DD)
    root_symbol=None, # specify root symbol
    type=None, # specify option type (ContractType.CALL or ContractType.PUT)	
)
		
res = trade_client.get_option_contracts(req)

for response in res:
    print(len(response), type(response))
    print(len(response[1]))
    print(type(response[1][0]))
    break