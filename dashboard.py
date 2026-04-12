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
tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard", "📝 Nhật ký", "🤖 Tác vụ", "📊 Phân tích"])

# --- Tab 1: Dashboard ---
with tab1:
    st.header("📊 Tổng quan hệ thống")
    
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

# --- Tab 2: Nhật ký ---
with tab2:
    st.header("📝 Nhật ký đầu tư")
    
    # Hiển thị nội dung file INVESTMENT_DIARY.md
    diary_path = "memory/INVESTMENT_DIARY.md"
    if os.path.exists(diary_path):
        with open(diary_path, 'r', encoding='utf-8') as f:
            diary_content = f.read()
        st.markdown(diary_content)
    else:
        st.info("Chưa có nhật ký đầu tư nào.")

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
