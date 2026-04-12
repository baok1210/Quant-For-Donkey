# 🏛️ Solana DCA AI Learner

> Hệ thống đầu tư định lượng trên Solana với khả năng tự học và tự cải thiện.

**Version:** v1.0.0 | **Release Date:** 2026-04-13

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/GUI-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Tính năng

- **Monthly Sniper DCA**: Tìm kiếm thời điểm vàng duy nhất trong tháng để giải ngân vốn lớn
- **Multi-Agent System**: 3 AI agents (Bull / Bear / Arbiter) tranh luận để đưa ra quyết định DCA tối ưu
- **Adaptive DCA**: Tự điều chỉnh chiến lược giữa "DCA thường ngày" và "Sniper DCA tháng"
- **Risk Engine**: Kelly Criterion, VaR, Volatility Scaling, Max Drawdown control
- **Signal Engine**: RSI, MACD, On-chain metrics, Whale tracking
- **Reflection Engine**: Tự ghi nhật ký, đánh giá sai lầm và rút bài học
- **Improvement Proposer**: Tự động phân tích nhật ký để đề xuất cải tiến mô hình
- **AI Brain (Online)**: Tích hợp GPT-4, Gemini để phân tích thị trường thời gian thực
- **Custom Model Selection**: Chọn bất kỳ model AI nào (GPT-4, GPT-3.5, Gemini Pro, Gemini Flash)
- **Settings GUI**: Tab cấu hình chuyên nghiệp để quản lý API Keys và tham số
- **Version Management**: Quản lý phiên bản, rollback khi cần

## 🏗️ Kiến trúc

```
Signal Engine → Multi-Agent System → Risk Engine → Monthly Planner → AI Brain (GPT-4/Gemini)
                                                              ↓
                                                      Reflection Engine (Tự học)
                                                              ↓
                                                      Improvement Proposer (Đề xuất)
                                                              ↓
                                                      Adaptive DCA (Thực thi)
```

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

## 📁 Cấu trúc thư mục

```
solana-dca-ai-learner/
├── VERSION                  # Số phiên bản hiện tại
├── CHANGELOG.md             # Lịch sử thay đổi
├── config.py               # Tham số hệ thống
├── main.py                 # Entry point CLI
├── dashboard.py            # GUI Streamlit
├── requirements.txt        # Dependencies
├── .env.example            # Template API keys
├── .gitignore              # Git ignore rules
├── README.md               # Tài liệu chính
├── USAGE.md                # Hướng dẫn chi tiết
├── engine/
│   ├── reflection.py       # Bộ máy tự phản biện
│   ├── agents.py           # Multi-Agent System
│   ├── risk.py             # Quản trị rủi ro
│   ├── signals.py          # Tín hiệu phân tích
│   ├── monthly_planner.py  # Kế hoạch DCA hàng tháng
│   ├── ai_brain.py         # AI Brain (GPT-4/Gemini)
│   ├── exchanges.py        # Kết nối sàn giao dịch
│   └── online_learner.py   # AI học online
├── memory/
│   ├── INVESTMENT_DIARY.md  # Nhật ký đầu tư
│   └── LESSONS_LEARNED.md   # Bài học rút ra
├── data/                    # Dữ liệu thu thập
├── reports/                 # Báo cáo hiệu suất
├── backtests/               # Kết quả backtest
└── strategies/              # Chiến lược giao dịch
```

## 🔄 Vòng lặp tự cải thiện

1. **Thu thập** dữ liệu thị trường & on-chain
2. **Phân tích** qua Signal Engine + Multi-Agent System
3. **Gửi cho AI Brain** (GPT-4/Gemini) để phân tích chuyên sâu
4. **Quyết định** DCA amount qua Risk Engine
5. **Ghi nhận** quyết định vào Investment Diary
6. **Đánh giá** kết quả sau 1 tuần
7. **Rút bài học** và đề xuất cải tiến mô hình
8. **Tự động điều chỉnh** trọng số dựa trên hiệu suất
9. **Lặp lại** với mô hình đã được cải thiện

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

## ⚠️ Disclaimer

Đây là công cụ hỗ trợ quyết định, **không phải lời khuyên đầu tư**. Luôn tự nghiên cứu (DYOR) trước khi giao dịch.

## 📄 License

MIT License
