import requests
import pandas as pd
import os
ALPHAVANTAGEKEY = os.environ.get("ALPHAVANTAGE")

# Get status
url = f'https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={ALPHAVANTAGEKEY}'
r = requests.get(url)
data = r.json()
