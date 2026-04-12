"""
Unit tests for Kelly Criterion and Risk Engine
"""
import pytest
from engine.risk import RiskEngine

def test_kelly_criterion_correct_formula():
    """Test Kelly với công thức đúng: f* = W - (1-W)/R"""
    risk_engine = RiskEngine()
    
    # Test case 1: Win rate = 60%, avg_win = 15%, avg_loss = 10%
    # R = 15/10 = 1.5
    # Kelly = 0.6 - (1-0.6)/1.5 = 0.6 - 0.4/1.5 = 0.6 - 0.2667 = 0.3333
    # Half Kelly = 0.1667
    kelly = risk_engine.kelly_criterion(0.6, 0.15, 0.10)
    expected = (0.6 - (1-0.6)/(0.15/0.10)) * 0.5  # Half Kelly
    assert abs(kelly - expected) < 0.01

def test_kelly_edge_cases():
    """Test các trường hợp biên"""
    risk_engine = RiskEngine()
    
    # Test với avg_loss = 0 (tránh chia cho 0)
    kelly = risk_engine.kelly_criterion(0.6, 0.15, 0.0)
    assert kelly == 0.0
    
    # Test với avg_win = 0
    kelly = risk_engine.kelly_criterion(0.6, 0.0, 0.10)
    assert kelly == 0.0
    
    # Test với win_rate = 0
    kelly = risk_engine.kelly_criterion(0.0, 0.15, 0.10)
    assert kelly == 0.0

def test_position_size_calculation():
    """Test tính toán position size"""
    risk_engine = RiskEngine(initial_capital=10000)
    
    position = risk_engine.calculate_position_size(
        win_rate=0.6, avg_win=0.15, avg_loss=0.10, volatility=0.3
    )
    
    # Phải nhỏ hơn capital
    assert position < 10000
    # Phải dương nếu Kelly > 0
    assert position > 0

if __name__ == "__main__":
    test_kelly_criterion_correct_formula()
    test_kelly_edge_cases()
    test_position_size_calculation()
    print("✅ All Kelly criterion tests passed!")
