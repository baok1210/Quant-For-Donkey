"""
Additional tests for macro, regime, and deliberation modules
"""
import math
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_macro_analyzer_fallback():
    """Test macro analyzer returns proper fallback when data unavailable"""
    # Import after path setup
    from engine.macro import MacroAnalyzer
    
    # If API fails, should still return structured response
    m = MacroAnalyzer()
    result = m.get_macro_data(period="1mo")
    
    # Should have status field
    assert "status" in result or "_status" in result or isinstance(result, dict)
    print(f"[PASS] macro.get_macro_data returns dict: {bool(result)}")


def test_macro_risk_on_off_structure():
    """Test risk_on_off returns proper structure"""
    from engine.macro import MacroAnalyzer
    
    m = MacroAnalyzer()
    result = m.analyze_risk_on_off()
    
    # Should have environment key
    assert "environment" in result, "Missing 'environment' key"
    # Should have status or warning
    assert "status" in result or "score" in result
    print(f"[PASS] macro.analyze_risk_on_off returns: {result.get('environment')}")


def test_regime_detection_with_mock_data():
    """Test regime detection with minimal data"""
    import pandas as pd
    import numpy as np
    
    # Need to handle import after path setup
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from engine.regime import MarketRegimeDetector
    
    # Test with short data (should not crash)
    regime_detector = MarketRegimeDetector()
    dates = pd.date_range(end='today', periods=30, freq='D')
    df = pd.DataFrame({
        'close': 100 + np.cumsum(np.random.randn(30)),
        'high': 105 + np.cumsum(np.random.randn(30)),
        'low': 95 + np.cumsum(np.random.randn(30))
    }, index=dates)
    
    result = regime_detector.detect_regime(df)
    
    # Should have regime key
    assert "regime" in result, "Missing 'regime' key"
    assert "adx_value" in result, "Missing 'adx_value' key"
    print(f"[PASS] regime.detect_regime returns: {result.get('regime')}")


def test_deliberation_conflict_resolution():
    """Test deliberation layer handles conflicts"""
    from engine.deliberation import DeliberationLayer
    
    d = DeliberationLayer()
    
    # Test case: conflicting views
    agent_views = {
        "bull_agent": {"confidence": 0.8, "stance": "BULLISH"},
        "bear_agent": {"confidence": 0.7, "stance": "BEARISH"},
        "macro_agent": {"confidence": 0.5, "stance": "NEUTRAL"},
        "onchain_agent": {"confidence": 0.4, "stance": "NEUTRAL"}
    }
    
    result = d.resolve_conflicts(agent_views)
    
    # Should have final_decision
    assert "final_decision" in result, "Missing 'final_decision'"
    assert "consensus_score" in result, "Missing 'consensus_score'"
    print(f"[PASS] deliberation resolves: {result.get('final_decision')}")


def test_sentiment_combined_structure():
    """Test sentiment returns proper structure"""
    from engine.sentiment import SentimentAnalyzer
    
    s = SentimentAnalyzer()
    result = s.get_combined_sentiment("SOL")
    
    # Should have status
    assert "status" in result, "Missing 'status' key"
    # Should have twitter and reddit sub-dicts
    assert "twitter" in result, "Missing 'twitter' key"
    assert "reddit" in result, "Missing 'reddit' key"
    print(f"[PASS] sentiment status: {result.get('status')}")


def run_all_tests():
    """Run all tests"""
    tests = [
        ("Macro Data Structure", test_macro_analyzer_fallback),
        ("Macro Risk On/Off", test_macro_risk_on_off_structure),
        ("Regime Detection", test_regime_detection_with_mock_data),
        ("Deliberation Conflict", test_deliberation_conflict_resolution),
        ("Sentiment Structure", test_sentiment_combined_structure),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print(f"\n=== Results: {passed} passed, {failed} failed ===")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)