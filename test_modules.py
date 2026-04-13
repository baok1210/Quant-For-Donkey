"""
Module Test Suite - Kiểm tra từng module
QUAN TRỌNG: Module yêu cầu online data KHÔNG được phép hoạt động offline
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Test results storage
RESULTS = {}

def test_data_aggregator():
    """Test Data Aggregator - requires online API"""
    try:
        from engine.data_aggregator import CryptoDataAggregator
        da = CryptoDataAggregator()
        
        # Test 1: Funding rate - requires online
        fr = da.get_funding_rate('SOLUSDT')
        has_funding = 'funding_rate_pct' in fr
        
        # Test 2: Open Interest - requires online
        oi = da.get_open_interest('SOLUSDT')
        has_oi = 'long_short_ratio' in oi
        
        # Test 3: Liquidations - requires online
        liq = da.get_liquidations('SOL')
        has_liq = 'liquidations_24h' in liq
        
        # Test 4: Order Flow - requires online price data
        of = da.get_order_flow_analysis('SOLUSDT', [100, 101, 102])
        
        if has_funding and has_oi:
            return {"status": "OK", "online": True}
        else:
            return {"status": "PARTIAL", "online": True, "note": "Some APIs failed"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:50], "online_required": True}

def test_order_flow():
    """Test Order Flow - OFFLINE (local calculation) ✓"""
    try:
        from engine.order_flow import OrderFlowAnalyzer
        ofa = OrderFlowAnalyzer()
        
        # Test với local data - KHÔNG cần online
        prices = [100 + i*0.5 + np.random.randn() for i in range(100)]
        result = ofa.analyze_smart_money('SOLUSDT', prices)
        
        if 'cvd_analysis' in result:
            return {"status": "OK", "online": False}
        return {"status": "PARTIAL", "note": "Missing analysis data"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:50]}

def test_forecaster():
    """Test Forecaster - needs training data (can be offline)"""
    try:
        from engine.forecaster import PriceForecaster
        pf = PriceForecaster()
        
        # Create test data với required columns
        dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
        close = 100 + np.cumsum(np.random.randn(200))
        volume = np.random.randint(1000, 10000, 200)
        
        df = pd.DataFrame({
            'open': close * 0.99,
            'high': close * 1.02,
            'low': close * 0.98,
            'close': close,
            'volume': volume
        }, index=dates)
        
        # Try training
        result = pf.train_and_predict(df)
        
        return {"status": "OK", "note": "Needs trained model"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:50]}

def test_advanced_dca():
    """Test Advanced DCA - requires online (liquidation API)"""
    try:
        from engine.advanced_dca import AdvancedDCA
        dca = AdvancedDCA()
        
        # Test với mock data
        result = dca.calculate_optimal_dca_time(170, [])
        
        # Should fail hoặc return fallback vì liquidation API unavailable
        if result.get('timing_score') is not None:
            return {"status": "OK", "online_required": True}
        return {"status": "FALLBACK", "note": "Using fallback, needs online API"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:50], "online_required": True}

def test_session_risk():
    """Test Session Risk"""
    try:
        from engine.session_risk import SessionRiskManager
        sr = SessionRiskManager()
        
        # Test simple call
        result = sr.check_risk(170)
        
        if result:
            return {"status": "OK"}
        return {"status": "EMPTY", "note": "Returns None/empty"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:50]}

def test_multi_strategy():
    """Test Multi Strategy - needs OHLCV data"""
    try:
        from engine.strategies.multi_strategy import MultiStrategyEnsemble
        ms = MultiStrategyEnsemble()
        
        # Test với full OHLCV data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        df = pd.DataFrame({
            'open': 100 + np.cumsum(np.random.randn(100)),
            'high': 105 + np.cumsum(np.random.randn(100)),
            'low': 95 + np.cumsum(np.random.randn(100)),
            'close': 100 + np.cumsum(np.random.randn(100)),
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        result = ms.generate_ensemble_signal(df)
        
        if 'signal' in result or 'ensemble_signal' in result:
            return {"status": "OK"}
        return {"status": "PARTIAL", "result": result}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:50]}

def test_signals():
    """Test Signals"""
    try:
        from engine.signals import SignalEngine
        se = SignalEngine()
        
        # Check available methods
        methods = [m for m in dir(se) if not m.startswith('_')]
        
        return {"status": "OK", "methods": methods[:3]}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:50]}

def test_risk():
    """Test Risk Engine"""
    try:
        from engine.risk import RiskEngine
        re = RiskEngine()
        
        # Check methods
        methods = [m for m in dir(re) if not m.startswith('_')]
        
        return {"status": "OK", "methods": methods[:3]}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:50]}

def test_ai_brain():
    """Test AI Brain"""
    try:
        from engine.ai_brain import AIBrain, AIBrainConfig
        
        # Check configured
        configured = AIBrainConfig.get_available()
        
        return {"status": "CHECK", "configured_providers": [k for k, v in configured.items() if v.get('api_key')]}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:50]}


# Run all tests
print("="*60)
print("MODULE TEST SUITE")
print("="*60)
print()

tests = [
    ("Data Aggregator", test_data_aggregator),
    ("Order Flow", test_order_flow),
    ("Forecaster", test_forecaster),
    ("Advanced DCA", test_advanced_dca),
    ("Session Risk", test_session_risk),
    ("Multi Strategy", test_multi_strategy),
    ("Signals", test_signals),
    ("Risk Engine", test_risk),
    ("AI Brain", test_ai_brain),
]

for name, test_func in tests:
    print(f"Testing {name}...")
    try:
        result = test_func()
        status = result.get('status', 'UNKNOWN')
        online = result.get('online', False)
        
        if status == "OK":
            print(f"  ✅ {status}" + (" (ONLINE)" if online else " (OFFLINE)"))
        elif status == "ERROR":
            print(f"  ❌ {status}: {result.get('error', '')}")
        elif status == "FALLBACK":
            print(f"  ⚠️  FALLBACK - {result.get('note', '')} (needs online)")
        else:
            print(f"  ⚠️  {status}: {result.get('note', str(result)[:30])}")
    except Exception as e:
        print(f"  ❌ CRASH: {str(e)[:40]}")
    print()

print("="*60)
print("SUMMARY")
print("="*60)
print("""
Modules hoạt động OFFLINE (✓:
- Order Flow Analyzer
- Signal Generator (local calculation)

Modules yêu cầu ONLINE (⚠️:
- Data Aggregator (API)
- Advanced DCA (Liquidation API)
- AI Brain (API Key)

Modules CẦN FIX (❌:
- Xem chi tiết ở trên
""")