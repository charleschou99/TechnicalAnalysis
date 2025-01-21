import unittest
import pandas as pd
from src.signal.Volume_Price_divergence import price_volume_divergence_signal
from src.backtest.Volume_Price_divergence import calculate_sharpe_ratio
from src.technicalanalysis.technicalanalysis import fibonacci_retracement
from src.technicalanalysis.target import inverse_Bollinger_Bands, inverse_ATR, inverse_Stochastic_Oscillator

class TestTechnicalAnalysis(unittest.TestCase):

    def setUp(self):
        # Example DataFrame
        self.example_data = pd.DataFrame({
            'Close': [100, 102, 101, 103, 104, 106, 105, 107, 109, 108, 110],
            'High': [101, 103, 102, 104, 105, 107, 106, 108, 110, 109, 111],
            'Low': [99, 101, 100, 102, 103, 105, 104, 106, 108, 107, 109],
            'Volume': [1000, 950, 1100, 1050, 1000, 1200, 1150, 1300, 1250, 1400, 1350]
        })

    def test_volume_price_divergence_signal(self):
        df = price_volume_divergence_signal(self.example_data, window=3)
        self.assertIn('Signal', df.columns)
        self.assertTrue(all(signal in ["Buy", "Sell", "Hold"] for signal in df['Signal']))

    def test_inverse_Bollinger_Bands(self):
        upper_band = inverse_Bollinger_Bands(self.example_data, window=3, target_band='upper')
        lower_band = inverse_Bollinger_Bands(self.example_data, window=3, target_band='lower')
        self.assertGreater(upper_band, lower_band)

    def test_inverse_ATR(self):
        atr_value = inverse_ATR(self.example_data, window=3)
        self.assertIsInstance(atr_value, float)
        self.assertGreater(atr_value, 0)

    def test_inverse_Stochastic_Oscillator(self):
        k_threshold = inverse_Stochastic_Oscillator(self.example_data, window=3, target='%K', target_value=80)
        d_threshold = inverse_Stochastic_Oscillator(self.example_data, window=3, target='%D', target_value=20)
        self.assertIsInstance(k_threshold, float)
        self.assertIsInstance(d_threshold, float)

    def test_fibonacci_retracement(self):
        fib_levels = fibonacci_retracement(high=110, low=100)
        expected_levels = ['0.0%', '23.6%', '38.2%', '50.0%', '61.8%', '78.6%', '100.0%']
        for level in expected_levels:
            self.assertIn(level, fib_levels)

    def test_sharpe_ratio(self):
        dummy_returns = pd.Series([0.01, 0.02, -0.005, 0.015, -0.01])
        sharpe = calculate_sharpe_ratio(dummy_returns)
        self.assertIsInstance(sharpe, float)
        self.assertGreater(sharpe, 0)

def run_tests():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTechnicalAnalysis)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    run_tests()
    # unittest.main(argv=['first-arg-is-ignored'], exit=False)
