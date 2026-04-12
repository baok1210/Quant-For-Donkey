"""
Advanced DCA Strategy - DCA theo Timing chuyên nghiệp
Dựa trên: Funding Cycles, Liquidation Zones, Weekend Effect, Correlation
"""
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List
from engine.data_aggregator import CryptoDataAggregator

class AdvancedDCA:
    """DCA với timing tối ưu dựa trên dữ liệu chuyên nghiệp"""
    
    def __init__(self):
        self.data_aggregator = CryptoDataAggregator()
        self.last_dca_time = None
        self.dca_amount = 100  # $100 default
        self.weekend_multiplier = 0.7  # Giảm 30% vào cuối tuần
    
    def calculate_optimal_dca_time(self, current_price: float, 
                                  btc_price: float = None,
                                  sol_price: float = None) -> Dict:
        """
        Tính thời điểm DCA tối ưu dựa trên:
        1. Funding Rate (Bullish/Bearish Squeeze)
        2. Weekend Effect
        3. Liquidation Clusters
        4. BTC/SOL Correlation
        """
        # 1. Funding Rate Analysis
        funding_data = self.data_aggregator.get_funding_rate("SOLUSDT")
        funding_rate = funding_data["funding_rate_pct"]
        
        # 2. Weekend Effect
        is_weekend = datetime.now().weekday() in [5, 6]  # Sat/Sun
        weekend_mult = self.weekend_multiplier if is_weekend else 1.0
        
        # 3. Liquidation Analysis (mock)
        liquidations = self.data_aggregator.get_liquidations("SOL")
        near_liq_zone = self._is_near_liquidation_zone(current_price, liquidations["major_liq_zones"])
        
        # 4. Correlation Analysis
        correlation = self.data_aggregator.calculate_correlation(
            [btc_price] * 24 if btc_price else [100] * 24,
            [sol_price] * 24 if sol_price else [100] * 24
        )
        
        # Logic quyết định timing
        timing_score = 0
        reason = []
        
        # Funding Rate: < -0.01% = Short Squeeze = Good Buy
        if funding_rate < -0.01:
            timing_score += 0.8
            reason.append("SHORT_SQUEEZE_OPPORTUNITY")
        elif funding_rate > 0.01:
            timing_score -= 0.5
            reason.append("LONG_SQUEEZE_CAUTION")
        
        # Near Liquidation Zone
        if near_liq_zone["near_zone"]:
            timing_score += 0.6 if near_liq_zone["direction"] == "SHORT_LIQUIDATION" else -0.3
            reason.append(f"NEAR_LIQ_ZONE_{near_liq_zone['direction']}")
        
        # Weekend Effect
        if is_weekend:
            timing_score -= 0.2  # Giảm điểm vì volume thấp
            reason.append("WEEKEND_LOW_VOL")
        
        # High Correlation (BTC dip = SOL dip)
        if correlation["correlation"] > 0.7 and btc_price and btc_price < self._get_btc_support():
            timing_score += 0.4
            reason.append("BTC_DIP_FOLLOW")
        
        # Amount Adjustment
        base_amount = self.dca_amount * weekend_mult
        adjusted_amount = base_amount * (1 + timing_score)  # Tăng khi điểm cao
        
        return {
            "should_dca": timing_score > 0.3,
            "timing_score": timing_score,
            "recommended_amount": adjusted_amount,
            "reasons": reason,
            "funding_rate": funding_rate,
            "is_weekend": is_weekend,
            "correlation": correlation["correlation"]
        }
    
    def _is_near_liquidation_zone(self, current_price: float, zones: List[float], tolerance=0.5) -> Dict:
        """Kiểm tra có gần vùng liquidation không"""
        for zone in zones:
            distance_pct = abs(current_price - zone) / current_price * 100
            if distance_pct < tolerance:
                return {
                    "near_zone": True,
                    "zone_price": zone,
                    "distance_pct": distance_pct,
                    "direction": "SHORT_LIQUIDATION" if current_price > zone else "LONG_LIQUIDATION"
                }
        return {"near_zone": False}
    
    def _get_btc_support(self) -> float:
        """Mock: Lấy support của BTC (thực tế sẽ từ technical analysis)"""
        return 60000  # Mock giá support
