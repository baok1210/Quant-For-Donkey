"""
Backtesting Engine - Chạy thử nghiệm chiến lược trên dữ liệu lịch sử
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

class BacktestingEngine:
    """Chạy backtest với dữ liệu lịch sử để đánh giá hiệu suất chiến lược"""
    
    def __init__(self, initial_capital: float = 1000):
        self.initial_capital = initial_capital
        self.results = {}
        
    def run_backtest(self, 
                     price_data: pd.DataFrame, 
                     strategy_func, 
                     weights: Dict[str, float] = None) -> Dict:
        """
        Chạy backtest với dữ liệu giá và chiến lược
        
        Args:
            price_data: Dữ liệu OHLCV
            strategy_func: Hàm chiến lược (ví dụ: buy_when_rsi_oversold)
            weights: Trọng số các chỉ báo từ AI Offline
        """
        capital = self.initial_capital
        positions = []  # Danh sách giao dịch
        portfolio_values = [capital]
        
        # Thêm các chỉ báo kỹ thuật
        df = price_data.copy()
        df['rsi'] = self._calculate_rsi(df['close'])
        df['macd'], df['signal'] = self._calculate_macd(df['close'])
        
        # Chạy chiến lược qua từng thời điểm
        for i in range(26, len(df)):  # Bắt đầu sau khi có đủ dữ liệu cho RSI/MACD
            current_price = df.iloc[i]['close']
            
            # Gọi chiến lược để quyết định mua/bán
            signal = strategy_func(df.iloc[:i+1], weights)
            
            # Thực hiện giao dịch dựa trên tín hiệu
            if signal == "BUY" and capital > current_price:
                shares = capital / current_price
                positions.append({
                    "date": df.iloc[i]['timestamp'],
                    "action": "BUY",
                    "price": current_price,
                    "shares": shares,
                    "capital": capital
                })
                capital = 0
                
            elif signal == "SELL" and len(positions) > 0 and positions[-1]['action'] == 'BUY':
                shares = positions[-1]['shares']
                capital = shares * current_price
                positions.append({
                    "date": df.iloc[i]['timestamp'],
                    "action": "SELL",
                    "price": current_price,
                    "shares": shares,
                    "capital": capital
                })
                
            portfolio_values.append(capital if capital > 0 else positions[-1]['shares'] * current_price if positions else self.initial_capital)
        
        # Tính toán kết quả
        final_value = portfolio_values[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        max_drawdown = self._calculate_max_drawdown(portfolio_values)
        sharpe_ratio = self._calculate_sharpe_ratio(portfolio_values)
        
        self.results = {
            "initial_capital": self.initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "trade_count": len([p for p in positions if p['action'] in ['BUY', 'SELL']]),
            "positions": positions,
            "portfolio_history": portfolio_values
        }
        
        return self.results
    
    def _calculate_rsi(self, prices, period=14):
        """Tính RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal_period=9):
        """Tính MACD"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        return macd, signal
    
    def _calculate_max_drawdown(self, portfolio_values):
        """Tính Max Drawdown"""
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (portfolio_values - peak) / peak
        return abs(drawdown.min())
    
    def _calculate_sharpe_ratio(self, portfolio_values, risk_free_rate=0.02):
        """Tính Sharpe Ratio"""
        returns = np.diff(portfolio_values) / portfolio_values[:-1]
        excess_returns = returns - risk_free_rate/252  # Giả định 252 ngày giao dịch
        if np.std(excess_returns) == 0:
            return 0
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
