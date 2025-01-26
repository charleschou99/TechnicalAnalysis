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

def backtest_rsi_distrib_strategy(ticker: str, start_date: str, end_date: str, initial_capital: float = 10000,
                                   alpha: float = 0.2, window: int = 14, lag: int = 1,
                                   fees_type: str = "-", fees_amount: float = 0):
    """
    Backtest the RSI distribution-based strategy with lag and brokerage fees.

    Parameters:
        ticker: str
            Stock ticker to backtest.
        start_date: str
            Start date for historical data.
        end_date: str
            End date for historical data.
        initial_capital: float
            Starting capital for the backtest.
        alpha: float
            Quantile value for defining upper and lower thresholds.
        window: int
            RSI window size.
        lag: int
            Number of days to wait before executing the signal.
        fees_type: str
            "-" for flat fees or "%" for proportional fees.
        fees_amount: float
            Fee amount based on the fees_type.

    Returns:
        pd.DataFrame
            DataFrame containing portfolio performance.
    """

    # Fetch historical data
    df = fetch_alpaca_data(ticker, '1D', start_date, end_date)

    # Apply the RSI distribution strategy
    df = RSI_distrib(df, alpha=alpha, window=window, lag=lag)

    # Initialize backtest variables
    cash = initial_capital
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
        close_price = df['Close'].iloc[i]

        if df['Execute'].iloc[i] == 'Open':
            next_open_price = df['Open'].iloc[i]

        elif df['Execute'].iloc[i] == 'Close':
            next_open_price = df['Close'].iloc[i]

        else:
            next_open_price = None

        # Buy signal
        if signal == "Buy" and cash > 0 and next_open_price:
            fee = calculate_fees(cash)
            effective_cash = cash - fee
            position = effective_cash / next_open_price
            cash = 0

        # Sell signal
        elif signal == "Sell" and position > 0 and next_open_price:
            proceeds = position * next_open_price
            fee = calculate_fees(proceeds)
            cash = proceeds - fee
            position = 0

        # Portfolio value tracking
        stock_value = position * close_price
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
    df = backtest_rsi_distrib_strategy(ticker="AMD", start_date="2022-11-01", end_date="2025-01-01",
                                       alpha=0.1, window=5, lag=1, fees_type="%", fees_amount=0.05)
    fig = plot_portfolio(df)
    fig.show()
