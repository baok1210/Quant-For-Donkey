# 🏛️ Solana DCA AI Learner

> Hệ thống đầu tư định lượng trên Solana với khả năng tự học, tự cải thiện và tích hợp TradingView.

**Version:** v2.0.0 | **Release Date:** 2026-04-13

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/GUI-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

---

## 🎯 Tổng quan

Solana DCA AI Learner là một hệ thống giao dịch định lượng (Quant Trading) hoàn chỉnh với khả năng:
- **Tự học từ lịch sử** (Offline Learning)
- **Phân tích thời gian thực** (Online Learning với GPT-4/Gemini)
- **Tự động khám phá indicator mới** từ TradingView
- **Backtest và tối ưu hóa** chiến lược tự động
- **Quản lý rủi ro chuyên nghiệp** với Circuit Breakers

---

## ✨ Tính năng chính

### 🧠 **AI & Machine Learning**
- **Multi-Agent System**: 3 AI agents (Bull / Bear / Arbiter) tranh luận để đưa ra quyết định
- **AI Brain (Online)**: Tích hợp GPT-4, Gemini để phân tích thị trường thời gian thực
- **Offline Learning**: Tự học từ nhật ký đầu tư và tự điều chỉnh trọng số
- **ML Forecasting**: XGBoost dự báo giá 24h tới
- **Deliberation Layer**: Hội đồng AI thảo luận trước khi quyết định

### 📊 **Phân tích & Dữ liệu**
- **Market Regime Detection**: Phát hiện 5 trạng thái thị trường (Bull/Bear/Sideways/Crisis/Transition)
- **Sentiment Analysis**: Phân tích cảm xúc từ Twitter & Reddit
- **On-chain Data**: TVL, DEX Volume, Whale movements, Network health (real-time)
- **Macro Indicators**: S&P 500, DXY, VIX, Gold, BTC correlation
- **Technical Indicators**: RSI, MACD, EMA, Bollinger Bands, và hơn 20 chỉ báo khác

### 🔄 **TradingView Integration (NEW!)**
- **Auto-Discovery**: Tự động phát hiện các indicator hot/trending từ TradingView
- **Pine Script Converter**: Chuyển đổi Pine Script sang Python tự động
- **Auto-Backtesting**: Chạy backtest cho indicator mới và xếp hạng hiệu suất
- **Smart Selection**: Tự động chọn top indicator tốt nhất để tích hợp

### 💰 **Chiến lược & Thực thi**
- **Monthly Sniper DCA**: Tìm thời điểm vàng duy nhất trong tháng để giải ngân
- **Adaptive DCA**: Tự điều chỉnh số tiền DCA theo điều kiện thị trường
- **Multi-Exchange Support**: Binance, OKX, Bybit, Coinbase, Kraken với Smart Order Routing
- **Portfolio Optimization**: Markowitz Mean-Variance, Black-Litterman
- **Paper Trading Mode**: Mô phỏng giao dịch mà không dùng tiền thật

### 🛡️ **Quản lý Rủi ro**
- **Kelly Criterion (Fixed)**: Công thức đúng `f* = W - (1-W)/R`
- **Circuit Breakers**: Dừng giao dịch khi drawdown > 20%
- **VaR & CVaR**: Đo lường rủi ro tối đa
- **Position Sizing**: Giới hạn tối đa 25% vốn mỗi lệnh
- **Max Drawdown Control**: Theo dõi và cảnh báo sụt giảm

