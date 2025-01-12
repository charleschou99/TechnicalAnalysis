# Technical Analysis Project

A Python-based project for performing technical analysis on financial data. This project includes various indicators and strategies, along with backtesting capabilities.

## Features

- **Volume-Price Divergence Signal**
- **Bollinger Bands, ATR, Stochastic Oscillator**
- **Fibonacci Retracement Levels**
- **Sharpe Ratio Calculation**
- **Portfolio Performance Visualization with Plotly**

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/charleschou99/TechnicalAnalysis.git
   cd TechnicalAnalysis
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   
## Usage

### 1. Backtest a Trading Strategy

Run the `backtest_volume_signal.py` script to backtest the volume-price divergence strategy on a stock (e.g., AMD):

```bash
python backtest_volume_signal.py
```

**Example Output:**
```
Final Portfolio Value: $12,345.67
Total Profit: $2,345.67
Return: 23.46%
Sharpe Ratio: 1.45
```

### 2. Customize Backtest Parameters

You can modify the ticker, time range, and initial capital in `backtest_strategy`:

```python
backtest_strategy(ticker="AMD", start_date="2022-11-01", end_date="2023-11-01", initial_capital=10000)
```

### 3. Visualize Portfolio Performance

After running the backtest, a Plotly graph will appear, showing:

- **Portfolio Value** over time
- **Cash Balance**
- **Stock Holdings Value**

## Project Structure

```

├── dataGetter                  # Data retrieval from Yahoo Finance (v0)
├── signal                      # Signal generation scripts
├── backtest                    # Backtest and example script
├── tests                       # Example script for base functions
├── requirements.txt            # Python package dependencies
├── README.md                   # Project documentation
```

## Dependencies

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.

---

Feel free to contribute, report issues, or suggest improvements!
