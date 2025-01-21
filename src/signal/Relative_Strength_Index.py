"""
https://trendspider.com/learning-center/rsi-trading-strategies/
"""

import pandas as pd
from src.technicalanalysis.technicalanalysis import RSI, SMA, EMA


def rsi_signal(
        dataframe: pd.DataFrame,
        window: int = 14,
        rsi_sell_threshold: float = 70.0,
        rsi_buy_threshold: float = 30.0,
        rsi_signal_line_ma: str = "SMA",
        rsi_signal_line_window: int = 14,
):
    """
    Generate RSI divergence signals based on the given thresholds and moving average type.

    Parameters:
        dataframe: pd.DataFrame
            Input data containing price information.
        window: int
            Window size for RSI calculation.
        rsi_sell_threshold: float
            RSI value above which sell signals are considered.
        rsi_buy_threshold: float
            RSI value below which buy signals are considered.
        rsi_signal_line_ma: str
            Type of moving average for smoothing RSI ("SMA" or "EMA").
        rsi_signal_line_window: int
            Window size for smoothing the RSI values.

    Returns:
        pd.DataFrame
            DataFrame with buy/sell/hold signals based on RSI divergence.
    """
    # Calculate RSI
    dataframe = RSI(dataframe=dataframe, window=window)

    # Smooth RSI if needed
    rsi_column = f"RSI_{window}"
    if rsi_signal_line_ma == "SMA":
        dataframe = SMA(dataframe=dataframe, window=rsi_signal_line_window, columns=[rsi_column])
    elif rsi_signal_line_ma == "EMA":
        dataframe = EMA(dataframe=dataframe, window=rsi_signal_line_window, columns=[rsi_column])

    smoothed_rsi_col = f"{rsi_signal_line_ma}_{rsi_signal_line_window}_{rsi_column}"

    # Identify divergences and generate signals
    signals = []
    for i in range(1, len(dataframe)):
        prev_price = dataframe['Close'].iloc[i - 1]
        curr_price = dataframe['Close'].iloc[i]
        # prev_rsi = dataframe[smoothed_rsi_col].iloc[i - 1]
        # curr_rsi = dataframe[smoothed_rsi_col].iloc[i]
        prev_rsi = dataframe[rsi_column].iloc[i - 1]
        curr_rsi = dataframe[rsi_column].iloc[i]

        # Bullish divergence: price lower lows, RSI higher lows
        if curr_price < prev_price and curr_rsi > prev_rsi and curr_rsi < rsi_buy_threshold:
            signals.append("Buy")
        # Bearish divergence: price higher highs, RSI lower highs
        elif curr_price > prev_price and curr_rsi < prev_rsi and curr_rsi > rsi_sell_threshold:
            signals.append("Sell")
        else:
            signals.append("Hold")

    # Align signals with the DataFrame
    signals.insert(0, "Hold")  # First entry has no divergence
    dataframe['Signal'] = signals

    return dataframe

if __name__=="__main__":
    df = pd.DataFrame({
        'Close': [100, 102, 101, 103, 104, 106, 105, 107, 109, 108, 110]
    })
    df_with_signals = rsi_signal(df, window=14, rsi_sell_threshold=70, rsi_buy_threshold=30)
    print(df_with_signals[['Close', 'RSI_14', 'Signal']])
