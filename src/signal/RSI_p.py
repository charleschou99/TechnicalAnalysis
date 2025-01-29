"""
Custom signal: RSI signal, BB entry, RSI exit
"""

import pandas as pd
import numpy as np
from src.technicalanalysis.technicalanalysis import RSI, SMA, EMA, Bollinger_Bands
from src.technicalanalysis.target import inverse_RSI, inverse_Bollinger_Bands

def RSI_distrib(dataframe: pd.DataFrame,
                alpha: float = 0.2,
                window: int = 14,
                dist_window: int = 100,
                lag: int = 1,
                rsi_exit_up: float = 65.0,
                rsi_exit_down: float = 35.0,
                bb_target_std: float=2.0):
    """
    Generate RSI distribution based on the given thresholds and integrate Bollinger Bands and inverse RSI.

    Parameters:
        dataframe: pd.DataFrame
            Input data containing price information.
        window: int
            Window size for RSI calculation.
        dist_window: int
            Window size for RSI quantile calculation.
        alpha: float
            Quantile, between 0 and 1.
        lag: int
            Number of days to lag to execute the order after the signal.
        rsi_exit_up: float
            RSI value spread at which to clear the position for sold shares.
        rsi_exit_down: float
            RSI value spread at which to clear the position for bought shares.


    Returns:
        pd.DataFrame
            DataFrame with buy/sell/hold signals and quantities based on RSI divergence.
    """
    # Calculate RSI
    dataframe = RSI(dataframe=dataframe, window=window)
    # Calculate Bollinger Bands
    dataframe = Bollinger_Bands(dataframe, window=window)

    signals = ["Hold"] * (dist_window + lag)
    execute_prices = [None] * (dist_window + lag)
    quantities = [0] * (dist_window + lag)
    position = 0
    next_quantity = 0.1  # Start with 10% of portfolio

    for i in range(dist_window + lag, len(dataframe) - 1):

        # Calculate quantiles
        quantile_down = min(np.quantile(dataframe[f'RSI_{window}'].iloc[i-dist_window:i].dropna(), alpha / 2), 30)
        quantile_up = max(np.quantile(dataframe[f'RSI_{window}'].iloc[i-dist_window:i].dropna(), 1 - alpha / 2), 70)

        current_rsi = dataframe[f'RSI_{window}'].iloc[i]

        # Check for exit condition using inverse RSI
        if position > 0:  # Long position
            exit_price = inverse_RSI(dataframe.iloc[:i+1], window=window, target_rsi=rsi_exit_down)
            signals.append("Sell")
            execute_prices.append(exit_price)
            quantities.append(position)
            position = 0
            next_quantity = 0.1
        elif position < 0:  # Short position
            exit_price = inverse_RSI(dataframe.iloc[:i+1], window=window, target_rsi=rsi_exit_up)
            signals.append("Buy")
            execute_prices.append(exit_price)
            quantities.append(-position)
            position = 0
            next_quantity = 0.1
        else:
            # Entry signals using Bollinger Bands
            if current_rsi < quantile_down:
                entry_price = inverse_Bollinger_Bands(dataframe.iloc[:i+1], window=window, target_band='lower', target_std=bb_target_std)
                signals.append("Buy")
                execute_prices.append(entry_price)
                quantities.append(next_quantity)
                position += next_quantity
                next_quantity = 0.3 if next_quantity == 0.1 else 0.1
            elif current_rsi > quantile_up:
                entry_price = inverse_Bollinger_Bands(dataframe.iloc[:i+1], window=window, target_band='upper', target_std=bb_target_std)
                signals.append("Sell")
                execute_prices.append(entry_price)
                quantities.append(next_quantity)
                position -= next_quantity
                next_quantity = 0.3 if next_quantity == 0.1 else 0.1
            else:
                signals.append("Hold")
                execute_prices.append(None)
                quantities.append(0)

    signals = signals + ["Hold"]
    execute_prices = execute_prices + [None]
    quantities = quantities + [0]

    # Add signals and quantities to the dataframe
    dataframe['Signal'] = signals
    dataframe['Execute'] = execute_prices
    dataframe['Quantity'] = quantities

    return dataframe