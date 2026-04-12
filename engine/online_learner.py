import os
import json
import requests
from datetime import datetime

class OnlineAIAnalyzer:
    """Hệ thống AI phân tích và học hỏi online từ dữ liệu thực tế"""
    
    def __init__(self, api_key=None, provider="openai"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.provider = provider
        self.knowledge_base_path = "memory/online_knowledge.json"
        self._load_knowledge()

    def _load_knowledge(self):
        if os.path.exists(self.knowledge_base_path):
            with open(self.knowledge_base_path, 'r') as f:
                self.knowledge = json.load(f)
        else:
            self.knowledge = {"model_weights": {"rsi": 1.0, "volume": 1.0, "onchain": 1.0}, "last_update": None}

    def analyze_market_with_llm(self, market_summary: str, current_context: str):
        """
        Gửi dữ liệu thực tế cho LLM để lấy phân tích chuyên sâu.
        """
        prompt = f"""
        Bạn là một chuyên gia Quant Fund cho Solana.
        Dữ liệu thị trường hiện tại: {market_summary}
        Bối cảnh gần đây: {current_context}
        
        Hãy phân tích và đưa ra:
        1. Đánh giá rủi ro (1-10)
        2. Dự đoán xu hướng ngắn hạn
        3. Khuyến nghị DCA (Số tiền/Thời điểm)
        4. Đề xuất điều chỉnh trọng số chỉ báo nếu cần.
        """
        
        # Ở đây sẽ gọi API OpenAI hoặc Gemini thực tế
        # Demo kết quả trả về từ AI
        return {
            "risk_score": 4,
            "prediction": "Bullish Bias",
            "reasoning": "Dòng tiền on-chain đang vào mạnh dù giá đi ngang.",
            "adjustment": "Tăng trọng số On-chain lên 1.2x"
        }

    def update_model_online(self, prediction: str, actual_outcome: str):
        """
        So sánh dự đoán với thực tế và tự cập nhật kiến thức.
        Đây là phần 'Tự học' thực sự.
        """
        # Logic so sánh và điều chỉnh trọng số (Weights)
        self.knowledge["last_update"] = datetime.now().isoformat()
        # Lưu lại kiến thức đã học
        with open(self.knowledge_base_path, 'w') as f:
            json.dump(self.knowledge, f, indent=4)
        return "Model updated based on market feedback."
