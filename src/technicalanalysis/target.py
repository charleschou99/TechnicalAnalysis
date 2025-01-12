import pandas as pd
import numpy as np

def inverse_RSI(dataframe: pd.DataFrame, window: int = 14, target_rsi: float = 50):
    """
    Compute the threshold closing price needed to reach a target RSI value.

    dataframe pd.DataFrame: source of data
    window int: size of the rolling window for RSI
    target_rsi float: desired RSI value to achieve
    """
    if 'Close' not in dataframe.columns:
        raise ValueError("DataFrame must contain a 'Close' column.")

    delta = dataframe['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=window).mean().iloc[-1]
    avg_loss = pd.Series(loss).rolling(window=window).mean().iloc[-1]

    if avg_loss == 0:
        return np.nan  # Cannot compute RSI if avg_loss is zero

    target_rs = (100 - target_rsi) / target_rsi
    required_avg_gain = target_rs * avg_loss

    # Calculate the necessary price change to reach the target RSI
    price_change_needed = (required_avg_gain * window) - (avg_gain * (window - 1))
    threshold_price = dataframe['Close'].iloc[-1] + price_change_needed

    return threshold_price


def inverse_Bollinger_Bands(dataframe: pd.DataFrame, window: int = 14, target_band: str = 'upper'):
    """
    Compute the threshold closing price needed to reach the target Bollinger Band.

    target_band str: 'upper' or 'lower'
    """
    sma = dataframe['Close'].rolling(window=window).mean().iloc[-1]
    std = dataframe['Close'].rolling(window=window).std().iloc[-1]

    if target_band == 'upper':
        threshold_price = sma + 2 * std
    elif target_band == 'lower':
        threshold_price = sma - 2 * std
    else:
        raise ValueError("target_band must be either 'upper' or 'lower'")

    return threshold_price


def inverse_ATR(dataframe: pd.DataFrame, window: int = 14):
    """
    Compute the price change needed to match the current ATR value.
    """
    high_low = dataframe['High'] - dataframe['Low']
    high_close = abs(dataframe['High'] - dataframe['Close'].shift(1))
    low_close = abs(dataframe['Low'] - dataframe['Close'].shift(1))

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean().iloc[-1]

    return dataframe['Close'].iloc[-1] + atr


def inverse_Stochastic_Oscillator(dataframe: pd.DataFrame, window: int = 14, target: str = '%K',
                                  target_value: float = 50):
    """
    Compute the price needed to achieve a target %K or %D value in the Stochastic Oscillator.

    target str: '%K' or '%D'
    target_value float: Desired value for %K or %D
    """
    lowest_low = dataframe['Low'].rolling(window=window).min().iloc[-1]
    highest_high = dataframe['High'].rolling(window=window).max().iloc[-1]

    if target == '%K':
        threshold_price = lowest_low + ((target_value / 100) * (highest_high - lowest_low))
    elif target == '%D':
        dataframe['%K'] = 100 * ((dataframe['Close'] - lowest_low) / (highest_high - lowest_low))
        threshold_price = dataframe['%K'].rolling(window=3).mean().iloc[-1]
    else:
        raise ValueError("target must be either '%K' or '%D'")

    return threshold_price
