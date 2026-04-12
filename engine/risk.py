"""
Advanced Risk Engine - Quản trị rủi ro & Bảo vệ vốn
Bao gồm: Kelly Criterion, VaR, Stop-loss, Trailing Stop, Circuit Breakers
"""

import numpy as np
from typing import Dict, List, Optional

class RiskEngine:
    """Bộ máy quản trị rủi ro cao cấp"""
    
    def __init__(self, initial_capital: float = 1000, 
                 max_drawdown_limit: float = 0.20,
                 max_daily_loss_limit: float = 0.05):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_drawdown_limit = max_drawdown_limit
        self.max_daily_loss_limit = max_daily_loss_limit
        
        self.peak_capital = initial_capital
        self.daily_start_capital = initial_capital
        self.active_positions = {} # {symbol: {entry_price, amount, stop_loss, trailing_stop}}
        
    def calculate_kelly_size(self, win_rate: float, avg_win: float, avg_loss: float, 
                             fraction: float = 0.5) -> float:
        """
        Tính toán Kelly Criterion đúng công thức:
        f* = W - (1 - W) / R
        với W = win_rate, R = avg_win / avg_loss
        """
        if avg_loss == 0: return 0.1 # Tránh chia cho 0
        
        r = avg_win / avg_loss
        kelly_f = win_rate - (1 - win_rate) / r
        
        # Áp dụng fraction (Half-Kelly) và giới hạn an toàn
        safe_size = max(0, kelly_f * fraction)
        return min(safe_size, 0.25) # Không bao giờ quá 25% vốn 1 lệnh

    def update_position_protection(self, symbol: str, current_price: float) -> Dict:
        """
        Cập nhật Stop-loss và Trailing Stop cho vị thế đang mở
        """
        if symbol not in self.active_positions:
            return {"action": "NONE"}
            
        pos = self.active_positions[symbol]
        entry_price = pos['entry_price']
        stop_loss = pos['stop_loss']
        trailing_stop_pct = pos.get('trailing_stop_pct', 0.05)
        
        # 1. Kiểm tra Stop-loss cố định
        if current_price <= stop_loss:
            return {"action": "LIQUIDATE", "reason": "STOP_LOSS_HIT"}
            
        # 2. Cập nhật Trailing Stop
        highest_price = pos.get('highest_price', entry_price)
        if current_price > highest_price:
            pos['highest_price'] = current_price
            # Nâng stop-loss lên theo giá cao nhất
            new_stop = current_price * (1 - trailing_stop_pct)
            if new_stop > stop_loss:
                pos['stop_loss'] = new_stop
                
        # 3. Kiểm tra Trailing Stop mới
        if current_price <= pos['stop_loss']:
            return {"action": "LIQUIDATE", "reason": "TRAILING_STOP_HIT"}
            
        return {"action": "HOLD", "current_stop": pos['stop_loss']}

    def check_circuit_breakers(self, daily_pnl: float) -> Dict:
        """
        Kiểm tra các "cầu chì" bảo vệ tài khoản
        """
        # 1. Daily Loss Limit
        daily_loss_pct = daily_pnl / self.daily_start_capital
        if daily_loss_pct <= -self.max_daily_loss_limit:
            return {"status": "HALTED", "reason": "DAILY_LOSS_LIMIT_EXCEEDED"}
            
        # 2. Max Drawdown Limit
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        if drawdown >= self.max_drawdown_limit:
            return {"status": "HALTED", "reason": "MAX_DRAWDOWN_REACHED"}
            
        return {"status": "OPERATIONAL"}

    def get_max_allowed_loss(self, volatility: float) -> float:
        """
        Tính toán VaR (Value at Risk) đơn giản để giới hạn rủi ro
        """
        # Giả định phân phối chuẩn, 95% confidence (1.65 sigma)
        var_95 = 1.65 * volatility * self.current_capital
        return var_95
