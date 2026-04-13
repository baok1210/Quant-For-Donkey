# Check learning base
import sys
sys.path.insert(0, '.')

from engine.backtest_engine import get_backtest_engine

bt = get_backtest_engine()
data = bt.get_learning_data()

print('=== LEARNING BASE ===')
print('Total decisions:', len(data.get('decisions', [])))
print()

for d in data.get('decisions', [])[:5]:
    print(f"Outcome: {d.get('outcome')}")
    print(f"  RSI entry: {d.get('entry_rsi')}")
    print(f"  PnL %: {d.get('pnl_pct')}")
    print()
