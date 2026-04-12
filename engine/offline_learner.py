import json
import os
import re

class OfflineLearner:
    """
    AI Offline Learning: Tự học từ lịch sử giao dịch và nhật ký bài học
    mà không cần kết nối mạng.
    """
    
    def __init__(self):
        self.diary_path = "memory/INVESTMENT_DIARY.md"
        self.lessons_path = "memory/LESSONS_LEARNED.md"
        self.model_path = "memory/offline_model.json"
        self.weights = self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, "r") as f:
                return json.load(f)
        return {
            "rsi_weight": 1.0,
            "macd_weight": 1.0,
            "onchain_weight": 1.0,
            "sentiment_weight": 1.0,
            "learning_rate": 0.05
        }

    def learn_from_diary(self):
        """Phân tích nhật ký để điều chỉnh trọng số"""
        if not os.path.exists(self.diary_path):
            return "Chưa có nhật ký để học."

        with open(self.diary_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Logic: Nếu tìm thấy từ khóa thất bại liên quan đến RSI
        if "RSI sai" in content or "RSI không chính xác" in content:
            self.weights["rsi_weight"] -= self.weights["learning_rate"]
            
        if "đẩy mạnh" in content or "thành công" in content:
            # Tìm xem thành công nhờ cái gì
            if "on-chain" in content.lower():
                self.weights["onchain_weight"] += self.weights["learning_rate"]
        
        self._save_model()
        return "AI đã học xong từ nhật ký và cập nhật trọng số mới."

    def _save_model(self):
        with open(self.model_path, "w") as f:
            json.dump(self.weights, f, indent=4)

    def get_optimized_weights(self):
        return self.weights
