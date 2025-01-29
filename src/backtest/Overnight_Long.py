"""
We buy at close on day t and sell at open on day t+1
"""
import pandas as pd
import numpy as np
from src.data.Alpaca import fetch_alpaca_data
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"


class OvernightLongBacktest:
    def __init__(self, df: pd.DataFrame, initial_capital: float = 10000, risk_free_rate: float = 0.03):
        self.data = df
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
        self.portfolio_values = []
        self.cash_values = []
        self.stock_values = []
        self.daily_returns = []
        self.benchmark_values = []
        self.benchmark_returns = []
        self.backtest_results = self.compute_backtest()

    def compute_sharpe_ratio(self, returns):
        """
        Calculate the Sharpe Ratio of the portfolio.
        """
        excess_returns = [d - (self.risk_free_rate / 252) for d in returns]
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return sharpe_ratio

    def plot_portfolio(self):
        """
        Plot portfolio value, cash, and stock position over time using Plotly.
        """
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.data["Caldt"], y=self.portfolio_values, mode='lines', name='Portfolio Value'))
        fig.add_trace(go.Scatter(x=self.data["Caldt"], y=self.cash_values, mode='lines', name='Cash'))
        fig.add_trace(go.Scatter(x=self.data["Caldt"], y=self.stock_values, mode='lines', name='Stock Value'))
        fig.add_trace(go.Scatter(x=self.data["Caldt"], y=self.benchmark_values, mode='lines', name='Buy & Hold Benchmark'))

        fig.update_layout(
            title='Overnight Long Strategy Performance',
            xaxis_title='Date',
            yaxis_title='Value ($)',
            legend_title='Legend'
        )
        return fig

    def compute_backtest(self):
        """
        Run the backtest for the overnight long strategy.
        """
        cash = self.initial_capital
        position = 0

        # Buy & Hold benchmark
        benchmark_position = self.initial_capital / self.data['Close'].iloc[0]

        for i in range(len(self.data)):
            if i == len(self.data) - 1:
                self.portfolio_values.append(self.portfolio_values[-1])
                self.cash_values.append(self.cash_values[-1])
                self.stock_values.append(self.stock_values[-1])
                self.benchmark_values.append(benchmark_position * self.data['Close'].iloc[i])
                break

            close_price = self.data['Close'].iloc[i]
            next_open_price = self.data['Open'].iloc[i + 1]

            # Buy at close price
            position = cash / close_price
            cash = 0

            # Sell at next day's open price
            proceeds = position * next_open_price
            cash = proceeds
            position = 0

            portfolio_value = cash
            self.portfolio_values.append(portfolio_value)
            self.cash_values.append(cash)
            self.stock_values.append(position)

            # Benchmark tracking
            benchmark_value = benchmark_position * self.data['Close'].iloc[i]
            self.benchmark_values.append(benchmark_value)

            # Calculate daily returns
            if i > 0:
                daily_return = (portfolio_value - self.portfolio_values[-2]) / self.portfolio_values[-2]
                benchmark_return = (benchmark_value - self.benchmark_values[-2]) / self.benchmark_values[-2]
                self.daily_returns.append(daily_return)
                self.benchmark_returns.append(benchmark_return)

        final_value = self.portfolio_values[-1]
        profit = final_value - self.initial_capital
        return_rate = (profit / self.initial_capital) * 100
        sharpe_ratio = self.compute_sharpe_ratio(self.daily_returns)

        benchmark_final_value = self.benchmark_values[-1]
        benchmark_profit = benchmark_final_value - self.initial_capital
        benchmark_return = (benchmark_profit / self.initial_capital) * 100
        benchmark_sharpe = self.compute_sharpe_ratio(self.benchmark_returns)

        print(f"Final Portfolio Value: ${final_value:.2f}")
        print(f"Total Profit: ${profit:.2f}")
        print(f"Return: {return_rate:.2f}%")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"\nBenchmark Performance:")
        print(f"Final Buy & Hold Value: ${benchmark_final_value:.2f}")
        print(f"Total Profit: ${benchmark_profit:.2f}")
        print(f"Return: {benchmark_return:.2f}%")
        print(f"Benchmark Sharpe Ratio: {benchmark_sharpe:.2f}")

        self.data['Portfolio_Value'] = self.portfolio_values
        self.data['Cash'] = self.cash_values
        self.data['Stock_Value'] = self.stock_values
        self.data['Benchmark_Value'] = self.benchmark_values

        return self.data

if __name__ == "__main__":
    frequency = "1D"
    ticker = "TSLA"
    start_date = "2017-01-01"
    end_date = "2025-01-01"

    # Fetch historical data
    df = fetch_alpaca_data(ticker, '1D', start_date, end_date)
    backtester = OvernightLongBacktest(df)
    fig = backtester.plot_portfolio()
    fig.show()
