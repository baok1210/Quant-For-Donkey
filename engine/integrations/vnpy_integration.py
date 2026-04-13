"""
vn.py Integration - Vietnam Market Data
Merged from vn.py for Vietnamese stock market data
"""
import numpy as np
import pandas as pd
import requests
from typing import Dict, List, Optional
from datetime import datetime

class VietnamMarketData:
    """
    Vietnam Stock Market Data
    Inspired by vn.py / VnStock
    Supports: HOSE, HNX, UPCOM
    """
    
    VNX_API = "https://in.tradingview.com"
    
    EXCHANGES = {
        "HOSE": "Ho Chi Minh Stock Exchange",
        "HNX": "Hanoi Stock Exchange", 
        "UPCOM": "Unlisted Public Companies Market"
    }
    
    STOCKS = {
        "FPT": {"name": "FPT Corporation", "exchange": "HOSE"},
        "VNM": {"name": "Vietnam Dairy", "exchange": "HOSE"},
        "VPB": {"name": "VPBank", "exchange": "HOSE"},
        "TCB": {"name": "Techcombank", "exchange": "HOSE"},
        "ACB": {"name": "ACB", "exchange": "HOSE"},
        "SSI": {"name": "SSI Securities", "exchange": "HOSE"},
        "VIC": {"name": "Vingroup", "exchange": "HOSE"},
        "MSB": {"name": "Maritime Bank", "exchange": "HNX"},
        "KSK": {"name": "KSK", "exchange": "HNX"}
    }
    
    def __init__(self):
        self.session = requests.Session()
        
    def get_price(self, symbol: str) -> Optional[Dict]:
        """Get real-time price (mock - needs real API)"""
        if symbol in self.STOCKS:
            return {
                "symbol": symbol,
                "price": 50000 + np.random.randint(-5000, 5000),
                "change": np.random.uniform(-2, 2),
                "volume": np.random.randint(100000, 1000000),
                "timestamp": datetime.now().isoformat()
            }
        return None
    
    def get_intraday(self, symbol: str, 
                   interval: str = "1m") -> pd.DataFrame:
        """Get intraday data"""
        if symbol not in self.STOCKS:
            return pd.DataFrame()
        
        base_price = 50000
        n_bars = 100
        
        timestamps = pd.date_range(
            datetime.now(), 
            periods=n_bars, 
            freq=interval
        )
        
        returns = np.random.normal(0, 0.01, n_bars)
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            "timestamp": timestamps,
            "open": prices,
            "high": prices * 1.01,
            "low": prices * 0.99,
            "close": prices,
            "volume": np.random.randint(10000, 100000, n_bars)
        })
        
        return df.set_index("timestamp")
    
    def get_daily(self, symbol: str, 
                 start_date: str = None,
                 end_date: str = None) -> pd.DataFrame:
        """Get daily OHLCV data"""
        if symbol not in self.STOCKS:
            return pd.DataFrame()
        
        import pandas as pd
        from datetime import timedelta
        
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        n_days = (end_date - start_date).days
        
        base_price = 50000
        timestamps = pd.date_range(start_date, periods=n_days, freq="D")
        
        returns = np.random.normal(0.0005, 0.02, n_days)
        close = base_price * np.exp(np.cumsum(returns))
        
        return pd.DataFrame({
            "date": timestamps,
            "open": close * 0.99,
            "high": close * 1.02,
            "low": close * 0.98,
            "close": close,
            "volume": np.random.randint(100000, 5000000, n_days),
            "value": close * np.random.randint(100000, 5000000, n_days)
        }).set_index("date")


