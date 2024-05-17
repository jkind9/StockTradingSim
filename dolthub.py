import requests
import pandas as pd
from datetime import datetime
import os

def create_unique_values_query(table_name, column_name):
    query = f"SELECT DISTINCT {column_name} FROM {table_name};"
    return query
import json


    
  # # Construct the SQL query
  # query_options = f"""
  # SELECT *
  # FROM option_chain
  # WHERE ticker IN ({tickers_str})
  # """
# res = requests.get(
#   'https://www.dolthub.com/api/v1alpha1/{}/{}/{}'.format("post-no-preference", "options", "master"),
#   params={'q': query_minmax_date},
#   )
# print("Restype:: ", res)
# print("RESPONSE: ", res.json())

# query = create_unique_values_query("ohlcv", "act_symbol")
# res = requests.get(
#   'https://www.dolthub.com/api/v1alpha1/{}/{}/{}'.format("post-no-preference", "stocks", "master"),
#   params={'q': query},
#   )
# df_stock = pd.DataFrame(res.json()["rows"])

# query = create_unique_values_query("option_chain", "act_symbol")
# res = requests.get(
#   'https://www.dolthub.com/api/v1alpha1/{}/{}/{}'.format("post-no-preference", "options", "master"),
#   params={'q': query},
#   )
# df_options = pd.DataFrame(res.json()["rows"])

# # print(df_options)

# unique_tickers = set(df_options.act_symbol.values+df_stock.act_symbol.values)
# with open("Tickerlist.txt", "w+") as file:
#   for ticker in list(unique_tickers):
#       file.write(ticker +"\n")
#---------------------------------------------------------------------
def get_ticker_data(start_date=None, end_date=None):
  # Get min max start date from the existing data, if doesnt exist use min max of tables
  # returns true if new data found else returns false


  if "stock.csv" in os.listdir("sim_data") and "options.csv" in os.listdir("sim_data"):
    df_stock = pd.read_csv("sim_data/stock.csv")
    df_options = pd.read_csv("sim_data/options.csv")
    min_date = min(df_stock.date.values+df_options.date.values)
    max_date = max(df_stock.date.values+df_options.date.values)
    start_date = max_date
    end_date = datetime.today().date()
  
  if start_date==end_date and start_date is not None:
     print("No new data")
     return True
  print("New data found, gathering data between: ", start_date, end_date)
  #--------------------------------------------------------------------------------
  with open('sim_data/Tickerlist.txt', 'r') as file:
    tickers = file.read().splitlines()
  # Convert ticker names to a format suitable for SQL IN clause
  #--------------------------------------------------------------------------------
  # Construct the SQL query
  query_options = f"""
  SELECT *
  FROM option_chain
  """
  # Construct the SQL query
  query_stock = f"""
  SELECT *
  FROM ohlcv
  """
  if start_date is not None:
    # If there is a start and end date specified in the queries then add in the where clause to the end of the query using string concatination
    query_options += f"""
    AND date >= '{start_date}' AND date <= '{end_date}';
    """
    # Construct the SQL query
    query_stock += f"""
    AND date >= '{start_date}' AND date <= '{end_date}';
    """
  print("OPTIONS QUERY:: ", query_options)
  res = requests.get(
  'https://www.dolthub.com/api/v1alpha1/{}/{}/{}'.format("post-no-preference", "options", "master"),
  params={'q': query_options},
  )
  df_options = pd.DataFrame(res.json()["rows"])
  df_options_filtered = df_options[df_options['act_symbol'].isin(tickers)]

  print(df_options_filtered)
  update_csv("sim_data/options.csv", df_options_filtered)

  #--------------------------------------------------------------------------------


  res = requests.get(
  'https://www.dolthub.com/api/v1alpha1/{}/{}/{}'.format("post-no-preference", "stocks", "master"),
  params={'q': query_stock},
  )
  df_stock = pd.DataFrame(res.json()["rows"])
  df_stock_filtered = df_options[df_stock['act_symbol'].isin(tickers)]
  
  update_csv("sim_data/stock.csv", df_stock_filtered)
  return True

def data_csv_to_json():
  df_stock = pd.read_csv("sim_data/stock.csv")
  stock_dict = df_stock.groupby('date').apply(lambda x: x.to_dict(orient='records')).to_dict()
  df_options = pd.read_csv("sim_data/options.csv")
  options_dict = df_options.groupby('date').apply(lambda x: x.to_dict(orient='records')).to_dict()

  master_dict ={"options":options_dict, "stock":stock_dict}
  with open("sim_data/CF.json", "w+") as file:
     file.write(json.dumps(master_dict))

def update_csv(file_path, newdata):
  if os.path.basename(file_path) in os.listdir(os.path.dirname(file_path)):
    df_existing = pd.read_csv(file_path)
    df_combined = pd.concat([df_existing, newdata], ignore_index=True)
  else:
    df_combined=newdata
  df_combined.to_csv(file_path, index=False)