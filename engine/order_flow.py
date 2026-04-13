"""
Order Flow Analysis Engine (v4.3.1)
Phân tích dữ liệu order book để phát hiện:
- Cumulative Volume Delta (CVD)
- Absorption zones
- Delta divergence
- Smart money tracking
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import requests
from collections import defaultdict

class OrderFlowAnalyzer:
    """
    Phân tích dữ liệu order book để phát hiện các dấu hiệu từ smart money
    """
    
    def __init__(self, binance_api_url: str = "https://fapi.binance.com/fapi/v1"):
        self.binance_api_url = binance_api_url
    
    def get_orderbook_depth(self, symbol: str = "SOLUSDT", depth: int = 100) -> Dict:
        """
        Lấy order book depth từ Binance
        """
        try:
            url = f"{self.binance_api_url}/depth"
            params = {"symbol": symbol, "limit": depth}
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json()
            
            if 'bids' in data and 'asks' in data:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "bids": data['bids'],
                    "asks": data['asks'],
                    "symbol": symbol
                }
        except Exception as e:
            print(f"⚠️ Orderbook fetch error: {e}")
            return None
    
    def calculate_cvd(self, bids: List[List], asks: List[List], 
                     window: int = 100) -> Dict:
        """
        Tính Cumulative Volume Delta (CVD) từ orderbook
        CVD = SUM(bid_volume) - SUM(ask_volume) trên từng mức giá
        """
        bid_volumes = [float(bid[1]) for bid in bids[:window]]
        ask_volumes = [float(ask[1]) for ask in asks[:window]]
        
        # Tính CVD từng cấp giá
        cvd_levels = []
        for i in range(min(len(bid_volumes), len(ask_volumes))):
            bid_vol = bid_volumes[i]
            ask_vol = ask_volumes[i]
            cvd = bid_vol - ask_vol
            cvd_levels.append({
                "price": float(bids[i][0]),
                "bid_volume": bid_vol,
                "ask_volume": ask_vol,
                "cvd": cvd
            })
        
        # Tính cumulative
        cumulative_cvd = []
        cumsum = 0
        for level in cvd_levels:
            cumsum += level['cvd']
            cumulative_cvd.append({
                **level,
                "cumulative_cvd": cumsum
            })
        
        return {
            "levels": cumulative_cvd,
            "total_cvd": cumsum,
            "max_positive_cvd": max([l['cumulative_cvd'] for l in cumulative_cvd if l['cumulative_cvd'] > 0], default=0),
            "max_negative_cvd": min([l['cumulative_cvd'] for l in cumulative_cvd if l['cumulative_cvd'] < 0], default=0)
        }
    
    def detect_absorption_zones(self, cvd_data: Dict, threshold: float = 1000) -> List[Dict]:
        """
        Phát hiện vùng hấp thụ (Absorption Zones) từ CVD
        """
        zones = []
        current_zone = None
        
        for level in cvd_data['levels']:
            cvd = level['cumulative_cvd']
            
            # Nếu CVD vượt ngưỡng dương (mua mạnh)
            if cvd > threshold:
                if not current_zone:
                    current_zone = {
                        "start_price": level['price'],
                        "start_cvd": cvd,
                        "max_cvd": cvd,
                        "end_price": level['price'],
                        "end_cvd": cvd,
                        "zone_type": "BUY_ABSORPTION",
                        "volume": level['bid_volume']
                    }
                else:
                    current_zone['end_price'] = level['price']
                    current_zone['end_cvd'] = cvd
                    current_zone['max_cvd'] = max(current_zone['max_cvd'], cvd)
                    current_zone['volume'] += level['bid_volume']
            
            # Nếu không còn vùng hấp thụ
            elif current_zone:
                zones.append(current_zone)
                current_zone = None
        
        # Thêm zone cuối cùng nếu còn
        if current_zone:
            zones.append(current_zone)
        
        return zones
    
    def calculate_delta_divergence(self, cvd_data: Dict, price_data: List[float]) -> Dict:
        """
        Tính Delta Divergence giữa CVD và giá
        """
        if not cvd_data['levels'] or len(price_data) < 2:
            return {"divergence": None, "confidence": 0}
        
        # Lấy CVD cuối cùng và giá cuối cùng
        last_cvd = cvd_data['levels'][-1]['cumulative_cvd']
        last_price = price_data[-1]
        
        # Tính tỷ lệ giữa CVD và giá
        if last_price > 0:
            ratio = last_cvd / last_price
            divergence = "BULLISH" if ratio > 0.1 else "BEARISH" if ratio < -0.1 else "NEUTRAL"
            confidence = abs(ratio) * 100
            
            return {
                "divergence": divergence,
                "confidence": min(confidence, 100),
                "cvd_ratio": ratio,
                "timestamp": datetime.now().isoformat()
            }
        
        return {"divergence": None, "confidence": 0}
    
    def analyze_smart_money(self, symbol: str = "SOLUSDT", price_data: List[float] = None) -> Dict:
        """
        Phân tích toàn diện từ smart money
        """
        orderbook = self.get_orderbook_depth(symbol)
        if not orderbook:
            return {"error": "Failed to fetch orderbook"}
        
        # Tính CVD
        cvd_result = self.calculate_cvd(orderbook['bids'], orderbook['asks'])
        
        # Phát hiện vùng hấp thụ
        absorption_zones = self.detect_absorption_zones(cvd_result, threshold=500)
        
        # Delta divergence
        delta_div = self.calculate_delta_divergence(cvd_result, price_data or [])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "cvd_analysis": cvd_result,
            "absorption_zones": absorption_zones,
            "delta_divergence": delta_div,
            "smart_money_indicators": {
                "high_buy_pressure": cvd_result['max_positive_cvd'] > 10000,
                "high_sell_pressure": cvd_result['max_negative_cvd'] < -10000,
                "buy_absorption_zones": len(absorption_zones) > 0,
                "divergence_signal": delta_div['divergence']
            }
        }