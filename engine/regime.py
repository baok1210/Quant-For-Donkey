"""
Market Regime Detection - Phân loại trạng thái thị trường
Phân loại: Bullish, Bearish, Sideways, Volatile/Crisis
"""
import pandas as pd
import numpy as np

class MarketRegimeDetector:
    def __init__(self, window_short=20, window_long=50, adx_window=14):
        self.window_short = window_short
        self.window_long = window_long
        self.adx_window = adx_window

    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Tính ADX (Average Directional Index)
        """
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate +DM and -DM
        plus_dm = (high.diff() > low.diff()).astype(int) * (high.diff().where(high.diff() > low.diff(), 0))
        minus_dm = (low.diff() > high.diff()).astype(int) * (low.diff().where(low.diff() > high.diff(), 0))
        
        # Normalize DM and TR
        plus_dm = plus_dm / tr * 100
        minus_dm = minus_dm / tr * 100
        tr = tr / tr * 100
        
        # Calculate +DI and -DI
        plus_di = plus_dm.ewm(span=period, adjust=False).mean()
        minus_di = minus_dm.ewm(span=period, adjust=False).mean()
        
        # Calculate DX
        dx_num = abs(plus_di - minus_di)
        dx_denom = (plus_di + minus_di)
        dx = (dx_num / dx_denom * 100).fillna(0)
        
        # Calculate ADX
        adx = dx.ewm(span=period, adjust=False).mean()
        
        return adx

    def detect_regime(self, df: pd.DataFrame) -> dict:
        """
        Phát hiện regime dựa trên Moving Averages, Volatility và ADX
        """
        if len(df) < self.window_long:
            return {"regime": "UNKNOWN", "score": 0}

        close = df['close']
        high = df['high']
        low = df['low']
        
        ma_short = close.rolling(window=self.window_short).mean()
        ma_long = close.rolling(window=self.window_long).mean()
        
        # 1. Trend Detection
        is_bullish = ma_short.iloc[-1] > ma_long.iloc[-1]
        price_above_ma = close.iloc[-1] > ma_short.iloc[-1]
        
        # 2. ADX for Trend Strength
        adx = self.calculate_adx(high, low, close, self.adx_window)
        adx_value = adx.iloc[-1] if not adx.empty else 0
        
        # 3. Volatility (ATR-like)
        std_dev = close.tail(self.window_short).std()
        avg_price = close.tail(self.window_short).mean()
        volatility_ratio = std_dev / avg_price
        
        # 4. Logic phân loại với ADX
        if volatility_ratio > 0.05: # Biến động cực mạnh (>5% std dev)
            regime = "CRISIS/VOLATILE"
            action_bias = "DEFENSIVE"
        elif adx_value > 25 and is_bullish and price_above_ma:
            regime = "STRONG_BULL"
            action_bias = "AGGRESSIVE"
        elif adx_value > 25 and not is_bullish and not price_above_ma:
            regime = "STRONG_BEAR"
            action_bias = "CAUTIOUS_DCA"
        elif adx_value < 20:
            regime = "SIDEWAYS"
            action_bias = "NEUTRAL"
        elif is_bullish and price_above_ma:
            regime = "BULLISH"
            action_bias = "MODERATE"
        elif not is_bullish and not price_above_ma:
            regime = "BEARISH"
            action_bias = "CAUTIOUS"
        else:
            regime = "TRANSITION"
            action_bias = "NEUTRAL"

        return {
            "regime": regime,
            "action_bias": action_bias,
            "volatility": volatility_ratio,
            "adx_value": adx_value,
            "trend_strength": abs(ma_short.iloc[-1] - ma_long.iloc[-1]) / ma_long.iloc[-1]
        }
