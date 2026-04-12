"""
TradingView Indicator Backtester - Chạy backtest cho các indicator mới
"""
import pandas as pd
import numpy as np
from typing import Dict, List

class TVBacktester:
    """Chạy backtest cho các indicator từ TradingView"""
    
    def __init__(self):
        self.backtest_results = {}
    
    def run_backtest(self, indicator_func, data: pd.DataFrame, params: Dict = None) -> Dict:
        """
        Chạy backtest cho một indicator function
        """
        if params is None:
            params = {}
        
        try:
            # Apply indicator to data
            df_with_indicator = indicator_func(data, **params)
            
            # Generate signals based on indicator values
            signals = self._generate_signals(df_with_indicator)
            
            # Calculate backtest metrics
            metrics = self._calculate_metrics(data, signals)
            
            result = {
                "success": True,
                "metrics": metrics,
                "signals": signals,
                "indicator_params": params,
                "backtest_date": pd.Timestamp.now().isoformat()
            }
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "backtest_date": pd.Timestamp.now().isoformat()
            }
    
    def _generate_signals(self, df_with_indicator: pd.DataFrame) -> List[Dict]:
        """
        Tự động sinh tín hiệu từ indicator
        """
        signals = []
        
        # Example: Look for common indicator columns
        for i in range(1, len(df_with_indicator)):
            row = df_with_indicator.iloc[i]
            prev_row = df_with_indicator.iloc[i-1]
            
            # Generic signal generation logic
            # This would be customized based on the specific indicator
            if 'rsi' in df_with_indicator.columns:
                if row['rsi'] < 30 and prev_row['rsi'] >= 30:  # Oversold to neutral
                    signals.append({
                        "date": row.name,
                        "signal": "BUY",
                        "strength": "STRONG"
                    })
                elif row['rsi'] > 70 and prev_row['rsi'] <= 70:  # Overbought to neutral
                    signals.append({
                        "date": row.name,
                        "signal": "SELL",
                        "strength": "STRONG"
                    })
            
            if 'macd' in df_with_indicator.columns and 'signal' in df_with_indicator.columns:
                if row['macd'] > row['signal'] and prev_row['macd'] <= prev_row['signal']:
                    signals.append({
                        "date": row.name,
                        "signal": "BUY",
                        "strength": "MODERATE"
                    })
                elif row['macd'] < row['signal'] and prev_row['macd'] >= prev_row['signal']:
                    signals.append({
                        "date": row.name,
                        "signal": "SELL",
                        "strength": "MODERATE"
                    })
        
        return signals
    
    def _calculate_metrics(self, data: pd.DataFrame, signals: List[Dict]) -> Dict:
        """
        Tính toán các chỉ số hiệu suất backtest
        """
        # Calculate returns from signals
        returns = []
        positions = []
        
        for signal in signals:
            # Find the corresponding price
            try:
                idx = data.index.get_loc(signal['date'])
                if idx + 1 < len(data):  # Can close position tomorrow
                    entry_price = data.iloc[idx]['close']
                    exit_price = data.iloc[idx + 1]['close']
                    
                    if signal['signal'] == 'BUY':
                        ret = (exit_price - entry_price) / entry_price
                    elif signal['signal'] == 'SELL':
                        ret = (entry_price - exit_price) / entry_price
                    else:
                        ret = 0
                    
                    returns.append(ret)
                    positions.append({
                        "entry_date": signal['date'],
                        "exit_date": data.index[idx + 1],
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "return": ret,
                        "signal": signal['signal']
                    })
            except KeyError:
                continue  # Date not found in data
        
        if not returns:
            return {
                "total_return": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0,
                "win_rate": 0,
                "total_trades": 0,
                "avg_return_per_trade": 0
            }
        
        returns_series = pd.Series(returns)
        
        # Calculate metrics
        total_return = (1 + returns_series).prod() - 1
        avg_return = returns_series.mean()
        vol = returns_series.std() * np.sqrt(252)  # Annualized volatility
        
        # Sharpe ratio (assuming risk-free rate = 0)
        sharpe_ratio = avg_return / vol if vol != 0 else 0
        
        # Max drawdown
        cumulative = (1 + returns_series).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        win_rate = (returns_series > 0).sum() / len(returns_series)
        
        return {
            "total_return": float(total_return),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "win_rate": float(win_rate),
            "total_trades": len(returns),
            "avg_return_per_trade": float(avg_return),
            "annualized_volatility": float(vol)
        }
