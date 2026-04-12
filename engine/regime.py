"""
Market Regime Detection - Phân loại trạng thái thị trường
Phân loại: Bullish, Bearish, Sideways, Volatile/Crisis
"""
import pandas as pd
import numpy as np

class MarketRegimeDetector:
    def __init__(self, window_short=20, window_long=50):
        self.window_short = window_short
        self.window_long = window_long

    def detect_regime(self, df: pd.DataFrame) -> dict:
        """
        Phát hiện regime dựa trên Moving Averages, Volatility và ADX
        """
        if len(df) < self.window_long:
            return {"regime": "UNKNOWN", "score": 0}

        close = df['close']
        ma_short = close.rolling(window=self.window_short).mean()
        ma_long = close.rolling(window=self.window_long).mean()
        
        # 1. Trend Detection
        is_bullish = ma_short.iloc[-1] > ma_long.iloc[-1]
        price_above_ma = close.iloc[-1] > ma_short.iloc[-1]
        
        # 2. Volatility (ATR-like)
        std_dev = close.tail(self.window_short).std()
        avg_price = close.tail(self.window_short).mean()
        volatility_ratio = std_dev / avg_price
        
        # 3. Logic phân loại
        if volatility_ratio > 0.05: # Biến động cực mạnh (>5% std dev)
            regime = "CRISIS/VOLATILE"
            action_bias = "DEFENSIVE"
        elif is_bullish and price_above_ma:
            regime = "STRONG_BULL"
            action_bias = "AGGRESSIVE"
        elif not is_bullish and not price_above_ma:
            regime = "STRONG_BEAR"
            action_bias = "CAUTIOUS_DCA"
        elif abs(ma_short.iloc[-1] - ma_long.iloc[-1]) / ma_long.iloc[-1] < 0.01:
            regime = "SIDEWAYS"
            action_bias = "NEUTRAL"
        else:
            regime = "TRANSITION"
            action_bias = "NEUTRAL"

        return {
            "regime": regime,
            "action_bias": action_bias,
            "volatility": volatility_ratio,
            "trend_strength": abs(ma_short.iloc[-1] - ma_long.iloc[-1]) / ma_long.iloc[-1]
        }
