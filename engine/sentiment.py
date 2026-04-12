"""
Sentiment Analysis - Phân tích cảm xúc từ Twitter và Reddit
"""
import os
import requests
from typing import Dict, List
from datetime import datetime, timedelta

class SentimentAnalyzer:
    """Phân tích cảm xúc từ mạng xã hội"""
    
    def __init__(self):
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        
    def get_twitter_sentiment(self, keyword="SOL", count=100) -> Dict:
        """
        Lấy sentiment từ Twitter (X) API v2
        """
        if not self.twitter_bearer_token:
            return {"sentiment_score": 0, "error": "No Twitter API key"}
        
        # Twitter API v2 endpoint
        url = f"https://api.twitter.com/2/tweets/search/recent"
        headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
        params = {
            "query": f"{keyword} -is:retweet lang:en",
            "max_results": min(count, 100),
            "tweet.fields": "created_at,public_metrics"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code != 200:
                return {"sentiment_score": 0, "error": f"Twitter API error: {response.status_code}"}
            
            data = response.json()
            tweets = data.get("data", [])
            
            # Phân tích đơn giản: đếm từ khóa tích cực/tiêu cực
            positive_words = ["bullish", "moon", "pump", "buy", "long", "up", "gain", "profit"]
            negative_words = ["bearish", "dump", "sell", "short", "down", "loss", "crash", "fear"]
            
            positive_count = 0
            negative_count = 0
            
            for tweet in tweets:
                text = tweet.get("text", "").lower()
                positive_count += sum(1 for word in positive_words if word in text)
                negative_count += sum(1 for word in negative_words if word in text)
            
            # Tính sentiment score (-1 đến 1)
            total = positive_count + negative_count
            if total == 0:
                sentiment_score = 0
            else:
                sentiment_score = (positive_count - negative_count) / total
            
            return {
                "sentiment_score": sentiment_score,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "tweet_count": len(tweets),
                "source": "twitter"
            }
        except Exception as e:
            return {"sentiment_score": 0, "error": str(e)}
    
    def get_reddit_sentiment(self, subreddit="solana", limit=100) -> Dict:
        """
        Lấy sentiment từ Reddit
        """
        if not self.reddit_client_id or not self.reddit_client_secret:
            return {"sentiment_score": 0, "error": "No Reddit API key"}
        
        try:
            # Reddit API endpoint
            auth = requests.auth.HTTPBasicAuth(self.reddit_client_id, self.reddit_client_secret)
            data = {
                "grant_type": "client_credentials",
                "username": os.getenv("REDDIT_USERNAME", ""),
                "password": os.getenv("REDDIT_PASSWORD", "")
            }
            headers = {"User-Agent": "SolanaDCABot/1.0"}
            
            # Get access token
            token_response = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers,
                timeout=10
            )
            
            if token_response.status_code != 200:
                return {"sentiment_score": 0, "error": "Reddit auth failed"}
            
            token = token_response.json().get("access_token")
            headers["Authorization"] = f"bearer {token}"
            
            # Get posts
            url = f"https://oauth.reddit.com/r/{subreddit}/hot"
            params = {"limit": limit}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return {"sentiment_score": 0, "error": "Reddit API error"}
            
            posts = response.json().get("data", {}).get("children", [])
            
            # Phân tích sentiment
            positive_words = ["bullish", "moon", "pump", "buy", "long", "up", "gain", "profit"]
            negative_words = ["bearish", "dump", "sell", "short", "down", "loss", "crash", "fear"]
            
            positive_count = 0
            negative_count = 0
            
            for post in posts:
                title = post.get("data", {}).get("title", "").lower()
                positive_count += sum(1 for word in positive_words if word in title)
                negative_count += sum(1 for word in negative_words if word in title)
            
            total = positive_count + negative_count
            if total == 0:
                sentiment_score = 0
            else:
                sentiment_score = (positive_count - negative_count) / total
            
            return {
                "sentiment_score": sentiment_score,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "post_count": len(posts),
                "source": "reddit"
            }
        except Exception as e:
            return {"sentiment_score": 0, "error": str(e)}
    
    def get_combined_sentiment(self, keyword="SOL") -> Dict:
        """
        Kết hợp sentiment từ nhiều nguồn
        """
        twitter_sentiment = self.get_twitter_sentiment(keyword)
        reddit_sentiment = self.get_reddit_sentiment("solana")
        
        # Trung bình có trọng số (Twitter 60%, Reddit 40%)
        twitter_score = twitter_sentiment.get("sentiment_score", 0)
        reddit_score = reddit_sentiment.get("sentiment_score", 0)
        
        combined_score = (twitter_score * 0.6) + (reddit_score * 0.4)
        
        return {
            "combined_sentiment": combined_score,
            "twitter": twitter_sentiment,
            "reddit": reddit_sentiment,
            "interpretation": self._interpret_sentiment(combined_score)
        }
    
    def _interpret_sentiment(self, score: float) -> str:
        """Diễn giải sentiment score"""
        if score > 0.3:
            return "VERY_BULLISH"
        elif score > 0.1:
            return "BULLISH"
        elif score > -0.1:
            return "NEUTRAL"
        elif score > -0.3:
            return "BEARISH"
        else:
            return "VERY_BEARISH"
