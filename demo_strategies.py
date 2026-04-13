#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Test tất cả các chiến lược giao dịch
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append('.')

# Import các chiến lược
from engine.strategies.ema_crossover import EMACrossoverStrategy
from engine.strategies.atr_breakout import ATRStopLossStrategy as ATRBreakoutStrategy
from engine.strategies.bollinger_squeeze import BollingerSqueezeStrategy
from engine.strategies.grid_trading import GridTradingStrategy
from engine.strategies.regime_adaptive import RegimeAdaptiveStrategy
from engine.strategies.multi_strategy import MultiStrategyEnsemble

def generate_test_data(days=365):
    """Tạo dữ liệu test 1 năm"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    np.random.seed(42)
    
    # Tạo dữ liệu giá giả lập
    base_price = 100
    returns = np.random.normal(0.001, 0.02, days)
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Thêm trend và seasonality
    trend = np.linspace(0, 0.5, days)
    seasonality = 10 * np.sin(2 * np.pi * np.arange(days) / 30)
    prices = prices * (1 + trend/100) + seasonality
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': prices * (1 + np.random.normal(0.01, 0.01, days)),
        'low': prices * (1 - np.random.normal(0.01, 0.01, days)),
        'close': prices,
        'volume': np.random.randint(1000, 10000, days)
    })
    
    return df

def test_ema_crossover():
    """Test EMA Crossover Strategy"""
    print("[TEST] Testing EMA Crossover Strategy...")
    df = generate_test_data(100)
    strategy = EMACrossoverStrategy()
    
    signals = []
    for i in range(20, len(df)):
        window = df.iloc[i-20:i]
        signal, confidence = strategy.generate_signal(window)
        signals.append(signal)
    
    print(f"  Buy signals: {signals.count('BUY')}")
    print(f"  Sell signals: {signals.count('SELL')}")
    print(f"  Hold signals: {signals.count('HOLD')}")
    return signals

def test_atr_breakout():
    """Test ATR Breakout Strategy"""
    print("[TEST] Testing ATR Breakout Strategy...")
    df = generate_test_data(100)
    strategy = ATRBreakoutStrategy()
    
    signals = []
    for i in range(20, len(df)):
        window = df.iloc[i-20:i]
        signal, confidence = strategy.generate_signal(window)
        signals.append(signal)
    
    print(f"  Buy signals: {signals.count('BUY')}")
    print(f"  Sell signals: {signals.count('SELL')}")
    return signals

def test_bollinger_squeeze():
    """Test Bollinger Bands Squeeze Strategy"""
    print("[TEST] Testing Bollinger Squeeze Strategy...")
    df = generate_test_data(100)
    strategy = BollingerSqueezeStrategy()
    
    signals = []
    for i in range(20, len(df)):
        window = df.iloc[i-20:i]
        signal, confidence = strategy.generate_signal(window)
        signals.append(signal)
    
    print(f"  Buy signals: {signals.count('BUY')}")
    print(f"  Sell signals: {signals.count('SELL')}")
    return signals

def test_grid_trading():
    """Test Grid Trading Strategy"""
    print("[TEST] Testing Grid Trading Strategy...")
    strategy = GridTradingStrategy(grid_levels=5, spacing_pct=2.0)
    
    # Test với các mức giá khác nhau
    test_prices = [95, 100, 105, 110]
    for price in test_prices:
        signal = strategy.generate_signal(price)
        print(f"  Price ${price}: {signal}")
    
    return strategy

def test_regime_adaptive():
    """Test Regime Adaptive Strategy"""
    print("[TEST] Testing Regime Adaptive Strategy...")
    df = generate_test_data(200)
    strategy = RegimeAdaptiveStrategy()
    
    # Detect regime
    regime = strategy.detect_regime(df)
    print(f"  Detected Regime: {regime}")
    
    # Get strategy for regime
    selected_strategy = strategy.select_strategy(df)
    print(f"  Selected Strategy: {selected_strategy.__class__.__name__}")
    
    return regime, selected_strategy

def test_multi_strategy_ensemble():
    """Test Multi-Strategy Ensemble"""
    print("[TEST] Testing Multi-Strategy Ensemble...")
    df = generate_test_data(100)
    ensemble = MultiStrategyEnsemble()
    
    result = ensemble.generate_ensemble_signal(df)
    print(f"  Final Signal: {result['final_signal']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Strategy Votes: {result['votes']}")
    
    return result

def main():
    print("=== DEMO: Testing All Trading Strategies ===")
    print("=" * 50)
    
    # Test từng chiến lược
    test_ema_crossover()
    test_atr_breakout() 
    test_bollinger_squeeze()
    test_grid_trading()
    test_regime_adaptive()
    test_multi_strategy_ensemble()
    
    print("\n" + "="*50)
    print("[OK] All strategies tested successfully!")
    print("[INFO] Strategies tested:")
    print("  - EMA Crossover (9/21)")
    print("  - ATR Breakout (2.0x)")
    print("  - Bollinger Squeeze")
    print("  - Grid Trading")
    print("  - Regime Adaptive")
    print("  - Multi-Strategy Ensemble")
    print("\n[DONE] All strategies are ready for backtesting!")

if __name__ == "__main__":
    main()