"""
Short Term Trading Strategies That Work
"""

import pandas as pd
import numpy as np
from src.technicalanalysis.technicalanalysis import RSI, SMA


def rsi_sma_signal(dataframe: pd.DataFrame):
    """
    Generate a trading signal based on the following conditions:
    - Buy when the stock is above its 200-day moving average AND the 2-period RSI is below 5.
    - Exit when the stock closes above its 5-period moving average.

    Parameters:
        dataframe: pd.DataFrame
            Input data containing price information.

    Returns:
        pd.DataFrame
            DataFrame with buy/sell/hold signals and quantities based on conditions.
    """
    # Compute moving averages
    dataframe = SMA(dataframe, window=200, columns=['Close'])
    dataframe = SMA(dataframe, window=5, columns=['Close'])

    # Compute RSI (2-period)
    dataframe = RSI(dataframe, window=2)

    signals = ["Hold"] * len(dataframe)
    execute_prices = [None] * len(dataframe)
    quantities = [0] * len(dataframe)
    position = 0  # Track whether we are in a trade

    for i in range(200, len(dataframe) - 1):
        close_price = dataframe['Close'].iloc[i]
        sma_200 = dataframe[f'SMA_200_Close'].iloc[i]
        sma_5 = dataframe[f'SMA_5_Close'].iloc[i]
        rsi_2 = dataframe[f'RSI_2'].iloc[i]

        if position == 0 and close_price > sma_200 and rsi_2 < 5:
            signals[i] = "Buy"
            execute_prices[i] = close_price
            quantities[i] = 1  # Always buy full position
            position = 1
        elif position > 0 and close_price > sma_5:
            signals[i] = "Sell"
            execute_prices[i] = close_price
            quantities[i] = -1  # Always sell full position
            position = 0
        else:
            signals[i] = "Hold"
            execute_prices[i] = None
            quantities[i] = 0

    dataframe['Signal'] = signals
    dataframe['Execute'] = execute_prices
    dataframe['Quantity'] = quantities

    return dataframe
