from src.data.Alpaca import fetch_alpaca_dividends, fetch_alpaca_data
import pandas as pd
import requests
import os



if __name__ == "__main__":
    # check account status
    # url='https://paper-api.alpaca.markets/v2/account'
    # headers = {"accept": "application/json",
    #            "APCA-API-KEY-ID":os.environ.get("ALPACA_KEY"),
    #            'APCA-API-SECRET-KEY':os.environ.get("ALPACA_SECRET")}
    # response = requests.get(url, headers=headers)
    # print(response.text)

    symbol = 'SPY'
    start_date = '2024-01-01'
    end_date = '2025-01-01'
    # spy_intra_data = fetch_alpaca_data(symbol, '1Min', start_date, end_date)
    spy_daily_data = fetch_alpaca_data(symbol, '1D', start_date, end_date)
    # dividends = fetch_alpaca_dividends(symbol, start_date, end_date)

