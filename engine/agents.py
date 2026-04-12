"""
Multi-Agent System cho Solana Quant Fund
Bao gồm 3 agents: Bull (Aggressive), Bear (Conservative), Arbiter (Decision Maker)
"""

import json
from typing import Dict, List

class BaseAgent:
    """Base class cho tất cả agents"""
    def __init__(self, name: str, personality: str):
        self.name = name
        self.personality = personality
        self.confidence_history = []
        
    def analyze(self, market_data: Dict) -> Dict:
        """Phân tích thị trường và đưa ra ý kiến"""
        raise NotImplementedError

class BullAgent(BaseAgent):
    """Agent Diều Hâu - Tìm kiếm cơ hội tăng trưởng"""
    def __init__(self):
        super().__init__("Bull Agent", "Aggressive")
        
    def analyze(self, market_data: Dict) -> Dict:
        """
        Tìm kiếm tín hiệu tích cực:
        - RSI oversold
        - Volume tăng
        - On-chain metrics tích cực
        """
        signals = []
        confidence = 0.0
        
        # Kiểm tra RSI
        if market_data.get("rsi", 50) < 30:
            signals.append("RSI oversold - cơ hội mua")
            confidence += 0.3
            
        # Kiểm tra volume
        if market_data.get("volume_change", 0) > 0.2:
            signals.append("Volume tăng 20% - dòng tiền vào")
            confidence += 0.2
            
        # Kiểm tra active wallets
        if market_data.get("active_wallets_change", 0) > 0.1:
            signals.append("Số ví active tăng 10%")
            confidence += 0.2
            
        return {
            "agent": self.name,
            "stance": "BULLISH",
            "confidence": min(confidence, 1.0),
            "signals": signals,
            "recommendation": "DCA ngay" if confidence > 0.5 else "Quan sát thêm"
        }

class BearAgent(BaseAgent):
    """Agent Chim Ưng - Cảnh báo rủi ro"""
    def __init__(self):
        super().__init__("Bear Agent", "Conservative")
        
    def analyze(self, market_data: Dict) -> Dict:
        """
        Tìm kiếm tín hiệu tiêu cực:
        - RSI overbought
        - Phí mạng cao
        - Whale movements
        """
        warnings = []
        risk_score = 0.0
        
        # Kiểm tra RSI
        if market_data.get("rsi", 50) > 70:
            warnings.append("RSI overbought - nguy cơ điều chỉnh")
            risk_score += 0.3
            
        # Kiểm tra phí mạng
        if market_data.get("priority_fee", 0) > 0.001:
            warnings.append("Phí mạng cao - mạng quá tải")
            risk_score += 0.2
            
        # Kiểm tra whale movements
        if market_data.get("whale_outflow", 0) > 1000:
            warnings.append("Cá voi đang chuyển SOL lên sàn")
            risk_score += 0.3
            
        return {
            "agent": self.name,
            "stance": "BEARISH",
            "risk_score": min(risk_score, 1.0),
            "warnings": warnings,
            "recommendation": "Dừng DCA" if risk_score > 0.5 else "Giảm khối lượng"
        }

class ArbiterAgent(BaseAgent):
    """Agent Trọng Tài - Ra quyết định cuối cùng"""
    def __init__(self):
        super().__init__("Arbiter Agent", "Balanced")
        
    def decide(self, bull_analysis: Dict, bear_analysis: Dict) -> Dict:
        """
        Tổng hợp ý kiến từ Bull và Bear để ra quyết định
        """
        bull_confidence = bull_analysis.get("confidence", 0)
        bear_risk = bear_analysis.get("risk_score", 0)
        
        # Tính điểm tổng hợp
        net_score = bull_confidence - bear_risk
        
        # Quyết định
        if net_score > 0.3:
            action = "DCA_AGGRESSIVE"
            amount_multiplier = 1.5
        elif net_score > 0:
            action = "DCA_NORMAL"
            amount_multiplier = 1.0
        elif net_score > -0.3:
            action = "DCA_CONSERVATIVE"
            amount_multiplier = 0.5
        else:
            action = "HOLD"
            amount_multiplier = 0.0
            
        return {
            "agent": self.name,
            "decision": action,
            "amount_multiplier": amount_multiplier,
            "net_score": net_score,
            "reasoning": f"Bull confidence: {bull_confidence:.2f}, Bear risk: {bear_risk:.2f}",
            "bull_signals": bull_analysis.get("signals", []),
            "bear_warnings": bear_analysis.get("warnings", [])
        }

class MultiAgentSystem:
    """Hệ thống quản lý các agents"""
    def __init__(self):
        self.bull = BullAgent()
        self.bear = BearAgent()
        self.arbiter = ArbiterAgent()
        
    def run_analysis(self, market_data: Dict) -> Dict:
        """Chạy phân tích từ tất cả agents"""
        bull_view = self.bull.analyze(market_data)
        bear_view = self.bear.analyze(market_data)
        final_decision = self.arbiter.decide(bull_view, bear_view)
        
        return {
            "timestamp": market_data.get("timestamp"),
            "bull_view": bull_view,
            "bear_view": bear_view,
            "final_decision": final_decision
        }

# Test
if __name__ == "__main__":
    system = MultiAgentSystem()
    
    # Mock data
    test_data = {
        "timestamp": "2026-04-12T22:30:00",
        "rsi": 28,
        "volume_change": 0.25,
        "active_wallets_change": 0.15,
        "priority_fee": 0.0005,
        "whale_outflow": 500
    }
    
    result = system.run_analysis(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
