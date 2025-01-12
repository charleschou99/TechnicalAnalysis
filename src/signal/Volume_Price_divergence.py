"""
@EXAMPLE
"""


from src.technicalanalysis.technicalanalysis import volume_moving_average
import pandas as pd


def price_volume_divergence_signal(dataframe: pd.DataFrame, window: int = 14):
    dataframe = volume_moving_average(dataframe, window)
    signals = []

    for i in range(1, len(dataframe)):
        price_change = dataframe['Close'].iloc[i] - dataframe['Close'].iloc[i - 1]
        volume_change = dataframe['Volume_MA'].iloc[i] - dataframe['Volume_MA'].iloc[i - 1]

        if price_change > 0 and volume_change < 0:
            signals.append("Sell")
        elif price_change < 0 and volume_change > 0:
            signals.append("Buy")
        else:
            signals.append("Hold")

    signals.insert(0, "Hold")
    dataframe['Signal'] = signals
    return dataframe

    signals.insert(0, "Hold")  # Align with DataFrame index
    dataframe['Signal'] = signals
    return dataframe


if __name__ == "__main__":
    # Example DataFrame
    example_data = {
        'Close': [100, 102, 101, 103, 104, 106, 105, 107, 109, 108, 110],
        'Volume': [1000, 950, 1100, 1050, 1000, 1200, 1150, 1300, 1250, 1400, 1350]
    }

    df = pd.DataFrame(example_data)

    # Apply the divergence signal detection
    df_with_signals = price_volume_divergence_signal(df, window=3)
    print(df_with_signals[['Close', 'Volume', 'Volume_MA', 'Signal']])
