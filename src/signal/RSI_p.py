"""
Custom signal: get the distribution of RSI, and try to predict the next RSI
"""

import pandas as pd
import numpy as np
from src.technicalanalysis.technicalanalysis import RSI, SMA, EMA, Bollinger_Bands
from src.technicalanalysis.target import inverse_RSI

def RSI_distrib(dataframe: pd.DataFrame,
                alpha: float = 0.2,
                window: int = 14,
                lag: int = 1,
                rsi_exit_up: float = 65.0,
                rsi_exit_down: float = 35.0):
    """
    Generate RSI distribution based on the given thresholds and moving average type.

    Parameters:
        dataframe: pd.DataFrame
            Input data containing price information.
        window: int
            Window size for RSI calculation.
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

    # Calculate quantiles
    quantile_down = np.quantile(dataframe[f'RSI_{window}'].dropna(), alpha / 2)
    quantile_up = np.quantile(dataframe[f'RSI_{window}'].dropna(), 1 - alpha / 2)

    signals = ["Hold"] * lag
    execute_prices = [None] * lag
    quantities = [0] * lag
    position = 0
    next_quantity = 0.1  # Start with 10% of portfolio

    for i in range(lag, len(dataframe)):
        current_rsi = dataframe[f'RSI_{window}'].iloc[i]
        next_open = dataframe['Open'].iloc[i + lag] if i + lag < len(dataframe) else np.nan

        # Check for exit condition
        if position > 0 and current_rsi >= rsi_exit_down:  # Clear long position
            signals.append("Sell")
            execute_prices.append(next_open)
            quantities.append(position)
            position = 0
            next_quantity = 0.1  # Reset to 10%
        elif position < 0 and current_rsi <= rsi_exit_up:  # Clear short position
            signals.append("Buy")
            execute_prices.append(next_open)
            quantities.append(-position)
            position = 0
            next_quantity = 0.1  # Reset to 10%
        else:
            # Entry signals
            if current_rsi < quantile_down:
                signals.append("Buy")
                execute_prices.append(next_open)
                quantities.append(next_quantity)
                position += next_quantity
                next_quantity = 0.3 if next_quantity == 0.1 else 0.1  # Alternate quantities
            elif current_rsi > quantile_up:
                signals.append("Sell")
                execute_prices.append(next_open)
                quantities.append(next_quantity)
                position -= next_quantity
                next_quantity = 0.3 if next_quantity == 0.1 else 0.1  # Alternate quantities
            else:
                signals.append("Hold")
                execute_prices.append(None)
                quantities.append(0)

    # Add signals and quantities to the dataframe
    dataframe['Signal'] = signals
    dataframe['Execute'] = execute_prices
    dataframe['Quantity'] = quantities

    return dataframe

# Example usage
# df = pd.DataFrame({
#     'Open': [100, 102, 103, 101, 105, 107, 109, 108],
#     'Close': [101, 103, 102, 105, 106, 108, 110, 109]
# })
# df_with_signals = RSI_distrib(df, alpha=0.2, window=14, lag=1, rsi_exit=50)
# print(df_with_signals[['Open', 'Close', 'RSI_14', 'Signal', 'Quantity', 'Execute']])
