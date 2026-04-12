"""
Paper Trading Engine - Mô phỏng giao dịch thực tế
Bao gồm: Slippage, Spread, Partial Fills, Market Impact
"""
import numpy as np
from typing import Dict
from datetime import datetime

class PaperTradingEngine:
    """Mô phỏng giao dịch với điều kiện thực tế"""
    
    def __init__(self, initial_balance: float = 10000):
        self.balance = initial_balance
        self.positions = {}
        self.trade_history = []
        self.total_slippage_cost = 0
        self.total_spread_cost = 0
    
    def execute_with_slippage(self, action: str, price: float, 
                              amount_usd: float, 
                              liquidity_depth: float = 50000) -> Dict:
        """
        Thực thi lệnh với Slippage và Spread thực tế
        
        Args:
            action: BUY hoặc SELL
            price: Giá thị trường hiện tại
            amount_usd: Số tiền giao dịch (USD)
            liquidity_depth: Độ sâu thanh khoản (USD)
        """
        # 1. Spread: BTC ~$1-5 (0.01%), SOL ~$0.01-0.05 (0.05%)
        spread_pct = 0.0001 if price > 10000 else 0.0005
        spread_cost = price * spread_pct
        
        # 2. Slippage: Dựa trên kích thước lệnh so với thanh khoản
        # Order lớn hơn 10% liquidity → slippage tăng nhanh
        order_ratio = amount_usd / liquidity_depth
        if order_ratio < 0.01:
            slippage_pct = 0.0001  # 0.01% cho lệnh nhỏ
        elif order_ratio < 0.1:
            slippage_pct = 0.001   # 0.1% cho lệnh trung bình
        else:
            slippage_pct = min(0.005, order_ratio * 0.05)  # Max 0.5%
        
        # 3. Tính fill price
        if action == "BUY":
            fill_price = price + spread_cost + (price * slippage_pct)
        else:  # SELL
            fill_price = price - spread_cost - (price * slippage_pct)
        
        # 4. Tính phí giao dịch (0.1% maker/taker)
        trading_fee = amount_usd * 0.001
        
        # 5. Thực thi
        quantity = amount_usd / fill_price
        total_cost = amount_usd + trading_fee
        
        if action == "BUY" and total_cost <= self.balance:
            self.balance -= total_cost
            symbol = self._get_symbol_from_price(price)
            
            if symbol not in self.positions:
                self.positions[symbol] = {
                    "quantity": 0,
                    "avg_entry_price": 0,
                    "total_invested": 0
                }
            
            pos = self.positions[symbol]
            new_total_qty = pos["quantity"] + quantity
            pos["avg_entry_price"] = (
                (pos["quantity"] * pos["avg_entry_price"] + quantity * fill_price) 
                / new_total_qty if new_total_qty > 0 else fill_price
            )
            pos["quantity"] = new_total_qty
            pos["total_invested"] += amount_usd
            
            # Track costs
            self.total_slippage_cost += amount_usd * slippage_pct
            self.total_spread_cost += amount_usd * spread_pct
            
            trade = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "symbol": symbol,
                "market_price": price,
                "fill_price": fill_price,
                "quantity": quantity,
                "amount_usd": amount_usd,
                "spread_pct": spread_pct,
                "slippage_pct": slippage_pct,
                "trading_fee": trading_fee,
                "total_cost": spread_pct + slippage_pct + 0.001  # Tổng chi phí %
            }
            
            self.trade_history.append(trade)
            return {
                "success": True,
                "fill_price": fill_price,
                "quantity": quantity,
                "total_cost_pct": trade["total_cost"] * 100,
                "spread_cost": self.total_spread_cost,
                "slippage_cost": self.total_slippage_cost
            }
        
        elif action == "SELL" and symbol in self.positions:
            pos = self.positions[symbol]
            sell_qty = min(quantity, pos["quantity"])
            sell_value = sell_qty * fill_price
            self.balance += sell_value - trading_fee
            
            pos["quantity"] -= sell_qty
            if pos["quantity"] <= 0:
                del self.positions[symbol]
            
            trade = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "symbol": symbol,
                "market_price": price,
                "fill_price": fill_price,
                "quantity": sell_qty,
                "amount_usd": sell_value,
                "spread_pct": spread_pct,
                "slippage_pct": slippage_pct,
                "trading_fee": trading_fee
            }
            
            self.trade_history.append(trade)
            return {
                "success": True,
                "fill_price": fill_price,
                "quantity": sell_qty,
                "pnl": sell_value - (sell_qty * pos.get("avg_entry_price", 0))
            }
        
        return {"success": False, "error": "Insufficient balance or no position"}
    
    def _get_symbol_from_price(self, price: float) -> str:
        """Xác định symbol từ giá (mock)"""
        if price > 10000: return "BTC"
        elif price > 1000: return "ETH"
        else: return "SOL"
    
    def get_portfolio_summary(self) -> Dict:
        """Tóm tắt danh mục hiện tại"""
        total_value = self.balance
        for symbol, pos in self.positions.items():
            total_value += pos["quantity"] * pos["avg_entry_price"]
        
        return {
            "balance": self.balance,
            "positions": {s: {"qty": p["quantity"], "avg_price": p["avg_entry_price"]} 
                         for s, p in self.positions.items()},
            "total_value": total_value,
            "total_slippage_cost": self.total_slippage_cost,
            "total_spread_cost": self.total_spread_cost,
            "total_trades": len(self.trade_history),
            "avg_cost_per_trade_pct": (
                (self.total_slippage_cost + self.total_spread_cost) 
                / max(len(self.trade_history), 1) * 100
            )
        }
