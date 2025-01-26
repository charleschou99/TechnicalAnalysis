import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import plotly.io as pio
pio.renderers.default = "browser"
from src.technicalanalysis.technicalanalysis import RSI, SMA, EMA

from src.data.Alpaca import fetch_alpaca_data

symbol = 'AMD'
start_date = '2018-01-01'
end_date = '2025-01-01'

rsi_window = 5

daily_data = fetch_alpaca_data(symbol, '1D', start_date, end_date)

#fig = px.line(daily_data, y='Close', x='Caldt')
#fig.show()

daily_data = RSI(daily_data, rsi_window)
daily_data = daily_data.dropna()

# fig = px.histogram(daily_data, x='RSI_5')
# fig.show()

alpha = 0.2

quantile_down = np.quantile(daily_data[f'RSI_{rsi_window}'], alpha/2)
quantile_up   = np.quantile(daily_data[f'RSI_{rsi_window}'], 1 - alpha/2)

