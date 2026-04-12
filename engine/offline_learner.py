"""
AI Offline Learner - Tự học từ lịch sử giao dịch và nhật ký đầu tư
Cơ chế: Phân tích thành bại -> Điều chỉnh trọng số (Weight Optimization)
"""
import os
import json
import re
from typing import Dict, List
import pandas as pd

class OfflineLearner:
    """Bộ não tự học offline của hệ thống"""
    
    def __init__(self, diary_path="memory/INVESTMENT_DIARY.md", model_path="memory/offline_model.json"):
        self.diary_path = diary_path
        self.model_path = model_path
        self.default_weights = {
            "rsi_weight": 0.3,
            "macd_weight": 0.3,
            "onchain_weight": 0.2,
            "sentiment_weight": 0.2
        }
        self.model_state = self.load_model()

    def load_model(self) -> Dict:
        """Load trạng thái đã học"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"weights": self.default_weights, "total_learned": 0, "lessons": []}

    def analyze_diary(self):
        """
        Đọc và phân tích INVESTMENT_DIARY.md để rút bài học
        """
        if not os.path.exists(self.diary_path):
            return "No diary found."

        with open(self.diary_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex tìm các entry lệnh
        # Giả định format: [2026-xx-xx] Decision: BUY | Result: +5% (WIN)
        wins = len(re.findall(r"Result:.*WIN", content))
        losses = len(re.findall(r"Result:.*LOSS", content))
        
        # Phân tích sâu hơn: Nếu MACD báo BUY mà vẫn LOSS -> Giảm trọng số MACD
        # Đây là logic tối ưu hóa cơ bản
        if losses > wins and losses > 0:
            self.model_state["weights"]["macd_weight"] *= 0.95
            self.model_state["weights"]["rsi_weight"] *= 1.05 # Tăng cái khác bù vào
            
        self.model_state["total_learned"] += (wins + losses)
        self.save_model()
        
        return f"✅ Đã học được từ {wins} lệnh thắng và {losses} lệnh thua."

    def save_model(self):
        """Lưu model sau khi học"""
        with open(self.model_path, 'w', encoding='utf-8') as f:
            json.dump(self.model_state, f, indent=4, ensure_ascii=False)

    def get_optimized_weights(self) -> Dict:
        """Trả về trọng số đã được tối ưu cho Signal Engine"""
        return self.model_state["weights"]
