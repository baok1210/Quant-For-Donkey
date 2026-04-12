"""
Real-time Price Stream - Đa nguồn dữ liệu giá
1. CoinGecko: Miễn phí, 10-30 req/phút, không cần API key
2. Binance WebSocket: Real-time, độ trễ mili giây, miễn phí
3. DIA Free Crypto API: 3000+ tokens, không cần API key
"""
import os
import json
import time
import asyncio
import aiohttp
import requests
import websockets
from typing import Dict, List, Optional, Callable
from datetime import datetime

class CoinGeckoAPI:
    """
    CoinGecko API - Gói Public miễn phí
    Giới hạn: 10-30 requests/phút
    Không cần API key
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    @staticmethod
    def get_price(ids: List[str] = ["solana", "bitcoin", "ethereum", "ripple"],
                  vs_currencies: List[str] = ["usd"]) -> Dict:
        """
        Lấy giá từ CoinGecko
        
        Args:
            ids: List coin ids (solana, bitcoin, ethereum, ripple)
            vs_currencies: List currencies (usd, btc, eth)
        
        Returns:
            Dict chứa giá từ CoinGecko
        """
        try:
            params = {
                "ids": ",".join(ids),
                "vs_currencies": ",".join(vs_currencies)
            }
            
            response = requests.get(
                f"{CoinGeckoAPI.BASE_URL}/simple/price",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                for coin_id, price_data in data.items():
                    for currency, price in price_data.items():
                        prices[f"{coin_id}_{currency}"] = price
                
                return {
                    "source": "coingecko",
                    "prices": prices,
                    "sol_usd": prices.get("solana_usd", 0),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"source": "coingecko", "error": f"HTTP {response.status_code}", "sol_usd": 0}
        except Exception as e:
            return {"source": "coingecko", "error": str(e), "sol_usd": 0}
    
    @staticmethod
    def get_market_data(ids: List[str] = ["solana"]) -> Dict:
        """Lấy dữ liệu thị trường mở rộng"""
        try:
            prices = {}
            for coin_id in ids:
                response = requests.get(
                    f"{CoinGeckoAPI.BASE_URL}/simple/price",
                    params={
                        "ids": coin_id,
                        "vs_currencies": "usd",
                        "include_market_cap": "true",
                        "include_24hr_vol": "true",
                        "include_24hr_change": "true"
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if coin_id in data:
                        prices[coin_id] = data[coin_id]
            
            return {"source": "coingecko", "market_data": prices}
        except Exception as e:
            return {"source": "coingecko", "error": str(e)}


class BinanceWebSocket:
    """
    Binance WebSocket - Dữ liệu real-time, độ trễ mili giây
    Hoàn toàn miễn phí, không cần API key cho public streams
    """
    
    STREAM_URL = "wss://stream.binance.com:9443/ws"
    REST_URL = "https://api.binance.com/api/v3"
    
    def __init__(self):
        self.current_price = None
        self.price_history = []
        self.callbacks: List[Callable] = []
        self.running = False
    
    def get_price_rest(self, symbol: str = "SOLUSDT") -> Dict:
        """
        Lấy giá qua REST API (không cần WebSocket)
        """
        try:
            response = requests.get(
                f"{self.REST_URL}/ticker/price",
                params={"symbol": symbol},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                price = float(data["price"])
                self.current_price = price
                self.price_history.append({
                    "price": price,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "source": "binance_rest",
                    "symbol": symbol,
                    "price": price,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"source": "binance_rest", "error": f"HTTP {response.status_code}", "price": 0}
        except Exception as e:
            return {"source": "binance_rest", "error": str(e), "price": 0}
    
    def get_ticker_24h(self, symbol: str = "SOLUSDT") -> Dict:
        """Lấy thống kê 24h từ Binance"""
        try:
            response = requests.get(
                f"{self.REST_URL}/ticker/24hr",
                params={"symbol": symbol},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "binance_24h",
                    "symbol": data.get("symbol"),
                    "price": float(data.get("lastPrice", 0)),
                    "price_change": float(data.get("priceChange", 0)),
                    "price_change_pct": float(data.get("priceChangePercent", 0)),
                    "high_24h": float(data.get("highPrice", 0)),
                    "low_24h": float(data.get("lowPrice", 0)),
                    "volume_24h": float(data.get("volume", 0)),
                    "quote_volume_24h": float(data.get("quoteVolume", 0)),
                    "trades_24h": int(data.get("count", 0)),
                    "timestamp": datetime.now().isoformat()
                }
            return {"source": "binance_24h", "error": "API error"}
        except Exception as e:
            return {"source": "binance_24h", "error": str(e)}
    
    async def stream_price(self, symbol: str = "solusdt"):
        """
        WebSocket stream - Nhận giá real-time (độ trễ mili giây)
        
        Usage:
            async for price in binance_ws.stream_price("solusdt"):
                print(price)
        """
        uri = f"{self.STREAM_URL}/{symbol.lower()}@trade"
        
        try:
            async with websockets.connect(uri) as ws:
                self.running = True
                while self.running:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=30)
                        data = json.loads(message)
                        
                        price = float(data["p"])  # Price
                        quantity = float(data["q"])  # Quantity
                        trade_time = data["T"]  # Trade timestamp
                        
                        self.current_price = price
                        self.price_history.append({
                            "price": price,
                            "quantity": quantity,
                            "timestamp": datetime.fromtimestamp(trade_time/1000).isoformat()
                        })
                        
                        # Gọi callbacks
                        for callback in self.callbacks:
                            callback(price)
                        
                        yield {
                            "price": price,
                            "quantity": quantity,
                            "trade_time": trade_time,
                            "timestamp": datetime.now().isoformat()
                        }
                    except asyncio.TimeoutError:
                        continue
        except Exception as e:
            print(f"WebSocket error: {e}")
            self.running = False
    
    def add_callback(self, callback: Callable):
        """Thêm callback khi có giá mới"""
        self.callbacks.append(callback)
    
    def stop_stream(self):
        """Dừng stream"""
        self.running = False


class DIAAPI:
    """
    DIA Free Crypto API - 3000+ tokens, không cần API key
    URL: https://api.diadata.org/v1/
    """
    
    BASE_URL = "https://api.diadata.org/v1"
    
    @staticmethod
    def get_price(symbol: str = "SOL", exchange: str = "uniswap") -> Dict:
        """
        Lấy giá từ DIA
        
        Args:
            symbol: Symbol (SOL, BTC, ETH)
            exchange: Exchange (uniswap, binance, etc)
        
        Returns:
            Dict chứa giá từ DIA
        """
        try:
            response = requests.get(
                f"{DIAAPI.BASE_URL}/assetQuotation/{exchange}/{symbol.upper()}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "dia",
                    "symbol": data.get("Symbol"),
                    "price": float(data.get("Price", 0)),
                    "volume_24h": float(data.get("Volume24h", 0)),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"source": "dia", "error": f"HTTP {response.status_code}", "price": 0}
        except Exception as e:
            return {"source": "dia", "error": str(e), "price": 0}
    
    @staticmethod
    def get_all_prices() -> Dict:
        """Lấy tất cả giá từ DIA"""
        try:
            response = requests.get(
                f"{DIAAPI.BASE_URL}/quotation",
                timeout=10
            )
            
            if response.status_code == 200:
                return {"source": "dia", "all_prices": response.json()}
            return {"source": "dia", "error": "API error"}
        except Exception as e:
            return {"source": "dia", "error": str(e)}


class PriceAggregator:
    """
    Tổng hợp giá từ 3 nguồn:
    1. CoinGecko (REST, 10-30 req/phút)
    2. Binance (REST + WebSocket, real-time mili giây)
    3. DIA (REST, 3000+ tokens)
    """
    
    def __init__(self):
        self.coingecko = CoinGeckoAPI()
        self.binance = BinanceWebSocket()
        self.dia = DIAAPI()
        self.last_update = None
    
    def fetch_all_sources(self) -> Dict:
        """
        Lấy giá từ tất cả nguồn
        
        Returns:
            Dict chứa giá từ 3 nguồn
        """
        results = {
            "coingecko": None,
            "binance": None,
            "dia": None,
            "average_sol": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. CoinGecko
        cg_result = self.coingecko.get_price(["solana", "bitcoin", "ethereum"], ["usd"])
        results["coingecko"] = cg_result
        
        # 2. Binance REST
        binance_result = self.binance.get_price_rest("SOLUSDT")
        results["binance"] = binance_result
        
        # 3. DIA
        dia_result = self.dia.get_price("SOL", "uniswap")
        results["dia"] = dia_result
        
        # Tính giá trung bình SOL
        sol_prices = []
        if cg_result.get("sol_usd"):
            sol_prices.append(cg_result["sol_usd"])
        if binance_result.get("price"):
            sol_prices.append(binance_result["price"])
        if dia_result.get("price"):
            sol_prices.append(dia_result["price"])
        
        if sol_prices:
            results["average_sol"] = sum(sol_prices) / len(sol_prices)
            results["price_count"] = len(sol_prices)
        else:
            results["average_sol"] = 0
            results["price_count"] = 0
        
        self.last_update = datetime.now()
        return results
    
    def get_best_source(self) -> str:
        """Xác định nguồn đáng tin cậy nhất"""
        # Ưu tiên: Binance > CoinGecko > DIA
        if self.binance.current_price:
            return "binance"
        
        results = self.fetch_all_sources()
        if results["coingecko"] and not results["coingecko"].get("error"):
            return "coingecko"
        if results["dia"] and not results["dia"].get("error"):
            return "dia"
        
        return "none"
    
    def start_realtime_stream(self, callback: Callable = None):
        """
        Bắt đầu stream real-time từ Binance WebSocket
        """
        if callback:
            self.binance.add_callback(callback)
        
        async def stream():
            async for trade in self.binance.stream_price("solusdt"):
                if callback:
                    callback(trade["price"])
        
        asyncio.run(stream())
    
    def get_solana_market_overview(self) -> Dict:
        """
        Tổng quan thị trường SOL từ tất cả nguồn
        """
        all_data = self.fetch_all_sources()
        binance_24h = self.binance.get_ticker_24h("SOLUSDT")
        
        return {
            "price_sources": all_data,
            "binance_24h": binance_24h,
            "summary": {
                "sol_price_avg": all_data.get("average_sol", 0),
                "sol_price_binance": all_data.get("binance", {}).get("price", 0),
                "sol_price_coingecko": all_data.get("coingecko", {}).get("sol_usd", 0),
                "price_change_24h": binance_24h.get("price_change_pct", 0),
                "volume_24h": binance_24h.get("quote_volume_24h", 0),
                "high_24h": binance_24h.get("high_24h", 0),
                "low_24h": binance_24h.get("low_24h", 0),
            },
            "timestamp": datetime.now().isoformat()
        }
