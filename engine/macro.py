"""
Macro Indicator Integration - S&P 500, DXY, VIX, Gold, BTC Correlation
"""
import yfinance as yf
import pandas as pd
from typing import Dict

class MacroAnalyzer:
    """Phân tích các chỉ số vĩ mô ảnh hưởng đến Crypto"""
    
    def __init__(self):
        # Các mã ticker vĩ mô quan trọng
        self.tickers = {
            "SPX": "^GSPC",  # S&P 500
            "DXY": "DX-Y.NYB", # US Dollar Index
            "VIX": "^VIX",   # Volatility Index
            "GOLD": "GC=F",   # Gold Futures
            "BTC": "BTC-USD"  # Bitcoin
        }

    def get_macro_data(self, period="1mo") -> Dict:
        """Lấy dữ liệu vĩ mô gần đây"""
        results = {}
        for name, ticker in self.tickers.items():
            try:
                data = yf.download(ticker, period=period, progress=False)
                if not data.empty:
                    last_price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2]
                    change = (last_price - prev_price) / prev_price
                    results[name] = {
                        "price": float(last_price),
                        "change_pct": float(change),
                        "trend": "UP" if change > 0 else "DOWN"
                    }
            except:
                continue
        return results

    def analyze_risk_on_off(self) -> str:
        """
        Xác định môi trường đầu tư: RISK_ON hay RISK_OFF
        Logic: SPX UP + VIX DOWN + DXY DOWN = RISK_ON
        """
        data = self.get_macro_data()
        if not data: return "NEUTRAL"
        
        score = 0
        if data.get("SPX", {}).get("trend") == "UP": score += 1
        if data.get("VIX", {}).get("trend") == "DOWN": score += 1
        if data.get("DXY", {}).get("trend") == "DOWN": score += 1
        
        if score >= 2: return "RISK_ON"
        if score <= 1: return "RISK_OFF"
        return "NEUTRAL"
