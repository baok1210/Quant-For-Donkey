"""
Paper Trading Engine - Mô phỏng giao dịch mà không dùng tiền thật
"""
import pandas as pd
from typing import Dict, List

class PaperTrader:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0  # SOL held
        self.trades = []

    def execute_order(self, action: str, price: float, amount_usd: float = None):
        """
        Execute lệnh ảo
        """
        if action == "BUY":
            if self.capital >= amount_usd:
                sol_amount = amount_usd / price
                self.position += sol_amount
                self.capital -= amount_usd
                self.trades.append({
                    "action": "BUY",
                    "price": price,
                    "amount_usd": amount_usd,
                    "amount_sol": sol_amount,
                    "capital_after": self.capital
                })
        elif action == "SELL":
            if self.position > 0:
                sol_to_sell = amount_usd / price if amount_usd else self.position
                sol_to_sell = min(sol_to_sell, self.position)  # Không bán quá số có
                
                usd_gained = sol_to_sell * price
                self.position -= sol_to_sell
                self.capital += usd_gained
                self.trades.append({
                    "action": "SELL",
                    "price": price,
                    "amount_usd": usd_gained,
                    "amount_sol": sol_to_sell,
                    "capital_after": self.capital
                })

    def get_portfolio_value(self, current_price: float):
        return self.capital + (self.position * current_price)

    def get_pnl(self, current_price: float):
        total_value = self.get_portfolio_value(current_price)
        return total_value - self.initial_capital
