"""
Custom signal: get the distribution of RSI, and try to predict the next RSI
"""

import pandas as pd
import numpy as np
from src.technicalanalysis.technicalanalysis import RSI, SMA, EMA

def RSI_distrib(dataframe:pd.DataFrame,
                alpha:float = 0.2,
                window: int = 14,
                lag:int = 1
                ):
    """
    Generate RSI distribution based on the given thresholds and moving average type.

    Parameters:
        dataframe: pd.DataFrame
            Input data containing price information.
        window: int
            Window size for RSI calculation.
        alpha: float
            quantile, between 0 and 1.
        lag: int
            number of days to lag to execute the order after the signal.

    Returns:
        pd.DataFrame
            DataFrame with buy/sell/hold signals based on RSI divergence.
    """
    # Calculate RSI
    dataframe = RSI(dataframe=dataframe, window=window)

    # Calculate quantiles
    quantile_down = np.quantile(dataframe[f'RSI_{window}'].dropna(), alpha / 2)
    quantile_up = np.quantile(dataframe[f'RSI_{window}'].dropna(), 1 - alpha / 2)

    signals = [("Hold", None) for i in range(lag)]
    for i in range(len(dataframe) - lag):
        current_rsi = dataframe[f'RSI_{window}'].iloc[i]
        next_open = 'Close' if i + 1 < len(dataframe) else np.nan

        if current_rsi < quantile_down:
            signals.append(("Sell", next_open))
        elif current_rsi > quantile_up:
            signals.append(("Buy", next_open))
        else:
            signals.append(("Hold", None))

    # Extract only signal types for dataframe
    dataframe['Signal'] = [signal[0] for signal in signals]
    dataframe['Execute'] = [signal[1] for signal in signals]

    return dataframe
