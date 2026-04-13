"""
Learning Loop Logic - Đúng cách để hệ thống học từ quá khứ

FLOW ĐÚNG:
1. BACKTEST trên historical data → tạo decisions + outcomes
2. PHÂN TÍCH patterns từ profitable decisions  
3. TỐI ƯU params dựa trên outcomes
4. DÙNG learned params cho decisions mới
5. CẬP NHẬT outcome sau mỗi trade → học thêm
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from itertools import product

class LearningLoop:
    """
    Vòng lặp học đúng logic cho DCA
    """
    
    def __init__(self, memory_dir="memory/"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
        # Files
        self.backtest_results = os.path.join(memory_dir, "backtest_results.json")
        self.patterns_file = os.path.join(memory_dir, "learned_patterns.json")
        self.params_file = os.path.join(memory_dir, "optimized_params.json")
        
        # Learned data
        self.learned_patterns = self._load_patterns()
        self.optimized_params = self._load_params()
    
    def _load_patterns(self) -> Dict:
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {"profitable_signals": [], "losing_signals": [], "patterns": []}
    
    def _load_params(self) -> Dict:
        if os.path.exists(self.params_file):
            with open(self.params_file, 'r') as f:
                return json.load(f)
        return {"rsi_oversold": 30, "rsi_overbought": 70, "ma_fast": 9, "ma_slow": 21}
    
    # ============== BƯỚC 1: BACKTEST ĐỂ TẠO OUTCOMES ==============
    
    def run_historical_backtest(self, df: pd.DataFrame, 
                           strategy_params: Dict = None) -> List[Dict]:
        """
        Chạy backtest trên dữ liệu quá khứ để tạo decisions + outcomes
        ĐÂY LÀ BƯỚC QUAN TRỌNG NHẤT để có data học!
        """
        if df is None or len(df) < 60:
            return []
        
        params = strategy_params or self.optimized_params
        decisions = []
        
        # Simple RSI strategy backtest
        rsi_window = params.get("rsi_window", 14)
        oversold = params.get("rsi_oversold", 30)
        overbought = params.get("rsi_overbought", 70)
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        avg_gain = gain.rolling(rsi_window).mean()
        avg_loss = loss.rolling(rsi_window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Simulate trades
        position = 0
        entry_price = 0
        
        for i in range(rsi_window, len(df)):
            current_rsi = rsi.iloc[i]
            price = df['close'].iloc[i]
            date = df.index[i]
            
            if pd.isna(current_rsi):
                continue
            
            # BUY signal
            if current_rsi < oversold and position == 0:
                position = 1
                entry_price = price
                entry_date = date
                
            # SELL signal  
            elif current_rsi > overbought and position == 1:
                pnl_pct = ((price - entry_price) / entry_price) * 100
                
                # Decision với OUTCOME!
                decision = {
                    "timestamp": str(entry_date),
                    "entry_price": entry_price,
                    "exit_price": price,
                    "exit_date": str(date),
                    "action": "BUY",
                    "rsi_entry": current_rsi,
                    "outcome": "PROFIT" if pnl_pct > 0 else "LOSS",
                    "profit_pct": pnl_pct
                }
                decisions.append(decision)
                
                position = 0
        
        # Save backtest results
        self._save_backtest_results(decisions)
        
        return decisions
    
    def _save_backtest_results(self, decisions: List[Dict]):
        """Lưu backtest results để học"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_decisions": len(decisions),
            "decisions": decisions
        }
        with open(self.backtest_results, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # ============== BƯỚC 2: PHÂN TÍCH PATTERNS ==============
    
    def learn_from_history(self, df: pd.DataFrame = None):
        """
        HỌC từ quá khứ:
        1. Chạy backtest → tạo decisions + outcomes
        2. Phân tích patterns có lãi vs lỗ
        3. Tối ưu parameters
        """
        # B1: Run backtest
        if df is not None:
            decisions = self.run_historical_backtest(df)
            if not decisions:
                return {"message": "Không đủ data để backtest"}
        
        # Load decisions
        if not os.path.exists(self.backtest_results):
            return {"message": "Chưa có backtest results"}
        
        with open(self.backtest_results, 'r') as f:
            data = json.load(f)
        
        decisions = data.get("decisions", [])
        if not decisions:
            return {"message": "Không có decisions để học"}
        
        # B2: Phân tích patterns
        profitable = [d for d in decisions if d.get("outcome") == "PROFIT"]
        losing = [d for d in decisions if d.get("outcome") == "LOSS"]
        
        # Tìm RSI ranges có lãi
        if profitable:
            avg_rsi_profit = np.mean([d.get("rsi_entry", 50) for d in profitable])
        else:
            avg_rsi_profit = 50
        
        if losing:
            avg_rsi_loss = np.mean([d.get("rsi_entry", 50) for d in losing])
        else:
            avg_rsi_loss = 50
        
        # Tối ưu parameters
        new_params = {
            "rsi_oversold": int(avg_rsi_profit) - 5 if avg_rsi_profit < 50 else 25,
            "rsi_overbought": int(avg_rsi_loss) + 5 if avg_rsi_loss > 50 else 75,
            "rsi_window": 14
        }
        
        # Lưu learned patterns
        self.learned_patterns = {
            "profitable_signals": [d for d in profitable[:10]],
            "losing_signals": [d for d in losing[:10]],
            "avg_rsi_profit": avg_rsi_profit,
            "avg_rsi_loss": avg_rsi_loss,
            "win_rate": len(profitable) / len(decisions) if decisions else 0
        }
        
        # Save
        with open(self.patterns_file, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2, default=str)
        
        with open(self.params_file, 'w') as f:
            json.dump(new_params, f, indent=2)
        
        return {
            "total_decisions": len(decisions),
            "profitable": len(profitable),
            "losing": len(losing),
            "win_rate": self.learned_patterns["win_rate"],
            "optimized_params": new_params
        }
    
    # ============== BƯỚC 3: DÙNG LEARNED ==============
    
    def get_optimized_params(self) -> Dict:
        """Lấy params đã tối ưu từ quá khứ"""
        return self.optimized_params
    
    def should_buy(self, rsi: float) -> bool:
        """
        Dùng patterns đã học để quyết định
        """
        if not self.learned_patterns.get("profitable_signals"):
            return rsi < 35  # Default fallback
        
        avg_rsi = self.learned_patterns.get("avg_rsi_profit", 35)
        return rsi < avg_rsi
    
    def should_sell(self, rsi: float) -> bool:
        """Dùng patterns đã học để quyết định"""
        if not self.learned_patterns.get("losing_signals"):
            return rsi > 65  # Default fallback
        
        avg_rsi = self.learned_patterns.get("avg_rsi_loss", 65)
        return rsi > avg_rsi
    
    # ============== BƯỚC 4: UPDATE SAU MỖI TRADE ==============
    
    def record_outcome(self, entry_price: float, exit_price: float, 
                   entry_rsi: float, date):
        """
        Cập nhật outcome sau mỗi trade thực tế
        """
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        outcome = "PROFIT" if pnl_pct > 0 else "LOSS"
        
        # Load existing
        if os.path.exists(self.backtest_results):
            with open(self.backtest_results, 'r') as f:
                data = json.load(f)
            decisions = data.get("decisions", [])
        else:
            decisions = []
        
        # Add new outcome
        decisions.append({
            "timestamp": str(date),
            "entry_price": entry_price,
            "exit_price": exit_price,
            "action": "BUY",
            "rsi_entry": entry_rsi,
            "outcome": outcome,
            "profit_pct": pnl_pct
        })
        
        # Save
        data["decisions"] = decisions[-100:]  # Keep last 100
        with open(self.backtest_results, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        # Re-learn periodically
        if len(decisions) % 10 == 0:
            self.learn_from_history()
        
        return outcome


# Singleton
_learning_loop = None

def get_learning_loop() -> LearningLoop:
    global _learning_loop
    if _learning_loop is None:
        _learning_loop = LearningLoop()
    return _learning_loop