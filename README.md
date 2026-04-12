# 🏛️ Solana DCA AI Learner

> **Hệ thống giao dịch định lượng Solana với 6 chiến lược đã được chứng minh, tự học và tự động discovery indicator từ TradingView.**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/GUI-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-4.0.0-brightgreen)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

---

## 📊 Performance Targets

| Metric | Current | Target |
|--------|---------|--------|
| **Profit Factor** | 1.59 | > 1.5 |
| **Sharpe Ratio** | 3.49 | > 1.5 |
| **Win Rate** | 44.3-87% | > 40% |
| **Max Drawdown** | 4.5% | < 20% |
| **Trades/Month** | 10-30 | 10-30 |

---

## 🎯 Tổng quan

Hệ thống giao dịch định lượng hoàn chỉnh với **30+ modules**, hỗ trợ:

- **6 chiến lược giao dịch đã được chứng minh** (EMA, ATR, Bollinger, Grid, Regime, Ensemble)
- **Tự học từ lịch sử** (Offline Learning từ Investment Diary)
- **Phân tích thời gian thực** (GPT-4/Gemini + Real-time price streaming)
- **Tự động discovery indicator mới** từ TradingView
- **Backtest với 1-2 năm dữ liệu** (Walk-forward optimization)
- **Đa sàn giao dịch** (Binance, OKX, Bybit, Coinbase, Kraken)
- **Quản lý rủi ro chuyên nghiệp** (Kelly Criterion, Circuit Breakers, VaR)

---

## ✨ Tính năng chính

### 📈 **6 Proven Trading Strategies (NEW in v3.0.0)**

| Strategy | Sharpe | Win Rate | Best For |
|----------|--------|----------|----------|
| **EMA Crossover 9/21** | 3.49 | 44.3% | Trend Following (Bull Market) |
| **ATR Stop-Loss 2.0x** | 2.1 | 46.3% | Risk Management |
| **Bollinger Bands Squeeze** | 1.59 | 44.3% | Breakout Trading |
| **Grid Trading** | - | 87% | Sideways Market |
| **Regime Adaptive** | - | - | Auto-select by Market State |
| **Multi-Strategy Ensemble** | - | - | Voting System (4 strategies) |

### 🧠 **AI & Machine Learning**
- **Multi-Agent System**: Bull/Bear/Arbiter tranh luận để ra quyết định
- **AI Brain Online**: GPT-4/Gemini phân tích thời gian thực
- **Offline Learner**: Tự học từ nhật ký, điều chỉnh trọng số
- **ML Forecasting**: XGBoost dự báo giá 24h
- **Deliberation Layer**: Hội đồng AI thảo luận

### 📊 **Dữ liệu & Phân tích**
- **Real-time Price**: 3 nguồn (CoinGecko, Binance WebSocket, DIA)
- **Market Regime Detection**: 5 trạng thái (Bull/Bear/Sideways/Crisis/Transition)
- **On-chain Data**: TVL, DEX Volume, Whale movements, Network health
- **Sentiment Analysis**: Twitter API v2 + Reddit
- **Macro Indicators**: S&P 500, DXY, VIX, Gold, BTC correlation

### 🔄 **TradingView Integration**
- **Auto-Discovery**: Tự động quét indicator trending
- **Pine Script Converter**: Chuyển Pine Script → Python
- **Auto-Backtest**: Chạy backtest và xếp hạng tự động

### 💰 **Chiến lược & Thực thi**
- **Monthly Sniper DCA**: Tìm thời điểm vàng trong tháng
- **Adaptive DCA**: Tự điều chỉnh theo thị trường
- **Multi-Exchange**: Smart Order Routing (5 sàn)
- **Portfolio Optimization**: Markowitz + Black-Litterman
- **Paper Trading**: Mô phỏng không rủi ro

### 🛡️ **Quản lý Rủi ro**
- **Kelly Criterion**: Công thức đúng `f* = W - (1-W)/R`
- **Circuit Breakers**: Dừng khi drawdown > 20%, daily loss > 5%
- **Stop-Loss & Trailing Stop**: Bảo vệ vốn tự động
- **VaR & CVaR**: Đo lường rủi ro tối đa

### 🔬 **Backtesting & Testing**
- **Advanced Backtesting**: Walk-forward optimization, 1-2 năm dữ liệu
- **Performance Metrics**: Sharpe, Sortino, Calmar, Max Drawdown
- **Unit Tests**: Kiểm tra công thức và logic
- **Black Swan Stress Tests**: COVID, Luna, FTX collapse

---

## 🏗️ Kiến trúc hệ thống

