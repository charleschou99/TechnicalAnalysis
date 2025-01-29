"""
RSI_p with Backtest_class.py
"""

from src.backtest.Backtest_class import BacktestSingleStock
from src.data.Alpaca import fetch_alpaca_data
from src.signal.RSI_p import RSI_distrib

import plotly.io as pio
pio.renderers.default = "browser"

if __name__ == "__main__":
    risk_free_rate = 0.03
    frequency = "1D"
    ticker = "AMD"
    start_date = "2024-01-01"
    end_date = "2025-01-01"
    initial_capital = 10000
    leverage = 2
    alpha = 0.2
    window = 5
    dist_window = 21
    lag = 1
    rsi_exit_up = 70
    rsi_exit_down = 30
    bb_target_std = 2.5
    fees_type = "%"
    fees_amount = 0.005

    # Fetch historical data
    df = fetch_alpaca_data(ticker, '1H', start_date, end_date)
    # Apply the RSI distribution strategy
    df = RSI_distrib(df, alpha=alpha, window=window, dist_window=dist_window, lag=lag, rsi_exit_up=rsi_exit_up, rsi_exit_down=rsi_exit_down, bb_target_std=bb_target_std)

    backtester = BacktestSingleStock(df=df, risk_free_rate=risk_free_rate, frequency=frequency)
    backtester.compute_backtest(initial_capital=initial_capital, leverage=leverage, fees_type=fees_type, fees_amount=fees_amount)

    fig = backtester.plot_portfolio()
    fig.show()

    results = backtester.data