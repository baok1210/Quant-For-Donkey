"""
Regime Adaptive Strategy - Multi-Strategy System
5 Regimes: Bull, Bear, Sideways, Crisis, Transition
"""
from typing import Dict, Tuple
from engine.strategies.ema_crossover import EMACrossoverStrategy
from engine.strategies.grid_trading import GridTradingStrategy
from engine.strategies.bollinger_squeeze import BollingerSqueezeStrategy

class RegimeAdaptiveStrategy:
    """Tự động chọn chiến lược phù hợp theo trạng thái thị trường"""
    
    def __init__(self):
        self.strategies = {
            "STRONG_BULL": EMACrossoverStrategy(fast_period=9, slow_period=21),
            "STRONG_BEAR": GridTradingStrategy(grid_levels=5, spacing_pct=1.0),
            "SIDEWAYS": GridTradingStrategy(grid_levels=10, spacing_pct=2.0),
            "CRISIS": None,  # Defensive/Hold
            "TRANSITION": BollingerSqueezeStrategy()
        }
    
    def detect_regime(self, df) -> str:
        """
        Detect market regime từ dữ liệu
        """
        if len(df) < 50:
            return "UNKNOWN"
        
        close = df['close']
        returns = close.pct_change()
        
        # Tính volatility
        volatility = returns.rolling(20).std().iloc[-1]
        
        # Tính trend
        sma_50 = close.rolling(50).mean()
        sma_200 = close.rolling(200).mean()
        current_price = close.iloc[-1]
        
        trend = "BULL" if current_price > sma_50.iloc[-1] else "BEAR"
        
        # Xác định regime
        if volatility < 0.02 and trend == "BULL":
            return "STRONG_BULL"
        elif volatility < 0.02 and trend == "BEAR":
            return "STRONG_BEAR"
        elif volatility > 0.05:
            return "CRISIS"
        elif abs(current_price - sma_50.iloc[-1]) / sma_50.iloc[-1] < 0.03:
            return "SIDEWAYS"
        else:
            return "TRANSITION"
    
    def select_strategy(self, df) -> Tuple[str, object]:
        """Chọn chiến lược phù hợp"""
        regime = self.detect_regime(df)
        strategy = self.strategies.get(regime)
        
        return regime, strategy
    
    def generate_signal(self, df) -> Dict:
        """Generate signal với regime-aware strategy"""
        regime, strategy = self.select_strategy(df)
        
        if strategy is None:
            return {
                "signal": "HOLD",
                "confidence": 0.5,
                "regime": regime,
                "reason": "Defensive mode - waiting for clearer signal"
            }
        
        signal, confidence = strategy.generate_signal(df)
        
        return {
            "signal": signal,
            "confidence": confidence,
            "regime": regime,
            "strategy_used": strategy.__class__.__name__
        }
    
    def get_regime_metrics(self) -> Dict:
        """Return metrics cho từng regime"""
        return {
            "STRONG_BULL": {"win_rate": 0.52, "avg_return": 0.08},
            "STRONG_BEAR": {"win_rate": 0.48, "avg_return": -0.03},
            "SIDEWAYS": {"win_rate": 0.65, "avg_return": 0.02},
            "CRISIS": {"win_rate": 0.35, "avg_return": -0.15},
            "TRANSITION": {"win_rate": 0.44, "avg_return": 0.03}
        }
