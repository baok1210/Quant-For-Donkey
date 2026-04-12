import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
import os

# Import các module từ hệ thống
import sys
sys.path.append('.')

from engine.reflection import ReflectionEngine
from engine.agents import MultiAgentSystem
from engine.risk import RiskEngine
from engine.signals import SignalEngine

# --- Cấu hình trang ---
st.set_page_config(
    page_title="Solana Quant Fund AI",
    page_icon="📊",
    layout="wide"
)

# --- Header ---
st.title("🏛️ Solana Quant Fund AI Dashboard")
st.markdown("""
*Hệ thống đầu tư định lượng trên Solana với khả năng tự học*
""")

# --- Sidebar ---
st.sidebar.header("⚙️ Cài đặt")
st.sidebar.markdown("Cấu hình hệ thống")

# --- Main Content ---
# Tạo các tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Dashboard", "📝 Nhật ký", "🤖 Tác vụ", "📊 Phân tích", "⚙️ Cấu hình"])

# --- Tab 5: Cấu hình ---
with tab5:
    st.header("⚙️ Cấu hình hệ thống")
    st.markdown("Quản lý API Keys và thông số vận hành của AI.")

    # Phân nhóm cấu hình
    with st.expander("🧠 Cấu hình AI Brain", expanded=True):
        col_ai1, col_ai2 = st.columns(2)
        with col_ai1:
            provider = st.selectbox("Chọn AI Provider", ["openai", "gemini"], index=0)
        with col_ai2:
            model_list = {
                "openai": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
                "gemini": ["gemini-pro", "gemini-flash"]
            }
            selected_model = st.selectbox("Chọn Model", model_list[provider])
        
        openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")

    with st.expander("🏦 Cấu hình Sàn giao dịch (Binance/OKX)", expanded=False):
        exchange = st.selectbox("Chọn Sàn thực thi", ["Binance", "OKX"])
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            api_key = st.text_input(f"{exchange} API Key", type="password")
        with col_ex2:
            api_secret = st.text_input(f"{exchange} Secret Key", type="password")
        
        if exchange == "OKX":
            passphrase = st.text_input("OKX Passphrase", type="password")

    with st.expander("💰 Thông số đầu tư & Rủi ro", expanded=False):
        col_inv1, col_inv2 = st.columns(2)
        with col_inv1:
            init_cap = st.number_input("Vốn khởi đầu ($)", value=1000.0)
            dca_amt = st.number_input("Số tiền DCA cơ bản ($)", value=100.0)
        with col_inv2:
            max_dd = st.slider("Max Drawdown Limit (%)", 5, 50, 20)
            kelly = st.slider("Kelly Fraction", 0.1, 1.0, 0.5)

    if st.button("💾 Lưu cấu hình", type="primary"):
        # Logic lưu vào file .env hoặc config.json
        config_data = {
            "AI_PROVIDER": provider,
            "AI_MODEL": selected_model,
            "OPENAI_API_KEY": openai_key,
            "GEMINI_API_KEY": gemini_key,
            "INITIAL_CAPITAL": init_cap,
            "BASE_DCA_AMOUNT": dca_amt,
            "MAX_DRAWDOWN": max_dd / 100,
            "KELLY_FRACTION": kelly
        }
        # Lưu file config
        with open("config_settings.json", "w") as f:
            json.dump(config_data, f, indent=4)
        st.success("✅ Đã lưu cấu hình thành công! Vui lòng khởi động lại hệ thống để áp dụng.")

from engine.monthly_planner import MonthlyPlanner

