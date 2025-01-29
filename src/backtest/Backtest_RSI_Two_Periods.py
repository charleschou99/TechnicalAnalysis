import pandas as pd
from src.signal.RSI_Two_Periods import rsi_sma_signal
from src.backtest.Backtest_class import BacktestSingleStock
from src.data.Alpaca import fetch_alpaca_data
import plotly.io as pio
pio.renderers.default = "browser"

def backtest_rsi_sma_strategy(df: pd.DataFrame, initial_capital: float = 10000, leverage: float = 1.0,
                              fees_type: str = "%", fees_amount: float = 0.005, frequency: str = "1D"):
    """
    Backtest the RSI and SMA-based trading strategy using the BacktestSingleStock class.

    Parameters:
        df: pd.DataFrame
            Stock data containing OHLC prices.
        initial_capital: float
            Starting capital for the backtest.
        leverage: float
            Maximum leverage allowed.
        fees_type: str
            "-" for flat fees or "%" for proportional fees.
        fees_amount: float
            Fee amount based on the fees_type.
        frequency: str
            Frequency of data used (e.g., "daily", "1H", "15min").

    Returns:
        pd.DataFrame
            DataFrame containing portfolio performance metrics.
    """
    # Apply the RSI & SMA strategy to generate buy/sell signals
    df = rsi_sma_signal(df)

    # Run the backtest using BacktestSingleStock class
    backtest = BacktestSingleStock(df, risk_free_rate=0.03, frequency=frequency)
    backtest.compute_backtest(initial_capital=initial_capital, leverage=leverage,
                                        fees_type=fees_type, fees_amount=fees_amount)

    # Plot the results
    fig = backtest.plot_portfolio()
    fig.show()

    return backtest

# Example usage:
# df = fetch_alpaca_data("SPY", "1D", "2020-01-01", "2023-01-01")
# backtest_rsi_sma_strategy(df, initial_capital=10000, leverage=1.5, fees_type="%", fees_amount=0.001)

if __name__ == "__main__":

    df = fetch_alpaca_data("SPY", "1D", "2020-01-01", "2025-01-01")
    backtest_rsi_sma_strategy(df, initial_capital=10000, leverage=1.5, fees_type="%", fees_amount=0.005)