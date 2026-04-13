"""
LEARNING DATA MANAGER - FIXED LOGIC
=================================
Logic đúng:
- LƯU decisions SAU KHI CÓ OUTCOME (hoặc từ backtest)
- HOẶC tạo OUTCOME từ BACKTEST trước
- SAU ĐÓ MỚI học từ decisions có outcome
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class FixedLearningDataManager:
    """
    Learning data manager với logic đúng:
    1. Lưu decision sau khi đã có outcome (backtest hoặc trade xong)
    2. HOẶC tạo outcome bằng cách chạy backtest trước
    """
    
    def __init__(self, memory_dir: str = "memory/"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
        self.history_file = os.path.join(memory_dir, "decision_history.json")
        self.load()
    
    def load(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"decisions": [], "outcomes": []}
    
    def save(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    # ============== METHOD 1: RECORD WITH OUTCOME (từ backtest hoặc trade xong) ==============
    
    def record_decision_with_outcome(self, 
                                timestamp: str,
                                price_in: float,
                                price_out: float,
                                decision: str,  # BUY/SELL
                                indicators: Dict) -> Dict:
        """
        Ghi decision ĐÃ CÓ OUTCOME
        ĐÂY LÀ METHOD ĐÚNG!
        """
        pnl_pct = 0
        outcome = "HOLD"
        
        if decision == "BUY" and price_out > 0:
            pnl_pct = ((price_out - price_in) / price_in) * 100
            outcome = "PROFIT" if pnl_pct > 0 else "LOSS"
        
        record = {
            "timestamp": timestamp,
            "price_in": price_in,
            "price_out": price_out,
            "decision": decision,
            "outcome": outcome,
            "pnl_pct": pnl_pct,
            "indicators": indicators,
            "has_outcome": True  # QUAN TRỌNG!
        }
        
        self.data["decisions"].append(record)
        self.data["decisions"] = self.data["decisions"][-500:]  # Keep last 500
        self.save()
        
        return record
    
    # ============== METHOD 2: BACKTEST TO CREATE OUTCOMES ==============
    
    def run_backtest_and_learn(self, df, strategy) -> List[Dict]:
        """
        CHẠY BACKTEST để tạo decisions WITH OUTCOMES
        Sau đó lưu vào history để học
        """
        if df is None or len(df) < 30:
            return []
        
        decisions = []
        
        # Simple RSI backtest
        close = df['close']
        
        for i in range(14, len(df) - 1):
            # Entry
            entry_price = close.iloc[i]
            date_in = str(df.index[i])
            
            # RSI calculation
            delta = close.diff()
            gain = delta.where(delta > 0, 0)
            loss = (-delta).where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean().iloc[i]
            avg_loss = loss.rolling(14).mean().iloc[i]
            
            if avg_loss == 0:
                continue
            rsi = 100 - (100 / (1 + avg_gain / avg_loss))
            
            # Decision based on RSI
            if rsi < 30:
                decision = "BUY"
            elif rsi > 70:
                decision = "SELL"
            else:
                continue
            
            # Exit (next period)
            if i + 1 < len(df):
                exit_price = close.iloc[i + 1]
                date_out = str(df.index[i + 1])
                
                # Record with OUTCOME (từ backtest)
                rec = self.record_decision_with_outcome(
                    timestamp=date_in,
                    price_in=entry_price,
                    price_out=exit_price,
                    decision=decision,
                    indicators={"rsi_entry": rsi}
                )
                decisions.append(rec)
        
        return decisions
    
    # ============== METHOD 3: HỌC TỪ DECISIONS CÓ OUTCOME ==============
    
    def learn(self) -> Dict:
        """
        HỌC từ decisions đã có outcome
        """
        decisions = [d for d in self.data["decisions"] if d.get("has_outcome")]
        
        if len(decisions) < 5:
            return {"message": "Chưa đủ data để học", "count": len(decisions)}
        
        # Phân tích
        profitable = [d for d in decisions if d.get("outcome") == "PROFIT"]
        losing = [d for d in decisions if d.get("outcome") == "LOSS"]
        
        # Tìm RSI ranges có lãi
        rsi_profit = [d["indicators"]["rsi_entry"] for d in profitable if "rsi_entry" in d.get("indicators", {})]
        rsi_loss = [d["indicators"]["rsi_entry"] for d in losing if "rsi_entry" in d.get("indicators", {})]
        
        learned = {
            "total_decisions": len(decisions),
            "profitable": len(profitable),
            "losing": len(losing),
            "win_rate": len(profitable) / len(decisions),
            "best_rsi_buy_range": (min(rsi_profit), max(rsi_profit)) if rsi_profit else (0, 30),
            "worst_rsi_buy_range": (min(rsi_loss), max(rsi_loss)) if rsi_loss else (0, 30)
        }
        
        return learned
    
    # ============== METHOD 4: QUYẾT ĐỊNH DỰA TRÊN LEARNED ==============
    
    def should_decide(self, rsi: float) -> Dict:
        """
        Dùng learned rules để quyết định
        """
        learned = self.learn()
        
        if "best_rsi_buy_range" in learned:
            min_rsi, max_rsi = learned["best_rsi_buy_range"]
            
            if rsi < min_rsi:
                return {"decision": "BUY", "reason": f"RSI {rsi:.0f} < {min_rsi:.0f} (learned profitable zone)"}
            elif rsi > max_rsi + 20:
                return {"decision": "SELL", "reason": f"RSI {rsi:.0f} > {max_rsi + 20}"}
        
        return {"decision": "HOLD", "reason": "Chưa có learned data - using default"}


# Singleton
_ldm = None

def get_fixed_learning_manager():
    global _ldm
    if _ldm is None:
        _ldm = FixedLearningDataManager()
    return _ldm