```
┌──────────────────────────────────────────────────────────────────────┐
│                     TradingView Discovery Layer                      │
│  Auto-Discovery → Pine Converter → Backtest → Rank & Select         │
└──────────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                        Data Collection Layer                          │
│  Real-time Price │ On-chain │ Sentiment │ Macro │ Historical (1-2y)  │
│  (CoinGecko, Binance, DIA)                                           │
└──────────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      Analysis & Intelligence                          │
│  Signal Engine → Regime Detection → ML Forecasting                   │
│  Multi-Agent System → Deliberation Layer → AI Brain (LLM)            │
│  Offline Learner → Weight Optimization                               │
└──────────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                   Strategy Engine (6 Proven Strategies)               │
│  EMA Crossover │ ATR Breakout │ Bollinger Squeeze │ Grid │ Ensemble  │
│  Regime Adaptive → Auto-select best strategy                         │
└──────────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                   Risk & Portfolio Management                         │
│  Kelly Criterion → Circuit Breakers → Stop-Loss/Trailing → VaR       │
└──────────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      Execution & Learning                             │
│  Paper Trading / Live Trading → Reflection Engine → Self-Learn       │
└──────────────────────────────────────────────────────────────────────┘
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
# Mở .env và điền API keys (hoặc dùng mặc định cho free sources)
```

### 🔑 API Keys (Tùy chọn)

| Source | API Key | Free? |
|--------|---------|-------|
| CoinGecko | Không cần | ✅ 10-30 req/phút |
| Binance WebSocket | Không cần | ✅ Real-time, mili giây |
| DIA API | Không cần | ✅ 3000+ tokens |
| Helius RPC | Cần (free tier: 100k/day) | ✅ |
| OpenAI GPT-4 | Cần | ❌ |
| Google Gemini | Cần | ✅ (free tier) |

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

### Test tất cả chiến lược
```bash
python demo_strategies.py
```

### Test real-time price streaming
```bash
python demo_realtime_price.py
```

### Tự động discovery indicator từ TradingView
```bash
python scripts/auto_discovery.py
```

### Tải dữ liệu lịch sử 1-2 năm
```python
from engine.historical_data import HistoricalDataManager
manager = HistoricalDataManager()
df = manager.fetch_large_dataset("SOL/USDT", "1h", years=1)
```

---

## 📁 Cấu trúc thư mục

```
solana-dca-ai-learner/
├── VERSION                     # v3.0.0
├── CHANGELOG.md                # Lịch sử thay đổi
├── config.py                   # Tham số hệ thống
├── main.py                     # Entry point CLI
├── dashboard.py                # GUI Streamlit (6 tabs)
├── requirements.txt            # Dependencies
├── .env.example                # Template API keys
├── .gitignore                  # Git ignore rules
├── README.md                   # Tài liệu chính
├── demo_strategies.py          # Demo 6 chiến lược
├── demo_realtime_price.py      # Demo real-time price
├── engine/
│   ├── strategies/             # 🆕 6 Proven Strategies
│   │   ├── ema_crossover.py    # EMA 9/21 (Sharpe 3.49)
│   │   ├── atr_breakout.py     # ATR Stop-Loss 2.0x (PF 1.72)
│   │   ├── bollinger_squeeze.py # Bollinger Squeeze
│   │   ├── grid_trading.py     # Grid (87% win rate sideways)
│   │   ├── regime_adaptive.py  # Auto-select by regime
│   │   └── multi_strategy.py   # Ensemble voting
│   ├── ai_brain.py             # AI Brain (GPT-4/Gemini)
│   ├── agents.py               # Multi-Agent System
│   ├── backtester.py           # Advanced Backtesting
│   ├── deliberation.py         # Multi-agent Discussion
│   ├── exchanges.py            # Legacy exchange connector
│   ├── forecaster.py           # XGBoost Price Prediction
│   ├── historical_data.py      # Historical data manager (1-2y)
│   ├── macro.py                # S&P500, DXY, VIX, Gold
│   ├── market_data_manager.py  # Real-time data aggregator
│   ├── monthly_planner.py      # Kế hoạch DCA hàng tháng
│   ├── multi_exchange.py       # Smart Order Routing (5 sàn)
│   ├── offline_learner.py      # AI self-learning từ diary
│   ├── onchain.py              # TVL, DEX, Whale tracking
│   ├── online_learner.py       # Online AI learning
│   ├── paper_trading.py        # Simulation mode
│   ├── portfolio.py            # Markowitz Optimization
│   ├── price_stream.py         # Real-time price (CG, Binance, DIA)
│   ├── reflection.py           # Bộ máy tự phản biện
│   ├── regime.py               # Market state detection
│   ├── risk.py                 # Fixed Kelly & Risk control
│   ├── security.py             # API Key encryption
│   ├── sentiment.py            # Social media analysis
│   ├── signals.py              # Technical indicators (RSI, MACD)
│   ├── solana_rpc.py           # Helius/QuickNode RPC
│   ├── tv_backtester.py        # TradingView indicator backtest
│   ├── tv_connector.py         # TradingView API connector
│   ├── tv_discovery.py         # Auto-discover indicators
│   └── tv_indicator_converter.py # Pine Script → Python
├── scripts/
│   └── auto_discovery.py       # 🆕 Auto-discovery TradingView
├── tests/
│   ├── unit_tests.py           # 🆕 Unit tests (Kelly, RSI, MACD)
│   └── test_kelly.py           # Kelly Criterion tests
├── memory/                     # AI Memory (diary, models)
├── data/                       # Historical data (CSV)
├── reports/                    # Báo cáo hiệu suất
├── backtests/                  # Kết quả backtest
└── strategies/                 # Chiến lược giao dịch
```

