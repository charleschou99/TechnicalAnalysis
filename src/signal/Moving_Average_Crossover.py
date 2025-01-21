"""
https://trendspider.com/learning-center/moving-average-crossover-strategies/
"""
import pandas as pd
from src.technicalanalysis.technicalanalysis import EMA, SMA

def ma_crossover_signal(
        dataframe: pd.DataFrame,
        base_line_window: int = 14,
        base_line_ma_type: str = "SMA",
        base_line_column: list[str] = ["Close"],
        signal_line_window: int = 50,
        signal_line_ma_type: str = "SMA",
        signal_line_column: list[str] = ["Close"]
):
    """
    Generate signals based on the moving average crossover strategy.

    Parameters:
        dataframe: pd.DataFrame
            Input data containing price information.
        base_line_window: int
            Window for the baseline moving average.
        base_line_ma_type: str
            Type of moving average for the baseline ("SMA" or "EMA").
        base_line_column: list[str]
            Columns to calculate the baseline moving average on.
        signal_line_window: int
            Window for the signal line moving average.
        signal_line_ma_type: str
            Type of moving average for the signal line ("SMA" or "EMA").
        signal_line_column: list[str]
            Columns to calculate the signal line moving average on.

    Returns:
        pd.DataFrame
            DataFrame with buy/sell signals.
    """
    # Calculate the baseline moving average
    if base_line_ma_type == "SMA":
        dataframe = SMA(dataframe=dataframe, window=base_line_window, columns=base_line_column)
    elif base_line_ma_type == "EMA":
        dataframe = EMA(dataframe=dataframe, window=base_line_window, columns=base_line_column)

    # Calculate the signal line moving average
    if signal_line_ma_type == "SMA":
        dataframe = SMA(dataframe=dataframe, window=signal_line_window, columns=signal_line_column)
    elif signal_line_ma_type == "EMA":
        dataframe = EMA(dataframe=dataframe, window=signal_line_window, columns=signal_line_column)

    # Extract column names for moving averages
    base_line_col = f"{base_line_ma_type}_{base_line_window}_{base_line_column[0]}"
    signal_line_col = f"{signal_line_ma_type}_{signal_line_window}_{signal_line_column[0]}"

    # Generate signals
    signals = []
    for i in range(len(dataframe)):
        if i == 0:
            signals.append("Hold")
        else:
            prev_base = dataframe[base_line_col].iloc[i - 1]
            prev_signal = dataframe[signal_line_col].iloc[i - 1]
            curr_base = dataframe[base_line_col].iloc[i]
            curr_signal = dataframe[signal_line_col].iloc[i]

            if prev_base <= prev_signal and curr_base > curr_signal:
                signals.append("Buy")
            elif prev_base >= prev_signal and curr_base < curr_signal:
                signals.append("Sell")
            else:
                signals.append("Hold")

    dataframe['Signal'] = signals
    return dataframe

# Example usage
if __name__ == "__main__":
    df = pd.DataFrame({
        'Close': [100, 102, 101, 103, 104, 106, 105, 107, 109, 108, 110]
    })
    df_with_signals = ma_crossover_signal(df, base_line_window=14, signal_line_window=50)
    print(df_with_signals[['Close', 'Signal']])
