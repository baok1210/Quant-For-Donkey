"""
Signal Engine - Bộ máy tạo tín hiệu giao dịch
Tối ưu hóa tính toán MACD, RSI và tích hợp dữ liệu on-chain Solana chuyên sâu.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union
from datetime import datetime

class SignalEngine:
    """Bộ máy tạo tín hiệu với thuật toán chuẩn hóa"""
    
    def __init__(self):
        self.signal_history = []
        
    def calculate_rsi(self, prices: Union[List[float], np.ndarray], period: int = 14) -> float:
        """
        Tính RSI chuẩn theo phương pháp Wilder's Smoothing
        """
        if len(prices) < period + 1:
            return 50.0
            
        prices = np.array(prices)
        deltas = np.diff(prices)
        seed = deltas[:period]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        
        if down == 0:
            return 100.0
            
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100. / (1. + rs)

        for i in range(period, len(prices)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period

            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)

        return float(rsi[-1])
    
    def calculate_macd(self, prices: List[float]) -> Dict:
        """
        Tính MACD chuẩn: 
        MACD Line = EMA(12) - EMA(26)
        Signal Line = EMA(9) of MACD Line
        """
        if len(prices) < 35: # Cần đủ dữ liệu để EMA(26) và Signal(9) ổn định
            return {"macd": 0, "signal": 0, "histogram": 0, "trend": "neutral"}
            
        s = pd.Series(prices)
        ema12 = s.ewm(span=12, adjust=False).mean()
        ema26 = s.ewm(span=26, adjust=False).mean()
        
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        last_macd = macd_line.iloc[-1]
        last_signal = signal_line.iloc[-1]
        last_hist = histogram.iloc[-1]
        
        return {
            "macd": float(last_macd),
            "signal": float(last_signal),
            "histogram": float(last_hist),
            "trend": "bullish" if last_hist > 0 else "bearish"
        }
    
    def calculate_solana_onchain(self, data: Dict) -> Dict:
        """
        Phân tích On-chain Solana chuyên sâu (Helius/Solscan/Jito)
        """
        metrics = {
            "tps_health": 1.0,        # 0.0 - 1.0
            "congestion_level": 0.0,  # 0.0 - 1.0
            "whale_activity": 0.0,    # -1.0 - 1.0 (Dòng tiền ròng)
            "jito_boost": 0.0         # Tín hiệu từ MEV/Tips
        }
        
        # 1. TPS & Block Health
        tps = data.get("tps", 2500)
        metrics["tps_health"] = min(tps / 3000, 1.0)
        
        # 2. Congestion (Dựa trên priority fees)
        fee = data.get("priority_fee", 0.000005)
        metrics["congestion_level"] = min(fee / 0.001, 1.0)
        
        # 3. Whale Activity
        inflow = data.get("whale_inflow", 0)
        outflow = data.get("whale_outflow", 0)
        if inflow + outflow > 0:
            metrics["whale_activity"] = (inflow - outflow) / (inflow + outflow)
            
        # 4. Jito MEV Tips (Smart Money Indicator)
        tips = data.get("jito_tips_24h", 0)
        metrics["jito_boost"] = min(tips / 2000, 1.0)
        
        return metrics

    def generate_signal(self, market_data: Dict) -> Dict:
        """
        Tổng hợp tất cả tín hiệu (Technical + On-chain + Sentiment)
        """
        prices = market_data.get("prices", [])
        if not prices:
            return {"error": "No price data"}
            
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        onchain = self.calculate_solana_onchain(market_data)
        sentiment = market_data.get("sentiment_score", 0.0) # Từ engine/sentiment.py
        
        # Scoring Logic (Trọng số điều chỉnh được)
        # Technical: 40%, On-chain: 40%, Sentiment: 20%
        
        # Technical Score (-1 to 1)
        tech_score = 0
        if rsi < 30: tech_score += 0.5
        elif rsi > 70: tech_score -= 0.5
        if macd["trend"] == "bullish": tech_score += 0.5
        else: tech_score -= 0.5
        
        # On-chain Score (-1 to 1)
        oc_score = (onchain["tps_health"] * 0.3) + \
                   (onchain["whale_activity"] * 0.4) + \
                   ((1 - onchain["congestion_level"]) * 0.3)
        
        # Final Aggregate Score
        final_score = (tech_score * 0.4) + (oc_score * 0.4) + (sentiment * 0.2)
        
        # Signal Mapping
        if final_score > 0.4:
            signal = "STRONG_BUY"
        elif final_score > 0.15:
            signal = "BUY"
        elif final_score > -0.15:
            signal = "HOLD"
        elif final_score > -0.4:
            signal = "SELL"
        else:
            signal = "STRONG_SELL"
            
        return {
            "timestamp": datetime.now().isoformat(),
            "signal": signal,
            "score": float(final_score),
            "metrics": {
                "rsi": rsi,
                "macd": macd,
                "onchain": onchain,
                "sentiment": sentiment
            }
        }
