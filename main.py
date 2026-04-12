"""
Main Entry Point - Solana Quant Fund AI
Tích hợp tất cả các components: Reflection Engine, Multi-Agent System, Risk Engine, Signal Engine
"""

import json
from datetime import datetime
from engine.reflection import ReflectionEngine
from engine.agents import MultiAgentSystem
from engine.risk import RiskEngine
from engine.signals import SignalEngine
from engine.monthly_planner import MonthlyPlanner

class SolanaQuantFund:
    """Hệ thống quản lý quỹ đầu tư Solana"""
    
    def __init__(self, initial_capital: float = 10000):
        self.reflection = ReflectionEngine()
        self.agents = MultiAgentSystem()
        self.risk = RiskEngine(initial_capital)
        self.signals = SignalEngine()
        self.monthly_planner = MonthlyPlanner()  # Thêm monthly planner
        
        self.capital = initial_capital
        self.dca_history = []
        self.performance_log = []
        
    def run_daily_analysis(self, market_data: dict) -> dict:
        """
        Chạy phân tích hàng ngày
        
        Args:
            market_data: Dữ liệu thị trường
        
        Returns:
            Quyết định DCA cho ngày hôm nay
        """
        print("\n" + "="*60)
        print(f"🔍 PHÂN TÍCH HÀNG NGÀY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Bước 1: Tạo tín hiệu
        print("\n📊 Bước 1: Tạo tín hiệu kỹ thuật & on-chain")
        signal = self.signals.generate_signal(market_data)
        print(f"   Signal: {signal['signal_type']} (Confidence: {signal['confidence']:.2%})")
        print(f"   RSI: {signal['rsi']:.2f} | MACD: {signal['macd_trend']}")
        
        # Bước 2: Phân tích đa tác vụ
        print("\n🤖 Bước 2: Phân tích từ Multi-Agent System")
        agent_analysis = self.agents.run_analysis(market_data)
        
        bull_view = agent_analysis["bull_view"]
        bear_view = agent_analysis["bear_view"]
        final_decision = agent_analysis["final_decision"]
        
        print(f"   🐂 Bull Agent: {bull_view['stance']} (Confidence: {bull_view['confidence']:.2%})")
        for signal_item in bull_view['signals'][:2]:
            print(f"      ✓ {signal_item}")
            
        print(f"   🐻 Bear Agent: {bear_view['stance']} (Risk: {bear_view['risk_score']:.2%})")
        for warning in bear_view['warnings'][:2]:
            print(f"      ⚠ {warning}")
            
        print(f"   ⚖️  Arbiter Decision: {final_decision['decision']} (Score: {final_decision['net_score']:.2f})")
        
        # Bước 3: Quản trị rủi ro
        print("\n⚠️  Bước 3: Quản trị rủi ro")
        
        # Lấy lịch sử lợi nhuận (mock data)
        returns = market_data.get("historical_returns", [-0.05, 0.03, 0.02, -0.02, 0.04])
        var = self.risk.calculate_var(returns)
        print(f"   Value at Risk (95%): {var:.2%}")
        
        # Tính Kelly Criterion
        win_rate = market_data.get("win_rate", 0.55)
        avg_win = market_data.get("avg_win", 0.15)
        avg_loss = market_data.get("avg_loss", 0.10)
        kelly = self.risk.kelly_criterion(win_rate, avg_win, avg_loss)
        print(f"   Kelly Fraction: {kelly:.2%}")
        
        # Tính position size
        volatility = market_data.get("volatility", 0.3)
        position_size = self.risk.calculate_position_size(win_rate, avg_win, avg_loss, volatility)
        print(f"   Position Size: ${position_size:.2f}")
        
        # Bước 4: Quyết định DCA
        print("\n💰 Bước 4: Quyết định DCA")
        
        base_dca = 100  # $100 mỗi ngày
        market_condition = "bull" if signal['score'] > 0 else "bear"
        adaptive_dca = self.risk.adaptive_dca_amount(base_dca, market_condition, volatility)
        
        print(f"   Base DCA: ${base_dca:.2f}")
        print(f"   Market Condition: {market_condition.upper()}")
        print(f"   Adaptive DCA: ${adaptive_dca:.2f}")
        
        # Bước 5: Ghi nhận quyết định
        print("\n📝 Bước 5: Ghi nhận quyết định vào nhật ký")
        
        decision_summary = f"{final_decision['decision']} - {signal['signal_type']}"
        reason = f"Bull: {bull_view['recommendation']}, Bear: {bear_view['recommendation']}"
        
        self.reflection.log_decision(
            decision=decision_summary,
            reason=reason,
            amount=f"${adaptive_dca:.2f}",
            risk_assessment=f"VaR: {var:.2%}, Drawdown: {self.risk.max_drawdown:.2%}",
            data_sources="RSI, MACD, On-chain, Whale movements"
        )
        print("   ✓ Quyết định đã được ghi lại")
        
        # Bước 6: Phân tích kế hoạch tháng
        print("\n📅 Bước 6: Phân tích kế hoạch DCA tháng")
        monthly_plan = self.monthly_planner.find_entry_window(None, signal)
        print(f"   Kế hoạch tháng: {monthly_plan['recommendation']}")
        print(f"   Độ tin cậy: {monthly_plan['confidence']:.2%}")
        print(f"   Lý do: {monthly_plan['reason']}")
        
        # Nếu là "STRONG_ENTRY_NOW", giải ngân toàn bộ vốn tháng
        if monthly_plan['recommendation'] == "STRONG_ENTRY_NOW":
            total_monthly_budget = 3000  # Giả sử ngân sách 1 tháng là $3000
            adaptive_dca = total_monthly_budget  # Giải ngân 1 lần duy nhất
            print(f"   💰 GIẢI NGÂN TOÀN BỘ: ${adaptive_dca:.2f}")
        
        # Tổng hợp kết quả
        result = {
            "timestamp": datetime.now().isoformat(),
            "signal": signal,
            "agent_analysis": final_decision,
            "dca_amount": adaptive_dca,
            "decision": final_decision['decision'],
            "monthly_plan": monthly_plan,
            "risk_metrics": self.risk.get_risk_metrics()
        }
        
        return result
    
    def evaluate_performance(self, actual_price_change: float, dca_amount: float):
        """
        Đánh giá hiệu suất của quyết định DCA
        
        Args:
            actual_price_change: Thay đổi giá thực tế (%)
            dca_amount: Số tiền DCA
        """
        pnl = dca_amount * actual_price_change
        
        self.performance_log.append({
            "timestamp": datetime.now().isoformat(),
            "dca_amount": dca_amount,
            "price_change": actual_price_change,
            "pnl": pnl
        })
        
        # Cập nhật vốn
        self.capital += pnl
        self.risk.capital = self.capital
        
        # Cập nhật drawdown
        drawdown = self.risk.update_drawdown(self.capital)
        
        print(f"\n📈 Đánh giá hiệu suất:")
        print(f"   Giá thay đổi: {actual_price_change:.2%}")
        print(f"   P&L: ${pnl:.2f}")
        print(f"   Vốn hiện tại: ${self.capital:.2f}")
        print(f"   Drawdown: {drawdown:.2%}")
        
        # Nếu drawdown quá cao, ghi nhận bài học
        if drawdown > 0.1:
            self.reflection._add_lesson(
                f"Drawdown {drawdown:.2%} - Cần điều chỉnh chiến lược",
                "Tăng tỷ lệ cash, giảm position size"
            )

# Test
if __name__ == "__main__":
    fund = SolanaQuantFund(initial_capital=10000)
    
    # Mock market data
    test_market_data = {
        "timestamp": datetime.now().isoformat(),
        "prices": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 108, 105, 102, 98, 95, 92, 90, 88, 85],
        "rsi": 28,
        "volume_change": 0.25,
        "active_wallets": {"prev": 100000, "current": 115000},
        "tx_volume": {"prev": 1000000, "current": 1200000},
        "whale_transfers": {"outflow": 500},
        "priority_fee": 0.0003,
        "volatility": 0.3,
        "win_rate": 0.55,
        "avg_win": 0.15,
        "avg_loss": 0.10,
        "historical_returns": [-0.05, 0.03, 0.02, -0.02, 0.04]
    }
    
    # Chạy phân tích
    result = fund.run_daily_analysis(test_market_data)
    
    print("\n" + "="*60)
    print("📊 KẾT QUẢ PHÂN TÍCH")
    print("="*60)
    print(json.dumps({
        "decision": result["decision"],
        "dca_amount": result["dca_amount"],
        "signal": result["signal"]["signal_type"],
        "confidence": result["signal"]["confidence"]
    }, indent=2, ensure_ascii=False))
