import pandas as pd
import numpy as np
import plotly.graph_objects as go

class BacktestSingleStock:

    def __init__(self, df: pd.DataFrame = None, risk_free_rate: float = 0.03, frequency: str = "daily"):
        self.data = df
        self.risk_free_rate = risk_free_rate
        self.frequency = frequency
        self.portfolio_values = []
        self.cash_values = []
        self.stock_values = []
        self.daily_returns = []

    def compute_sharpe_ratio(self):
        """
        Calculate the Sharpe Ratio of the portfolio.
        """
        frequency_mapping = {
            '1min': 252 * 6.5 * 60,  # Assuming 6.5 hours of trading per day
            '5min': 252 * 6.5 * 12,  # Assuming 6.5 hours of trading per day
            '15min': 252 * 26,      # 26 intervals per day
            '1H': 252 * 6.5,        # 6.5 trading hours per day
            '1D': 252,               # 252 trading days per year
            '1W': 52,                # 52 weeks per year
            '1Y': 1
        }
        annualization_factor = frequency_mapping.get(self.frequency, 252)
        excess_returns = [d - (self.risk_free_rate / annualization_factor) for d in self.daily_returns]
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(annualization_factor)
        return sharpe_ratio

    def plot_portfolio(self):
        """
        Plot portfolio value, cash, and stock position over time using Plotly.
        """
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.data.index, y=self.portfolio_values, mode='lines', name='Portfolio Value'))
        fig.add_trace(go.Scatter(x=self.data.index, y=self.cash_values, mode='lines', name='Cash'))
        fig.add_trace(go.Scatter(x=self.data.index, y=self.stock_values, mode='lines', name='Stock Value'))

        fig.update_layout(
            title='Portfolio Performance Over Time',
            xaxis_title='Date',
            yaxis_title='Value ($)',
            legend_title='Legend'
        )
        return fig

    def compute_backtest(self, initial_capital: float = 10000, leverage: float = 1.0, fees_type: str = "-", fees_amount: float = 0):
        """
        Run the backtest based on the signal data provided.
        """
        cash = initial_capital
        max_cash_available = leverage * initial_capital
        max_short_position = leverage * initial_capital
        position = 0

        for i in range(len(self.data)):
            signal = self.data['Signal'].iloc[i]
            execute_price = self.data['Execute'].iloc[i]
            quantity = self.data['Quantity'].iloc[i]
            low = self.data['Low'].iloc[i]
            high = self.data['High'].iloc[i]

            if execute_price is not None:
                if (execute_price >= low) and (execute_price <= high):
                    trade_value = quantity * initial_capital

                    if signal == "Sell" and position > 0:
                        proceeds = position * execute_price
                        fee = fees_amount if fees_type == "-" else proceeds * fees_amount
                        cash += proceeds - fee
                        position = 0
                        max_cash_available = leverage * cash
                        max_short_position = leverage * cash

                    elif signal == "Buy" and position < 0:
                        proceeds = -position * execute_price
                        fee = fees_amount if fees_type == "-" else proceeds * fees_amount
                        cash -= proceeds + fee
                        position = 0
                        max_cash_available = leverage * cash
                        max_short_position = leverage * cash

                    elif signal == "Buy" and cash - trade_value >= max_cash_available:
                        fee = fees_amount if fees_type == "-" else trade_value * fees_amount
                        cash -= (trade_value + fee)
                        position += trade_value / execute_price

                    elif signal == "Sell" and cash - trade_value <= max_short_position:
                        fee = fees_amount if fees_type == "-" else trade_value * fees_amount
                        cash += (trade_value - fee)
                        position -= trade_value / execute_price

            stock_value = position * self.data['Close'].iloc[i] if position != 0 else 0
            portfolio_value = cash + stock_value

            self.portfolio_values.append(portfolio_value)
            self.cash_values.append(cash)
            self.stock_values.append(stock_value)

            if i > 0:
                daily_return = (portfolio_value - self.portfolio_values[-2]) / self.portfolio_values[-2]
                self.daily_returns.append(daily_return)

        final_value = self.portfolio_values[-1]
        profit = final_value - initial_capital
        return_rate = (profit / initial_capital) * 100
        sharpe_ratio = self.compute_sharpe_ratio()

        print(f"Final Portfolio Value: ${final_value:.2f}")
        print(f"Total Profit: ${profit:.2f}")
        print(f"Return: {return_rate:.2f}%")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

        self.data['Portfolio_Value'] = self.portfolio_values
        self.data['Cash'] = self.cash_values
        self.data['Stock_Value'] = self.stock_values
