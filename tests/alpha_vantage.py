import requests
import os
import pandas as pd

api_key = os.environ.get("ALPHAVANTAGE")
# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey={api_key}'
r = requests.get(url)
data = r.json()

df = pd.DataFrame.from_dict(data.get('Time Series (5min)'), orient='index')
df = df.sort_index()

print(data)