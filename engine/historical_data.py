"""
Historical Data Manager - Tải và quản lý dữ liệu OHLCV quy mô lớn
Hỗ trợ tải 1-2 năm dữ liệu từ Binance/OKX cho Backtesting
"""
import os
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import time

class HistoricalDataManager:
    """Quản lý dữ liệu lịch sử cho Backtest và Offline Learning"""
    
    def __init__(self, storage_path="data/historical"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
        })

    def fetch_large_dataset(self, symbol="SOL/USDT", timeframe="1h", years=1):
        """
        Tải dữ liệu lịch sử lớn (ví dụ 1-2 năm)
        """
        print(f"🚀 Bắt đầu tải {years} năm dữ liệu cho {symbol} ({timeframe})...")
        
        since = self.exchange.parse8601((datetime.now() - timedelta(days=365*years)).isoformat())
        all_ohlcv = []
        
        while since < self.exchange.milliseconds():
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit=1000)
                if not ohlcv:
                    break
                    
                since = ohlcv[-1][0] + 1
                all_ohlcv.extend(ohlcv)
                print(f"✅ Đã tải đến: {datetime.fromtimestamp(since/1000).strftime('%Y-%m-%d %H:%M')}")
                
                # Tránh bị ban IP
                time.sleep(self.exchange.rateLimit / 1000)
                
            except Exception as e:
                print(f"❌ Lỗi khi tải: {e}")
                time.sleep(10)
                continue
                
        # Convert sang DataFrame
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('datetime', inplace=True)
        
        # Lưu file
        file_name = f"{symbol.replace('/', '_')}_{timeframe}_{years}y.csv"
        file_path = os.path.join(self.storage_path, file_name)
        df.to_csv(file_path)
        
        print(f"🏁 Đã lưu {len(df)} nến vào {file_path}")
        return df

    def load_local_data(self, symbol="SOL/USDT", timeframe="1h", years=1):
        """Load dữ liệu từ file CSV cục bộ"""
        file_name = f"{symbol.replace('/', '_')}_{timeframe}_{years}y.csv"
        file_path = os.path.join(self.storage_path, file_name)
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, index_col='datetime', parse_dates=True)
            return df
        return None
