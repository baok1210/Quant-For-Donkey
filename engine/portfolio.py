"""
Portfolio Optimization - Markowitz Mean-Variance, Black-Litterman
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List, Tuple

class PortfolioOptimizer:
    """Tối ưu hóa danh mục đầu tư"""
    
    def __init__(self, risk_free_rate=0.02):
        self.risk_free_rate = risk_free_rate
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Tính lợi suất hàng ngày"""
        return prices.pct_change().dropna()
    
    def calculate_covariance_matrix(self, returns: pd.DataFrame) -> np.ndarray:
        """Tính ma trận hiệp phương sai"""
        return returns.cov().values
    
    def calculate_expected_returns(self, returns: pd.DataFrame) -> np.ndarray:
        """Tính lợi suất kỳ vọng"""
        return returns.mean().values * 252  # Annualized
    
    def portfolio_performance(self, weights: np.ndarray, 
                             mean_returns: np.ndarray, 
                             cov_matrix: np.ndarray) -> Tuple[float, float]:
        """
        Tính Sharpe Ratio và Volatility của danh mục
        """
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
        
        return sharpe_ratio, portfolio_std
    
    def negative_sharpe(self, weights: np.ndarray, 
                       mean_returns: np.ndarray, 
                       cov_matrix: np.ndarray) -> float:
        """Hàm mục tiêu: tối đa hóa Sharpe (tối thiểu hóa âm Sharpe)"""
        return -self.portfolio_performance(weights, mean_returns, cov_matrix)[0]
    
    def optimize_portfolio(self, returns: pd.DataFrame, 
                          method="max_sharpe") -> Dict:
        """
        Tối ưu hóa danh mục
        
        Args:
            returns: DataFrame lợi suất hàng ngày
            method: "max_sharpe", "min_variance", "equal_weight"
        """
        mean_returns = self.calculate_expected_returns(returns)
        cov_matrix = self.calculate_covariance_matrix(returns)
        num_assets = len(returns.columns)
        
        # Ràng buộc: tổng trọng số = 1
        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        
        # Giới hạn: mỗi trọng số từ 0 đến 1
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        # Trọng số ban đầu
        init_guess = np.array([1/num_assets] * num_assets)
        
        if method == "max_sharpe":
            result = minimize(
                self.negative_sharpe,
                init_guess,
                args=(mean_returns, cov_matrix),
                method="SLSQP",
                bounds=bounds,
                constraints=constraints
            )
        elif method == "min_variance":
            result = minimize(
                lambda w: np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))),
                init_guess,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints
            )
        else:  # equal_weight
            result = {"x": init_guess}
        
        optimal_weights = result["x"]
        sharpe, volatility = self.portfolio_performance(optimal_weights, mean_returns, cov_matrix)
        portfolio_return = np.sum(mean_returns * optimal_weights)
        
        return {
            "weights": dict(zip(returns.columns, optimal_weights)),
            "expected_return": portfolio_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe,
            "method": method
        }
    
    def black_litterman(self, market_cap_weights: Dict[str, float],
                       views: Dict[str, float],
                       confidence: float = 0.5) -> Dict:
        """
        Black-Litterman Model: Kết hợp thị trường với quan điểm cá nhân
        
        Args:
            market_cap_weights: Trọng số theo vốn hóa thị trường
            views: Quan điểm về lợi suất kỳ vọng (ví dụ: {"SOL": 0.15})
            confidence: Độ tin cậy vào quan điểm (0-1)
        """
        # Trọng số thị trường
        market_weights = np.array(list(market_cap_weights.values()))
        
        # Điều chỉnh theo quan điểm
        adjusted_weights = market_weights.copy()
        
        for asset, view_return in views.items():
            idx = list(market_cap_weights.keys()).index(asset)
            # Tăng trọng số nếu quan điểm tích cực
            adjustment = view_return * confidence
            adjusted_weights[idx] *= (1 + adjustment)
        
        # Chuẩn hóa
        adjusted_weights = adjusted_weights / adjusted_weights.sum()
        
        return {
            "weights": dict(zip(market_cap_weights.keys(), adjusted_weights)),
            "method": "black_litterman",
            "confidence": confidence
        }
    
    def rebalance_portfolio(self, current_weights: Dict[str, float],
                           target_weights: Dict[str, float],
                           current_prices: Dict[str, float],
                           total_capital: float) -> Dict:
        """
        Tính toán các lệnh rebalance cần thiết
        """
        rebalance_orders = {}
        
        for asset in current_weights.keys():
            current_pct = current_weights[asset]
            target_pct = target_weights.get(asset, 0)
            
            current_value = total_capital * current_pct
            target_value = total_capital * target_pct
            
            diff = target_value - current_value
            
            if abs(diff) > total_capital * 0.01:  # Chỉ rebalance nếu chênh lệch > 1%
                price = current_prices.get(asset, 1)
                amount = diff / price
                
                rebalance_orders[asset] = {
                    "action": "BUY" if amount > 0 else "SELL",
                    "amount": abs(amount),
                    "value": abs(diff),
                    "current_pct": current_pct,
                    "target_pct": target_pct
                }
        
        return rebalance_orders
