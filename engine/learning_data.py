"""
Learning Data Manager - Lưu dữ liệu quá khứ để học liên tục
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

class LearningDataManager:
    """
    Quản lý dữ liệu học từ quá khứ
    Lưu trữ tất cả decisions và outcomes để OfflineLearner học
    """
    
    def __init__(self, data_dir: str = "memory/"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.diary_path = os.path.join(data_dir, "INVESTMENT_DIARY.md")
        self.dca_history_path = os.path.join(data_dir, "dca_history.json")
        self.trade_history_path = os.path.join(data_dir, "trade_history.json")
        self.market_snapshot_path = os.path.join(data_dir, "market_snapshots.json")
        
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing data"""
        # DCA history
        if os.path.exists(self.dca_history_path):
            with open(self.dca_history_path, 'r') as f:
                self.dca_history = json.load(f)
        else:
            self.dca_history = {"dcas": [], "total_invested": 0}
        
        # Trade history
        if os.path.exists(self.trade_history_path):
            with open(self.trade_history_path, 'r') as f:
                self.trade_history = json.load(f)
        else:
            self.trade_history = {"trades": []}
    
    # ============== GHI LẠI DỮ LIỆU ==============
    
    def record_dca_decision(self, 
                       price: float,
                       action: str,  # BUY, HOLD, SELL
                       amount: float,
                       reason: Dict,
                       confidence: float,
                       ai_recommendation: str = None):
        """
        Ghi lại quyết định DCA
        Đây là dữ liệu quan trọng nhất để học!
        """
        timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "price": price,
            "action": action,
            "amount": amount,
            "confidence": confidence,
            "reason": reason,
            "ai_recommendation": ai_recommendation,
            "outcome": None,  # Will update later when we know result
            "profit_pct": None  # Will update later
        }
        
        # Add to history
        self.dca_history["dcas"].append(record)
        
        if action == "BUY":
            self.dca_history["total_invested"] = self.dca_history.get("total_invested", 0) + amount
        
        # Save
        self._save_dca_history()
        
        # Update diary
        self._append_to_diary(record)
        
        return record["timestamp"]
    
    def record_trade_result(self,
                      decision_timestamp: str,
                      exit_price: float,
                      result: str):  # PROFIT, LOSS, BREAK_EVEN
        """
        Ghi kết quả - cập nhật sau khi trade hoàn thành
        Quan trọng để học từ outcomes!
        """
        # Find the decision
        for dca in self.dca_history["dcas"]:
            if dca["timestamp"] == decision_timestamp:
                dca["outcome"] = result
                dca["exit_price"] = exit_price
                dca["exit_timestamp"] = datetime.now().isoformat()
                
                if dca.get("action") == "BUY":
                    entry = dca.get("price", 0)
                    if entry > 0:
                        dca["profit_pct"] = ((exit_price - entry) / entry) * 100
                
                break
        
        self._save_dca_history()
    
    def record_market_snapshot(self,
                        price: float,
                        indicators: Dict):
        """
        Lưu market snapshot mỗi ngày
        Để Backtest học patterns
        """
        timestamp = datetime.now().isoformat()
        
        snapshot = {
            "timestamp": timestamp,
            "price": price,
            "indicators": indicators
        }
        
        # Load existing
        if os.path.exists(self.market_snapshot_path):
            with open(self.market_snapshot_path, 'r') as f:
                snapshots = json.load(f)
        else:
            snapshots = []
        
        snapshots.append(snapshot)
        
        # Keep only last 1000
        if len(snapshots) > 1000:
            snapshots = snapshots[-1000:]
        
        # Save
        with open(self.market_snapshot_path, 'w') as f:
            json.dump(snapshots, f, indent=2)
    
    def record_backtest_result(self,
                     strategy: str,
                     metrics: Dict):
        """
        Lưu kết quả backtest để WalkForward học
        """
        backtest_dir = "memory/backtest_results"
        os.makedirs(backtest_dir, exist_ok=True)
        
        filename = f"{backtest_dir}/{strategy}_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "strategy": strategy,
                "metrics": metrics
            }, f, indent=2)
    
    # ============== LẤY DỮ LIỆU HỌC ==============
    
    def get_decisions_for_learning(self) -> List[Dict]:
        """Lấy tất cả decisions có outcome để học"""
        learned = []
        for dca in self.dca_history.get("dcas", []):
            if dca.get("outcome") is not None:  # Has result
                learned.append(dca)
        return learned
    
    def get_profitable_decisions(self) -> List[Dict]:
        """Lấy các quyết định có lãi"""
        return [d for d in self.get_decisions_for_learning() 
                if d.get("outcome") == "PROFIT"]
    
    def get_losing_decisions(self) -> List[Dict]:
        """Lấy các quyết định có lỗ"""
        return [d for d in self.get_decisions_for_learning() 
                if d.get("outcome") == "LOSS"]
    
    def get_stats(self) -> Dict:
        """Thống kê học từ dữ liệu"""
        decisions = self.get_decisions_for_learning()
        
        if not decisions:
            return {"total_decisions": 0, "message": "Chưa có dữ liệu học"}
        
        profits = len([d for d in decisions if d.get("outcome") == "PROFIT"])
        losses = len([d for d in decisions if d.get("outcome") == "LOSS"])
        
        profit_pcts = [d.get("profit_pct", 0) for d in decisions if d.get("profit_pct")]
        avg_profit = sum(profit_pcts) / len(profit_pcts) if profit_pcts else 0
        
        return {
            "total_decisions": len(decisions),
            "profitable": profits,
            "losing": losses,
            "win_rate": profits / len(decisions) if decisions else 0,
            "avg_profit_pct": avg_profit
        }
    
    # ============== INTERNAL ==============
    
    def _save_dca_history(self):
        """Save DCA history"""
        with open(self.dca_history_path, 'w') as f:
            json.dump(self.dca_history, f, indent=2)
    
    def _append_to_diary(self, record: Dict):
        """Append to markdown diary"""
        timestamp = record["timestamp"]
        price = record["price"]
        action = record["action"]
        confidence = record["confidence"]
        
        with open(self.diary_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## {timestamp}\n")
            f.write(f"- **Action**: {action}\n")
            f.write(f"- **Price**: ${price}\n")
            f.write(f"- **Confidence**: {confidence*100:.0f}%\n")
            f.write(f"- **Reason**: {record.get('reason', {})}\n")
            if record.get("ai_recommendation"):
                f.write(f"- **AI**: {record['ai_recommendation']}\n")


# Singleton
_ldm = None

def get_learning_manager() -> LearningDataManager:
    global _ldm
    if _ldm is None:
        _ldm = LearningDataManager()
    return _ldm


# ============== AUTO-SAVE ==============

def auto_record_daily(price: float, indicators: Dict):
    """
    Gọi mỗi ngày để lưu market snapshot
    """
    ldm = get_learning_manager()
    ldm.record_market_snapshot(price, indicators)


def auto_record_decision(price: float, action: str, amount: float, 
                    reason: Dict, confidence: float, ai_rec: str = None):
    """
    Gọi khi có quyết định DCA
    """
    ldm = get_learning_manager()
    return ldm.record_dca_decision(price, action, amount, reason, confidence, ai_rec)


def auto_record_result(decision_ts: str, exit_price: float, result: str):
    """
    Gọi khi trade hoàn thành
    """
    ldm = get_learning_manager()
    ldm.record_trade_result(decision_ts, exit_price, result)