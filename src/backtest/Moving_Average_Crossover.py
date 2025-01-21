from src.data.dataGetter import yfinanceGetter
from src.signal.Moving_Average_Crossover import ma_crossover_signal
import pandas as pd
import numpy as np
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

def backtest_ma_crossover_strategy(ticker: str, start_date: str, end_date: str, initial_capital: float = 10000,
                                    base_line_window: int = 14, signal_line_window: int = 50,
                                    fees_type: str = "-", fees_amount: float = 0):
    """
    Backtest the Moving Average Crossover strategy with brokerage fees.

    Parameters:
        ticker: str
            Stock ticker to backtest.
        start_date: str
            Start date for historical data.
        end_date: str
            End date for historical data.
        initial_capital: float
            Starting capital for the backtest.
        base_line_window: int
            Window for the baseline moving average.
        signal_line_window: int
            Window for the signal line moving average.
        fees_type: str
            "-" for flat fees or "%" for proportional fees.
        fees_amount: float
            Fee amount based on the fees_type.

    Returns:
        pd.DataFrame: DataFrame containing portfolio performance.
    """
    # Initialize data getter
    data_getter = yfinanceGetter()

    # Fetch historical data
    data = data_getter.history(
        tickers=ticker,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=True
    )

    # Extract DataFrame for the specific ticker
    df = data[ticker]

    # Apply the moving average crossover strategy
    df = ma_crossover_signal(df, base_line_window=base_line_window, signal_line_window=signal_line_window)

    # Initialize backtest variables
    cash = initial_capital
    position = 0
    portfolio_values = []
    cash_values = []
    stock_values = []
    daily_returns = []

    for i in range(1, len(df)):
        signal = df['Signal'].iloc[i]
        close_price = df['Close'].iloc[i]

        # Calculate fees
        def calculate_fees(amount):
            if fees_type == "%":
                return np.abs(amount * fees_amount)
            elif fees_type == "-":
                return fees_amount
            else:
                raise ValueError("Invalid fees_type. Use '-' for flat fees or '%' for proportional fees.")

        # Buy signal
        if signal == "Buy" and cash > 0:
            fee = calculate_fees(cash)
            effective_cash = cash - fee
            position = effective_cash / close_price
            cash = 0

        # Sell signal
        elif signal == "Sell" and position > 0:
            proceeds = position * close_price
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
        if i > 1:
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
    df = df.iloc[1:]  # Align with computed values
    df['Portfolio_Value'] = portfolio_values
    df['Cash'] = cash_values
    df['Stock_Value'] = stock_values

    return df

if __name__ == "__main__":
    import plotly.io as pio
    pio.renderers.default = "browser"

    # Backtest on AMD for the past year with brokerage fees
    df = backtest_ma_crossover_strategy(ticker="AMD", start_date="2022-11-01", end_date="2023-11-01",
                                        fees_type="%", fees_amount=0.01)
    fig = plot_portfolio(df)
    fig.show()
