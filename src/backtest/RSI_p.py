import pandas as pd
import numpy as np
from src.data.Alpaca import fetch_alpaca_data
from src.signal.RSI_p import RSI_distrib
import plotly.graph_objects as go

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    """
    Calculate the Sharpe Ratio of the portfolio.
    """
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
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
                                                       leverage: float = 1.0, alpha: float = 0.2, window: int = 14, lag: int = 1,
                                                       rsi_exit_up: float = 65.0, rsi_exit_down: float = 35.0, fees_type: str = "-", fees_amount: float = 0):
    """
    Backtest the RSI distribution-based strategy using Alpaca with leverage, short selling, and brokerage fees.

    Parameters:
        ticker: str
            Stock ticker to backtest.
        start_date: str
            Start date for historical data.
        end_date: str
            End date for historical data.
        initial_capital: float
            Starting capital for the backtest.
        leverage: float
            Maximum leverage allowed (e.g., leverage=2 allows 2x initial capital).
        alpha: float
            Quantile value for defining upper and lower thresholds.
        window: int
            RSI window size.
        lag: int
            Number of days to wait before executing the signal.
        rsi_exit: float
            RSI value at which to clear the position.
        fees_type: str
            "-" for flat fees or "%" for proportional fees.
        fees_amount: float
            Fee amount based on the fees_type.

    Returns:
        pd.DataFrame
            DataFrame containing portfolio performance.
    """
    # Fetch historical data
    df = fetch_alpaca_data(ticker, '1min', start_date, end_date)

    # Apply the RSI distribution strategy
    df = RSI_distrib(df, alpha=alpha, window=window, lag=lag, rsi_exit_up=rsi_exit_up, rsi_exit_down=rsi_exit_down)

    # Initialize backtest variables
    cash = initial_capital
    max_cash_available = leverage * initial_capital
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

        if execute_price is not None:
            trade_value = quantity * portfolio_values[-1] if portfolio_values else quantity * initial_capital

            if signal == "Buy" and trade_value <= (max_cash_available - cash):
                # Open a long position
                fee = calculate_fees(trade_value)
                cash -= (trade_value + fee)
                position += trade_value / execute_price

            elif signal == "Sell" and trade_value <= (max_cash_available - cash):
                # Open a short position
                fee = calculate_fees(trade_value)
                cash += (trade_value - fee)
                position -= trade_value / execute_price

            elif signal == "Close Buy" and position > 0:
                # Close a long position
                proceeds = position * execute_price
                fee = calculate_fees(proceeds)
                cash += proceeds - fee
                position = 0

            elif signal == "Close Sell" and position < 0:
                # Close a short position
                proceeds = -position * execute_price
                fee = calculate_fees(proceeds)
                cash -= proceeds + fee
                position = 0

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
    sharpe_ratio = calculate_sharpe_ratio(pd.Series(daily_returns))

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

    # Backtest on AMD for the past year
    df = backtest_rsi_distrib_strategy_with_leverage_alpaca(ticker="AMD", start_date="2024-01-01", end_date="2025-01-01",
                                                            initial_capital=10000, leverage=2, alpha=0.4, window=5, lag=1,
                                                            rsi_exit_up=70, rsi_exit_down=30, fees_type="%", fees_amount=0.005)
    fig = plot_portfolio(df)
    fig.show()