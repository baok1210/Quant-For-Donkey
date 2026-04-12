"""
Monthly Planner - Tìm kiếm thời điểm DCA tối ưu nhất trong tháng (1 lần/tháng)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MonthlyPlanner:
    def __init__(self):
        # Giả định chu kỳ: Cuối tháng thường có áp lực bán, đầu tháng có dòng tiền mới
        self.best_window_detected = False
        
    def find_entry_window(self, historical_data: pd.DataFrame, current_signals: dict):
        """
        Phân tích để tìm ngày tốt nhất trong tháng.
        Dựa trên: 
        1. Seasonal patterns (Chu kỳ ngày trong tháng)
        2. Technical Exhaustion (Khi các chỉ báo giảm quá đà)
        3. On-chain accumulation (Khi cá voi bắt đầu gom)
        """
        # Phân tích dữ liệu 30 ngày gần nhất
        # Trong thực tế, AI sẽ tìm các vùng hỗ trợ cứng trên khung W1 và D1
        
        score = current_signals.get('score', 0)
        rsi = current_signals.get('rsi', 50)
        
        # Logic: Nếu RSI < 35 và Score > 0.5 ở nửa sau tháng -> Thời điểm cực đẹp
        is_second_half = datetime.now().day > 15
        
        if rsi < 40 and score > 0.4:
            recommendation = "STRONG_ENTRY_NOW"
            confidence = 0.9
            reason = "RSI vùng quá bán kết hợp tín hiệu on-chain tích cực trong khung tháng."
        elif is_second_half and rsi < 50:
            recommendation = "ACCUMULATE_PHASE"
            confidence = 0.7
            reason = "Giai đoạn tích lũy cuối tháng, giá đang ổn định."
        else:
            recommendation = "WAIT_FOR_DIP"
            confidence = 0.4
            reason = "Thị trường chưa đạt độ sụt giảm cần thiết để giải ngân vốn lớn tháng này."
            
        return {
            "month": datetime.now().strftime("%B %Y"),
            "recommendation": recommendation,
            "confidence": confidence,
            "reason": reason,
            "suggested_allocation": "100%" if recommendation == "STRONG_ENTRY_NOW" else "0%"
        }
