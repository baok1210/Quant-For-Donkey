"""
Dynamic Risk Engine - Quản trị rủi ro thông minh
Bao gồm: Kelly Criterion, VaR, Volatility Scaling
"""

import numpy as np
from typing import Dict, List

class RiskEngine:
    """Bộ máy quản trị rủi ro động"""
    
    def __init__(self, initial_capital: float = 10000):
        self.capital = initial_capital
        self.max_drawdown = 0.0
        self.peak_capital = initial_capital
        self.trade_history = []
        
    def kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Tính toán Kelly Criterion để xác định % vốn nên đầu tư
        
        Kelly % = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        Args:
            win_rate: Tỷ lệ thắng (0-1)
            avg_win: Lợi nhuận trung bình khi thắng (%)
            avg_loss: Thua lỗ trung bình khi thua (%)
        
        Returns:
            Kelly fraction (0-1)
        """
        if avg_win <= 0:
            return 0.0
            
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        # Áp dụng Half Kelly để an toàn hơn
        kelly_fraction = max(0, min(kelly * 0.5, 0.25))  # Giới hạn tối đa 25%
        
        return kelly_fraction
    
    def calculate_position_size(self, 
                                win_rate: float, 
                                avg_win: float, 
                                avg_loss: float,
                                volatility: float) -> float:
        """
        Tính toán kích thước vị thế dựa trên Kelly và Volatility
        
        Args:
            win_rate: Tỷ lệ thắng
            avg_win: Lợi nhuận trung bình
            avg_loss: Thua lỗ trung bình
            volatility: Độ biến động thị trường (0-1)
        
        Returns:
            Số tiền nên đầu tư
        """
        kelly_fraction = self.kelly_criterion(win_rate, avg_win, avg_loss)
        
        # Điều chỉnh theo volatility (volatility cao -> giảm position)
        volatility_adjustment = 1 - min(volatility, 0.5)
        
        adjusted_fraction = kelly_fraction * volatility_adjustment
        
        position_size = self.capital * adjusted_fraction
        
        return position_size
    
    def calculate_var(self, returns: List[float], confidence_level: float = 0.95) -> float:
        """
        Tính Value at Risk (VaR) - Mức thua lỗ tối đa có thể xảy ra
        
        Args:
            returns: Danh sách lợi nhuận lịch sử
            confidence_level: Mức độ tin cậy (0.95 = 95%)
        
        Returns:
            VaR value
        """
        if not returns:
            return 0.0
            
        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence_level) * 100)
        
        return abs(var)
    
    def update_drawdown(self, current_capital: float):
        """Cập nhật Maximum Drawdown"""
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
            
        drawdown = (self.peak_capital - current_capital) / self.peak_capital
        
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
            
        return drawdown
    
    def should_stop_trading(self, current_drawdown: float, max_allowed_drawdown: float = 0.2) -> bool:
        """
        Kiểm tra xem có nên dừng giao dịch không
        
        Args:
            current_drawdown: Drawdown hiện tại
            max_allowed_drawdown: Drawdown tối đa cho phép (mặc định 20%)
        
        Returns:
            True nếu nên dừng
        """
        return current_drawdown > max_allowed_drawdown
    
    def adaptive_dca_amount(self, 
                           base_amount: float,
                           market_condition: str,
                           volatility: float) -> float:
        """
        Điều chỉnh số tiền DCA dựa trên điều kiện thị trường
        
        Args:
            base_amount: Số tiền DCA cơ bản
            market_condition: "bull", "bear", "sideways"
            volatility: Độ biến động (0-1)
        
        Returns:
            Số tiền DCA đã điều chỉnh
        """
        # Điều chỉnh theo market condition
        if market_condition == "bull":
            condition_multiplier = 1.2
        elif market_condition == "bear":
            condition_multiplier = 1.5  # DCA nhiều hơn khi giá giảm
        else:  # sideways
            condition_multiplier = 1.0
            
        # Điều chỉnh theo volatility
        if volatility > 0.5:
            volatility_multiplier = 0.7  # Giảm khi quá biến động
        elif volatility > 0.3:
            volatility_multiplier = 0.9
        else:
            volatility_multiplier = 1.0
            
        adjusted_amount = base_amount * condition_multiplier * volatility_multiplier
        
        return adjusted_amount
    
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
    kelly = risk_engine.kelly_criterion(win_rate=0.6, avg_win=0.15, avg_loss=0.10)
    print(f"Kelly Fraction: {kelly:.2%}")
    
    # Test Position Size
    position = risk_engine.calculate_position_size(
        win_rate=0.6, 
        avg_win=0.15, 
        avg_loss=0.10,
        volatility=0.3
    )
    print(f"Position Size: ${position:.2f}")
    
    # Test Adaptive DCA
    dca_amount = risk_engine.adaptive_dca_amount(
        base_amount=100,
        market_condition="bear",
        volatility=0.4
    )
    print(f"Adaptive DCA Amount: ${dca_amount:.2f}")
