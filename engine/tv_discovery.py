"""
TradingView Discovery - Tự động phát hiện và đánh giá các indicator mới
"""
from typing import List, Dict
from datetime import datetime, timedelta

class TVDiscovery:
    """Phát hiện và đánh giá các indicator từ TradingView"""
    
    def __init__(self):
        self.evaluated_indicators = {}
        
    def discover_new_indicators(self, connector) -> List[Dict]:
        """
        Tìm kiếm các indicator mới nổi từ TradingView
        """
        trending = connector.get_trending_indicators()
        
        # Filter indicators based on criteria
        filtered_indicators = []
        for indicator in trending:
            # Criteria: rating > 4.5 AND popularity > 80
            if indicator.get("rating", 0) > 4.5 and indicator.get("popularity", 0) > 80:
                filtered_indicators.append(indicator)
        
        return filtered_indicators
    
    def evaluate_indicator(self, indicator_data: Dict) -> Dict:
        """
        Đánh giá một indicator dựa trên các tiêu chí
        """
        name = indicator_data.get("name", "Unknown")
        rating = indicator_data.get("rating", 0)
        popularity = indicator_data.get("popularity", 0)
        description = indicator_data.get("description", "")
        
        # Calculate composite score
        # Weighted score: 40% rating + 30% popularity + 30% complexity bonus
        complexity_bonus = len(description) / 100  # Longer descriptions = more complex
        
        score = (rating * 0.4) + (popularity * 0.003) + complexity_bonus
        
        evaluation = {
            "name": name,
            "rating": rating,
            "popularity": popularity,
            "complexity_bonus": complexity_bonus,
            "composite_score": score,
            "evaluation_date": datetime.now().isoformat(),
            "suitability": self._assess_suitability(indicator_data)
        }
        
        # Store evaluation
        self.evaluated_indicators[name] = evaluation
        
        return evaluation
    
    def _assess_suitability(self, indicator_data: Dict) -> str:
        """
        Đánh giá mức độ phù hợp với hệ thống
        """
        description = indicator_data.get("description", "").lower()
        name = indicator_data.get("name", "").lower()
        
        # Check for relevant keywords
        technical_keywords = ["trend", "momentum", "oscillator", "support", "resistance", "breakout"]
        sentiment_keywords = ["sentiment", "news", "social", "media"]
        volume_keywords = ["volume", "flow", "accumulation", "distribution"]
        
        if any(keyword in description for keyword in technical_keywords):
            return "TECHNICAL_STRONG"
        elif any(keyword in description for keyword in sentiment_keywords):
            return "SENTIMENT_RELEVANT"
        elif any(keyword in description for keyword in volume_keywords):
            return "VOLUME_BASED"
        else:
            return "GENERAL_PURPOSE"
    
    def get_top_indicators(self, limit: int = 5) -> List[Dict]:
        """
        Lấy danh sách top indicator theo điểm số
        """
        sorted_indicators = sorted(
            self.evaluated_indicators.values(),
            key=lambda x: x["composite_score"],
            reverse=True
        )
        return sorted_indicators[:limit]
