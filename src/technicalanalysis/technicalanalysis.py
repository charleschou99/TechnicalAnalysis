"""
Functions to transform time series of OHLCV
"""
import pandas as pd
import numpy as np

def SMA(dataframe:pd.DataFrame=None, window:int=14, columns:list=None):
    """
    Simple moving average
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window, number of rows given the dataframe
    columns list[str]: list of column names to compute sma
    """
    for col in columns:
        dataframe[f"SMA_{window}_{col}"] = dataframe[col].rolling(window).mean()
    return dataframe

def SME(dataframe:pd.DataFrame=None, window:int=14, columns:list=None):
    """
    Simple moving median
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window, number of rows given the dataframe
    columns list[str]: list of column names to compute sme
    """
    for col in columns:
        dataframe[f"SME_{window}_{col}"] = dataframe[col].rolling(window).median()
    return dataframe

def EMA(dataframe:pd.DataFrame=None, window:int=14, columns:list=None,
        com=None, span=None, halflife=None, alpha=None, min_periods=0, adjust=True, ignore_na=False, times=None):
    """
    Exponential moving average
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window, number of rows given the dataframe
    columns list[str]: list of column names to compute ema
    arguments of dataframe.ewm : https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html
    """
    if window is not None:
        span = window
    for col in columns:
        # default span
        dataframe[f"EMA_{window}_{col}"] = dataframe[col].ewm(com=com, span=span, halflife=halflife, alpha=alpha,
        min_periods=min_periods, adjust=False, ignore_na=ignore_na, times=times).mean()
    return dataframe

def volume_moving_average(dataframe: pd.DataFrame, window: int = 14):
    """
    Calculate the moving average of trading volume.
    """
    dataframe['Volume_MA'] = dataframe['Volume'].rolling(window=window).mean()
    return dataframe

def realised_volatility(dataframe: pd.DataFrame, window: int = 14, model: str = "CloseToClose"):
    """
    Rolling realised volatility
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window
    model str: formula used for the realised volatility ('CloseToClose', 'Parkinson', 'GarmanKlass', 'RogersSatchell', 'YangZhang')
    """
    if model == "CloseToClose":
        dataframe['Log_Returns'] = np.log(dataframe['Close'] / dataframe['Close'].shift(1))
        dataframe['Realised_Volatility'] = dataframe['Log_Returns'].rolling(window=window).std() * np.sqrt(window)
    elif model == "Parkinson":
        dataframe['Range'] = np.log(dataframe['High'] / dataframe['Low'])
        dataframe['Realised_Volatility'] = dataframe['Range'].rolling(window=window).apply(lambda x: np.sqrt((x**2).mean() / (4 * np.log(2))))
    elif model == "GarmanKlass":
        dataframe['GK'] = 0.5 * (np.log(dataframe['High'] / dataframe['Low'])**2) - (2 * np.log(2) - 1) * (np.log(dataframe['Close'] / dataframe['Open'])**2)
        dataframe['Realised_Volatility'] = dataframe['GK'].rolling(window=window).sum() ** 0.5
    elif model == "RogersSatchell":
        dataframe['RS'] = (np.log(dataframe['High'] / dataframe['Close']) * np.log(dataframe['High'] / dataframe['Open'])) + \
                           (np.log(dataframe['Low'] / dataframe['Close']) * np.log(dataframe['Low'] / dataframe['Open']))
        dataframe['Realised_Volatility'] = dataframe['RS'].rolling(window=window).sum() ** 0.5
    elif model == "YangZhang":
        dataframe['Open_Close'] = np.log(dataframe['Open'] / dataframe['Close'].shift(1))
        dataframe['Close_Close'] = np.log(dataframe['Close'] / dataframe['Close'].shift(1))
        dataframe['RS'] = (np.log(dataframe['High'] / dataframe['Close']) * np.log(dataframe['High'] / dataframe['Open'])) + \
                           (np.log(dataframe['Low'] / dataframe['Close']) * np.log(dataframe['Low'] / dataframe['Open']))
        k = 0.34 / (1.34 + (window + 1)/(window - 1))
        dataframe['YZ'] = (1 - k) * dataframe['Open_Close'].rolling(window=window).var() + \
                          k * dataframe['RS'].rolling(window=window).mean() + \
                          dataframe['Close_Close'].rolling(window=window).var()
        dataframe['Realised_Volatility'] = np.sqrt(dataframe['YZ'])
    return dataframe

