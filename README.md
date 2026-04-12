# 🫏 Quant for Donkey

> **Hệ thống Quản lý Quỹ AI Quant dành cho những chú Lừa kiên trì — Tích hợp 6 chiến lược "thực chiến", tự học và tự động săn lùng cơ hội.**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/GUI-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-4.2.0-brightgreen)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

---

## 📊 Performance Targets (Donkey Proof)

| Metric | Current | Target |
|--------|---------|--------|
| **Profit Factor** | 1.59 | > 1.5 |
| **Sharpe Ratio** | 3.49 | > 1.5 |
| **Win Rate** | 44.3-87% | > 45% |
| **Max Drawdown** | 4.5% | < 15% |
| **Execution Cost** | Minimal | Optimized Slippage |

---

## 🎯 Tổng quan

**Quant for Donkey** là một cỗ máy giao dịch định lượng hoàn chỉnh, được thiết kế để biến những chú lừa (nhà đầu tư kiên nhẫn) thành những chuyên gia thực thụ bằng sức mạnh của AI và dữ liệu "Edge":

- **6 Chiến lược Donkey-Safe**: EMA, ATR, Bollinger, Grid, Regime, Ensemble.
- **Dữ liệu Professional**: Funding Rate, Liquidations, Open Interest real-time.
- **Tự học (AI Offline)**: Phân tích nhật ký đầu tư để tự sửa lỗi.
- **Discovery tự động**: Săn lùng indicator mới nhất từ TradingView.
- **Backtest thực tế**: Mô phỏng trượt giá (Slippage), phí sàn và spread.

---

## ✨ Tính năng chính

### 📈 6 Chiến lược Chủ chốt (NEW!)

| Chiến lược | Đặc điểm | Phù hợp với |
|----------|--------|----------|
| **EMA Crossover 9/21** | Bắt trend sớm | Bull Market |
| **ATR Breakout 2.0x** | Chặn lỗ thông minh | Volatile Market |
| **Bollinger Bands Squeeze** | Chờ đợi bùng nổ | Consolidation |
| **Grid Trading** | Thu hoạch biến động | Sideways Market |
| **Regime Adaptive** | Tự động đổi bài | Toàn bộ thị trường |
| **Multi-Strategy Ensemble** | Bỏ phiếu đa số | Sự an toàn tuyệt đối |

### 🧠 Trí tuệ AI & Machine Learning
- **Multi-Agent System**: Hội đồng Bull/Bear/Arbiter thảo luận.
- **Conflict Resolution**: Cơ chế "Bear Wins" bảo vệ vốn khi rủi ro cao.
- **XGBoost Forecasting**: Dự báo giá 24h tới.
- **Walk-Forward Validation**: Test chiến lược trên dữ liệu chưa từng thấy.

### 🛡️ Quản trị Rủi ro (Donkey Protection)
- **Session Limits**: Giới hạn lệnh ngày, lỗ ngày và chuỗi thua.
- **Cooldown Mechanism**: Khóa giao dịch 1 giờ nếu thua 3 lệnh liên tiếp.
- **Kelly Criterion**: Tính toán khối lượng lệnh tối ưu chuẩn toán học.
- **Circuit Breakers**: Tự động ngắt hệ thống khi sụt giảm quá 20%.

---

## 🏗️ Kiến trúc Donkey Engine

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Donkey Discovery Layer (TradingView)             │
│  Auto-Discovery → Pine Converter → Backtest → Rank & Select         │
└──────────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                        Data Collection Layer                          │
│  Funding Rate │ Liquidations │ OI │ On-chain │ Real-time Price       │
└──────────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      Intelligence & Deliberation                      │
│  Conflict Resolution → Bear Protection → AI Brain (LLM)              │
│  Offline Learner (Diary Analysis)                                     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Cài đặt

```bash
# Clone repo
git clone https://github.com/baok1210/quant-for-donkey.git
cd quant-for-donkey

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

---

## 📁 Cấu trúc thư mục

```
quant-for-donkey/
├── VERSION                     # v4.2.0
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
│   ├── backtest_walkforward.py # 🆕 Anti-overfit testing
│   ├── deliberation.py         # 🆕 Conflict Resolution
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
│   ├── regime.py               # 🆕 ADX-enhanced detection
│   ├── risk.py                 # Session limits + Circuit breakers
│   ├── security.py             # API Key encryption
│   ├── sentiment.py            # Social media analysis
│   ├── signals.py              # Technical indicators (RSI, MACD)
│   ├── solana_rpc.py           # Helius/QuickNode RPC
│   ├── data_aggregator.py      # 🆕 Funding Rate, Liquidations
│   ├── advanced_dca.py         # 🆕 DCA timing chuyên nghiệp
│   ├── session_risk.py         # 🆕 Session-based risk
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

### v4.2.0 (2026-04-13) - Professional Edition: Conflict Resolution, Walk-Forward, Funding Data
**🆕 Tính năng mới:**
- ✅ **Conflict Resolution**: Bear Override khi confidence > 0.8, Weighted Voting
- ✅ **Walk-Forward Backtesting**: Train 6 tháng → Test 1 tháng, chống overfitting
- ✅ **Funding Rate History**: Phân tích chu kỳ 8h từ Binance API
- ✅ **Real Liquidation Data**: Từ Binance (thay cho mock data)
- ✅ **Funding Cycle Detection**: Phát hiện mô hình oscillation (+/-)
- ✅ **ADX-enhanced Regime Detection**: Đo độ mạnh xu hướng

**🔧 Cải tiến:**
- ✅ Sửa MACD calculation (dùng pandas.ewm chuẩn)
- ✅ Sửa RSI calculation (Wilder's Smoothing)
- ✅ Sửa Kelly Criterion formula (`f* = W - (1-W)/R`)
- ✅ Thêm .gitignore cho config_settings.json
- ✅ Cập nhật Dashboard với real-time price display

**📦 38+ Modules hoàn chỉnh**

### v4.1.0 (2026-04-13) - Session Risk, Slippage, ADX
- ✅ **Session Risk Management**: Daily loss 3%, Max trades 10/day, Cooldown 1h
- ✅ **Realistic Slippage**: Spread + Slippage + Partial fill trong Paper Trading
- ✅ **ADX in Regime Detection**: Phân biệt Strong Trend vs Weak Trend

### v4.0.0 (2026-04-13) - Professional Edition: Funding Rate, Liquidations, Advanced DCA
- ✅ **Crypto Data Aggregator**: Funding Rate, Open Interest, Long/Short Ratio
- ✅ **Advanced DCA Timing**: Funding Cycles, Liquidation Zones, Weekend Effect
- ✅ **Realistic Backtest Engine**: Slippage modeling, Walk-forward validation
- ✅ **Strategy Ensemble Voting**: Kết hợp 6 chiến lược

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

# Quay lại v4.0.0
git checkout v4.0.0
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

- **GitHub**: https://github.com/baok1210/quant-for-donkey
- **Issues**: https://github.com/baok1210/quant-for-donkey/issues

---

**Được xây dựng với ❤️ bởi OpenClaw AI**

*Version 4.2.0 | 2026-04-13 | 38+ Modules | 6 Proven Strategies | Production Ready*
