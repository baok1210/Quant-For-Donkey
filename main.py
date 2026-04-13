"""
Main Entry Point - Solana Quant Fund AI v4.0.0 (Professional Edition)
Tích hợp: Advanced DCA, Real-time Data, Risk Management, Strategies Ensemble
"""

import json
from datetime import datetime
import os
import sys

from engine.reflection import ReflectionEngine
from engine.agents import MultiAgentSystem
from engine.risk import RiskEngine
from engine.signals import SignalEngine
from engine.monthly_planner import MonthlyPlanner
from engine.ai_brain import AIBrain
from engine.data_aggregator import CryptoDataAggregator
from engine.advanced_dca import AdvancedDCA
from engine.session_risk import SessionRiskManager
from engine.market_data_manager import MarketDataManager
from engine.strategies.multi_strategy import MultiStrategyEnsemble
from engine.offline_learner import OfflineLearner
from engine.deliberation import DeliberationLayer
from engine.backtest_walkforward import WalkForwardBacktester
from engine.order_flow import OrderFlowAnalyzer
from engine.forecaster import PriceForecaster

class SolanaQuantFund:
    """Hệ thống quản lý quỹ đầu tư Solana - Phiên bản Chuyên nghiệp"""
    
    def __init__(self, initial_capital: float = 10000, ai_provider=None, ai_model=None):
        # ... (rest of code)
        self.order_flow = OrderFlowAnalyzer()
        # Ưu tiên load từ file cấu hình của người dùng lưu từ GUI
        user_config = {}
        if os.path.exists("config_settings.json"):
            with open("config_settings.json", "r") as f:
                user_config = json.load(f)
        
        # Merge các tham số
        provider = ai_provider or user_config.get("AI_PROVIDER", "openai")
        model = ai_model or user_config.get("AI_MODEL", "gpt-4-turbo")
        self.capital = initial_capital or user_config.get("INITIAL_CAPITAL", 10000)
        
        # Load API keys vào environment nếu có từ config
        if user_config.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = user_config["OPENAI_API_KEY"]
        if user_config.get("GEMINI_API_KEY"):
            os.environ["GEMINI_API_KEY"] = user_config["GEMINI_API_KEY"]

        # Core Engines
        self.reflection = ReflectionEngine()
        self.offline_learner = OfflineLearner()
        self.ai_brain = AIBrain(provider=provider, model=model)
        
        # Professional Modules (v4.0.0)
        self.data_aggregator = CryptoDataAggregator()
        self.advanced_dca = AdvancedDCA()
        self.session_risk = SessionRiskManager()
        self.strategy_ensemble = MultiStrategyEnsemble()
        self.forecaster = PriceForecaster()  # Auto-retraining XGBoost
        
        # Legacy/Support Modules
        self.agents = MultiAgentSystem()
        self.risk = RiskEngine(self.capital)
        self.signals = SignalEngine()
        self.monthly_planner = MonthlyPlanner()
        
        self.dca_history = []
        self.performance_log = []
        
        # Tự động tối ưu trọng số lúc khởi động
        self.offline_learner.analyze_diary()
        
    def run_daily_analysis(self, df_history=None) -> dict:
        """
        Chạy phân tích hàng ngày dựa trên dữ liệu thời gian thực
        
        Args:
            df_history: DataFrame chứa lịch sử OHLCV để test strategies
        """
        print("\n" + "="*60)
        print(f"🔍 PHÂN TÍCH CHUYÊN NGHIỆP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. Thu thập dữ liệu "Edge"
        print("\n📊 Bước 1: Thu thập Professional Data Edge")
        funding = self.data_aggregator.get_funding_rate("SOLUSDT")
        oi = self.data_aggregator.get_open_interest("SOLUSDT")
        liquidations = self.data_aggregator.get_liquidations("SOL")
        order_flow = self.data_aggregator.get_order_flow_analysis("SOLUSDT", df_history['close'].tolist() if df_history is not None else None)
        
        print(f"   Funding Rate: {funding['funding_rate_pct']:.4f}% ({funding['sentiment']})")
        print(f"   Long/Short Ratio: {oi['long_short_ratio']:.2f}")
        print(f"   Liquidations (24h): ${liquidations['liquidations_24h']:,.0f}")
        
        # Hiển thị thông tin Order Flow
        if order_flow.get("smart_money_indicators"):
            sm = order_flow["smart_money_indicators"]
            print(f"   Order Flow Signals:")
            print(f"      Buy Pressure: {'✅ HIGH' if sm['high_buy_pressure'] else '-low'}")
            print(f"      Sell Pressure: {'✅ HIGH' if sm['high_sell_pressure'] else 'low'}")
            print(f"      Absorption Zones: {'✅ YES' if sm['buy_absorption_zones'] else 'no'}")
            print(f"      Divergence: {sm['divergence_signal']}")
        
        # 2. Phân tích Chiến lược (Ensemble)
        print("\n🧠 Bước 2: Phân tích Chiến lược (Multi-Strategy Ensemble)")
        if df_history is not None and not df_history.empty:
            ensemble_result = self.strategy_ensemble.generate_ensemble_signal(df_history)
            strategy_signal = ensemble_result['final_signal']
            print(f"   Ensemble Signal: {strategy_signal} (Confidence: {ensemble_result['confidence']:.2f})")
            print(f"   Votes: {ensemble_result['votes']}")
        else:
            strategy_signal = "HOLD"
            print("   Không có dữ liệu lịch sử cho chiến lược (HOLD)")
        
        # 3. Dự báo giá (XGBoost Auto-Retraining)
        print("\n预测 Bước 3: Price Forecasting (Auto-Retraining)")
        forecast_result = self.forecaster.train_and_predict(df_history) if df_history is not None else {"status": "NO_DATA"}
        
        if forecast_result.get("status") == "OK":
            predicted_price = forecast_result["predicted_price"]
            expected_change = forecast_result["expected_change_pct"]
            model_version = forecast_result["model_version"]
            needs_retrain = forecast_result["needs_retrain"]
            
            print(f"   Dự báo: ${predicted_price:.2f} (Thay đổi: {expected_change:.2f}%)")
            print(f"   Model: v{model_version} | Retrain: {'✅' if needs_retrain else '✅Up-to-date'}")
        else:
            predicted_price = current_price
            expected_change = 0
            print("   Không thể dự báo (dữ liệu không đủ)")
        
        # 4. Phân tích Timing DCA chuyên nghiệp
        print("\n⏱️  Bước 4: Advanced DCA Timing")
        current_price = df_history['close'].iloc[-1] if df_history is not None else 150.0
        dca_timing = self.advanced_dca.calculate_optimal_dca_time(
            current_price=current_price,
            btc_price=65000,  # Mock BTC price
            sol_price=current_price
        )
        
        should_dca = dca_timing['should_dca']
        recommended_amount = dca_timing['recommended_amount']
        
        print(f"   Quyết định DCA: {'✅ YES' if should_dca else '⏳ DELAY'}")
        print(f"   Timing Score: {dca_timing['timing_score']:.2f}")
        for reason in dca_timing['reasons']:
            print(f"      ✓ {reason}")
            
        # 4. Quản lý Rủi ro Phiên giao dịch (Session Risk)
        print("\n🛡️  Bước 4: Session Risk Management")
        risk_check = self.session_risk.check_risk(self.capital)
        
        if risk_check["action"] == "BLOCK":
            print(f"   🛑 Giao dịch bị khóa: {risk_check['reason']}")
            should_dca = False
            recommended_amount = 0
        else:
            print("   ✅ Vượt qua kiểm tra rủi ro")
            
        # Tính toán Position Size an toàn (Kelly)
        if should_dca:
            kelly_size = self.risk.calculate_kelly_size(win_rate=0.45, avg_win=0.15, avg_loss=0.08)
            max_allowed = self.capital * kelly_size
            final_amount = min(recommended_amount, max_allowed)
            print(f"   Khối lượng an toàn (Half-Kelly): ${final_amount:.2f}")
        else:
            final_amount = 0
            
        # 5. Phân tích từ AI Brain (Online Learning)
        print("\n🤖 Bước 5: Tham vấn AI Brain")
        
        diary_content = ""
        if os.path.exists("memory/INVESTMENT_DIARY.md"):
            with open("memory/INVESTMENT_DIARY.md", "r", encoding="utf-8") as f:
                diary_content = f.read()
        
        ai_analysis = self.ai_brain.analyze_market({
            "price": current_price,
            "funding_rate": funding['funding_rate_pct'],
            "long_short_ratio": oi['long_short_ratio'],
            "strategy_signal": strategy_signal,
            "dca_timing_score": dca_timing['timing_score'],
            "order_flow": order_flow.get("smart_money_indicators", {}),
            "absorption_zones": len(order_flow.get("absorption_zones", [])),
            "delta_divergence": order_flow.get("delta_divergence", {}).get("divergence", "NEUTRAL"),
            "forecast_price": predicted_price,
            "forecast_change_pct": expected_change,
            "forecast_model_version": model_version,
            "forecast_needs_retrain": needs_retrain
        }, diary_content)
        
        print(f"   Khuyến nghị AI: {ai_analysis.get('recommendation', 'N/A')}")
        print(f"   Lý do: {ai_analysis.get('reasoning', 'N/A')}")
        
        # 6. Ghi nhận nhật ký
        if final_amount > 0:
            print("\n📝 Bước 6: Ghi nhận quyết định")
            self.reflection.log_decision(
                decision=f"DCA {strategy_signal}",
                reason=f"AI: {ai_analysis.get('recommendation')} | Timing: {dca_timing['timing_score']:.2f}",
                amount=f"${final_amount:.2f}",
                risk_assessment=f"Passed Session Risk, Kelly Size: {kelly_size:.2%}",
                data_sources="Funding Rate, L/S Ratio, XGBoost, 6 Strategies, Order Flow Analysis"
            )
            print("   ✓ Quyết định đã được lưu")
            
            # Update session risk
            self.session_risk.record_trade_result(0)  # Ghi nhận trade mới
            
        return {
            "timestamp": datetime.now().isoformat(),
            "funding_data": funding,
            "oi_data": oi,
            "strategy_signal": strategy_signal,
            "dca_timing": dca_timing,
            "final_amount": final_amount,
            "ai_analysis": ai_analysis
        }

# Test
if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    
    # Tạo mock data để test
    print("Khởi tạo hệ thống Quant Fund...")
    fund = SolanaQuantFund(initial_capital=10000)
    
    # Generate 100 days of mock data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    prices = 150 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 100)))
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': prices * 1.02,
        'low': prices * 0.98,
        'close': prices,
        'volume': np.random.randint(1000, 10000, 100)
    }).set_index('date')
    
    # Chạy phân tích
    result = fund.run_daily_analysis(df)