def RSI(dataframe: pd.DataFrame, window: int = 14):
    """
    Relative strength index
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window
    """
    delta = dataframe['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=window).mean()
    avg_loss = pd.Series(loss).rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi.index = dataframe.index
    dataframe[f'RSI_{window}'] = rsi
    return dataframe

def Bollinger_Bands(dataframe: pd.DataFrame, window: int = 14, volatility_model: str = "CloseToClose"):
    """
    Bollinger Bands with selectable volatility model
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window
    volatility_model str: model used for volatility calculation ('CloseToClose', 'Parkinson', 'GarmanKlass', 'RogersSatchell', 'YangZhang')
    """
    dataframe = realised_volatility(dataframe, window=window, model=volatility_model)
    dataframe['SMA'] = dataframe['Close'].rolling(window=window).mean()
    dataframe['Upper_Band'] = dataframe['SMA'] + (2 * dataframe['Realised_Volatility'])
    dataframe['Lower_Band'] = dataframe['SMA'] - (2 * dataframe['Realised_Volatility'])
    return dataframe

def MACD(dataframe: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9):
    """
    Moving Average Convergence Divergence
    dataframe pd.DataFrame: source of data
    short_window int: period for the short-term EMA
    long_window int: period for the long-term EMA
    signal_window int: period for the signal line
    """
    dataframe['EMA_short'] = dataframe['Close'].ewm(span=short_window, adjust=False).mean()
    dataframe['EMA_long'] = dataframe['Close'].ewm(span=long_window, adjust=False).mean()
    dataframe['MACD'] = dataframe['EMA_short'] - dataframe['EMA_long']
    dataframe['Signal_Line'] = dataframe['MACD'].ewm(span=signal_window, adjust=False).mean()
    return dataframe

def ATR(dataframe: pd.DataFrame, window: int = 14):
    """
    Average True Range
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window
    """
    dataframe['TR'] = np.maximum((dataframe['High'] - dataframe['Low']),
                                 np.maximum(abs(dataframe['High'] - dataframe['Close'].shift(1)),
                                            abs(dataframe['Low'] - dataframe['Close'].shift(1))))
    dataframe['ATR'] = dataframe['TR'].rolling(window=window).mean()
    return dataframe

def Stochastic_Oscillator(dataframe: pd.DataFrame, window: int = 14):
    """
    Stochastic Oscillator
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window
    """
    dataframe['Lowest_Low'] = dataframe['Low'].rolling(window=window).min()
    dataframe['Highest_High'] = dataframe['High'].rolling(window=window).max()
    dataframe['%K'] = 100 * ((dataframe['Close'] - dataframe['Lowest_Low']) / (dataframe['Highest_High'] - dataframe['Lowest_Low']))
    dataframe['%D'] = dataframe['%K'].rolling(window=3).mean()
    return dataframe

def fibonacci_retracement(high: float, low: float):
    """
    Calculate Fibonacci retracement levels based on a given high and low.

    high float: Highest price point
    low float: Lowest price point
    """
    diff = high - low
    levels = {
        '0.0%': high,
        '23.6%': high - 0.236 * diff,
        '38.2%': high - 0.382 * diff,
        '50.0%': high - 0.5 * diff,
        '61.8%': high - 0.618 * diff,
        '78.6%': high - 0.786 * diff,
        '100.0%': low
    }
    return levels