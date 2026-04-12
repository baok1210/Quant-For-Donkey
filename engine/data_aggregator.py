"""
Crypto Data Aggregator - Thu thập dữ liệu Edge cho Professional Traders
Funding Rate, Open Interest, Liquidations, Correlation
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

class CryptoDataAggregator:
    """Tổng hợp dữ liệu từ Binance Futures, Coinglass và các nguồn chuyên nghiệp"""
    
    def __init__(self):
        self.binance_fapi = "https://fapi.binance.com/fapi/v1"
        self.binance_data_api = "https://fapi.binance.com/futures/data"
        
    def get_funding_rate(self, symbol: str = "SOLUSDT") -> Dict:
        """Lấy Funding Rate thực tế (8h/lần)"""
        try:
            url = f"{self.binance_fapi}/premiumIndex"
            params = {"symbol": symbol}
            resp = requests.get(url, params=params, timeout=5).json()
            
            funding_rate = float(resp.get("lastFundingRate", 0))
            # Interpretation: 
            # > 0.01%: Longs pay Shorts (Bullish sentiment, possible long squeeze)
            # < 0: Shorts pay Longs (Bearish sentiment, possible short squeeze)
            
            return {
                "symbol": symbol,
                "funding_rate": funding_rate,
                "funding_rate_pct": funding_rate * 100,
                "next_funding_time": resp.get("nextFundingTime"),
                "sentiment": "OVERHEATED_LONG" if funding_rate > 0.0003 else ("OVERHEATED_SHORT" if funding_rate < -0.0003 else "NEUTRAL")
            }
        except:
            return {"funding_rate": 0.0001, "sentiment": "NEUTRAL"}

    def get_open_interest(self, symbol: str = "SOLUSDT") -> Dict:
        """Lấy Open Interest và Long/Short Ratio"""
        try:
            url = f"{self.binance_fapi}/openInterest"
            resp = requests.get(url, params={"symbol": symbol}, timeout=5).json()
            oi = float(resp.get("openInterest", 0))
            
            # Long/Short Ratio
            ls_url = f"{self.binance_data_api}/globalLongShortAccountRatio"
            ls_resp = requests.get(ls_url, params={"symbol": symbol, "period": "5m", "limit": 1}, timeout=5).json()
            ls_ratio = float(ls_resp[0]["longShortRatio"]) if ls_resp else 1.0
            
            return {
                "open_interest": oi,
                "long_short_ratio": ls_ratio,
                "timestamp": datetime.now().isoformat()
            }
        except:
            return {"open_interest": 0, "long_short_ratio": 1.0}

    def get_liquidations(self, symbol: str = "SOLUSDT") -> Dict:
        """Lấy dữ liệu Liquidation từ Binance API (Free Tier)"""
        try:
            # Lấy liquidation data từ Binance
            url = f"{self.binance_data_api}/liquidationOrders"
            params = {
                "symbol": symbol,
                "limit": 500  # Lấy 500 lệnh gần nhất
            }
            
            resp = requests.get(url, params=params, timeout=5).json()
            
            if resp:
                total_liq = sum(float(item['origQty']) * float(item['price']) for item in resp)
                
                # Phân loại long vs short
                long_liq = sum(float(item['origQty']) * float(item['price']) 
                              for item in resp if item['side'] == 'BUY')
                short_liq = total_liq - long_liq
                
                return {
                    "symbol": symbol,
                    "liquidations_24h": total_liq,
                    "long_liquidations": long_liq,
                    "short_liquidations": short_liq,
                    "long_short_liq_ratio": long_liq / short_liq if short_liq > 0 else float('inf'),
                    "fallback_mode": False,
                    "warning": None,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"⚠️ WARNING: Liquidation API failed ({e}). Using fallback mode.")
            pass
        
        # Fallback có cảnh báo rõ ràng
        return {
            "symbol": symbol,
            "liquidations_24h": 0,
            "long_liquidations": 0,
            "short_liquidations": 0,
            "long_short_liq_ratio": 1.0,
            "fallback_mode": True,
            "warning": "⚠️ API FAILED - Using estimated data. DCA timing may be unreliable.",
            "timestamp": datetime.now().isoformat()
        }

    def get_liquidation_zones(self, symbol: str = "SOLUSDT", current_price: float = None, tolerance_pct: float = 2.0) -> Dict:
        """
        Phát hiện vùng Liquidation Clusters thực sự
        Cluster các lệnh liquidation gần nhau thành zones
        """
        try:
            url = f"{self.binance_data_api}/liquidationOrders"
            params = {"symbol": symbol, "limit": 1000}
            resp = requests.get(url, params=params, timeout=5).json()
            
            if not resp:
                return {"zones": [], "fallback_mode": True, "warning": "No liquidation data"}
            
            # Cluster liquidations by price
            liq_prices = []
            for item in resp:
                price = float(item['price'])
                qty = float(item['origQty'])
                side = item['side']  # BUY = long liquidation, SELL = short liquidation
                liq_prices.append({"price": price, "size": qty, "side": side})
            
            # Group vào các cluster (tolerance 2%)
            liq_prices.sort(key=lambda x: x['price'])
            clusters = []
            current_cluster = []
            
            for liq in liq_prices:
                if not current_cluster:
                    current_cluster.append(liq)
                else:
                    ref_price = current_cluster[0]['price']
                    if abs(liq['price'] - ref_price) / ref_price < (tolerance_pct / 100):
                        current_cluster.append(liq)
                    else:
                        if len(current_cluster) >= 3:  # Chỉ lấy cluster có ít nhất 3 lệnh
                            clusters.append(current_cluster)
                        current_cluster = [liq]
            
            if len(current_cluster) >= 3:
                clusters.append(current_cluster)
            
            # Tính toán các zones
            zones = []
            for cluster in clusters:
                avg_price = sum(l['price'] for l in cluster) / len(cluster)
                total_size = sum(l['size'] for l in cluster)
                long_size = sum(l['size'] for l in cluster if l['side'] == 'BUY')
                short_size = sum(l['size'] for l in cluster if l['side'] == 'SELL')
                
                zones.append({
                    "avg_price": avg_price,
                    "total_size": total_size,
                    "long_liquidation_size": long_size,
                    "short_liquidation_size": short_size,
                    "count": len(cluster),
                    "dominant_side": "LONG" if long_size > short_size else "SHORT"
                })
            
            # Sắp xếp theo tổng size
            zones.sort(key=lambda x: x['total_size'], reverse=True)
            
            # Kiểm tra giá hiện tại có gần zone nào không
            near_zones = []
            if current_price:
                for zone in zones:
                    distance_pct = abs(current_price - zone['avg_price']) / current_price * 100
                    if distance_pct < tolerance_pct:
                        near_zones.append({
                            **zone,
                            "distance_pct": distance_pct,
                            "direction": "BELOW" if current_price > zone['avg_price'] else "ABOVE"
                        })
            
            return {
                "zones": zones[:10],  # Top 10 zones lớn nhất
                "near_zones": near_zones,
                "total_zones": len(zones),
                "fallback_mode": False,
                "warning": None
            }
        except Exception as e:
            print(f"⚠️ WARNING: Liquidation Zone Detection failed ({e})")
            return {"zones": [], "near_zones": [], "fallback_mode": True, "warning": f"API failed: {e}"}

    def get_funding_history(self, symbol: str = "SOLUSDT", limit: int = 100) -> List[Dict]:
        """Lấy lịch sử funding rate (cho phân tích chu kỳ)"""
        try:
            url = f"{self.binance_data_api}/fundingRate"
            params = {
                "symbol": symbol,
                "limit": limit
            }
            
            resp = requests.get(url, params=params, timeout=5).json()
            
            funding_history = []
            for item in resp:
                funding_history.append({
                    "funding_rate": float(item["fundingRate"]),
                    "timestamp": datetime.fromtimestamp(int(item["fundingTime"]) / 1000).isoformat(),
                    "mark_price": float(item["markPrice"])
                })
            
            return funding_history
        except:
            return []

    def calculate_correlation(self, btc_prices: List[float], sol_prices: List[float]) -> Dict:
        """Tính tương quan BTC vs SOL (Rolling Correlation)"""
        if len(btc_prices) < 24 or len(sol_prices) < 24:
            return {"correlation": 0.8, "status": "HIGH_CORRELATION"}
            
        corr = np.corrcoef(btc_prices[-24:], sol_prices[-24:])[0, 1]
        
        return {
            "correlation": corr,
            "interpretation": "STRONG" if corr > 0.8 else ("MODERATE" if corr > 0.5 else "WEAK")
        }

    def detect_funding_cycles(self, symbol: str = "SOLUSDT") -> Dict:
        """Phát hiện chu kỳ funding rate (8h cycle)"""
        history = self.get_funding_history(symbol, limit=50)
        
        if len(history) < 10:
            return {"cycle_detected": False, "pattern": "INSUFFICIENT_DATA"}
        
        # Tính chu kỳ: funding rate thường oscillate giữa + và -
        positive_count = sum(1 for h in history if h["funding_rate"] > 0)
        negative_count = len(history) - positive_count
        
        # Tính trung bình và độ lệch
        avg_funding = np.mean([h["funding_rate"] for h in history])
        std_funding = np.std([h["funding_rate"] for h in history])
        
        return {
            "cycle_detected": abs(avg_funding) < std_funding * 0.5,  # Nếu trung bình gần 0 -> có chu kỳ
            "avg_funding_rate": avg_funding,
            "std_funding_rate": std_funding,
            "positive_ratio": positive_count / len(history),
            "negative_ratio": negative_count / len(history),
            "pattern": "CYCLICAL" if abs(avg_funding) < std_funding * 0.5 else "BIASED"
        }