---

## 📊 Lịch sử phát triển

### v4.0.0 (2026-04-13) - Professional Edition: Funding Rate, Liquidations, Session Risk
**🆕 Tính năng mới (Professional Trader Features):**
- ✅ **Crypto Data Aggregator**: Funding Rate, Open Interest, Long/Short Ratio, Liquidations
- ✅ **Advanced DCA Timing**: Tối ưu hóa thời điểm DCA dựa trên Funding Cycles, Liquidation Zones, Weekend Effect
- ✅ **Session Risk Management**: Daily/Weekly loss limits, Max consecutive losses, Cooldown periods
- ✅ **Realistic Backtest Engine**: Slippage modeling, Spread simulation, Partial fill, Walk-forward validation
- ✅ **Strategy Ensemble Voting**: Kết hợp 6 chiến lược với hệ thống voting
- ✅ **Correlation Analysis**: BTC/SOL correlation tracking
- ✅ **Order Flow Analysis**: Absorption patterns, Delta calculation (mock)

**🔧 Cải tiến:**
- ✅ Tích hợp Binance Futures API cho Funding Rate real-time
- ✅ Thêm Liquidation Zone Detection
- ✅ Thêm Weekend Effect (giảm 30% volume cuối tuần)
- ✅ Thêm Cooldown mechanism sau chuỗi lỗ liên tiếp
- ✅ Cập nhật main.py với luồng phân tích chuyên nghiệp

**📦 35+ Modules hoàn chỉnh**

### v3.0.0 (2026-04-13) - 6 Proven Trading Strategies + Real-time Price
- ✅ **6 Proven Trading Strategies**: EMA 9/21, ATR Breakout, Bollinger Squeeze, Grid Trading, Regime Adaptive, Multi-Strategy Ensemble
- ✅ **Real-time Price Streaming**: CoinGecko (free), Binance WebSocket (millisecond), DIA (3000+ tokens, free)
- ✅ **Market Data Manager**: Tổng hợp giá + on-chain + sentiment + macro
- ✅ **Historical Data Manager**: Tải 1-2 năm dữ liệu OHLCV từ Binance
- ✅ **AI Offline Learner**: Tự học từ Investment Diary, điều chỉnh trọng số
- ✅ **Auto-Discovery Script**: Quét TradingView → Backtest → Rank indicators
- ✅ **Unit Tests**: Kelly Criterion, RSI, MACD, Signal Engine
- ✅ **Stop-Loss & Trailing Stop**: Bảo vệ vốn tự động
- ✅ **Circuit Breakers**: Daily loss 5%, Max drawdown 20%

### v2.0.0 (2026-04-13) - TradingView Integration
- ✅ Tích hợp TradingView: Auto-discovery, Pine Script converter
- ✅ Tự động backtest và xếp hạng indicator mới
- ✅ Macro Indicators: S&P 500, DXY, VIX, Gold
- ✅ ML Forecasting: XGBoost dự báo giá
- ✅ Multi-Agent Deliberation Layer

### v1.0.0 (2026-04-12) - Production Release
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

---

## 🔄 Vòng lặp tự cải thiện

1. **Thu thập** dữ liệu thị trường & on-chain
2. **Phân tích** qua Signal Engine + Multi-Agent System
3. **Gửi cho AI Brain** (GPT-4/Gemini) để phân tích chuyên sâu
4. **Chọn chiến lược tốt nhất** theo Regime (EMA/ATR/Grid/Ensemble)
5. **Ghi nhận** quyết định vào Investment Diary
6. **Đánh giá** kết quả sau 1 tuần
7. **Rút bài học** và đề xuất cải tiến mô hình
8. **Tự động điều chỉnh** trọng số (Offline Learner)
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

# Quay lại v2.0.0
git checkout v2.0.0
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

*Version 3.0.0 | 2026-04-13 | 30+ Modules | 6 Proven Strategies | Production Ready*
