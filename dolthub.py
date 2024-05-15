import requests
import pandas as pd
def create_unique_values_query(table_name, column_name):
    query = f"SELECT DISTINCT {column_name} FROM {table_name};"
    return query

# owner, database = 'dolthub', 'ip-to-country'
# "query_execution_status": "RowLimit",
#   "query_execution_message": "",
#   "repository_owner": "post-no-preference",
#   "repository_name": "options",
#   "commit_ref": "master",
#   "sql_query": "SELECT * FROM `option_chain`",

# query = 'SELECT * FROM `option_chain` LIMIT 10'
# res = requests.get(
#   'https://www.dolthub.com/api/v1alpha1/{}/{}/{}'.format("post-no-preference", "options", "master"),
#   params={'q': query},
#   )
# print(res.json())

query = create_unique_values_query("ohlcv", "act_symbol")
res = requests.get(
  'https://www.dolthub.com/api/v1alpha1/{}/{}/{}'.format("post-no-preference", "stocks", "master"),
  params={'q': query},
  )
df_stock = pd.DataFrame(res.json()["rows"])

query = create_unique_values_query("option_chain", "act_symbol")
res = requests.get(
  'https://www.dolthub.com/api/v1alpha1/{}/{}/{}'.format("post-no-preference", "options", "master"),
  params={'q': query},
  )
df_options = pd.DataFrame(res.json()["rows"])

# print(df_options)

unique_tickers = set(df_options.act_symbol.values+df_stock.act_symbol.values)
with open("Tickerlist.txt", "w+") as file:
    for ticker in list(unique_tickers):
        file.write(ticker +"\n")