# --- Tab 1: Dashboard ---
with tab1:
    st.header("📊 Tổng quan hệ thống")
    
    # Sniper DCA Monthly Plan
    st.info("🎯 **Kế hoạch DCA Sniper Tháng này:** Đang chờ thời điểm giá sụt giảm mạnh nhất để giải ngân.")
    
    # Hiển thị thông tin cơ bản
    col1, col2, col3 = st.columns(3)

    
    with col1:
        st.metric("Vốn hiện tại", "$10,000.00")
        st.metric("Drawdown tối đa", "0.00%")
        
    with col2:
        st.metric("Số lệnh DCA", "15")
        st.metric("ROI", "12.5%")
        
    with col3:
        st.metric("Tín hiệu mới", "BUY")
        st.metric("Confidence", "85%")
    
    # Biểu đồ hiệu suất
    st.subheader("📈 Hiệu suất theo thời gian")
    
    # Tạo dữ liệu giả lập cho biểu đồ
    dates = pd.date_range(start="2026-03-01", end=datetime.now(), freq='D')
    performance = [10000 + i*50 + (i%7)*20 for i in range(len(dates))]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=performance, mode='lines+markers', name='Vốn'))
    fig.update_layout(title='Hiệu suất vốn theo thời gian', xaxis_title='Ngày', yaxis_title='Vốn ($)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Thông tin rủi ro
    st.subheader("⚠️ Quản trị rủi ro")
    col_risk1, col_risk2 = st.columns(2)
    
    with col_risk1:
        st.write("**Value at Risk (95%)**")
        st.write("0.85%")
        
    with col_risk2:
        st.write("**Kelly Fraction**")
        st.write("15%")

with tab2:
    st.header("📝 Nhật ký & Tự cải thiện")
    
    col_diary, col_proposals = st.columns([2, 1])
    
    with col_diary:
        st.subheader("Nhật ký đầu tư")
        diary_path = "memory/INVESTMENT_DIARY.md"
        if os.path.exists(diary_path):
            with open(diary_path, 'r', encoding='utf-8') as f:
                diary_content = f.read()
            st.markdown(diary_content)
            
    with col_proposals:
        st.subheader("💡 Đề xuất cải tiến AI")
        reflection = ReflectionEngine()
        proposals = reflection.propose_improvements()
        
        if isinstance(proposals, list):
            for p in proposals:
                st.success(f"✓ {p}")
        else:
            st.info(proposals)


# --- Tab 3: Tác vụ ---
with tab3:
    st.header("🤖 Hệ thống tác vụ")
    
    # Hiển thị thông tin từ Multi-Agent System
    st.subheader("🔍 Phân tích từ các tác vụ")
    
    # Tạo mock data để demo
    mock_data = {
        "timestamp": datetime.now().isoformat(),
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
    
    # Tạo đối tượng và phân tích
    agents = MultiAgentSystem()
    agent_analysis = agents.run_analysis(mock_data)
    
    # Hiển thị kết quả
    col_bull, col_bear, col_arbiter = st.columns(3)
    
    with col_bull:
        st.subheader("🐂 Bull Agent")
        st.write(f"Stance: {agent_analysis['bull_view']['stance']}")
        st.write(f"Confidence: {agent_analysis['bull_view']['confidence']:.2%}")
        st.write("Signals:")
        for signal in agent_analysis['bull_view']['signals']:
            st.markdown(f"- {signal}")
            
    with col_bear:
        st.subheader("🐻 Bear Agent")
        st.write(f"Stance: {agent_analysis['bear_view']['stance']}")
        st.write(f"Risk Score: {agent_analysis['bear_view']['risk_score']:.2%}")
        st.write("Warnings:")
        for warning in agent_analysis['bear_view']['warnings']:
            st.markdown(f"- {warning}")
            
    with col_arbiter:
        st.subheader("⚖️ Arbiter Agent")
        st.write(f"Decision: {agent_analysis['final_decision']['decision']}")
        st.write(f"Net Score: {agent_analysis['final_decision']['net_score']:.2f}")
        st.write("Reasoning:")
        st.write(agent_analysis['final_decision']['reasoning'])

# --- Tab 4: Phân tích ---
with tab4:
    st.header("📊 Phân tích tín hiệu")
    
    # Tạo mock data
    signal_data = {
        "prices": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 108, 105, 102, 98, 95, 92, 90, 88, 85],
        "active_wallets": {"prev": 100000, "current": 115000},
        "tx_volume": {"prev": 1000000, "current": 1200000},
        "whale_transfers": {"outflow": 500},
        "priority_fee": 0.0003
    }
    
    # Tạo đối tượng và phân tích
    signals = SignalEngine()
    signal_result = signals.generate_signal(signal_data)
    
    st.subheader("📈 Tín hiệu phân tích")
    col_signal1, col_signal2 = st.columns(2)
    
    with col_signal1:
        st.write(f"**Loại tín hiệu:** {signal_result['signal_type']}")
        st.write(f"**Độ tin cậy:** {signal_result['confidence']:.2%}")
        st.write(f"**RSI:** {signal_result['rsi']:.2f}")
        st.write(f"**Trend MACD:** {signal_result['macd_trend']}")
        
    with col_signal2:
        st.write("**Các tín hiệu:**")
        for signal in signal_result['signals']:
            st.markdown(f"- {signal}")
            
    # Hiển thị chỉ số on-chain
    st.subheader("🌐 Chỉ số on-chain")
    onchain = signal_result['onchain_metrics']
    col_onchain1, col_onchain2 = st.columns(2)
    
    with col_onchain1:
        st.write(f"**Active Wallets:** {onchain['active_wallets_change']:+.2%}")
        st.write(f"**TX Volume:** {onchain['tx_volume_change']:+.2%}")
        
    with col_onchain2:
        st.write(f"**Whale Movements:** {onchain['whale_movements']} SOL")
        st.write(f"**Network Health:** {onchain['network_health']}")

# --- Footer ---
st.markdown("---")
st.caption("Solana Quant Fund AI v0.1.0 - Hệ thống tự học định lượng")
