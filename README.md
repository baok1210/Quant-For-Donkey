# 🫏 Quant for Donkey

> **Hệ thống Quản lý Quỹ AI Quant chuyên nghiệp với Tư duy Tự hiệu chỉnh (Self-Correction Loop)** — Tích hợp Order Flow, Learning với Outcomes, và Dashboard 2 chế độ.**

<p align="center">
  <img src="logo_qfd.jpg" width="200" alt="QFD Logo">
</p>

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/GUI-Streamlit-red)
![Version](https://img.shields.io/badge/Version-4.4.0-brightgreen)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

---

## 🎯 Tổng quan

**Quant for Donkey (QFD)** là hệ thống giao dịch định lượng với khả năng **tự học từ quá khứ** và **tự sửa lỗi logic**:

1. **Tự tạo Outcomes**: Chạy backtest trên dữ liệu lịch sử → tạo decisions với kết quả thực tế
2. **Tự học**: Phân tích patterns từ các quyết định có lãi/lỗ → tối ưu parameters
3. **Tự kiểm tra**: LogicGuard đảm bảo mọi module có dữ liệu đúng trước khi chạy
4. **Tự cải thiện**: Sau mỗi trade → cập nhật outcome → học thêm

---

## ✨ Tính năng v4.4.0

### 🧠 Self-Correction Loop (NEW!)
| Module | Chức năng |
|--------|----------|
| **LogicGuard** | Kiểm tra logic trước khi chạy - không cho phép "phỏng đoán" |
| **BacktestEngine** | Tạo dữ liệu học với OUTCOMES từ OHLCV |
| **LearningLoop** | Học từ decisions có outcome → tối ưu RSI thresholds |
| **FixedLearning** | Lưu decisions SAU KHI có kết quả |

### 🤖 Multi-Provider AI Brain
| Provider | Models | API Key Env |
|----------|--------|-------------|
| **OpenRouter** (Recommended) | 300+ models | `OPENROUTER_API_KEY` |
| **OpenAI** | GPT-5.4, GPT-4o | `OPENAI_API_KEY` |
| **Claude** | Sonnet 4.6, Opus 4.6 | `ANTHROPIC_API_KEY` |
| **Google** | Gemini 2.5 Pro/Flash | `GEMINI_API_KEY` |
| **DeepSeek** | DeepSeek R1 (Free!) | `DEEPSEEK_API_KEY` |
| **Custom** | Your own LLM | `CUSTOM_API_KEY` |

### 🌊 Order Flow & Smart Money
- **CVD**: Cumulative Volume Delta
- **Absorption Detection**: Vùng hấp thụ của whales
- **Delta Divergence**: Giá và volume mâu thuẫn

### 📊 6 Chiến lược
| Chiến lược | Đặc điểm |
|----------|----------|
| EMA Crossover 9/21 | Bắt trend sớm |
| ATR Breakout 2.0x | Stop loss thông minh |
| Bollinger Squeeze | Chờ bùng nổ |
| Grid Trading | Thu hoạch biến động |
| Regime Adaptive | Đổi bài theo thị trường |
| Multi-Strategy Ensemble | Vote đa số |

### 🔗 Integrations (v4.4.0)
| Module | Nguồn |
|--------|-------|
| **VectorBT** | High-performance backtesting |
| **Freqtrade** | Hyperopt, Edge, Strategy framework |
| **Hummingbot** | Market Making, DEX connectors |
| **vn.py** | Vietnam market data (HOSE/HNX) |

---

## 🏗️ Kiến trúc Self-Correcting

```
┌─────────────────────────────────────────────────────────┐
│                  LogicGuard (Kiểm tra)                 │
│  - Verify: Module cần Outcome?                      │
│  - Block nếu thiếu dữ liệu                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              BacktestEngine → Outcomes               │
│  - OHLCV → Simulate trades → PROFIT/LOSS          │
│  - Save to memory/learning_base.json              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              LearningLoop → Rules                   │
│  - Analyze: RSI ranges for PROFIT vs LOSS         │
│  - Optimize: RSI thresholds                       │
│  - Output: Learned rules                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Real-time Decision                      │
│  - Input: Current RSI, Price                     │
│  - Check: Learned thresholds                     │
│  - Output: BUY/SELL/HOLD                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Update & Re-learn                      │
│  - Record actual outcome                         │
│  - Periodic: Re-run LearningLoop                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Cài đặt

```bash
# Clone
git clone https://github.com/baok1210/Quant-For-Donkey.git
cd Quant-For-Donkey

# Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install
pip install -r requirements.txt

# Config
cp .env.example .env
# Thêm API keys (OpenRouter khuyến nghị)
```

---

## 📁 Cấu trúc modules

```
engine/
├── ai_brain.py          # Multi-provider AI
├── logic_guard.py        # Self-correction guard
├── backtest_engine.py    # Tạo outcomes
├── learning_loop.py     # Học từ outcomes
├── fixed_learning.py    # Lưu decisions
├── forecaster.py        # XGBoost prediction
├── order_flow.py        # Smart money
├── strategies/          # 6 chiến lược
└── integrations/       # VectorBT, Freqtrade, Hummingbot, vn.py
```

---

## 📊 Module Status

| Module | Needs Outcome | Status |
|--------|-------------|--------|
| Forecaster | ❌ | ✅ Predict |
| Order Flow | ❌ | ✅ Analysis |
| Multi Strategy | ❌ | ✅ Vote |
| **Learning Loop** | ✅ | ✅ Creates & Uses |
| **LogicGuard** | ✅ | ✅ Verifies |

---

## 📄 Chạy hệ thống

```bash
# CLI
python main.py

# Dashboard
streamlit run dashboard.py

# Test modules
python test_modules.py

# Audit system
python -c "from engine.logic_guard import audit_system; print(audit_system())"
```

---

## ⚠️ Disclaimer

Đây là công cụ hỗ trợ quyết định, **không phải lời khuyên đầu tư**.

---

**Version 4.4.0 | 2026-04-14 | Self-Correction Loop Enabled**
