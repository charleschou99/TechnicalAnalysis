"""
Example without backtester
"""
import pandas as pd
import numpy as np
from src.data.Alpaca import fetch_alpaca_data
from src.signal.RSI_p import RSI_distrib
import plotly.graph_objects as go


def calculate_sharpe_ratio(returns, risk_free_rate=0.01, frequency='daily'):
    """
    Calculate the Sharpe Ratio of the portfolio for different time frequencies.

    Parameters:
        returns (pd.Series): Series of portfolio returns.
        risk_free_rate (float): Annualized risk-free rate.
        frequency (str): Frequency of the data ('minutes', '15minutes', 'hourly', 'daily', 'weekly').

    Returns:
        float: Sharpe ratio
    """
    frequency_mapping = {
        '1min': 252 * 6.5 * 60,  # Assuming 6.5 hours of trading per day
        '5min': 252 * 6.5 * 12,  # Assuming 6.5 hours of trading per day
        '15min': 252 * 26,  # 26 intervals per day
        '1H': 252 * 6.5,  # 6.5 trading hours per day
        '1D': 252,  # 252 trading days per year
        '1W': 52,  # 52 weeks per year
        '1Y': 1,  # 52 weeks per year
    }

    if frequency not in frequency_mapping:
        raise ValueError("Invalid frequency. Choose from 'minutes', '15minutes', 'hourly', 'daily', 'weekly'.")

    annualization_factor = frequency_mapping[frequency]
    excess_returns = returns - (risk_free_rate / annualization_factor)
    sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(annualization_factor)

    return sharpe_ratio


def plot_portfolio(df):
    """
    Plot portfolio value, cash, and stock position over time using Plotly.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df['Portfolio_Value'], mode='lines', name='Portfolio Value'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Cash'], mode='lines', name='Cash'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Stock_Value'], mode='lines', name='Stock Value'))

    fig.update_layout(
        title='Portfolio Performance Over Time',
        xaxis_title='Date',
        yaxis_title='Value ($)',
        legend_title='Legend'
    )

    return fig

def backtest_rsi_distrib_strategy_with_leverage_alpaca(ticker: str, start_date: str, end_date: str, initial_capital: float = 10000,
                                                       leverage: float = 1.0, alpha: float = 0.2, window: int = 14, dist_window: int = 100, lag: int = 1,
                                                       rsi_exit_up: float = 65.0, rsi_exit_down: float = 35.0, bb_target_std: float = 2.0, fees_type: str = "-", fees_amount: float = 0):
    """
    Backtest the RSI distribution-based strategy using Alpaca with leverage, short selling, and brokerage fees.
    """
    # Fetch historical data
    df = fetch_alpaca_data(ticker, '15min', start_date, end_date)

    # Apply the RSI distribution strategy
    df = RSI_distrib(df, alpha=alpha, window=window, dist_window=dist_window, lag=lag, rsi_exit_up=rsi_exit_up, rsi_exit_down=rsi_exit_down, bb_target_std=bb_target_std)

    # Initialize backtest variables
    cash = initial_capital
    max_cash_available = leverage * cash
    max_short_position = leverage * cash
    position = 0
    portfolio_values = []
    cash_values = []
    stock_values = []
    daily_returns = []

    # Calculate fees
    def calculate_fees(amount):
        if fees_type == "%":
            return amount * fees_amount
        elif fees_type == "-":
            return fees_amount
        else:
            raise ValueError("Invalid fees_type. Use '-' for flat fees or '%' for proportional fees.")

    for i in range(len(df)):
        signal = df['Signal'].iloc[i]
        execute_price = df['Execute'].iloc[i]
        quantity = df['Quantity'].iloc[i]
        low = df['Low'].iloc[i]
        high = df['High'].iloc[i]

        if execute_price is not None:
            if (execute_price >= low) and (execute_price <= high):
                trade_value = quantity * initial_capital

                if signal == "Sell" and position > 0:
                    # Close a long position
                    proceeds = position * execute_price
                    fee = calculate_fees(proceeds)
                    cash += proceeds - fee
                    position = 0

                    max_cash_available = leverage * cash
                    max_short_position = leverage * cash


                elif signal == "Buy" and position < 0:
                    # Close a short position
                    proceeds = -position * execute_price
                    fee = calculate_fees(proceeds)
                    cash -= proceeds + fee
                    position = 0

                    max_cash_available = leverage * cash
                    max_short_position = leverage * cash

                elif signal == "Buy" and cash - trade_value >= max_cash_available:
                    # Open a long position
                    fee = calculate_fees(trade_value)
                    cash -= (trade_value + fee)
                    position += trade_value / execute_price

                elif signal == "Sell" and cash - trade_value <= max_short_position:
                    # Open a short position within the leverage limit
                    fee = calculate_fees(trade_value)
                    cash += (trade_value - fee)
                    position -= trade_value / execute_price

        # Portfolio value tracking
        stock_value = position * df['Close'].iloc[i] if position != 0 else 0
        portfolio_value = cash + stock_value

        portfolio_values.append(portfolio_value)
        cash_values.append(cash)
        stock_values.append(stock_value)

        # Calculate daily returns
        if i > 0:
            daily_return = (portfolio_value - portfolio_values[-2]) / portfolio_values[-2]
            daily_returns.append(daily_return)

    # Final portfolio value and Sharpe Ratio
    final_value = portfolio_values[-1]
    profit = final_value - initial_capital
    return_rate = (profit / initial_capital) * 100
    sharpe_ratio = calculate_sharpe_ratio(pd.Series(daily_returns), frequency='15min')

    print(f"Final Portfolio Value: ${final_value:.2f}")
    print(f"Total Profit: ${profit:.2f}")
    print(f"Return: {return_rate:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

    # Update DataFrame with portfolio tracking
    df['Portfolio_Value'] = portfolio_values
    df['Cash'] = cash_values
    df['Stock_Value'] = stock_values

    return df

if __name__ == "__main__":
    import plotly.io as pio
    pio.renderers.default = "browser"

    # Backtest on SPY for the past year
    df = backtest_rsi_distrib_strategy_with_leverage_alpaca(ticker="AMD", start_date="2020-01-01", end_date="2025-01-01",
                                                            initial_capital=10000, leverage=2, alpha=0.2, window=5,
                                                            dist_window=21, lag=1, rsi_exit_up=70, rsi_exit_down=30, bb_target_std=2.5,
                                                            fees_type="%", fees_amount=0.005)
    fig = plot_portfolio(df)
    fig.show()