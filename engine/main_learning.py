"""
GIAI ĐOẠN 4: Main.py với đầy đủ luồng dữ liệu
============================================
Luồng chuẩn:
1. Setup Wizard (kiểm tra API)
2. Backtest Engine (tạo learning base)
3. Offline Learner (rút rules)
4. Real-time Decision (AIBrain)
5. Periodic Update (cập nhật outcomes)
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from engine.setup_wizard import SetupWizard
from engine.ai_brain import AIBrain
from engine.learning_loop import get_learning_loop
from engine.learning_data import auto_record_decision
from engine.logic_guard import get_logic_guard

class QuantFundWithLearning:
    """
    Quant Fund với Self-Correction Loop
    """
    
    def __init__(self):
        # GIAI ĐOẠN 1: Setup & Verify
        print("="*50)
        print("GIAI DOAN 1: KHOI TAO & KIEM TRA")
        print("="*50)
        
        # Check API config
        self.wizard = SetupWizard()
        status = self.wizard.check_status()
        
        if not status.get('ai_provider'):
            print("Chua cau hinh AI Provider!")
        
        # Logic Guard
        self.logic_guard = get_logic_guard()
        
        # Check learning capability
        can_run, msg = self.logic_guard.can_run_module('learning_loop', {})
        print(f"Learning module: {msg}")
        
        # GIAI ĐOẠN 2: Backtest to Create Outcomes
        print()
        print("="*50)
        print("GIAI DOAN 2: TAO LEARNING DATA")
        print("="*50)
        
        self._create_learning_base()
        
        # GIAI ĐOẠN 3: Learn Rules
        print()
        print("="*50)
        print("GIAI DOAN 3: RUT TRIC QUY TAC")
        print("="*50)
        
        self._learn_rules()
        
        # GIAI ĐOẠN 4: Ready for Decision
        print()
        print("="*50)
        print("SAN SANG CHO QUYET DINH")
        print("="*50)
        
    def _create_learning_base(self):
        """Chạy backtest để tạo outcomes"""
        try:
            from engine.backtest_engine import get_backtest_engine
            
            bt = get_backtest_engine()
            
            # Generate or load price data
            dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
            price_data = pd.DataFrame({
                'close': 100 + np.cumsum(np.random.randn(200))
            }, index=dates)
            
            result = bt.run(price_data)
            
            print(f"Backtest: {result.get('total_trades', 0)} trades created")
            print(f"Win rate: {self._calculate_win_rate(result.get('decisions', [])):.1%}")
            
            return result
        except Exception as e:
            print(f"Backtest error: {e}")
            return {"status": "ERROR"}
    
    def _calculate_win_rate(self, decisions: list) -> float:
        """Tính win rate từ decisions"""
        if not decisions:
            return 0
        wins = sum(1 for d in decisions if d.get('outcome') == 'PROFIT')
        return wins / len(decisions)
    
    def _learn_rules(self):
        """Rút quy tắc từ learning base"""
        try:
            from engine.backtest_engine import get_backtest_engine
            
            bt = get_backtest_engine()
            data = bt.get_learning_data()
            
            decisions = data.get('decisions', [])
            
            if len(decisions) < 10:
                print("Chua du du lieu de hoc")
                return
            
            # Analyze patterns
            profitable = [d for d in decisions if d.get('outcome') == 'PROFIT']
            losing = [d for d in decisions if d.get('outcome') == 'LOSS']
            
            # Find RSI ranges
            rsi_profit = [d['entry_rsi'] for d in profitable if 'entry_rsi' in d]
            rsi_loss = [d['entry_rsi'] for d in losing if 'entry_rsi' in d]
            
            if rsi_profit:
                avg_profit = sum(rsi_profit) / len(rsi_profit)
                print(f"Avg RSI for PROFIT: {avg_profit:.1f}")
            
            if rsi_loss:
                avg_loss = sum(rsi_loss) / len(rsi_loss)
                print(f"Avg RSI for LOSS: {avg_loss:.1f}")
            
            print(f"Learning rules extracted from {len(decisions)} decisions")
            
        except Exception as e:
            print(f"Learn error: {e}")
    
    def run_decision(self, market_data: Dict) -> Dict:
        """
        GIAI ĐOẠN 4: Ra quyết định với Logic Guard
        """
        # Verify with Logic Guard
        can_run, msg = self.logic_guard.can_run_module('learning_loop', market_data)
        
        if not can_run:
            return {
                "decision": "HOLD",
                "reason": f"Logic Guard: {msg}",
                "status": "BLOCKED"
            }
        
        # Make decision using learned rules
        from engine.backtest_engine import get_backtest_engine
        bt = get_backtest_engine()
        
        # Get RSI from market data
        rsi = market_data.get('rsi', 50)
        
        # Use learned thresholds
        data = bt.get_learning_data()
        decisions = data.get('decisions', [])
        
        if decisions:
            # Find best RSI threshold from profitable trades
            profitable = [d for d in decisions if d.get('outcome') == 'PROFIT']
            if profitable:
                avg_rsi = sum(d['entry_rsi'] for d in profitable) / len(profitable)
                
                if rsi < avg_rsi:
                    return {
                        "decision": "BUY",
                        "reason": f"RSI {rsi:.1f} < {avg_rsi:.1f} (learned threshold)",
                        "source": "LEARNED"
                    }
        
        # Default fallback
        if rsi < 30:
            return {"decision": "BUY", "reason": "RSI oversold", "source": "DEFAULT"}
        elif rsi > 70:
            return {"decision": "SELL", "reason": "RSI overbought", "source": "DEFAULT"}
        
        return {"decision": "HOLD", "reason": "No clear signal", "source": "DEFAULT"}


# Run full flow
if __name__ == "__main__":
    print("="*60)
    print("QUANT FUND WITH SELF-CORRECTION LOOP")
    print("="*60)
    print()
    
    # Initialize
    fund = QuantFundWithLearning()
    
    # Test decision
    print()
    print("TEST DECISION:")
    result = fund.run_decision({"rsi": 25, "price": 170})
    print(f"Decision: {result}")
    
    print()
    print("HOAN TAT!")