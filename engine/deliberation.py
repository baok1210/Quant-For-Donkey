"""
Multi-Agent Deliberation Layer
Tạo một "Hội đồng AI" để thảo luận trước khi đưa ra quyết định cuối cùng.
"""
from typing import List, Dict

class DeliberationLayer:
    """Lớp thảo luận giữa các Agents chuyên biệt"""
    
    def __init__(self, agents: List[str]):
        self.agents = agents

    def deliberate(self, agent_views: Dict[str, dict]) -> dict:
        """
        Tổng hợp ý kiến từ các agent và giải quyết xung đột
        """
        # Logic: Weighted consensus
        total_score = 0
        reasons = []
        
        # Trọng số của các agent
        weights = {
            "bull_agent": 0.3,
            "bear_agent": 0.3,
            "macro_agent": 0.2,
            "onchain_agent": 0.2
        }

        for agent, view in agent_views.items():
            stance = view.get("stance", "NEUTRAL")
            confidence = view.get("confidence", 0.5)
            
            score = 0
            if stance == "BULLISH": score = 1
            elif stance == "BEARISH": score = -1
            
            total_score += score * weights.get(agent, 0.2) * confidence
            reasons.append(f"{agent}: {stance} ({confidence:.2f})")

        # Quyết định cuối cùng
        if total_score > 0.15:
            final_decision = "BUY"
        elif total_score < -0.15:
            final_decision = "SELL"
        else:
            final_decision = "HOLD"

        return {
            "final_decision": final_decision,
            "consensus_score": total_score,
            "agent_summaries": reasons
        }
