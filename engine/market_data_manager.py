"""
Market Data Manager - Quản lý dữ liệu thị trường real-time
Tích hợp: Price Stream, On-chain Data, Sentiment, Macro Indicators
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from engine.price_stream import SolanaPriceStream, PriceAggregator
from engine.onchain import OnChainAnalyzer
from engine.sentiment import SentimentAnalyzer
from engine.macro import MacroAnalyzer
from engine.signals import SignalEngine

class MarketDataManager:
    """Quản lý tất cả dữ liệu thị trường"""
    
    def __init__(self):
        self.price_stream = SolanaPriceStream()
        self.price_aggregator = PriceAggregator()
        self.onchain = OnChainAnalyzer()
        self.sentiment = SentimentAnalyzer()
        self.macro = MacroAnalyzer()
        self.signal_engine = SignalEngine()
        
        self.current_market_data = {}
        self.data_update_callbacks = []
        self.last_update = None
        
    def add_data_callback(self, callback):
        """Thêm callback khi dữ liệu được cập nhật"""
        self.data_update_callbacks.append(callback)
    
    def get_realtime_market_data(self) -> Dict:
        """
        Lấy toàn bộ dữ liệu thị trường real-time
        """
        market_data = {
            "timestamp": datetime.now().isoformat(),
            "price": {},
            "onchain": {},
            "sentiment": {},
            "macro": {},
            "signals": {}
        }
        
        # 1. Giá SOL real-time
        try:
            prices = self.price_aggregator.fetch_all_prices()
            market_data["price"] = {
                "sources": prices,
                "average": self.price_aggregator.get_average_price(),
                "current": self.price_stream.current_price
            }
        except Exception as e:
            market_data["price"]["error"] = str(e)
        
        # 2. Dữ liệu On-chain
        try:
            onchain_metrics = self.onchain.get_comprehensive_metrics()
            market_data["onchain"] = onchain_metrics
        except Exception as e:
            market_data["onchain"]["error"] = str(e)
        
        # 3. Sentiment từ mạng xã hội
        try:
            sentiment = self.sentiment.get_combined_sentiment("SOL")
            market_data["sentiment"] = sentiment
        except Exception as e:
            market_data["sentiment"]["error"] = str(e)
        
        # 4. Macro Indicators
        try:
            macro_data = self.macro.get_macro_data()
            risk_env = self.macro.analyze_risk_on_off()
            market_data["macro"] = {
                "indicators": macro_data,
                "risk_environment": risk_env
            }
        except Exception as e:
            market_data["macro"]["error"] = str(e)
        
        # 5. Tạo tín hiệu giao dịch
        try:
            # Chuẩn bị dữ liệu cho signal engine
            signal_input = {
                "prices": self.price_stream.price_history[-20:] if self.price_stream.price_history else [],
                "tps": market_data.get("onchain", {}).get("network_health", {}).get("tps", 2500),
                "priority_fee": market_data.get("onchain", {}).get("network_health", {}).get("priority_fee", 0.000005),
                "whale_inflow": market_data.get("onchain", {}).get("whale_movements", {}).get("total_whale_volume", 0),
                "whale_outflow": 0,
                "jito_tips_24h": 1500,
                "sentiment_score": market_data.get("sentiment", {}).get("combined_sentiment", 0)
            }
            
            signal = self.signal_engine.generate_signal(signal_input)
            market_data["signals"] = signal
        except Exception as e:
            market_data["signals"]["error"] = str(e)
        
        self.current_market_data = market_data
        self.last_update = datetime.now()
        
        # Gọi callbacks
        for callback in self.data_update_callbacks:
            callback(market_data)
        
        return market_data
    
    def get_price_history(self, minutes: int = 60) -> List[Dict]:
        """
        Lấy lịch sử giá trong N phút gần đây
        """
        if not self.price_stream.price_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        history = []
        
        for entry in self.price_stream.price_history:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= cutoff_time:
                    history.append(entry)
            except:
                continue
        
        return history
    
    def get_market_summary(self) -> Dict:
        """
        Tóm tắt thị trường cho dashboard
        """
        if not self.current_market_data:
            return {"error": "No data available"}
        
        data = self.current_market_data
        
        return {
            "timestamp": data.get("timestamp"),
            "sol_price": data.get("price", {}).get("average", 0),
            "signal": data.get("signals", {}).get("signal", "UNKNOWN"),
            "signal_score": data.get("signals", {}).get("score", 0),
            "risk_environment": data.get("macro", {}).get("risk_environment", "UNKNOWN"),
            "network_health": data.get("onchain", {}).get("network_health", {}).get("health", "UNKNOWN"),
            "sentiment": data.get("sentiment", {}).get("combined_sentiment", 0),
            "whale_activity": data.get("onchain", {}).get("whale_movements", {}).get("whale_count", 0)
        }
    
    def start_continuous_update(self, interval_seconds: int = 60):
        """
        Bắt đầu cập nhật dữ liệu liên tục
        """
        async def update_loop():
            while True:
                try:
                    self.get_realtime_market_data()
                    await asyncio.sleep(interval_seconds)
                except Exception as e:
                    print(f"Error in update loop: {e}")
                    await asyncio.sleep(interval_seconds)
        
        asyncio.run(update_loop())
