"""
Multi-Strategy Ensemble - Kết hợp nhiều chiến lược
Voting system để chọn tín hiệu tốt nhất
"""
import pandas as pd
from typing import Dict, List
from engine.strategies.ema_crossover import EMACrossoverStrategy
from engine.strategies.atr_breakout import ATRStopLossStrategy
from engine.strategies.bollinger_squeeze import BollingerSqueezeStrategy
from engine.strategies.regime_adaptive import RegimeAdaptiveStrategy

class MultiStrategyEnsemble:
    """Kết hợp nhiều chiến lược để tăng độ tin cậy"""
    
    def __init__(self):
        self.strategies = {
            "ema_crossover": EMACrossoverStrategy(),
            "atr_breakout": ATRStopLossStrategy(),
            "bollinger_squeeze": BollingerSqueezeStrategy(),
            "regime_adaptive": RegimeAdaptiveStrategy()
        }
        self.strategy_weights = {
            "ema_crossover": 0.3,
            "atr_breakout": 0.3,
            "bollinger_squeeze": 0.2,
            "regime_adaptive": 0.2
        }
    
    def generate_ensemble_signal(self, df: pd.DataFrame) -> Dict:
        """
        Tổng hợp tín hiệu từ tất cả chiến lược
        """
        signals = {}
        confidences = {}
        
        # Lấy tín hiệu từ từng chiến lược
        for name, strategy in self.strategies.items():
            if name == "regime_adaptive":
                result = strategy.generate_signal(df)
                signals[name] = result["signal"]
                confidences[name] = result["confidence"]
            else:
                signal, confidence = strategy.generate_signal(df)
                signals[name] = signal
                confidences[name] = confidence
        
        # Voting system
        buy_votes = sum(1 for s in signals.values() if s == "BUY")
        sell_votes = sum(1 for s in signals.values() if s == "SELL")
        hold_votes = sum(1 for s in signals.values() if s == "HOLD")
        
        # Weighted confidence
        weighted_confidence = sum(
            confidences[name] * self.strategy_weights[name]
            for name in self.strategies.keys()
        )
        
        # Determine final signal
        if buy_votes > sell_votes and buy_votes >= 2:
            final_signal = "BUY"
        elif sell_votes > buy_votes and sell_votes >= 2:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"
        
        return {
            "final_signal": final_signal,
            "confidence": weighted_confidence,
            "votes": {
                "buy": buy_votes,
                "sell": sell_votes,
                "hold": hold_votes
            },
            "individual_signals": signals,
            "individual_confidences": confidences,
            "strategy_agreement": (buy_votes + sell_votes) / len(self.strategies)
        }
    
    def get_ensemble_metrics(self) -> Dict:
        """Return combined metrics từ tất cả chiến lược"""
        metrics = {}
        for name, strategy in self.strategies.items():
            metrics[name] = strategy.get_strategy_metrics()
        
        # Calculate ensemble average
        avg_pf = sum(m.get("profit_factor", 1.5) for m in metrics.values()) / len(metrics)
        avg_wr = sum(m.get("win_rate", 0.44) for m in metrics.values()) / len(metrics)
        
        return {
            "ensemble_profit_factor": avg_pf,
            "ensemble_win_rate": avg_wr,
            "individual_strategies": metrics
        }
