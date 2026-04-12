"""
Session-Based Risk Management - Quản lý rủi ro theo phiên giao dịch
Daily/Weekly loss limits, Max trades, Cooldowns
"""
from datetime import datetime, timedelta
from typing import Dict

class SessionRiskManager:
    """Quản lý rủi ro theo phiên (daily, weekly)"""
    
    def __init__(self):
        self.daily_pnl = 0
        self.weekly_pnl = 0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.session_start = datetime.now()
        
        # Limits
        self.max_daily_loss = 0.03  # 3% per day
        self.max_weekly_loss = 0.10  # 10% per week
        self.max_daily_trades = 10
        self.max_consecutive_losses = 3
        self.cooldown_hours = 4
        
        # Tracking
        self.last_trade_time = None
        self.loss_streak_start = None
    
    def check_risk(self, portfolio_value: float) -> Dict:
        """
        Kiểm tra các giới hạn rủi ro
        """
        risk_checks = {
            "daily_loss": self._check_daily_loss(portfolio_value),
            "weekly_loss": self._check_weekly_loss(portfolio_value),
            "daily_trades": self._check_daily_trades(),
            "consecutive_losses": self._check_consecutive_losses(),
            "cooldown": self._check_cooldown()
        }
        
        # Nếu có bất kỳ lỗi nào, trả về hành động ngưng
        for check, result in risk_checks.items():
            if result["blocked"]:
                return {
                    "action": "BLOCK",
                    "reason": result["reason"],
                    "resume_time": result.get("resume_time"),
                    "checks": risk_checks
                }
        
        return {"action": "ALLOW", "checks": risk_checks}
    
    def _check_daily_loss(self, portfolio_value: float) -> Dict:
        """Kiểm tra giới hạn lỗ ngày"""
        daily_loss_pct = self.daily_pnl / portfolio_value if portfolio_value > 0 else 0
        
        if daily_loss_pct <= -self.max_daily_loss:
            resume_time = datetime.now() + timedelta(hours=24)
            return {
                "blocked": True,
                "reason": "DAILY_LOSS_LIMIT_EXCEEDED",
                "resume_time": resume_time.isoformat()
            }
        
        return {"blocked": False}
    
    def _check_weekly_loss(self, portfolio_value: float) -> Dict:
        """Kiểm tra giới hạn lỗ tuần"""
        weekly_loss_pct = self.weekly_pnl / portfolio_value if portfolio_value > 0 else 0
        
        if weekly_loss_pct <= -self.max_weekly_loss:
            resume_time = datetime.now() + timedelta(days=7)
            return {
                "blocked": True,
                "reason": "WEEKLY_LOSS_LIMIT_EXCEEDED",
                "resume_time": resume_time.isoformat()
            }
        
        return {"blocked": False}
    
    def _check_daily_trades(self) -> Dict:
        """Kiểm tra giới hạn số lệnh/ngày"""
        if self.daily_trades >= self.max_daily_trades:
            return {
                "blocked": True,
                "reason": "DAILY_TRADES_LIMIT_EXCEEDED",
                "resume_time": (datetime.now() + timedelta(hours=24)).isoformat()
            }
        
        return {"blocked": False}
    
    def _check_consecutive_losses(self) -> Dict:
        """Kiểm tra chuỗi lỗ liên tiếp"""
        if self.consecutive_losses >= self.max_consecutive_losses:
            resume_time = datetime.now() + timedelta(hours=self.cooldown_hours)
            return {
                "blocked": True,
                "reason": "CONSECUTIVE_LOSSES_LIMIT_EXCEEDED",
                "resume_time": resume_time.isoformat()
            }
        
        return {"blocked": False}
    
    def _check_cooldown(self) -> Dict:
        """Kiểm tra nếu đang trong cooldown"""
        if self.loss_streak_start:
            cooldown_end = self.loss_streak_start + timedelta(hours=self.cooldown_hours)
            if datetime.now() < cooldown_end:
                return {
                    "blocked": True,
                    "reason": "COOLDOWN_PERIOD_ACTIVE",
                    "resume_time": cooldown_end.isoformat()
                }
        
        return {"blocked": False}
    
    def record_trade_result(self, profit_loss: float, trade_time: datetime = None):
        """Ghi nhận kết quả giao dịch"""
        if trade_time is None:
            trade_time = datetime.now()
        
        # Update daily/weekly PnL
        self.daily_pnl += profit_loss
        self.weekly_pnl += profit_loss
        
        # Update trade count
        self.daily_trades += 1
        
        # Update consecutive losses
        if profit_loss < 0:
            self.consecutive_losses += 1
            if self.loss_streak_start is None:
                self.loss_streak_start = trade_time
        else:
            self.consecutive_losses = 0
            self.loss_streak_start = None
    
    def reset_daily_counters(self):
        """Reset counters đầu ngày mới"""
        now = datetime.now()
        if now.date() != self.session_start.date():
            self.daily_pnl = 0
            self.daily_trades = 0
            self.session_start = now
    
    def get_risk_summary(self) -> Dict:
        """Tóm tắt tình hình rủi ro"""
        return {
            "daily_pnl": self.daily_pnl,
            "weekly_pnl": self.weekly_pnl,
            "daily_trades": self.daily_trades,
            "consecutive_losses": self.consecutive_losses,
            "daily_loss_pct": self.daily_pnl / 1000 if 1000 > 0 else 0,  # Mock portfolio value
            "weekly_loss_pct": self.weekly_pnl / 1000 if 1000 > 0 else 0,
            "limits": {
                "max_daily_loss": self.max_daily_loss,
                "max_weekly_loss": self.max_weekly_loss,
                "max_daily_trades": self.max_daily_trades,
                "max_consecutive_losses": self.max_consecutive_losses
            }
        }
