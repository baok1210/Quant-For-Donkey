"""
Freqtrade Integration - Strategy Framework & Hyperopt
Merged from Freqtrade for advanced strategy optimization
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os

class FreqtradeStrategy:
    """
    Strategy framework-inspired by Freqtrade
    Features: Entry/Exit signals, ROI, Stoploss, Timeframe handling
    """
    
    def __init__(self, 
                 minimal_roi: Dict[float, float] = {0: 0.10},
                 stoploss: float = -0.10,
                 timeframe: str = "5m"):
        self.minimal_roi = minimal_roi
        self.stoploss = stoploss
        self.timeframe = timeframe
        self.populated_trades = False
        
    def populate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add indicators (override in subclass)"""
        df = data.copy()
        
        close = df['close']
        
        df['sma_9'] = close.rolling(9).mean()
        df['sma_21'] = close.rolling(21).mean()
        df['sma_50'] = close.rolling(50).mean()
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['hist'] = df['macd'] - df['signal']
        
        df['bb_middle'] = close.rolling(20).mean()
        std = close.rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + 2 * std
        df['bb_lower'] = df['bb_middle'] - 2 * std
        
        return df
    
    def populate_buy_trend(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate buy signals (override in subclass)
        Default: SMA crossover
        """
        buy = (df['sma_9'] > df['sma_21']) & (df['rsi'] < 50)
        return buy
    
    def populate_sell_trend(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate sell signals (override in subclass)
        Default: SMA crossover reverse
        """
        sell = (df['sma_9'] < df['sma_21']) | (df['rsi'] > 70)
        return sell
    
    def run(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run strategy on data
        """
        df = self.populate_indicators(data)
        buy_signals = self.populate_buy_trend(df)
        sell_signals = self.populate_sell_trend(df)
        
        return {
            "dataframe": df,
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "minimal_roi": self.minimal_roi,
            "stoploss": self.stoploss
        }


class FreqtradeHyperopt:
    """
    Hyperopt - Strategy Parameter Optimization
    Inspired by Freqtrade's hyperopt
    Uses random search for optimization
    """
    
    def __init__(self, 
                 strategy: FreqtradeStrategy,
                 max_epochs: int = 100,
                 random_state: int = 42):
        self.strategy = strategy
        self.max_epochs = max_epochs
        self.random_state = random_state
        self.best_loss = np.inf
        self.best_params = None
        self.results = []
        
    def optimize(self, data: pd.DataFrame, 
              param_ranges: Dict[str, tuple],
              target_metric: str = "sharpe") -> Dict:
        """
        Optimize strategy parameters using Random Search
        
        Args:
            param_ranges: Dict of parameter ranges
                e.g., {"sma_fast": (5, 20), "sma_slow": (20, 50)}
        """
        np.random.seed(self.random_state)
        
        for epoch in range(self.max_epochs):
            params = {
                name: np.random.randint(low, high)
                for name, (low, high) in param_ranges.items()
            }
            
            strategy = FreqtradeStrategy(
                minimal_roi=self.strategy.minimal_roi,
                stoploss=self.strategy.stoploss
            )
            
            try:
                result = self._evaluate_strategy(data, strategy, params)
                
                self.results.append({
                    **params,
                    "total_return": result["total_return"],
                    "sharpe": result["sharpe_ratio"],
                    "max_dd": result["max_drawdown"]
                })
                
                if result.get("loss", np.inf) < self.best_loss:
                    self.best_loss = result["loss"]
                    self.best_params = params
                    
            except:
                continue
        
        return {
            "best_params": self.best_params,
            "best_loss": self.best_loss,
            "all_results": pd.DataFrame(self.results)
        }
    
    def _evaluate_strategy(self, data: pd.DataFrame, 
                       strategy: FreqtradeStrategy,
                       params: Dict) -> Dict:
        """
        Evaluate strategy with parameters
        """
        df = strategy.populate_indicators(data)
        
        close = df['close'].values
        buy_signals = strategy.populate_buy_trend(df).values
        sell_signals = strategy.populate_sell_trend(df).values
        
        position = 0
        entry_price = 0
        trades = []
        equity = 10000
        
        for i in range(1, len(close)):
            if buy_signals[i] and position == 0:
                position = 1
                entry_price = close[i]
            elif sell_signals[i] and position == 1:
                pnl = (close[i] - entry_price) / entry_price
                if pnl < strategy.stoploss:
                    pnl = strategy.stoploss
                equity *= (1 + pnl)
                trades.append({"pnl": pnl, "entry": entry_price, "exit": close[i]})
                position = 0
        
        total_return = (equity - 10000) / 10000
        
        returns = [t['pnl'] for t in trades]
        if len(returns) > 1:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(365)
        else:
            sharpe = 0
        
        max_dd = min(returns) if returns else 0
        
        loss = -sharpe if len(returns) > 0 else 0
        
        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "loss": loss,
            "num_trades": len(trades)
        }
    
    def get_best_params(self) -> Dict:
        """Get best parameters found"""
        return self.best_params
    
    def save_results(self, path: str):
        """Save optimization results"""
        df_results = pd.DataFrame(self.results)
        df_results.to_csv(path, index=False)


class FreqtradeEdge:
    """
    Edge - Risk-based position sizing
    Inspired by Freqtrade Edge
    """
    
    def __init__(self, init_balance: float = 10000):
        self.init_balance = init_balance
        self.edge = {}
        
    def calculate(self, data: pd.DataFrame, 
              pairs: List[str],
              method: str = " Sharpe") -> Dict[str, float]:
        """
        Calculate Edge for each pair based on historical performance
        """
        for pair in pairs:
            try:
                returns = data['close'].pct_change().dropna()
                
                if method == "sharpe":
                    edge_val = returns.mean() / returns.std() * np.sqrt(365) if returns.std() > 0 else 0
                elif method == "sortino":
                    downside = returns[returns < 0].std()
                    edge_val = returns.mean() / downside * np.sqrt(365) if downside > 0 else 0
                else:
                    edge_val = returns.mean() * 365
                
                self.edge[pair] = edge_val
                
            except:
                self.edge[pair] = 0
        
        return self.edge
    
    def get_position_size(self, pair: str, 
                        total_capital: float,
                        risk_level: float = 0.5) -> float:
        """
        Calculate position size based on Edge
        """
        edge = self.edge.get(pair, 0)
        
        if edge > 0:
            size = total_capital * risk_level
        else:
            size = total_capital * risk_level * 0.5
        
        return size
    
    def normalize_edge(self) -> Dict[str, float]:
        """Normalize edge values to sum to 1"""
        total = sum(self.edge.values())
        
        if total == 0:
            return {k: 1/len(self.edge) for k in self.edge}
        
        return {k: v/total for k, v in self.edge.items()}


class FreqtradeBacktest:
    """
    Backtesting engine with realistic fee simulation
    Inspired by Freqtrade backtesting
    """
    
    def __init__(self,
                 init_balance: float = 10000,
                 fee: float = 0.001,
                 maker_fee: float = 0.001,
                 taker_fee: float = 0.002):
        self.init_balance = init_balance
        self.fee = fee
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        
    def run(self, data: pd.DataFrame, 
          strategy: FreqtradeStrategy,
          max_open_trades: int = 3,
          stake_amount: float = None) -> Dict:
        """
        Run backtest with realistic fees
        """
        df = strategy.populate_indicators(data)
        buy_signals = strategy.populate_buy_trend(df)
        sell_signals = strategy.populate_sell_trend(df)
        
        balance = self.init_balance
        open_trades = []
        closed_trades = []
        
        for i in range(len(df)):
            current_price = df['close'].iloc[i]
            current_time = df.index[i]
            
            if buy_signals.iloc[i] and len(open_trades) < max_open_trades:
                if stake_amount is None:
                    stake_amount = balance / max_open_trades
                
                trade = {
                    "entry_time": current_time,
                    "entry_price": current_price,
                    "amount": stake_amount / current_price,
                    "stake": stake_amount
                }
                trade["fee"] = stake_amount * self.taker_fee
                open_trades.append(trade)
                balance -= stake_amount + trade["fee"]
            
            roi = strategy.minimal_roi.get(0, 0.10)
            for trade in open_trades[:]:
                pnl_pct = (current_price - trade["entry_price"]) / trade["entry_price"]
                
                if pnl_pct >= roi or pnl_pct <= strategy.stoploss:
                    exit_value = trade["amount"] * current_price
                    exit_fee = exit_value * self.maker_fee
                    
                    trade["exit_time"] = current_time
                    trade["exit_price"] = current_price
                    trade["pnl"] = exit_value - trade["stake"] - trade["fee"] - exit_fee
                    trade["pnl_pct"] = pnl_pct
                    
                    closed_trades.append(trade)
                    balance += exit_value - exit_fee
                    open_trades.remove(trade)
        
        for trade in open_trades:
            final_value = trade["amount"] * df['close'].iloc[-1]
            trade["exit_time"] = df.index[-1]
            trade["exit_price"] = df['close'].iloc[-1]
            trade["pnl"] = final_value - trade["stake"] - trade["fee"]
            trade["pnl_pct"] = trade["pnl"] / trade["stake"]
            closed_trades.append(trade)
            balance += final_value
        
        total_profit = balance - self.init_balance
        
        return {
            "total_profit": total_profit,
            "total_profit_pct": total_profit / self.init_balance,
            "total_trades": len(closed_trades),
            "avg_trade_duration": "N/A",
            "wins": sum(1 for t in closed_trades if t.get("pnl", 0) > 0),
            "losses": sum(1 for t in closed_trades if t.get("pnl", 0) <= 0),
            "win_rate": sum(1 for t in closed_trades if t.get("pnl", 0) > 0) / max(1, len(closed_trades)),
            "closed_trades": closed_trades,
            "final_balance": balance
        }