### 🔬 **Backtesting & Testing**
- **Advanced Backtesting**: Walk-forward optimization với dữ liệu 1-2 năm
- **Performance Metrics**: Sharpe Ratio, Sortino Ratio, Calmar Ratio, Max Drawdown
- **Unit Tests**: Kiểm tra công thức Kelly và các hàm quan trọng
- **Out-of-sample Testing**: Đảm bảo không overfitting

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                    TradingView Integration                      │
│  Auto-Discovery → Pine Converter → Backtest → Rank & Select    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Data Collection Layer                       │
│  On-chain │ Sentiment │ Macro │ Multi-Exchange │ Historical    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Analysis & Intelligence                      │
│  Signal Engine → Regime Detection → ML Forecasting              │
│  Multi-Agent System → Deliberation Layer → AI Brain (LLM)       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Risk & Portfolio Management                   │
│  Kelly Criterion → Circuit Breakers → Portfolio Optimization    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Execution & Learning                        │
│  Paper Trading / Live Trading → Reflection Engine → Self-Learn  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Cài đặt

```bash
# Clone repo
git clone https://github.com/baok1210/solana-dca-ai-learner.git
cd solana-dca-ai-learner

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac

# Cài dependencies
pip install -r requirements.txt

# Cấu hình API keys
copy .env.example .env    # Windows
# cp .env.example .env   # Linux/Mac
# Mở .env và điền API keys
```

---

## 🖥️ Sử dụng

### Chạy Dashboard GUI
```bash
streamlit run dashboard.py
```

### Chạy phân tích (CLI)
```bash
python main.py
```

### Cấu hình qua Dashboard
1. Mở Dashboard
2. Chuyển sang tab **"⚙️ Cấu hình"**
3. Điền AI Provider (OpenAI/Gemini), chọn Model, nhập API Key
4. Điền thông tin sàn giao dịch (Binance/OKX) nếu dùng Live Trading
5. Điều chỉnh vốn, DCA amount, Max Drawdown, Kelly Fraction
6. Nhấn **"💾 Lưu cấu hình"**

---

## 📁 Cấu trúc thư mục

```
solana-dca-ai-learner/
├── VERSION                     # Số phiên bản hiện tại
├── CHANGELOG.md                # Lịch sử thay đổi
├── config.py                   # Tham số hệ thống
├── main.py                     # Entry point CLI
├── dashboard.py                # GUI Streamlit
├── requirements.txt            # Dependencies
├── .env.example                # Template API keys
├── .gitignore                  # Git ignore rules
├── README.md                   # Tài liệu chính
├── USAGE.md                    # Hướng dẫn chi tiết
├── engine/
│   ├── ai_brain.py             # AI Brain (GPT-4/Gemini)
│   ├── agents.py               # Multi-Agent System
│   ├── backtester.py           # Advanced Backtesting
│   ├── deliberation.py         # Multi-agent Discussion
│   ├── exchanges.py            # Legacy exchange connector
│   ├── forecaster.py           # XGBoost Price Prediction
│   ├── historical_data.py      # Historical data manager
│   ├── macro.py                # S&P500, DXY, VIX, Gold
│   ├── monthly_planner.py      # Kế hoạch DCA hàng tháng
│   ├── multi_exchange.py       # Smart Order Routing (5 sàn)
│   ├── offline_learner.py      # Offline AI self-learning
│   ├── onchain.py              # TVL, DEX, Whale tracking
│   ├── online_learner.py       # Online AI learning
│   ├── paper_trading.py        # Simulation mode
│   ├── portfolio.py            # Markowitz Optimization
│   ├── reflection.py           # Bộ máy tự phản biện
│   ├── regime.py               # Market state detection
│   ├── risk.py                 # Fixed Kelly & Risk control
│   ├── security.py             # API Key encryption
│   ├── sentiment.py            # Social media analysis
│   ├── signals.py              # Technical indicators
│   ├── tv_backtester.py        # TradingView indicator backtest
│   ├── tv_connector.py         # TradingView API connector
│   ├── tv_discovery.py         # Auto-discover indicators
│   └── tv_indicator_converter.py # Pine Script → Python
├── tests/
│   └── test_kelly.py           # Unit Tests
├── memory/                     # AI Memory (auto-generated)
├── data/                       # Dữ liệu thu thập
├── reports/                    # Báo cáo hiệu suất
├── backtests/                  # Kết quả backtest
└── strategies/                 # Chiến lược giao dịch
```

