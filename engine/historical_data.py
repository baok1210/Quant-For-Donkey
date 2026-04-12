"""
Historical Data - Thu thập và quản lý dữ liệu lịch sử cho AI học offline
"""
import pandas as pd
import os
from datetime import datetime, timedelta

class HistoricalDataManager:
    """Quản lý dữ liệu lịch sử cho AI Offline Learning"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def load_ohlcv(self, symbol="SOL-USDT", timeframe="1h"):
        """Load dữ liệu OHLCV từ file CSV"""
        filename = f"{self.data_dir}/{symbol}_{timeframe}.csv"
        if os.path.exists(filename):
            df = pd.read_csv(filename, parse_dates=["timestamp"])
            return df
        return None
    
    def save_ohlcv(self, df, symbol="SOL-USDT", timeframe="1h"):
        """Lưu dữ liệu OHLCV vào file CSV"""
        os.makedirs(self.data_dir, exist_ok=True)
        filename = f"{self.data_dir}/{symbol}_{timeframe}.csv"
        df.to_csv(filename, index=False)
        
    def get_latest_data(self, symbol="SOL-USDT", timeframe="1h"):
        """Lấy dữ liệu mới nhất"""
        df = self.load_ohlcv(symbol, timeframe)
        if df is not None:
            return df.tail(100)
        return None
    
    def generate_sample_data(self, days=30, timeframe="1h"):
        """Tạo dữ liệu mẫu để demo khi chưa có dữ liệu thật"""
        dates = pd.date_range(end=datetime.now(), periods=days*24, freq="1h")
        import numpy as np
        
        np.random.seed(42)
        base_price = 100
        prices = [base_price]
        for i in range(1, len(dates)):
            change = np.random.normal(0, 0.02)
            prices.append(prices[-1] * (1 + change))
            
        df = pd.DataFrame({
            "timestamp": dates,
            "open": prices,
            "high": [p * 1.02 for p in prices],
            "low": [p * 0.98 for p in prices],
            "close": prices,
            "volume": np.random.uniform(1000000, 5000000, len(dates))
        })
        
        self.save_ohlcv(df, "SOL-USDT", timeframe)
        return df
