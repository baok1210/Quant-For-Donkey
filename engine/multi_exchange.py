"""
Multi-Exchange Support - Smart Order Routing across exchanges
Hỗ trợ: Binance, OKX, Bybit, Coinbase, Kraken
"""
import ccxt
import os
from typing import Dict, List, Optional
from datetime import datetime

class MultiExchangeManager:
    """Quản lý nhiều sàn giao dịch với Smart Order Routing"""
    
    def __init__(self):
        self.exchanges = {}
        self._init_exchanges()
    
    def _init_exchanges(self):
        """Khởi tạo các exchange connection"""
        exchange_configs = {
            "binance": {
                "apiKey": os.getenv("BINANCE_API_KEY"),
                "secret": os.getenv("BINANCE_SECRET_KEY"),
                "options": {"defaultType": "spot"}
            },
            "okx": {
                "apiKey": os.getenv("OKX_API_KEY"),
                "secret": os.getenv("OKX_SECRET_KEY"),
                "password": os.getenv("OKX_PASSPHRASE"),
                "options": {"defaultType": "spot"}
            },
            "bybit": {
                "apiKey": os.getenv("BYBIT_API_KEY"),
                "secret": os.getenv("BYBIT_SECRET_KEY"),
                "options": {"defaultType": "spot"}
            },
            "coinbase": {
                "apiKey": os.getenv("COINBASE_API_KEY"),
                "secret": os.getenv("COINBASE_SECRET_KEY"),
                "password": os.getenv("COINBASE_PASSPHRASE"),
                "options": {"defaultType": "spot"}
            },
            "kraken": {
                "apiKey": os.getenv("KRAKEN_API_KEY"),
                "secret": os.getenv("KRAKEN_SECRET_KEY"),
                "options": {"defaultType": "spot"}
            }
        }
        
        for name, config in exchange_configs.items():
            if config["apiKey"]:
                try:
                    exchange_class = getattr(ccxt, name)
                    self.exchanges[name] = exchange_class(config)
                    self.exchanges[name].enableRateLimit = True
                except Exception as e:
                    print(f"Failed to init {name}: {e}")
    
    def get_ticker(self, symbol="SOL/USDT", exchange_name: Optional[str] = None) -> Dict:
        """
        Lấy giá hiện tại từ một hoặc tất cả sàn
        """
        results = {}
        
        exchanges_to_check = [exchange_name] if exchange_name else self.exchanges.keys()
        
        for name in exchanges_to_check:
            if name in self.exchanges:
                try:
                    ticker = self.exchanges[name].fetch_ticker(symbol)
                    results[name] = {
                        "symbol": ticker["symbol"],
                        "last": ticker["last"],
                        "bid": ticker["bid"],
                        "ask": ticker["ask"],
                        "volume": ticker["quoteVolume"],
                        "timestamp": ticker["timestamp"]
                    }
                except Exception as e:
                    results[name] = {"error": str(e)}
        
        return results
    
    def get_best_price(self, symbol="SOL/USDT", side="buy") -> Dict:
        """
        Tìm giá tốt nhất từ tất cả sàn (Smart Order Routing)
        """
        tickers = self.get_ticker(symbol)
        
        best = None
        best_exchange = None
        
        for exchange_name, data in tickers.items():
            if "error" not in data:
                if side == "buy":
                    price = data["ask"]
                else:
                    price = data["bid"]
                
                if best is None or (side == "buy" and price < best) or (side == "sell" and price > best):
                    best = price
                    best_exchange = exchange_name
        
        return {
            "best_exchange": best_exchange,
            "best_price": best,
            "all_prices": tickers
        }
    
    def execute_order(self, symbol, side, amount, exchange_name: Optional[str] = None) -> Dict:
        """
        Thực thi lệnh trên sàn được chọn hoặc sàn tốt nhất
        """
        if exchange_name:
            if exchange_name not in self.exchanges:
                return {"error": f"Exchange {exchange_name} not available"}
            exchange = self.exchanges[exchange_name]
        else:
            # Chọn sàn tốt nhất
            best = self.get_best_price(symbol, "buy" if side == "buy" else "sell")
            if not best["best_exchange"]:
                return {"error": "No available exchange"}
            exchange = self.exchanges[best["best_exchange"]]
        
        try:
            order = exchange.create_market_order(symbol, side, amount)
            return {
                "success": True,
                "order_id": order.get("id"),
                "exchange": exchange.name,
                "side": side,
                "amount": amount,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_balances(self, exchange_name: Optional[str] = None) -> Dict:
        """
        Lấy số dư từ một hoặc tất cả sàn
        """
        results = {}
        
        exchanges_to_check = [exchange_name] if exchange_name else self.exchanges.keys()
        
        for name in exchanges_to_check:
            if name in self.exchanges:
                try:
                    balance = self.exchanges[name].fetch_balance()
                    results[name] = {
                        "total": balance.get("total", {}),
                        "free": balance.get("free", {}),
                        "used": balance.get("used", {})
                    }
                except Exception as e:
                    results[name] = {"error": str(e)}
        
        return results
    
    def get_all_markets(self) -> List[str]:
        """
        Lấy danh sách tất cả cặp giao dịch khả dụng
        """
        markets = []
        for name, exchange in self.exchanges.items():
            try:
                exchange.load_markets()
                for symbol in exchange.markets.keys():
                    if "SOL" in symbol and "USDT" in symbol:
                        markets.append(f"{name}:{symbol}")
            except:
                pass
        return markets
