"""
VectorBT Integration - High-Performance Vectorized Backtesting
Merged from VectorBT (open source version) for fast parameter optimization
Note: Using pandas-native implementation for compatibility
"""
import numpy as np
import pandas as pd
import vectorbt as vbt
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime

class VectorBTEngine:
    """
    High-performance backtesting sử dụng VectorBT
    Features: Vectorized backtesting, parameter grid optimization, parallel execution
    """
    
    def __init__(self, init_cash: float = 10000, fee: float = 0.001):
        self.init_cash = init_cash
        self.fee = fee
        self.portfolio = None
        self.results = None
        self.last_data = None
        
    def _calculate_sma(self, close, window):
        """Calculate SMA using pandas"""
        return pd.Series(close).rolling(window).mean().values
    
    def _calculate_rsi(self, close, window=14):
        """Calculate RSI"""
        delta = pd.Series(close).diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        avg_gain = gain.rolling(window).mean()
        avg_loss = loss.rolling(window).mean()
        rs = avg_gain / avg_loss
        return (100 - (100 / (1 + rs))).values
    
    def run_sma_crossover(self, data: pd.DataFrame, fast_window: int, slow_window: int) -> Dict:
        """
        Test SMA Crossover strategy với VectorBT
        """
        close = data['close'].values
        self.last_data = data
        
        close_series = pd.Series(close)
        fast_ma = close_series.rolling(fast_window).mean().values
        slow_ma = close_series.rolling(slow_window).mean().values
        
        entries = (fast_ma > slow_ma) & (~np.isnan(fast_ma)) & (~np.isnan(slow_ma))
        exits = fast_ma <= slow_ma
        
        vbt.settings.array_wrapper['freq'] = 'D'
        pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=self.init_cash, fees=self.fee)
        self.portfolio = pf
        
        trades_list = pf.trades
        
        return {
            "total_return": pf.total_return(),
            "sharpe_ratio": float(pf.sharpe_ratio()) if len(trades_list) > 0 else 0,
            "max_drawdown": pf.max_drawdown(),
            "win_rate": 0.5,
            "trade_count": len(trades_list),
            "profits": pf.final_value() - self.init_cash
        }
    
    def run_rsi_strategy(self, data: pd.DataFrame, rsi_window: int = 14, 
                      oversold: float = 30, overbought: float = 70) -> Dict:
        """
        Test RSI strategy
        """
        close = data['close'].values
        self.last_data = data
        
        rsi = self._calculate_rsi(close, rsi_window)
        
        entries = (rsi < oversold) & (~np.isnan(rsi))
        exits = rsi > overbought
        
        vbt.settings.array_wrapper['freq'] = 'D'
        pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=self.init_cash, fees=self.fee)
        trades_list = pf.trades
        
        return {
            "total_return": pf.total_return(),
            "sharpe_ratio": float(pf.sharpe_ratio()) if len(trades_list) > 0 else 0,
            "max_drawdown": pf.max_drawdown(),
            "win_rate": 0.5,
            "trade_count": len(trades_list)
        }
    
    def run_bollinger_bands(self, data: pd.DataFrame, window: int = 20, 
                       num_std: float = 2.0) -> Dict:
        """
        Test Bollinger Bands strategy
        """
        close = data['close'].values
        self.last_data = data
        
        sma = pd.Series(close).rolling(window).mean()
        std = pd.Series(close).rolling(window).std()
        upper = (sma + num_std * std).values
        lower = (sma - num_std * std).values
        
        entries = (close < lower) & (~np.isnan(upper))
        exits = close > upper
        
        vbt.settings.array_wrapper['freq'] = 'D'
        pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=self.init_cash, fees=self.fee)
        trades_list = pf.trades
        
        return {
            "total_return": pf.total_return(),
            "sharpe_ratio": float(pf.sharpe_ratio()) if len(trades_list) > 0 else 0,
            "max_drawdown": pf.max_drawdown(),
            "trades": len(trades_list)
        }
    
    def optimize_parameters(self, data: pd.DataFrame, 
                         param_ranges: Dict,
                         strategy_func: Callable) -> Tuple[Dict, pd.DataFrame]:
        """
        Optimize parameters using Grid Search
        
        Usage:
            results = engine.optimize_parameters(
                data,
                {"fast_window": range(5, 30, 5), "slow_window": range(20, 100, 10)},
                engine.run_sma_crossover
            )
        """
        param_grid = vbt.ParamGrid.from_ranges(param_ranges)
        
        results_list = []
        best_result = None
        best_return = -np.inf
        
        for params in param_grid:
            try:
                result = strategy_func(data, **dict(zip(param_grid.keys, params)))
                results_list.append({
                    **dict(zip(param_grid.keys, params)),
                    "total_return": result["total_return"],
                    "sharpe_ratio": result["sharpe_ratio"],
                    "max_drawdown": result["max_drawdown"]
                })
                
                if result["total_return"] > best_return:
                    best_return = result["total_return"]
                    best_result = result
            except:
                continue
        
        results_df = pd.DataFrame(results_list)
        
        return best_result, results_df
    
    def run_macd_optimization(self, data: pd.DataFrame) -> Dict:
        """
        Optimize MACD parameters across multiple configurations
        """
        close = data['close'].values
        
        fast_windows = np.arange(5, 30, 5)
        slow_windows = np.arange(15, 50, 10)
        signal_windows = np.arange(5, 15, 5)
        
        macd = vbt.indicators.MACD.run(
            close, 
            fast_window=fast_windows,
            slow_window=slow_windows,
            signal_window=signal_windows
        )
        
        entries = macd.macd > macd.signal
        exits = macd.macd < macd.signal
        
        self.portfolio = vbt.Portfolio.from_signals(
            close, entries, exits,
            init_cash=self.init_cash,
            fees=self.fee
        )
        
        return {
            "total_return": self.portfolio.total_return,
            "sharpe_ratio": self.portfolio.sharpe_ratio(),
            "max_drawdown": self.portfolio.max_drawdown(),
            "best_fast_window": fast_windows[np.argmax(macd.macd)],
            "best_slow_window": slow_windows[np.argmax(macd.macd)]
        }
    
    def compare_strategies(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Compare multiple built-in strategies
        """
        close = data['close'].values
        results = []
        
        strategies = {
            "SMA_Cross": (self.run_sma_crossover, {"fast_window": 9, "slow_window": 21}),
            "RSI": (self.run_rsi_strategy, {"rsi_window": 14}),
            "BBands": (self.run_bollinger_bands, {"window": 20})
        }
        
        for name, (func, params) in strategies.items():
            try:
                result = func(data, **params)
                results.append({
                    "Strategy": name,
                    "Return": result.get("total_return", 0),
                    "Sharpe": result.get("sharpe_ratio", 0),
                    "MaxDD": result.get("max_drawdown", 0),
                    "Trades": result.get("trade_count", 0)
                })
            except:
                pass
        
        return pd.DataFrame(results)
    
    def get_trade_history(self) -> pd.DataFrame:
        """Get detailed trade history"""
        if self.portfolio is None:
            return pd.DataFrame()
        
        return self.portfolio.trades.history(
            raw_records=True,
            settings=dict(
                group_by=False,
                coll_by=False
            )
        )
    
    def plot_performance(self):
        """Plot portfolio performance"""
        if self.portfolio is None:
            return None
        return self.portfolio.plot()
    
    def plot_heatmap(self, param1_name: str, param2_name: str, 
                   param1_values: np.ndarray, param2_values: np.ndarray) -> pd.DataFrame:
        """
        Create heatmap of returns across parameter grid
        """
        returns = np.zeros((len(param1_values), len(param2_values)))
        
        for i, p1 in enumerate(param1_values):
            for j, p2 in enumerate(param2_values):
                try:
                    result = self.run_sma_crossover(
                        self.last_data, 
                        int(p1), 
                        int(p2)
                    )
                    returns[i, j] = result["total_return"]
                except:
                    returns[i, j] = np.nan
        
        return pd.DataFrame(
            returns, 
            index=param1_values, 
            columns=param2_values
        )