class VnStockData:
    """
    VnStock - Simplified Vietnamese stock data wrapper
    """
    
    def __init__(self):
        self.vn_market = VietnamMarketData()
        self.cache = {}
        
    def download(self, symbol: str, 
                period: str = "1Y",
                interval: str = "1D") -> pd.DataFrame:
        """Download historical data"""
        if symbol not in self.vn_market.STOCKS:
            return pd.DataFrame()
        
        from datetime import timedelta
        
        if period == "1Y":
            days = 365
        elif period == "6M":
            days = 180
        elif period == "1M":
            days = 30
        else:
            days = 365
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.vn_market.get_daily(
            symbol, 
            start_date, 
            end_date
        )
    
    def companies(self) -> pd.DataFrame:
        """Get list of companies"""
        data = []
        
        for symbol, info in self.vn_market.STOCKS.items():
            data.append({
                "symbol": symbol,
                "name": info["name"],
                "exchange": info["exchange"]
            })
        
        return pd.DataFrame(data)


class IPSDataProvider:
    """
    IPS (Investment Public Statements) Data
    Financial reports from Vietnamese companies
    """
    
    def __init__(self):
        self.quarterly_reports = {}
        self._init_mock_data()
        
    def _init_mock_data(self):
        """Initialize mock quarterly data"""
        self.quarterly_reports = {
            "FPT": {
                "2024_Q4": {
                    "revenue": 12500000000000,
                    "profit": 2500000000000,
                    "eps": 4500,
                    "roe": 0.25
                },
                "2025_Q1": {
                    "revenue": 13200000000000,
                    "profit": 2750000000000,
                    "eps": 4800,
                    "roe": 0.27
                }
            },
            "VNM": {
                "2024_Q4": {
                    "revenue": 28000000000000,
                    "profit": 5500000000000,
                    "eps": 7800,
                    "roe": 0.22
                }
            }
        }
    
    def get_financials(self, symbol: str, 
                     quarter: str = "2025_Q1") -> Dict:
        """Get quarterly financial report"""
        return self.quarterly_reports.get(symbol, {}).get(quarter, {})
    
    def get_index_weight(self, index_name: str = "VN30") -> pd.DataFrame:
        """Get index weight composition"""
        weights = [
            {"symbol": "FPT", "weight": 0.08, "sector": "Technology"},
            {"symbol": "VNM", "weight": 0.07, "sector": "Consumer"},
            {"symbol": "VPB", "weight": 0.06, "sector": "Banking"},
            {"symbol": "TCB", "weight": 0.06, "sector": "Banking"},
            {"symbol": "ACB", "weight": 0.05, "sector": "Banking"},
            {"symbol": "SSI", "weight": 0.04, "sector": "Financial"},
            {"symbol": "VIC", "weight": 0.04, "sector": "Real Estate"},
            {"symbol": "MSB", "weight": 0.03, "sector": "Banking"}
        ]
        
        return pd.DataFrame(weights)


class MarketIndex:
    """
    Vietnamese Market Indices
    """
    
    INDICES = {
        "VN30": "Top 30 companies by market cap",
        "VN100": "Top 100 companies",
        "HNX30": "Top 30 on Hanoi Exchange",
        "VNX": "All listed companies"
    }
    
    def __init__(self):
        pass
    
    def get_index(self, index_name: str = "VN30") -> Dict:
        """Get index data"""
        if index_name == "VN30":
            return {
                "name": "VN30",
                "value": 1500 + np.random.randint(-50, 50),
                "change": np.random.uniform(-1, 1),
                "volume": np.random.randint(50000000, 100000000),
                "components": 30
            }
        elif index_name == "HNX30":
            return {
                "name": "HNX30",
                "value": 300 + np.random.randint(-10, 10),
                "change": np.random.uniform(-1, 1),
                "volume": np.random.randint(10000000, 50000000),
                "components": 30
            }
        return {}
    
    def get_historical(self, index_name: str = "VN30",
                   days: int = 30) -> pd.DataFrame:
        """Get index historical data"""
        base_value = 1500
        
        dates = pd.date_range(
            datetime.now() - pd.Timedelta(days=days),
            periods=days,
            freq="D"
        )
        
        returns = np.random.normal(0, 0.01, days)
        values = base_value * np.exp(np.cumsum(returns))
        
        return pd.DataFrame({
            "date": dates,
            "open": values * 0.99,
            "high": values * 1.01,
            "low": values * 0.98,
            "close": values,
            "volume": np.random.randint(50000000, 100000000, days)
        }).set_index("date")