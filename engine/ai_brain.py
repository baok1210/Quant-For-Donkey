import os
import openai
from google import genai
from google.genai.types import GenerationConfig
import json

class AIBrain:
    """
    Module gọi API thật sự của AI (OpenAI hoặc Google Gemini)
    để phân tích dữ liệu thị trường và đưa ra quyết định DCA
    """
    
    # Danh sách model có sẵn
    AVAILABLE_MODELS = {
        "openai": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        "gemini": ["gemini-pro", "gemini-flash"]
    }
    
    def __init__(self, provider="openai", model="gpt-4-turbo", api_key=None):
        self.provider = provider
        self.model = model
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        
        if provider == "openai":
            openai.api_key = self.api_key
        elif provider == "gemini":
            genai.configure(api_key=self.api_key)
            self.model_instance = genai.GenerativeModel(model)
    
    def analyze_market(self, market_data: dict, investment_diary: str = ""):
        """
        Gửi dữ liệu thị trường và lịch sử đầu tư cho AI để phân tích
        
        Args:
            market_data: Dữ liệu thị trường (RSI, MACD, On-chain, v.v.)
            investment_diary: Nội dung INVESTMENT_DIARY.md (lịch sử quyết định)
        
        Returns:
            Phân tích từ AI với confidence score
        """
        if self.provider == "openai":
            return self._analyze_with_openai(market_data, investment_diary)
        elif self.provider == "gemini":
            return self._analyze_with_gemini(market_data, investment_diary)
    
    def _analyze_with_openai(self, market_data: dict, investment_diary: str):
        prompt = f"""
        Bạn là một chuyên gia đầu tư định lượng trên Solana.
        
        DỮ LIỆU THỊ TRƯỜNG HIỆN TẠI:
        - Giá SOL: {market_data.get('price', 'N/A')}
        - RSI (14): {market_data.get('rsi', 'N/A')}
        - MACD: {market_data.get('macd', 'N/A')}
        - Volume Change: {market_data.get('volume_change', 'N/A')}
        - Active Wallets Change: {market_data.get('active_wallets_change', 'N/A')}
        - Whale Outflow (24h): {market_data.get('whale_outflow', 'N/A')} SOL
        - Priority Fee: {market_data.get('priority_fee', 'N/A')} SOL
        
        LỊCH SỬ ĐẦU TƯ (INVESTMENT DIARY):
        {investment_diary}
        
        Hãy phân tích kỹ lưỡng và trả lời theo định dạng JSON:
        {{
            "recommendation": "STRONG_BUY | BUY | HOLD | SELL | STRONG_SELL",
            "confidence": 0.0-1.0,
            "reasoning": "Lý do phân tích",
            "suggested_allocation": "100% | 75% | 50% | 25% | 0%",
            "risk_assessment": "LOW | MEDIUM | HIGH | VERY_HIGH",
            "improvement_suggestions": ["Gợi ý cải tiến 1", "Gợi ý cải tiến 2"]
        }}
        """
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        try:
            # Trích xuất JSON từ response
            content = response.choices[0].message.content
            # Tìm đoạn JSON trong response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            return json.loads(json_str)
        except:
            # Nếu không parse được JSON, trả về raw content
            return {"raw_response": content}
    
    def _analyze_with_gemini(self, market_data: dict, investment_diary: str):
        prompt = f"""
        Bạn là một chuyên gia đầu tư định lượng trên Solana.
        
        DỮ LIỆU THỊ TRƯỜNG HIỆN TẠI:
        - Giá SOL: {market_data.get('price', 'N/A')}
        - RSI (14): {market_data.get('rsi', 'N/A')}
        - MACD: {market_data.get('macd', 'N/A')}
        - Volume Change: {market_data.get('volume_change', 'N/A')}
        - Active Wallets Change: {market_data.get('active_wallets_change', 'N/A')}
        - Whale Outflow (24h): {market_data.get('whale_outflow', 'N/A')} SOL
        - Priority Fee: {market_data.get('priority_fee', 'N/A')} SOL
        
        LỊCH SỬ ĐẦU TƯ (INVESTMENT DIARY):
        {investment_diary}
        
        Hãy phân tích kỹ lưỡng và trả lời theo định dạng JSON:
        {{
            "recommendation": "STRONG_BUY | BUY | HOLD | SELL | STRONG_SELL",
            "confidence": 0.0-1.0,
            "reasoning": "Lý do phân tích",
            "suggested_allocation": "100% | 75% | 50% | 25% | 0%",
            "risk_assessment": "LOW | MEDIUM | HIGH | VERY_HIGH",
            "improvement_suggestions": ["Gợi ý cải tiến 1", "Gợi ý cải tiến 2"]
        }}
        """
        
        response = self.model_instance.generate_content(prompt)
        
        try:
            # Trích xuất JSON từ response
            content = response.text
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            return json.loads(json_str)
        except:
            return {"raw_response": content}