---

## 📊 Lịch sử phát triển

### v2.0.0 (2026-04-13) - TradingView Integration
**Tính năng mới:**
- ✅ Tích hợp TradingView: Auto-discovery, Pine Script converter
- ✅ Tự động backtest và xếp hạng indicator mới
- ✅ Macro Indicators: S&P 500, DXY, VIX, Gold
- ✅ ML Forecasting: XGBoost dự báo giá
- ✅ Multi-Agent Deliberation Layer

### v1.0.0 (2026-04-12) - Production Release
**Tính năng cốt lõi:**
- ✅ Multi-Agent System (Bull/Bear/Arbiter)
- ✅ Reflection Engine (Tự học từ sai lầm)
- ✅ Risk Engine (Kelly Criterion, VaR)
- ✅ Signal Engine (RSI, MACD, On-chain)
- ✅ Monthly Sniper DCA
- ✅ AI Brain (GPT-4, Gemini)
- ✅ Custom Model Selection
- ✅ Professional Settings Tab
- ✅ Dashboard GUI (6 tabs)
- ✅ Version Management System

**Giai đoạn 1 (Nền tảng):**
- ✅ Market Regime Detection
- ✅ Advanced Backtesting Engine
- ✅ Fixed Kelly Criterion Formula
- ✅ Circuit Breakers
- ✅ Paper Trading Mode
- ✅ Unit Tests

**Giai đoạn 2 (Dữ liệu & Thực thi):**
- ✅ Sentiment Analysis (Twitter + Reddit)
- ✅ On-chain Data (TVL, DEX, Whale)
- ✅ Multi-Exchange Support (5 sàn)
- ✅ Portfolio Optimization (Markowitz, Black-Litterman)

**Giai đoạn 3 (Cao cấp & AI):**
- ✅ Macro Indicators Integration
- ✅ ML-based Price Forecasting
- ✅ Multi-Agent Collaboration

---

## 🔄 Vòng lặp tự cải thiện

1. **Thu thập** dữ liệu thị trường & on-chain
2. **Phân tích** qua Signal Engine + Multi-Agent System
3. **Gửi cho AI Brain** (GPT-4/Gemini) để phân tích chuyên sâu
4. **Quyết định** DCA amount qua Risk Engine
5. **Ghi nhận** quyết định vào Investment Diary
6. **Đánh giá** kết quả sau 1 tuần
7. **Rút bài học** và đề xuất cải tiến mô hình
8. **Tự động điều chỉnh** trọng số dựa trên hiệu suất
9. **Khám phá indicator mới** từ TradingView
10. **Lặp lại** với mô hình đã được cải thiện

---

## 🏷️ Quản lý phiên bản

Dự án theo dõi phiên bản theo chuẩn **Semantic Versioning (SemVer)**:

- **Major (X.0.0)**: Thay đổi lớn (ví dụ: thêm Live Trading)
- **Minor (1.X.0)**: Tính năng mới (ví dụ: thêm Gemini Flash)
- **Patch (1.0.X)**: Sửa lỗi nhỏ (bug fixes)

### Quay lại phiên bản cũ:
```bash
# Xem danh sách các version
git tag

# Quay lại v1.0.0
git checkout v1.0.0
```

---

## ⚠️ Disclaimer

Đây là công cụ hỗ trợ quyết định, **không phải lời khuyên đầu tư**. Luôn tự nghiên cứu (DYOR) trước khi giao dịch.

---

## 📄 License

MIT License

---

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo Pull Request hoặc Issue trên GitHub.

---

## 📞 Liên hệ

- **GitHub**: https://github.com/baok1210/solana-dca-ai-learner
- **Issues**: https://github.com/baok1210/solana-dca-ai-learner/issues

---

**Được xây dựng với ❤️ bởi OpenClaw AI**
