"""
Realistic Backtest Engine - Mô phỏng thực tế: Slippage, Spread, Partial Fill
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

class RealisticBacktestEngine:
    """Backtest với điều kiện thực tế"""
    
    def __init__(self):
        self.positions = []
        self.trades = []
        self.pnl_history = []
    
    def execute_with_realism(self, signal: str, price: float, 
                           orderbook_depth: Dict = None,
                           order_size: float = 1.0) -> Dict:
        """
        Mô phỏng execution thực tế
        """
        # 1. Tính Slippage dựa trên Orderbook Depth
        slippage = self._calculate_slippage(price, orderbook_depth, order_size)
        
        # 2. Tính Spread (BTC ~$1, SOL ~$0.5-2)
        spread = 0.5 if "SOL" in str(orderbook_depth) else 1.0  # Mock spread
        
        # 3. Fill Price = Market Price + Slippage + Spread/2
        fill_direction = 1 if signal == "BUY" else -1
        fill_price = price + (slippage * fill_direction) + (spread/2 * fill_direction)
        
        # 4. Kiểm tra Liquidity (Partial Fill nếu không đủ)
        available_liquidity = self._get_available_liquidity(orderbook_depth, signal)
        fill_ratio = min(1.0, available_liquidity / order_size) if available_liquidity else 1.0
        
        return {
            "signal": signal,
            "original_price": price,
            "fill_price": fill_price,
            "fill_ratio": fill_ratio,
            "slippage": slippage,
            "spread": spread,
            "actual_filled_size": order_size * fill_ratio,
            "execution_cost": abs(fill_price - price)  # Chi phí do slippage
        }
    
    def _calculate_slippage(self, price: float, orderbook_depth: Dict, order_size: float) -> float:
        """Tính slippage dựa trên orderbook depth"""
        if not orderbook_depth:
            # Default slippage: 0.1% cho BTC, 0.5% cho alt
            return price * (0.001 if price > 1000 else 0.005)
        
        # Simulate walking the book
        total_cost = 0
        remaining_size = order_size
        
        if order_size > 100:  # Large order
            return price * 0.005  # 0.5% slippage
        elif order_size > 10:  # Medium
            return price * 0.002  # 0.2%
        else:  # Small
            return price * 0.0005  # 0.05%
    
    def _get_available_liquidity(self, orderbook_depth: Dict, side: str) -> float:
        """Lấy liquidity khả dụng từ orderbook"""
        if not orderbook_depth:
            return 1000  # Default large liquidity
        
        if side == "BUY":
            return orderbook_depth.get("ask_liquidity", 1000)
        else:
            return orderbook_depth.get("bid_liquidity", 1000)
    
    def walk_forward_validation(self, df: pd.DataFrame, 
                              strategy_func,
                              train_window: int = 180, 
                              test_window: int = 30) -> Dict:
        """
        Walk-forward validation: Train 6 tháng, test 1 tháng
        """
        results = []
        
        for i in range(train_window, len(df) - test_window, test_window):
            train_df = df.iloc[i-train_window:i]
            test_df = df.iloc[i:i+test_window]
            
            # Train strategy
            trained_strategy = self._train_strategy(train_df, strategy_func)
            
            # Test on out-of-sample
            test_results = self._test_strategy(trained_strategy, test_df)
            
            results.append({
                "train_period": (df.index[i-train_window], df.index[i]),
                "test_period": (df.index[i], df.index[i+test_window]),
                "test_results": test_results,
                "sharpe": test_results.get("sharpe", 0),
                "profit_factor": test_results.get("profit_factor", 1.0)
            })
        
        return self._aggregate_walk_forward_results(results)
    
    def _train_strategy(self, train_df: pd.DataFrame, strategy_func):
        """Train strategy trên dữ liệu training"""
        # Mock: Return the strategy function itself
        return strategy_func
    
    def _test_strategy(self, strategy, test_df: pd.DataFrame) -> Dict:
        """Test strategy trên dữ liệu out-of-sample"""
        # Execute strategy with realistic simulation
        pnl = []
        for idx, row in test_df.iterrows():
            signal = strategy(row)  # Assume strategy returns signal
            if signal != "HOLD":
                execution = self.execute_with_realism(signal, row['close'])
                pnl.append(execution['fill_price'] - row['close'])  # Mock PnL
        
        if pnl:
            returns = pd.Series(pnl).pct_change().dropna()
            sharpe = returns.mean() / returns.std() if returns.std() != 0 else 0
            return {
                "sharpe": sharpe,
                "total_pnl": sum(pnl),
                "win_rate": len([p for p in pnl if p > 0]) / len(pnl) if pnl else 0,
                "max_dd": self._calculate_max_drawdown(pnl)
            }
        return {"sharpe": 0, "total_pnl": 0, "win_rate": 0}
    
    def _aggregate_walk_forward_results(self, results: List[Dict]) -> Dict:
        """Tổng hợp kết quả walk-forward"""
        if not results:
            return {}
        
        avg_sharpe = np.mean([r['sharpe'] for r in results])
        avg_pf = np.mean([r['profit_factor'] for r in results])
        
        return {
            "avg_sharpe": avg_sharpe,
            "avg_profit_factor": avg_pf,
            "total_periods": len(results),
            "results_by_period": results
        }
    
    def _calculate_max_drawdown(self, pnl_series: List[float]) -> float:
        """Tính Max Drawdown"""
        cumulative = np.cumsum(pnl_series)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / (running_max + 1e-8)
        return min(0, drawdown.min()) if drawdown.size > 0 else 0
