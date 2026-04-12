"""
Signal Engine - Tạo và đánh giá tín hiệu DCA
Bao gồm: Technical Analysis, On-chain Metrics, Sentiment Analysis
"""

import numpy as np
from typing import Dict, List
from datetime import datetime

class SignalEngine:
    """Bộ máy tạo tín hiệu"""
    
    def __init__(self):
        self.signal_history = []
        
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        Tính RSI (Relative Strength Index)
        
        Args:
            prices: Danh sách giá
            period: Chu kỳ tính toán
        
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # Default neutral
            
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, prices: List[float]) -> Dict:
        """
        Tính MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Danh sách giá
        
        Returns:
            MACD signal dict
        """
        if len(prices) < 26:
            return {"macd": 0, "signal": 0, "histogram": 0}
            
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        macd_line = ema_12 - ema_26
        
        # Tính signal line (EMA của MACD line)
        macd_values = []
        for i in range(12, len(prices)):
            ema_12 = self._calculate_ema(prices[:i], 12)
            ema_26 = self._calculate_ema(prices[:i], 26)
            macd_values.append(ema_12 - ema_26)
        
        signal_line = self._calculate_ema(macd_values, 9)
        
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram,
            "trend": "bullish" if histogram > 0 else "bearish"
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Tính EMA (Exponential Moving Average)"""
        if len(prices) < period:
            return np.mean(prices)
            
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
            
        return ema
    
    def calculate_onchain_metrics(self, data: Dict) -> Dict:
        """
        Tính toán các chỉ số on-chain
        
        Args:
            data: Dữ liệu on-chain
        
        Returns:
            On-chain metrics
        """
        metrics = {
            "active_wallets_change": 0.0,
            "tx_volume_change": 0.0,
            "whale_movements": 0,
            "network_health": "healthy"
        }
        
        # Tính toán từ dữ liệu đầu vào
        if "active_wallets" in data:
            prev_wallets = data["active_wallets"].get("prev", 100000)
            curr_wallets = data["active_wallets"].get("current", 100000)
            metrics["active_wallets_change"] = (curr_wallets - prev_wallets) / prev_wallets
        
        if "tx_volume" in data:
            prev_volume = data["tx_volume"].get("prev", 1000000)
            curr_volume = data["tx_volume"].get("current", 1000000)
            metrics["tx_volume_change"] = (curr_volume - prev_volume) / prev_volume
        
        if "whale_transfers" in data:
            metrics["whale_movements"] = data["whale_transfers"].get("outflow", 0)
        
        # Đánh giá sức khỏe mạng
        if data.get("priority_fee", 0) > 0.001:
            metrics["network_health"] = "congested"
        elif data.get("priority_fee", 0) > 0.0005:
            metrics["network_health"] = "busy"
            
        return metrics
    
    def generate_signal(self, market_data: Dict) -> Dict:
        """
        Tổng hợp tất cả tín hiệu và đưa ra đánh giá
        
        Args:
            market_data: Dữ liệu thị trường
        
        Returns:
            Signal evaluation
        """
        # Tính toán các chỉ báo kỹ thuật
        prices = market_data.get("prices", [100])
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        
        # Lấy dữ liệu on-chain
        onchain = self.calculate_onchain_metrics(market_data)
        
        # Tính điểm tổng hợp
        score = 0.0
        signals = []
        
        # RSI scoring
        if rsi < 30:
            score += 0.3
            signals.append("RSI oversold - cơ hội mua")
        elif rsi > 70:
            score -= 0.3
            signals.append("RSI overbought - cảnh báo")
            
        # MACD scoring
        if macd["histogram"] > 0:
            score += 0.2
            signals.append("MACD bullish")
        else:
            score -= 0.2
            signals.append("MACD bearish")
            
        # On-chain scoring
        if onchain["active_wallets_change"] > 0.1:
            score += 0.2
            signals.append("Active wallets tăng")
            
        if onchain["network_health"] == "congested":
            score -= 0.2
            signals.append("Mạng quá tải")
            
        # Xác định tín hiệu cuối cùng
        if score > 0.3:
            signal_type = "STRONG_BUY"
            confidence = min(score, 1.0)
        elif score > 0.1:
            signal_type = "BUY"
            confidence = min(score + 0.2, 1.0)
        elif score > -0.1:
            signal_type = "HOLD"
            confidence = 0.5
        elif score > -0.3:
            signal_type = "SELL"
            confidence = min(abs(score) + 0.2, 1.0)
        else:
            signal_type = "STRONG_SELL"
            confidence = min(abs(score), 1.0)
            
        return {
            "timestamp": datetime.now().isoformat(),
            "signal_type": signal_type,
            "confidence": confidence,
            "score": score,
            "rsi": rsi,
            "macd_trend": macd["trend"],
            "onchain_metrics": onchain,
            "signals": signals
        }

# Test
if __name__ == "__main__":
    engine = SignalEngine()
    
    # Mock data
    test_data = {
        "prices": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 108, 105, 102, 98, 95, 92, 90, 88, 85],
        "active_wallets": {"prev": 100000, "current": 115000},
        "tx_volume": {"prev": 1000000, "current": 1200000},
        "whale_transfers": {"outflow": 500},
        "priority_fee": 0.0003
    }
    
    signal = engine.generate_signal(test_data)
    print(f"Signal: {signal['signal_type']} (Confidence: {signal['confidence']:.2%})")
    print(f"Score: {signal['score']:.2f}")
    print(f"RSI: {signal['rsi']:.2f}")
    print(f"MACD Trend: {signal['macd_trend']}")
