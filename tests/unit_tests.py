"""
Unit Tests - Kiểm tra các module quan trọng
"""
import unittest
import numpy as np
import pandas as pd
from engine.signals import SignalEngine
from engine.risk import RiskEngine

class TestSignalEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = SignalEngine()
    
    def test_rsi_calculation(self):
        """Test RSI calculation accuracy"""
        # Test case: flat price should give RSI = 50
        flat_prices = [100] * 30
        rsi = self.engine.calculate_rsi(flat_prices)
        self.assertAlmostEqual(rsi, 50.0, places=1)
        
        # Test case: increasing price should give RSI > 70
        up_prices = list(range(100, 130))
        rsi_up = self.engine.calculate_rsi(up_prices)
        self.assertGreater(rsi_up, 70)
        
        # Test case: decreasing price should give RSI < 30
        down_prices = list(range(130, 100, -1))
        rsi_down = self.engine.calculate_rsi(down_prices)
        self.assertLess(rsi_down, 30)
    
    def test_macd_calculation(self):
        """Test MACD calculation"""
        # Test with simple increasing prices
        prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109] * 4  # 40 points
        macd_result = self.engine.calculate_macd(prices)
        
        # Should have reasonable values
        self.assertIsInstance(macd_result['macd'], float)
        self.assertIsInstance(macd_result['signal'], float)
        self.assertIsInstance(macd_result['histogram'], float)
    
    def test_signal_generation(self):
        """Test overall signal generation"""
        test_data = {
            "prices": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
            "tps": 2500,
            "priority_fee": 0.000005,
            "whale_inflow": 1000,
            "whale_outflow": 500,
            "jito_tips_24h": 1500,
            "sentiment_score": 0.3
        }
        
        signal = self.engine.generate_signal(test_data)
        self.assertIn('signal', signal)
        self.assertIn('score', signal)
        self.assertIn('metrics', signal)

class TestRiskEngine(unittest.TestCase):
    
    def setUp(self):
        self.risk_engine = RiskEngine(initial_capital=1000)
    
    def test_kelly_calculation(self):
        """Test Kelly Criterion calculation"""
        # Test case: 60% win rate, 2:1 win/loss ratio
        win_rate = 0.6
        avg_win = 2.0  # 200% on wins
        avg_loss = 1.0  # 100% on losses
        
        kelly_size = self.risk_engine.calculate_kelly_size(win_rate, avg_win, avg_loss)
        
        # Kelly formula: W - (1-W)/R = 0.6 - (0.4)/2 = 0.6 - 0.2 = 0.4
        # Half Kelly = 0.2
        expected = (win_rate - (1-win_rate)/(avg_win/avg_loss)) * 0.5
        self.assertAlmostEqual(kelly_size, expected, places=2)
        
        # Should not exceed 25%
        self.assertLessEqual(kelly_size, 0.25)
    
    def test_kelly_edge_cases(self):
        """Test Kelly with edge cases"""
        # Zero loss should return safe value
        size = self.risk_engine.calculate_kelly_size(0.5, 1.0, 0.0)
        self.assertEqual(size, 0.1)  # Default safe value
        
        # Negative Kelly should return 0
        size = self.risk_engine.calculate_kelly_size(0.3, 1.0, 2.0)
        self.assertGreaterEqual(size, 0)

class TestIntegration(unittest.TestCase):
    
    def test_end_to_end_flow(self):
        """Test integration between signal and risk engines"""
        signal_engine = SignalEngine()
        risk_engine = RiskEngine(initial_capital=1000)
        
        market_data = {
            "prices": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
            "tps": 2500,
            "priority_fee": 0.000005,
            "whale_inflow": 1000,
            "whale_outflow": 500,
            "jito_tips_24h": 1500,
            "sentiment_score": 0.3
        }
        
        # Generate signal
        signal = signal_engine.generate_signal(market_data)
        
        # Calculate position size based on signal confidence
        win_rate = 0.6  # Assume 60% based on signal confidence
        avg_win = 0.15 if signal['score'] > 0.2 else 0.10  # Higher win based on signal strength
        avg_loss = 0.08
        
        position_size = risk_engine.calculate_kelly_size(win_rate, avg_win, avg_loss)
        
        # Should have reasonable values
        self.assertIsInstance(position_size, float)
        self.assertGreaterEqual(position_size, 0)
        self.assertLessEqual(position_size, 0.25)

if __name__ == '__main__':
    unittest.main()
