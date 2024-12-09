"""
Functions to transform time series of OHLCV
"""
import pandas as pd

def SMA(dataframe:pd.DataFrame=None, window:int=14):
    """
    Simple moving average
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window, number of rows given the dataframe
    """
    dataframe["SMA"] = dataframe['Close'].rolling(window).mean()

def SME(dataframe:pd.DataFrame=None, window:int=14):
    """
    Simple moving median
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window, number of rows given the dataframe
    """
    dataframe["SME"] = dataframe['Close'].rolling(window).meidan()

def EMA(dataframe:pd.DataFrame=None, window:int=14):
    """
    Simple moving average
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window, number of rows given the dataframe
    """
    pass


def realised_volatility(dataframe:pd.DataFrame=None, window:int=14, model:str="CloseToClose"):

    """
    Rolling realised volatility
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window, number of rows given the dataframe
    model str: formula used for the realised volatility
    """


def RSI(dataframe:pd.DataFrame=None, window:int=14):
    """
    Relative strength index
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window, number of rows given the dataframe
    """
    pass

def Bollinger_Bands(dataframe: pd.DataFrame = None, window:int=14):
    """
    Bollinger Bands
    dataframe pd.DataFrame: source of data
    window int: size of the rolling window, number of rows given the dataframe
    """
    pass