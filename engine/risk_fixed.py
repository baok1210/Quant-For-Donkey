"""
Risk Engine với Kelly Criterion đã được sửa
"""

import numpy as np
from typing import Dict, List

class RiskEngine:
    """Bộ máy quản trị rủi ro với Kelly Criterion đã sửa"""
    
    def __init__(self, initial_capital: float = 10000):
        self.capital = initial_capital
        self.peak_capital = initial_capital
        self.max_drawdown = 0.0
        self.trade_history = []
        
    def kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Tính Kelly Criterion theo công thức đúng: f* = p - (1-p)/b
        với p = win_rate, b = avg_win/avg_loss
        """
        if avg_loss <= 0 or avg_win <= 0:
            return 0.0
            
        # Tính b = avg_win / avg_loss
        b = avg_win / avg_loss
        
        # Công thức Kelly: f* = p - (1-p)/b
        kelly_fraction = win_rate - (1 - win_rate) / b
        
        # Giới hạn trong khoảng 0-1
        kelly_fraction = max(0, min(kelly_fraction, 1))
        
        # Áp dụng Half-Kelly để an toàn
        half_kelly = kelly_fraction * 0.5
        
        # Giới hạn tối đa 25% vốn cho 1 lệnh
        return min(half_kelly, 0.25)
    
    def calculate_position_size(self, 
                              win_rate: float, 
                              avg_win: float, 
                              avg_loss: float,
                              volatility: float = 0.3) -> float:
        """
        Tính kích thước vị thế tối ưu
        """
        kelly_fraction = self.kelly_criterion(win_rate, avg_win, avg_loss)
        
        # Điều chỉnh theo độ biến động
        volatility_adjustment = 1.0 - min(volatility, 0.5)  # Volatility càng cao, position càng nhỏ
        
        adjusted_fraction = kelly_fraction * volatility_adjustment
        position_size = self.capital * adjusted_fraction
        
        return position_size
    
    def calculate_var(self, returns: List[float], confidence_level: float = 0.95) -> float:
        """
        Tính Value at Risk (VaR) với mức tin cậy cho trước
        """
        if not returns:
            return 0.0
            
        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence_level) * 100)
        return abs(var)
    
    def update_drawdown(self, current_capital: float):
        """Cập nhật drawdown hiện tại"""
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
            
        drawdown = (self.peak_capital - current_capital) / self.peak_capital
        self.max_drawdown = max(self.max_drawdown, drawdown)
        
        return drawdown
    
    def should_stop_trading(self, 
                          current_capital: float, 
                          max_drawdown_limit: float = 0.2) -> bool:
        """
        Kiểm tra xem có nên dừng giao dịch không
        """
        drawdown = self.update_drawdown(current_capital)
        return drawdown > max_drawdown_limit
    
    def get_risk_metrics(self) -> Dict:
        """Lấy các chỉ số rủi ro hiện tại"""
        return {
            "current_capital": self.capital,
            "peak_capital": self.peak_capital,
            "max_drawdown": self.max_drawdown,
            "total_trades": len(self.trade_history)
        }

# Test
if __name__ == "__main__":
    risk_engine = RiskEngine(initial_capital=10000)
    
    # Test Kelly Criterion
    kelly = risk_engine.kelly_criterion(
        win_rate=0.6,
        avg_win=0.15,  # 15% lợi nhuận trung bình khi thắng
        avg_loss=0.1     # 10% lỗ trung bình khi thua
    )
    print(f"Kelly Fraction: {kelly:.2%}")
    
    # Test position size
    position = risk_engine.calculate_position_size(
        win_rate=0.6,
        avg_win=0.15,
        avg_loss=0.1,
        volatility=0.3
    )
    print(f"Position size: ${position:.2f}")