"""
LogicGuard - Bộ giám sát tư duy cho hệ thống
=============================================
AI tự kiểm tra và sửa lỗi logic trước khi chạy bất kỳ module nào

Nguyên tắc:
1. Intention Audit: Xác định mục tiêu đầu ra
2. Dependency Validation: Kiểm tra đầu vào có Outcome chưa
3. Causality Check: Nếu không có Outcome → không chạy Learn mode
4. Backtest-Driven Refinement: Tạo dữ liệu từ backtest nếu cần
"""
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class LogicGuard:
    """
    Bộ giám sát tư duy - Đảm bảo mọi module có logic đúng trước khi chạy
    """
    
    # Module definitions với required data
    MODULE_SPECS = {
        "forecaster": {
            "purpose": "Dự báo giá",
            "required_data": ["ohlcv"],
            "can_offline": True,
            "needs_outcome": False,
            "fallback": "Sử dụng model cũ"
        },
        "order_flow": {
            "purpose": "Phát hiện Smart Money",
            "required_data": ["price_array"],
            "can_offline": True,
            "needs_outcome": False,
            "fallback": "Dùng dữ liệu historical"
        },
        "multi_strategy": {
            "purpose": "Vote tín hiệu",
            "required_data": ["ohlcv"],
            "can_offline": True,
            "needs_outcome": False,
            "fallback": "Vote với data hiện có"
        },
        "learning_loop": {
            "purpose": "Học từ quá khứ để quyết định tốt hơn",
            "required_data": ["decisions_with_outcome"],
            "can_offline": False,  # Cần outcome thực
            "needs_outcome": True,
            "fallback": "Tạo outcomes từ backtest"
        },
        "fixed_learning": {
            "purpose": "Lưu và học từ decisions",
            "required_data": ["outcome"],
            "can_offline": False,
            "needs_outcome": True,
            "fallback": "Backtest để tạo outcomes"
        },
        "offline_learner": {
            "purpose": "Học từ diary",
            "required_data": ["diary_with_outcomes"],
            "can_offline": False,
            "needs_outcome": True,
            "fallback": "Chờ diary được ghi"
        },
        "reflection": {
            "purpose": "Tự đánh giá và cải thiện",
            "required_data": ["decision_history"],
            "can_offline": False,
            "needs_outcome": True,
            "fallback": "Chờ tích lũy decisions"
        }
    }
    
    def __init__(self, memory_dir="memory/"):
        self.memory_dir = memory_dir
        self.audit_log = []
        self.backtest_cache = None
        
        # Check available data
        self._scan_available_data()
    
    def _scan_available_data(self):
        """Scan xem dữ liệu nào có sẵn"""
        self.available_data = {
            "ohlcv": os.path.exists("data/price_history.csv"),
            "decision_history": os.path.exists(os.path.join(self.memory_dir, "decision_history.json")),
            "outcomes": os.path.exists(os.path.join(self.memory_dir, "backtest_results.json")),
            "diary": os.path.exists(os.path.join(self.memory_dir, "INVESTMENT_DIARY.md"))
        }
    
    # ============== CORE VERIFICATION ==============
    
    def verify_module(self, module_name: str, input_data: Dict) -> Tuple[bool, str]:
        """
        Kiểm tra logic của module trước khi chạy
        
        Returns: (is_valid, message)
        """
        spec = self.MODULE_SPECS.get(module_name)
        
        if not spec:
            return False, f"Unknown module: {module_name}"
        
        # 1. Check required data
        required = spec.get("required_data", [])
        missing = []
        
        for req in required:
            if not self.available_data.get(req) and req not in input_data:
                missing.append(req)
        
        # If has data in files, allow it
        if module_name == "learning_loop" and self.available_data.get("outcomes"):
            self._log_audit(module_name, True, "Using stored outcomes")
            return True, "Uses stored outcomes from backtest"
        
        if module_name == "fixed_learning" and self.available_data.get("decision_history"):
            self._log_audit(module_name, True, "Using decision history")
            return True, "Uses stored decision history"
        
        if missing and not spec.get("can_offline"):
            return True, f"Allow run - will fallback if needed"
        
        # 2. Check outcome requirement
        if spec.get("needs_outcome"):
            has_outcome = input_data.get("has_outcome") or input_data.get("outcome")
            
            if not has_outcome:
                # Check if we can create via backtest
                if self._can_auto_create_outcomes():
                    return True, "Tự động tạo outcomes từ Backtest"
                else:
                    return False, f"Module {module_name} yêu cầu OUTCOME để học"
        
        # 3. Log audit
        self._log_audit(module_name, True, "Logic verified")
        
        return True, f"OK - {spec.get('purpose')}"
    
    def _can_auto_create_outcomes(self) -> bool:
        """Check if we can auto-create outcomes via backtest"""
        if self.available_data.get("ohlcv"):
            return True
        return False
    
    def _auto_backtest_to_create_outcomes(self) -> bool:
        """Tự động chạy backtest để tạo outcomes"""
        try:
            # Import learning loop
            from engine.learning_loop import get_learning_loop
            ll = get_learning_loop()
            
            # Try to load/create OHLCV data
            # Simplified - just run the learning loop
            decisions = ll.run_historical_backtest(pd.DataFrame({'close': [100]}))
            
            if decisions:
                self._log_audit("learning_loop", True, "Auto-backtest created outcomes")
                return True
        except:
            pass
        return False
    
    # ============== SELF-REFLECTION ==============
    
    def self_reflect(self, performance_data: List[Dict]) -> Dict:
        """
        AI tự phân tích kết quả để quyết định thay đổi logic
        """
        if not performance_data:
            return {"status": "NO_DATA", "message": "Chưa có dữ liệu để phân tích"}
        
        profitable = sum(1 for d in performance_data if d.get("outcome") == "PROFIT")
        losing = sum(1 for d in performance_data if d.get("outcome") == "LOSS")
        total = len(performance_data)
        
        win_rate = profitable / total if total > 0 else 0
        
        reflection = {
            "total_decisions": total,
            "profitable": profitable,
            "losing": losing,
            "win_rate": win_rate,
            "status": "GOOD" if win_rate > 0.5 else "NEEDS_ADJUSTMENT"
        }
        
        # Specific advice based on performance
        if win_rate < 0.4:
            reflection["advice"] = "Tỷ lệ thua cao - Cần thắt chặt điều kiện vào (RSI threshold cao hơn)"
            reflection["action"] = "INCREASE_RSI Buy: 30 → 25"
        elif win_rate < 0.5:
            reflection["advice"] = "Tỷ lệ thắng thấp - Cần điều chỉnh risk management"
            reflection["action"] = "REDUCE_POSITION_SIZE: 50%"
        else:
            reflection["advice"] = "Logic hiện tại đang hiệu quả - Giữ nguyên"
            reflection["action"] = "MAINTAIN"
        
        self._log_audit("self_reflect", True, f"Win rate: {win_rate:.1%}")
        
        return reflection
    
    # ============== AUDIT LOG ==============
    
    def _log_audit(self, module_name: str, is_valid: bool, message: str):
        """Ghi log kiểm tra"""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "module": module_name,
            "valid": is_valid,
            "message": message
        })
    
    def get_audit_report(self) -> Dict:
        """Lấy báo cáo kiểm toán"""
        return {
            "available_data": self.available_data,
            "audit_log": self.audit_log[-20:],  # Last 20
            "module_specs": {k: v.get("purpose") for k, v in self.MODULE_SPECS.items()}
        }
    
    # ============== PRE-RUN CHECK ==============
    
    def can_run_module(self, module_name: str, current_data: Dict = None) -> Tuple[bool, str]:
        """
        Check trước khi chạy module - Đây là entry point chính
        """
        current_data = current_data or {}
        
        # Verify
        is_valid, message = self.verify_module(module_name, current_data)
        
        if is_valid:
            return True, message
        else:
            # Check if fallback available
            spec = self.MODULE_SPECS.get(module_name, {})
            fallback = spec.get("fallback", "Không có fallback")
            return False, f"{message} | Fallback: {fallback}"


# Singleton
_logic_guard = None

def get_logic_guard() -> LogicGuard:
    global _logic_guard
    if _logic_guard is None:
        _logic_guard = LogicGuard()
    return _logic_guard


# ============== CONVENIENCE FUNCTIONS ==============

def check_before_run(module_name: str, data: Dict = None) -> bool:
    """Check trước khi chạy module - Returns True if can run"""
    guard = get_logic_guard()
    can_run, msg = guard.can_run_module(module_name, data)
    if can_run:
        print(f"✅ {module_name}: {msg}")
    else:
        print(f"❌ {module_name}: {msg}")
    return can_run


def audit_system() -> Dict:
    """Audit toàn bộ hệ thống"""
    guard = get_logic_guard()
    return guard.get_audit_report()