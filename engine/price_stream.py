"""
Real-time Price Stream - Kết nối Solana WebSocket để nhận giá SOL real-time
"""
import os
import json
import asyncio
import websockets
from typing import Dict, List, Optional
from datetime import datetime
import requests

class SolanaPriceStream:
    """Stream giá SOL real-time từ Solana RPC"""
    
    def __init__(self):
        self.helius_key = os.getenv("HELUS_API_KEY")
        self.quicknode_key = os.getenv("QUICKNODE_API_KEY")
        
        # Solana mainnet RPC endpoints
        self.rpc_endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
        ]
        
        if self.helius_key:
            self.helius_endpoint = f"https://mainnet.helius-rpc.com/?api-key={self.helius_key}"
        elif self.quicknode_key:
            self.helius_endpoint = f"https://{self.quicknode_key}.quiknode.pro/"
        else:
            self.helius_endpoint = self.rpc_endpoints[0]
        
        self.current_price = None
        self.price_history = []
        self.price_callbacks = []
        
    def get_current_price(self) -> Dict:
        """
        Lấy giá SOL hiện tại từ RPC (non-blocking)
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getLatestBlockhash",
                "params": [{"commitment": "confirmed"}]
            }
            
            response = requests.post(self.helius_endpoint, json=payload, timeout=5)
            if response.status_code == 200:
                # Lấy giá từ CoinGecko API (đáng tin cậy hơn)
                return self._get_price_from_coingecko()
            return {"price": 0, "error": "RPC error"}
        except:
            return self._get_price_from_coingecko()
    
    def _get_price_from_coingecko(self) -> Dict:
        """
        Lấy giá SOL từ CoinGecko API (đáng tin cậy)
        """
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "solana", "vs_currencies": "usd"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                price = data.get("solana", {}).get("usd", 0)
                
                self.current_price = price
                self.price_history.append({
                    "price": price,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Gọi callbacks nếu có
                for callback in self.price_callbacks:
                    callback(price)
                
                return {"price": price, "source": "coingecko"}
        except:
            pass
        
        return {"price": 0, "error": "All price sources failed"}
    
    def add_price_callback(self, callback):
        """
        Thêm callback function để nhận price updates
        """
        self.price_callbacks.append(callback)
    
    def start_price_stream(self):
        """
        Bắt đầu stream price (async)
        """
        async def stream():
            uri = "wss://api.mainnet-beta.solana.com"
            
            async with websockets.connect(uri) as websocket:
                # Subscribe to SOL/USDT orderbook
                subscribe_msg = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "subscribe",
                    "params": [
                        "account",
                        "So11111111111111111111111111111111111111112",  # SOL token account
                        {"commitment": "processed"}
                    ]
                }
                
                await websocket.send(json.dumps(subscribe_msg))
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if "params" in data:
                            # Process account update
                            self._process_account_update(data)
                            
                    except websockets.exceptions.ConnectionClosed:
                        break
        
        asyncio.run(stream())
    
    def _process_account_update(self, data):
        """
        Xử lý account update từ Solana RPC
        """
        # Trong thực tế sẽ parse account data để lấy price
        # Hiện tại dùng CoinGecko làm primary source
        price_data = self.get_current_price()
        
        if price_data.get("price"):
            self.current_price = price_data["price"]
            self.price_history.append({
                "price": price_data["price"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Gọi callbacks
            for callback in self.price_callbacks:
                callback(price_data["price"])

class PriceAggregator:
    """Tổng hợp giá từ nhiều nguồn"""
    
    def __init__(self):
        self.sources = {
            "coingecko": None,
            "binance": None,
            "okx": None,
            "bybit": None
        }
        self.stream = SolanaPriceStream()
        
    def fetch_all_prices(self) -> Dict:
        """
        Lấy giá từ tất cả sources
        """
        prices = {}
        
        # CoinGecko
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "solana", "vs_currencies": "usd"},
                timeout=5
            )
            if response.status_code == 200:
                prices["coingecko"] = response.json()["solana"]["usd"]
        except:
            pass
        
        # Binance
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price",
                params={"symbol": "SOLUSDT"},
                timeout=5
            )
            if response.status_code == 200:
                prices["binance"] = float(response.json()["price"])
        except:
            pass
        
        # OKX
        try:
            response = requests.get(
                "https://www.okx.com/api/v5/market/ticker",
                params={"instId": "SOL-USDT"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    prices["okx"] = float(data["data"][0]["last"])
        except:
            pass
        
        return prices
    
    def get_average_price(self) -> float:
        """
        Tính trung bình giá từ các sources
        """
        prices = self.fetch_all_prices()
        if prices:
            return sum(prices.values()) / len(prices)
        return self.stream.get_current_price().get("price", 0)
