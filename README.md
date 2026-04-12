# 🏛️ Solana Quant Fund AI

> Hệ thống đầu tư định lượng trên Solana với khả năng tự học và tự cải thiện.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/GUI-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Tính năng

- **Multi-Agent System**: 3 AI agents (Bull / Bear / Arbiter) tranh luận để đưa ra quyết định DCA tối ưu
- **Adaptive DCA**: Tự điều chỉnh số tiền DCA theo điều kiện thị trường
- **Risk Engine**: Kelly Criterion, VaR, Volatility Scaling, Max Drawdown control
- **Signal Engine**: RSI, MACD, On-chain metrics, Whale tracking
- **Reflection Engine**: Tự ghi nhật ký, đánh giá sai lầm và rút bài học
- **Dashboard GUI**: Giao diện Streamlit để theo dõi và quản lý

## 🏗️ Kiến trúc

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Signal      │   │  Multi-Agent │   │  Risk        │
│  Engine      │──>│  System      │──>│  Engine      │
│  (Dữ liệu)  │   │  (Phân tích) │   │  (Rủi ro)    │
└──────────────┘   └──────────────┘   └──────────────┘
        │                  │                  │
        └──────────┬───────┘                  │
                   ▼                          ▼
            ┌──────────────┐          ┌──────────────┐
            │  Reflection  │          │  Adaptive    │
            │  Engine      │          │  DCA         │
            │  (Tự học)    │          │  (Thực thi)  │
            └──────────────┘          └──────────────┘
```

## 🚀 Cài đặt

```bash
# Clone repo
git clone https://github.com/<your-username>/solana-quant-fund.git
cd solana-quant-fund

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Cài dependencies
pip install -r requirements.txt

# Cấu hình API keys
cp .env.example .env
# Mở .env và điền API keys
```

## 🖥️ Sử dụng

### Chạy Dashboard GUI
```bash
streamlit run dashboard.py
```

### Chạy phân tích (CLI)
```bash
python main.py
```

## 📁 Cấu trúc thư mục

```
solana-quant-fund/
├── config.py              # Tham số hệ thống
├── main.py                # Entry point CLI
├── dashboard.py           # GUI Streamlit
├── requirements.txt       # Dependencies
├── .env.example           # Template API keys
├── engine/
│   ├── reflection.py      # Bộ máy tự phản biện
│   ├── agents.py          # Multi-Agent System
│   ├── risk.py            # Quản trị rủi ro
│   └── signals.py         # Tín hiệu phân tích
├── memory/                # Bộ nhớ AI (auto-generated)
├── data/                  # Dữ liệu thu thập
├── reports/               # Báo cáo hiệu suất
└── backtests/             # Kết quả backtest
```

## 🔄 Vòng lặp tự cải thiện

1. **Thu thập** dữ liệu thị trường & on-chain
2. **Phân tích** qua Signal Engine + Multi-Agent System
3. **Quyết định** DCA amount qua Risk Engine
4. **Ghi nhận** quyết định vào Investment Diary
5. **Đánh giá** kết quả sau 1 tuần
6. **Rút bài học** và cập nhật trọng số mô hình
7. **Lặp lại** với mô hình đã được cải thiện

## ⚠️ Disclaimer

Đây là công cụ hỗ trợ quyết định, **không phải lời khuyên đầu tư**. Luôn tự nghiên cứu (DYOR) trước khi giao dịch.

## 📄 License

MIT License
