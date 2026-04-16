"""
Advanced Risk Engine - Quản trị rủi ro & Bảo vệ vốn
Bao gồm: Kelly Criterion, VaR, Stop-loss, Trailing Stop, Circuit Breakers, Session Limits
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class RiskEngine:
    """Bộ máy quản trị rủi ro cao cấp"""

    def __init__(
        self,
        initial_capital: float = 1000,
        max_drawdown_limit: float = 0.20,
        max_daily_loss_limit: float = 0.05,
    ):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_drawdown_limit = max_drawdown_limit
        self.max_daily_loss_limit = max_daily_loss_limit

        self.peak_capital = initial_capital
        self.daily_start_capital = initial_capital
        self.active_positions = {}

        # --- Session Limits (v4.1.0) ---
        self.consecutive_losses = 0
        self.daily_trade_count = 0
        self.max_daily_trades = 10
        self.max_consecutive_losses = 3
        self.cooldown_until = None
        self.daily_pnl = 0

    def check_trade_allowed(self) -> Dict:
        """
        Kiểm tra xem có được phép trade tiếp không (Session Limits)
        """
        now = datetime.now()

        # 1. Kiểm tra Cooldown
        if self.cooldown_until and now < self.cooldown_until:
            return {
                "allowed": False,
                "reason": "COOLDOWN_ACTIVE",
                "remaining": str(self.cooldown_until - now),
            }

        # 2. Kiểm tra Max Trades per Day
        if self.daily_trade_count >= self.max_daily_trades:
            return {"allowed": False, "reason": "MAX_DAILY_TRADES_EXCEEDED"}

        # 3. Kiểm tra Circuit Breakers (Daily Loss)
        if self.daily_pnl <= -(self.max_daily_loss_limit * self.daily_start_capital):
            return {"allowed": False, "reason": "DAILY_LOSS_LIMIT_HIT"}

        return {"allowed": True}

    def record_trade_result(self, pnl: float):
        """
        Ghi nhận kết quả giao dịch để cập nhật Session Limits
        """
        self.daily_trade_count += 1
        self.daily_pnl += pnl
        self.current_capital += pnl

        # Cập nhật Peak Capital cho Drawdown
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital

        # Kiểm tra chuỗi thua
        if pnl < 0:
            self.consecutive_losses += 1
            # Nếu thua 3 lệnh liên tiếp -> Cooldown 1h
            if self.consecutive_losses >= self.max_consecutive_losses:
                self.cooldown_until = datetime.now() + timedelta(hours=1)
                self.consecutive_losses = 0  # Reset sau khi kích hoạt cooldown
        else:
            self.consecutive_losses = 0  # Reset khi có lệnh thắng

    def reset_daily_session(self):
        """Reset các thông số khi sang ngày mới"""
        self.daily_trade_count = 0
        self.daily_pnl = 0
        self.daily_start_capital = self.current_capital
        self.cooldown_until = None

    def calculate_kelly_size(
        self, win_rate: float, avg_win: float, avg_loss: float, fraction: float = 0.5
    ) -> float:
        """
        Kelly Criterion: f* = W - (1 - W) / R
        """
        if avg_loss == 0:
            return 0.1
        r = avg_win / avg_loss
        kelly_f = win_rate - (1 - win_rate) / r
        safe_size = max(0, kelly_f * fraction)
        return min(safe_size, 0.25)

    def update_position_protection(self, symbol: str, current_price: float) -> Dict:
        """Stop-loss và Trailing Stop"""
        if symbol not in self.active_positions:
            return {"action": "NONE"}

        pos = self.active_positions[symbol]
        if current_price <= pos["stop_loss"]:
            return {"action": "LIQUIDATE", "reason": "STOP_LOSS_HIT"}

        highest = pos.get("highest_price", pos["entry_price"])
        if current_price > highest:
            pos["highest_price"] = current_price
            new_stop = current_price * (1 - pos.get("trailing_pct", 0.05))
            if new_stop > pos["stop_loss"]:
                pos["stop_loss"] = new_stop

        return {"action": "HOLD"}

    def calculate_lot_size(
        self,
        entry_price: float,
        swing_high: float,
        swing_low: float,
        risk_percent: float = 0.01,
        direction: str = "LONG",
    ) -> Dict:
        """
        Tính lot size dựa trên khoảng cách từ Entry đến Swing High/Low gần nhất
        """
        if direction.upper() == "LONG":
            stop_price = swing_low
            stop_distance = entry_price - stop_price
        else:
            stop_price = swing_high
            stop_distance = stop_price - entry_price

        if stop_distance <= 0:
            return {"error": "Invalid stop distance", "lot_size": 0}

        risk_amount = self.current_capital * risk_percent
        lot_size = risk_amount / stop_distance

        return {
            "entry_price": entry_price,
            "stop_price": stop_price,
            "stop_distance": stop_distance,
            "risk_amount": risk_amount,
            "lot_size": lot_size,
            "direction": direction.upper(),
        }

    def validate_risk(
        self, entry_price: float, stop_price: float, quantity: float
    ) -> Dict:
        """Validate rủi ro trước khi vào lệnh"""
        if entry_price <= 0 or stop_price <= 0 or quantity <= 0:
            return {"valid": False}

        stop_distance = abs(entry_price - stop_price)
        risk_amount = quantity * stop_distance
        risk_pct = risk_amount / self.current_capital

        if risk_pct > 0.02:
            return {"valid": False, "reason": f"Risk {risk_pct * 100:.2f}% exceeds 2%"}

        return {"valid": True, "risk_pct": risk_pct}
