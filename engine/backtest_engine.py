"""
GIAI ĐOẠN 2: Backtest Engine tạo Outcome
=========================================
Module này lấy dữ liệu OHLCV → chạy backtest → tạo decisions WITH outcomes
Lưu vào memory/learning_base.json
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class BacktestEngine:
    """
    Backtest Engine - Tạo dữ liệu học với OUTCOMES
    """
    
    def __init__(self, memory_dir="memory/"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        self.output_file = os.path.join(memory_dir, "learning_base.json")
        
    def run(self, 
            price_data: pd.DataFrame,
            initial_capital: float = 10000,
            rsi_oversold: int = 30,
            rsi_overbought: int = 70) -> Dict:
        """
        Chạy backtest và tạo learning data với OUTCOMES
        """
        if price_data is None or len(price_data) < 30:
            return {"status": "ERROR", "message": "Insufficient data"}
        
        # Ensure required columns
        if 'close' not in price_data.columns:
            return {"status": "ERROR", "message": "Need close price"}
        
        close = price_data['close']
        
        # Calculate RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Simulate trades
        decisions = []
        capital = initial_capital
        position = 0  # 0 = no position, 1 = long
        entry_price = 0
        entry_rsi = 0
        entry_date = None
        
        for i in range(14, len(price_data)):
            current_rsi = rsi.iloc[i]
            current_price = close.iloc[i]
            current_date = str(price_data.index[i])
            
            if pd.isna(current_rsi):
                continue
            
            # BUY signal
            if current_rsi < rsi_oversold and position == 0:
                position = 1
                entry_price = current_price
                entry_rsi = current_rsi
                entry_date = current_date
                entry_capital = capital
                
            # SELL signal (take profit or stop loss or RSI overbought)
            elif position == 1:
                # Exit conditions
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                should_exit = (
                    current_rsi > rsi_overbought or  # RSI overbought
                    pnl_pct > 5 or  # Take profit 5%
                    pnl_pct < -3  # Stop loss 3%
                )
                
                if should_exit:
                    outcome = "PROFIT" if pnl_pct > 0 else "LOSS"
                    
                    # SAVE DECISION WITH OUTCOME (CRITICAL!)
                    decision = {
                        "timestamp": entry_date,
                        "exit_date": current_date,
                        "entry_price": entry_price,
                        "exit_price": current_price,
                        "entry_rsi": entry_rsi,
                        "exit_rsi": current_rsi,
                        "decision": "BUY",
                        "outcome": outcome,
                        "pnl_pct": pnl_pct,
                        "capital_before": entry_capital,
                        "capital_after": capital * (1 + pnl_pct/100),
                        "holding_period": i - price_data.index.get_loc(pd.Timestamp(entry_date)),
                        # Input parameters used
                        "rsi_oversold": rsi_oversold,
                        "rsi_overbought": rsi_overbought
                    }
                    
                    decisions.append(decision)
                    
                    # Update capital
                    capital = capital * (1 + pnl_pct/100)
                    position = 0
        
        # Save to learning base
        result = {
            "created_at": datetime.now().isoformat(),
            "total_trades": len(decisions),
            "initial_capital": initial_capital,
            "final_capital": capital,
            "total_return_pct": ((capital - initial_capital) / initial_capital) * 100,
            "decisions": decisions
        }
        
        # Save
        with open(self.output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        return result
    
    def get_learning_data(self) -> Dict:
        """Lấy dữ liệu học đã tạo"""
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                return json.load(f)
        return {"decisions": []}
    
    def has_sufficient_data(self, min_trades: int = 50) -> bool:
        """Kiểm tra có đủ data để học chưa"""
        data = self.get_learning_data()
        return len(data.get("decisions", [])) >= min_trades


# Singleton
_backtest_engine = None

def get_backtest_engine() -> BacktestEngine:
    global _backtest_engine
    if _backtest_engine is None:
        _backtest_engine = BacktestEngine()
    return _backtest_engine


def run_backtest_and_create_outcomes(price_data: pd.DataFrame = None) -> Dict:
    """
    Main function: Lấy price data → Run backtest → Create outcomes
    """
    bt = get_backtest_engine()
    
    # Use provided data or try to load from file
    if price_data is None:
        # Try to load price history
        if os.path.exists("data/price_history.csv"):
            price_data = pd.read_csv("data/price_history.csv", parse_dates=['date'], index_col='date')
        else:
            # Generate synthetic data for demo
            dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
            price_data = pd.DataFrame({
                'close': 100 + np.cumsum(np.random.randn(200))
            }, index=dates)
    
    # Run backtest
    result = bt.run(price_data)
    
    return result