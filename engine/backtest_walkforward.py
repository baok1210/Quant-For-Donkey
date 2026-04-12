"""
Walk-Forward Backtesting Engine - Chống Overfitting
Rolling window: Train 6 tháng, Test 1 tháng, lặp lại
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Callable
from datetime import datetime
from engine.paper_trading import PaperTradingEngine

class WalkForwardBacktester:
    """
    Walk-Forward Optimization
    Giải quyết vấn đề overfitting bằng cách test trên dữ liệu "chưa từng thấy"
    """
    
    def __init__(self, train_window=180, test_window=30):
        self.train_window = train_window  # 6 tháng (dạng ngày)
        self.test_window = test_window    # 1 tháng (dạng ngày)
        self.results = []
    
    def run(self, df: pd.DataFrame, strategy_func: Callable,
            optimize_params: List[str] = None) -> Dict:
        """
        Chạy Walk-Forward test
        
        Args:
            df: DataFrame OHLCV
            strategy_func: Hàm sinh tín hiệu (price, params) -> signal
            optimize_params: Danh sách tham số cần tối ưu
        """
        if len(df) < self.train_window + self.test_window:
            return {"error": "Not enough data for walk-forward"}
        
        all_results = []
        step = self.test_window  # Cuộn theo test_window
        
        for i in range(self.train_window, len(df) - self.test_window + 1, step):
            train_df = df.iloc[i - self.train_window:i]
            test_df = df.iloc[i:i + self.test_window]
            
            # 1. Tối ưu tham số trên Train Set
            if optimize_params:
                best_params = self._optimize_params(train_df, strategy_func, optimize_params)
            else:
                best_params = {}
            
            # 2. Test trên Test Set (Out-of-Sample)
            test_result = self._test_on_sample(test_df, strategy_func, best_params)
            
            all_results.append({
                "train_start": df.index[i - self.train_window],
                "train_end": df.index[i - 1],
                "test_start": df.index[i],
                "test_end": df.index[i + self.test_window - 1],
                "best_params": best_params,
                "test_metrics": test_result
            })
        
        self.results = all_results
        return self._aggregate_results(all_results)
    
    def _optimize_params(self, train_df: pd.DataFrame, strategy_func: Callable,
                         params: List[str]) -> Dict:
        """Grid search đơn giản để tìm tham số tốt nhất trên train set"""
        # Mock: Trong thực tế sẽ dùng itertools.product
        # Đây là ví dụ với EMA periods
        best_sharpe = -999
        best_params = {}
        
        if "ema_fast" in params and "ema_slow" in params:
            for fast in [5, 9, 12, 20]:
                for slow in [21, 26, 50, 100]:
                    if fast >= slow:
                        continue
                    test_result = self._test_on_sample(
                        train_df, strategy_func, 
                        {"ema_fast": fast, "ema_slow": slow}
                    )
                    sharpe = test_result.get("sharpe_ratio", -999)
                    if sharpe > best_sharpe:
                        best_sharpe = sharpe
                        best_params = {"ema_fast": fast, "ema_slow": slow}
        
        return best_params if best_params else {"ema_fast": 9, "ema_slow": 21}
    
    def _test_on_sample(self, test_df: pd.DataFrame, strategy_func: Callable,
                        params: Dict) -> Dict:
        """Chạy test trên một khoảng dữ liệu"""
        paper = PaperTradingEngine(initial_balance=10000)
        
        for idx, row in test_df.iterrows():
            signal, _ = strategy_func(row, params)
            
            if signal == "BUY":
                paper.execute_with_slippage("BUY", row['close'], 500)
            elif signal == "SELL":
                paper.execute_with_slippage("SELL", row['close'], 500)
        
        summary = paper.get_portfolio_summary()
        
        # Tính metrics
        returns = [(t['fill_price'] - test_df.loc[test_df.index[test_df.index.get_loc(t.get('timestamp', ''))]['close'] if t['timestamp'] in test_df.index else 0)) 
                   for t in paper.trade_history]
        
        if returns:
            ret_series = pd.Series(returns)
            sharpe = ret_series.mean() / ret_series.std() if ret_series.std() > 0 else 0
            max_dd = abs(min(ret_series.cumsum().min(), 0))
            win_rate = len(ret_series[ret_series > 0]) / len(ret_series)
        else:
            sharpe = 0
            max_dd = 0
            win_rate = 0
        
        return {
            "final_balance": summary["total_value"],
            "total_return_pct": (summary["total_value"] - 10000) / 10000 * 100,
            "sharpe_ratio": sharpe,
            "max_drawdown_pct": max_dd,
            "win_rate": win_rate,
            "total_trades": len(paper.trade_history),
            "slippage_cost": summary.get("total_slippage_cost", 0),
            "spread_cost": summary.get("total_spread_cost", 0)
        }
    
    def _aggregate_results(self, all_results: List[Dict]) -> Dict:
        """Tổng hợp kết quả từ tất cả các test window"""
        if not all_results:
            return {"error": "No results"}
        
        sharpe_list = [r["test_metrics"]["sharpe_ratio"] for r in all_results]
        win_rate_list = [r["test_metrics"]["win_rate"] for r in all_results]
        return_list = [r["test_metrics"]["total_return_pct"] for r in all_results]
        trades_list = [r["test_metrics"]["total_trades"] for r in all_results]
        
        return {
            "avg_sharpe_ratio": np.mean(sharpe_list),
            "std_sharpe_ratio": np.std(sharpe_list),
            "avg_win_rate": np.mean(win_rate_list),
            "avg_return_pct": np.mean(return_list),
            "total_return_pct": sum(return_list),
            "total_trades": sum(trades_list),
            "num_test_windows": len(all_results),
            "consistency": len([s for s in sharpe_list if s > 0]) / len(sharpe_list),
            "per_window_results": all_results
        }
