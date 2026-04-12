"""
Advanced Backtesting Engine - Hỗ trợ Walk-forward và Portfolio Metrics
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Callable

class AdvancedBacktester:
    def __init__(self, initial_capital=10000, fee_pct=0.001):
        self.initial_capital = initial_capital
        self.fee_pct = fee_pct # Phí giao dịch 0.1%

    def run(self, df: pd.DataFrame, strategy_logic: Callable, params: dict):
        """
        Chạy mô phỏng chiến lược
        """
        capital = self.initial_capital
        position = 0 # 0: no position, >0: SOL amount
        equity_curve = []
        trades = []
        
        for i in range(len(df)):
            current_row = df.iloc[i]
            current_price = current_row['close']
            
            # 1. Gọi logic chiến lược
            signal, weight = strategy_logic(df.iloc[:i+1], params)
            
            # 2. Thực thi (giả lập)
            if signal == "BUY" and position == 0:
                # Mua tối đa theo weight (0.0 - 1.0)
                buy_amount = capital * weight
                fee = buy_amount * self.fee_pct
                position = (buy_amount - fee) / current_price
                capital -= buy_amount
                trades.append({"type": "BUY", "price": current_price, "date": current_row.name})
                
            elif signal == "SELL" and position > 0:
                sell_value = position * current_price
                fee = sell_value * self.fee_pct
                capital += (sell_value - fee)
                position = 0
                trades.append({"type": "SELL", "price": current_price, "date": current_row.name})
            
            # 3. Ghi nhận Equity
            current_equity = capital + (position * current_price)
            equity_curve.append(current_equity)

        return self._calculate_metrics(equity_curve, trades)

    def _calculate_metrics(self, equity_curve, trades):
        returns = pd.Series(equity_curve).pct_change().dropna()
        total_return = (equity_curve[-1] / self.initial_capital) - 1
        
        # Sharpe Ratio (Giả định risk-free rate = 0)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252*24) if returns.std() != 0 else 0
        
        # Drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / peak
        max_dd = drawdown.min()

        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "win_rate": self._calculate_win_rate(trades),
            "total_trades": len(trades),
            "equity_curve": equity_curve
        }

    def _calculate_win_rate(self, trades):
        if len(trades) < 2: return 0
        # Logic tính win rate từ các cặp BUY/SELL
        wins = 0
        for i in range(0, len(trades)-1, 2):
            if i+1 < len(trades):
                if trades[i+1]['price'] > trades[i]['price']: wins += 1
        return wins / (len(trades)/2) if len(trades) > 0 else 0
