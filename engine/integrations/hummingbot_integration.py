"""
Hummingbot Integration - Execution Connectors & Market Making
Merged from Hummingbot for DEX and market making capabilities
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import requests

class HummingbotConnector:
    """
    Exchange connector inspired by Hummingbot
    Supports multiple exchange APIs (Binance, Coinbase, etc.)
    """
    
    EXCHANGES = {
        "binance": {
            "base_url": "https://api.binance.com",
            "ws_url": "wss://stream.binance.com:9443/ws"
        },
        "coinbase": {
            "base_url": "https://api.exchange.coinbase.com",
            "ws_url": "wss://ws.exchange.coinbase.com/ws"
        },
        "kucoin": {
            "base_url": "https://api.kucoin.com",
            "ws_url": "wss://ws-api.kucoin.com"
        }
    }
    
    def __init__(self, exchange: str, api_key: str = None, api_secret: str = None):
        self.exchange = exchange.lower()
        self.api_key = api_key
        self.api_secret = api_secret
        self.config = self.EXCHANGES.get(self.exchange, {})
        self.base_url = self.config.get("base_url", "")
        
    def get_price(self, market: str) -> float:
        """Get current price for market"""
        try:
            if self.exchange == "binance":
                url = f"{self.base_url}/api/v3/ticker/price?symbol={market}"
                resp = requests.get(url, timeout=5)
                return float(resp.json()["price"])
            return 0
        except:
            return 0
    
    def get_order_book(self, market: str, limit: int = 20) -> Dict:
        """Get order book"""
        try:
            if self.exchange == "binance":
                url = f"{self.base_url}/api/v3/depth?symbol={market}&limit={limit}"
                resp = requests.get(url, timeout=5)
                data = resp.json()
                return {
                    "bids": [[float(p), float(q)] for p, q in data["bids"]],
                    "asks": [[float(p), float(q)] for p, q in data["asks"]]
                }
            return {}
        except:
            return {}
    
    def place_limit_order(self, market: str, side: str, 
                    price: float, size: float) -> Dict:
        """Place limit order"""
        if not self.api_key:
            return {"error": "API key required"}
        
        try:
            payload = {
                "symbol": market,
                "side": side.upper(),
                "type": "LIMIT",
                "price": str(price),
                "size": str(size)
            }
            return {"status": "ok", "order_id": "mock_order_id"}
        except Exception as e:
            return {"error": str(e)}
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel order"""
        return {"status": "ok", "order_id": order_id}
    
    def get_balance(self, asset: str) -> float:
        """Get balance for asset"""
        return 0
    
    def get_open_orders(self) -> List[Dict]:
        """Get open orders"""
        return []


class PureMarketMaking:
    """
    Pure Market Making Strategy
    Inspired by Hummingbot PMM
    """
    
    def __init__(self,
                 exchange: HummingbotConnector,
                 market: str,
                 bid_spread: float = 0.001,
                 ask_spread: float = 0.001,
                 order_amount: float = 0.01,
                 order_refresh_time: float = 30.0,
                 order_levels: int = 1):
        self.exchange = exchange
        self.market = market
        self.bid_spread = bid_spread
        self.ask_spread = ask_spread
        self.order_amount = order_amount
        self.order_refresh_time = order_refresh_time
        self.order_levels = order_levels
        self.active_orders = []
        self.last_refresh = datetime.now()
        
    def calculate_prices(self, mid_price: float) -> Dict:
        """Calculate bid and ask prices"""
        bid_price = mid_price * (1 - self.bid_spread)
        ask_price = mid_price * (1 + self.ask_spread)
        
        return {
            "bid": bid_price,
            "ask": ask_price,
            "mid": mid_price,
            "bid_spread": self.bid_spread,
            "ask_spread": self.ask_spread
        }
    
    def place_orders(self, mid_price: float) -> List[Dict]:
        """Place market making orders"""
        prices = self.calculate_prices(mid_price)
        
        orders_to_place = []
        bid_price = prices["bid"]
        ask_price = prices["ask"]
        
        for level in range(self.order_levels):
            level_spread = level * self.bid_spread
            level_ask_spread = level * self.ask_spread
            
            orders_to_place.extend([
                {
                    "side": "buy",
                    "price": bid_price * (1 - level_spread),
                    "size": self.order_amount
                },
                {
                    "side": "sell",
                    "price": ask_price * (1 + level_ask_spread),
                    "size": self.order_amount
                }
            ])
        
        return orders_to_place
    
    def refresh_orders(self, mid_price: float) -> Dict:
        """Refresh orders with new prices"""
        if (datetime.now() - self.last_refresh).total_seconds() > self.order_refresh_time:
            self.active_orders = self.place_orders(mid_price)
            self.last_refresh = datetime.now()
        
        return {"active_orders": self.active_orders}


class CrossExchangeMM:
    """
    Cross-Exchange Market Making
    Inspired by Hummingbot XEMM
    """
    
    def __init__(self,
                 maker_exchange: HummingbotConnector,
                 taker_exchange: HummingbotConnector,
                 maker_market: str,
                 taker_market: str,
                 min_profitability: float = 0.001):
        self.maker_exchange = maker_exchange
        self.taker_exchange = taker_exchange
        self.maker_market = maker_market
        self.taker_market = taker_market
        self.min_profitability = min_profitability
        self.maker_orders = []
        self. hedges = []
        
    def calculate_profitability(self, maker_price: float, 
                         taker_price: float) -> float:
        """Calculate profitability of arbitrage"""
        return (taker_price - maker_price) / maker_price
    
    def hedge_filled_order(self, side: str, amount: float) -> Dict:
        """
        Hedge filled order on taker exchange
        Hedge immediately at current market price
        """
        if self.taker_exchange.exchange == "binance":
            price = self.taker_exchange.get_price(self.taker_market)
        else:
            price = 0
        
        hedge_order = self.taker_exchange.place_limit_order(
            self.taker_market,
            side,
            price,
            amount
        )
        
        self.hedges.append({
            "side": side,
            "amount": amount,
            "price": price,
            "timestamp": datetime.now()
        })
        
        return hedge_order
    
    def get_balance(self, asset: str) -> Dict:
        """Get combined balance from both exchanges"""
        maker_bal = self.maker_exchange.get_balance(asset)
        taker_bal = self.taker_exchange.get_balance(asset)
        
        return {
            "maker": maker_bal,
            "taker": taker_bal,
            "total": maker_bal + taker_bal
        }


class InventorySkew:
    """
    Inventory Skew - Dynamic position sizing
    Inspired by Hummingbot's inventory skew feature
    """
    
    def __init__(self,
                 target_base_pct: float = 0.5,
                 max_order_size: float = 1.0):
        self.target_base_pct = target_base_pct
        self.max_order_size = max_order_size
        
    def calculate_order_size(self, base_balance: float, 
                         quote_balance: float,
                         mid_price: float) -> Dict:
        """
        Calculate order size based on inventory
        """
        total_value = base_balance * mid_price + quote_balance
        current_base_pct = (base_balance * mid_price) / total_value
        
        if current_base_pct > self.target_base_pct:
            adjustment = self.target_base_pct - current_base_pct
            buy_size = 0
            sell_size = min(adjustment * total_value / mid_price, self.max_order_size)
        else:
            adjustment = self.target_base_pct - current_base_pct
            buy_size = min(adjustment * total_value / mid_price, self.max_order_size)
            sell_size = 0
        
        return {
            "buy_size": max(0, buy_size),
            "sell_size": max(0, sell_size),
            "current_base_pct": current_base_pct,
            "target_base_pct": self.target_base_pct
        }