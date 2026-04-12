"""
Multi-Agent Deliberation Layer (v4.2.0)
Tích hợp Conflict Resolution, Bear Market Protection và Weighted Voting
"""
from typing import List, Dict
import numpy as np

class DeliberationLayer:
    """Lớp thảo luận và giải quyết xung đột giữa các AI Agents"""
    
    def __init__(self):
        # Trọng số mặc định của các Agent
        self.weights = {
            "bull_agent": 0.35,
            "bear_agent": 0.35,
            "macro_agent": 0.15,
            "onchain_agent": 0.15
        }

    def resolve_conflicts(self, agent_views: Dict[str, dict]) -> dict:
        """
        Xử lý xung đột: Ví dụ Bull cực mạnh vs Bear cũng cực mạnh
        """
        # 1. Trích xuất confidence và stance
        confidences = {k: v.get("confidence", 0) for k, v in agent_views.items()}
        stances = {k: v.get("stance", "NEUTRAL") for k, v in agent_views.items()}
        
        # 2. Logic "Bảo vệ vốn" (Loss Aversion): 
        # Nếu Bear Agent có confidence > 0.8 -> Bear thắng tuyệt đối (Dừng mua)
        bear_view = agent_views.get("bear_agent", {})
        if bear_view.get("confidence", 0) > 0.8:
            return {
                "final_decision": "SELL/HOLD",
                "reason": "CRITICAL_RISK_OVERRIDE: Bear Agent confidence is extremely high.",
                "consensus_score": -0.9,
                "override": True
            }

        # 3. Weighted Voting
        total_score = 0
        for agent, stance in stances.items():
            weight = self.weights.get(agent, 0.2)
            confidence = confidences.get(agent, 0)
            
            score = 0
            if "BULL" in stance: score = 1
            elif "BEAR" in stance: score = -1
            
            total_score += score * weight * confidence

        # 4. Xác định sự đồng thuận (Consensus Level)
        # Nếu điểm số gần 0 nhưng confidence các bên đều cao -> Xung đột mạnh
        max_conf = max(confidences.values())
        min_conf = min(confidences.values())
        conflict_detected = (max_conf > 0.7 and min_conf > 0.6 and abs(total_score) < 0.2)

        if conflict_detected:
            final_decision = "HOLD"
            reason = "HIGH_CONFLICT: Agents disagree significantly. Safety first."
        elif total_score > 0.2:
            final_decision = "BUY"
            reason = f"CONSENSUS_BULLISH: Weighted score {total_score:.2f}"
        elif total_score < -0.2:
            final_decision = "SELL"
            reason = f"CONSENSUS_BEARISH: Weighted score {total_score:.2f}"
        else:
            final_decision = "HOLD"
            reason = "NEUTRAL: No strong consensus."

        return {
            "final_decision": final_decision,
            "reason": reason,
            "consensus_score": float(total_score),
            "conflict_detected": conflict_detected,
            "agent_summary": stances
        }
