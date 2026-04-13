"""
Portfolio Management Engine (v4.3.2)
Tích hợp: Dynamic Rebalancing, Tax-loss Harvesting, Portfolio Rotation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

class PortfolioManager:
    """
    Quản lý danh mục đầu tư và tự động cân bằng lại tỷ trọng
    """
    
    def __init__(self, initial_assets: Dict[str, float] = None):
        # Assets format: {"SOL": 100, "USDC": 5000}
        self.assets = initial_assets or {"SOL": 0.0, "USDC": 10000.0}
        self.target_weights = {"SOL": 0.5, "USDC": 0.5}  # Mặc định 50/50
        self.rebalance_threshold = 0.05  # 5% drift threshold
        self.history = []

    def update_assets(self, assets: Dict[str, float]):
        """Cập nhật số dư tài sản thực tế"""
        self.assets = assets
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "assets": assets.copy()
        })

    def set_target_weights(self, weights: Dict[str, float]):
        """Thiết lập tỷ trọng mục tiêu (tổng phải bằng 1.0)"""
        if abs(sum(weights.values()) - 1.0) > 1e-6:
            raise ValueError("Tổng tỷ trọng phải bằng 1.0")
        self.target_weights = weights

    def calculate_rebalance(self, prices: Dict[str, float]) -> Dict:
        """
        Tính toán số lượng cần mua/bán để cân bằng lại danh mục
        """
        # 1. Tính tổng giá trị danh mục
        total_value = 0
        current_values = {}
        for asset, amount in self.assets.items():
            price = prices.get(asset, 1.0) if asset != "USDC" else 1.0
            val = amount * price
            current_values[asset] = val
            total_value += val
        
        if total_value == 0:
            return {"should_rebalance": False, "total_value": 0}
            
        # 2. Tính tỷ trọng hiện tại và sai lệch (drift)
        drifts = {}
        for asset, val in current_values.items():
            current_weight = val / total_value
            target_weight = self.target_weights.get(asset, 0)
            drifts[asset] = current_weight - target_weight
            
        # 3. Kiểm tra xem có cần rebalance không
        max_drift = max([abs(d) for d in drifts.values()])
        should_rebalance = max_drift >= self.rebalance_threshold
        
        # 4. Tính toán số lượng cần mua/bán
        trades = []
        for asset, drift in drifts.items():
            if abs(drift) > 0.001:  # Bỏ qua các sai lệch siêu nhỏ
                target_val = total_value * self.target_weights.get(asset, 0)
                diff_val = target_val - current_values[asset]
                
                price = prices.get(asset, 1.0) if asset != "USDC" else 1.0
                amount_to_trade = diff_val / price
                
                trades.append({
                    "asset": asset,
                    "action": "BUY" if diff_val > 0 else "SELL",
                    "amount": abs(amount_to_trade),
                    "value_usd": abs(diff_val),
                    "drift_pct": drift * 100
                })
        
        return {
            "should_rebalance": should_rebalance,
            "total_value": total_value,
            "max_drift_pct": max_drift * 100,
            "drifts": drifts,
            "trades": trades,
            "timestamp": datetime.now().isoformat()
        }

    def execute_rebalance(self, trades: List[Dict]):
        """Mô phỏng thực thi rebalance (sẽ kết nối với sàn sau)"""
        for trade in trades:
            asset = trade["asset"]
            action = trade["action"]
            amount = trade["amount"]
            
            if action == "BUY":
                self.assets[asset] += amount
                # Giả sử mua bằng USDC
                if asset != "USDC":
                    self.assets["USDC"] -= trade["value_usd"]
            else:
                self.assets[asset] -= amount
                if asset != "USDC":
                    self.assets["USDC"] += trade["value_usd"]
        
        print(f"✅ Executed rebalance trades: {len(trades)} assets updated.")

    def tax_loss_harvesting(self, holdings_data: List[Dict], threshold_loss: float = 0.1) -> List[Dict]:
        """
        Tìm kiếm các cơ hội chốt lỗ để tối ưu thuế (Tax-loss harvesting)
        holdings_data format: [{"asset": "SOL", "cost_basis": 150, "current_price": 120, "amount": 10}]
        """
        opportunities = []
        for holding in holdings_data:
            loss_pct = (holding["cost_basis"] - holding["current_price"]) / holding["cost_basis"]
            if loss_pct >= threshold_loss:
                opportunities.append({
                    "asset": holding["asset"],
                    "loss_pct": loss_pct * 100,
                    "suggested_action": "SELL_AND_REBUY",
                    "reason": f"Tax-loss harvesting: {loss_pct:.1%} loss detected."
                })
        return opportunities

    def get_portfolio_rotation_signal(self, market_regime: str, risk_score: float) -> Dict:
        """
        Xác định tín hiệu xoay chuyển danh mục (Portfolio Rotation)
        Ví dụ: Trong Bear Market -> Chuyển 80% sang USDC
        """
        if market_regime == "BEAR_MARKET" or risk_score > 0.7:
            return {
                "rotation": "DEFENSIVE",
                "target_weights": {"SOL": 0.2, "USDC": 0.8},
                "reason": "Market risk is high, rotating to stable assets."
            }
        elif market_regime == "BULL_MARKET":
            return {
                "rotation": "AGGRESSIVE",
                "target_weights": {"SOL": 0.8, "USDC": 0.2},
                "reason": "Strong bull market detected, rotating to growth assets."
            }
        else:
            return {
                "rotation": "BALANCED",
                "target_weights": {"SOL": 0.5, "USDC": 0.5},
                "reason": "Normal market conditions, maintaining balanced portfolio."
            }
