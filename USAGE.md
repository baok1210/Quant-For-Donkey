# Solana Quant Fund AI - Hướng dẫn sử dụng

## 🚀 Bắt đầu nhanh

### 1. Cài đặt Dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy phân tích hàng ngày
```bash
python main.py
```

## 📊 Cấu trúc hệ thống

### Reflection Engine (Bộ máy tự phản biện)
- **Chức năng:** Ghi lại mọi quyết định DCA và đánh giá kết quả
- **Output:** 
  - `memory/INVESTMENT_DIARY.md` - Nhật ký đầu tư
  - `memory/LESSONS_LEARNED.md` - Bài học rút ra

### Multi-Agent System (Hệ thống đa tác vụ)
- **Bull Agent:** Tìm kiếm cơ hội tăng trưởng
- **Bear Agent:** Cảnh báo rủi ro
- **Arbiter Agent:** Ra quyết định cuối cùng

### Risk Engine (Bộ máy quản trị rủi ro)
- **Kelly Criterion:** Tính toán % vốn tối ưu
- **VaR:** Đo lường rủi ro tối đa
- **Adaptive DCA:** Điều chỉnh số tiền DCA theo điều kiện thị trường

### Signal Engine (Bộ máy tạo tín hiệu)
- **Technical Analysis:** RSI, MACD, EMA
- **On-chain Metrics:** Active wallets, TX volume, Whale movements
- **Network Health:** Phí mạng, tình trạng mạng

## 🔄 Vòng lặp tự cải thiện

```
Ngày 1: Phân tích → DCA → Ghi nhận
   ↓
Ngày 2-7: Theo dõi kết quả
   ↓
Ngày 8: Đánh giá → Rút bài học → Cập nhật mô hình
   ↓
Ngày 9+: Áp dụng cải tiến → Lặp lại
```

## 📈 KPIs theo dõi

1. **Accuracy:** % dự đoán đúng
2. **Sharpe Ratio:** Risk-adjusted return
3. **Max Drawdown:** Mức sụt giảm tối đa
4. **Win Rate:** Tỷ lệ giao dịch thắng
5. **ROI:** Lợi nhuận trên vốn đầu tư

## 🛠️ Tùy chỉnh cấu hình

Chỉnh sửa `engine/config.py`:
```python
# Cấu hình DCA
BASE_DCA_AMOUNT = 100  # $100 mỗi ngày
MAX_DRAWDOWN = 0.20    # 20% drawdown tối đa
KELLY_FRACTION = 0.5   # Half Kelly

# Cấu hình Risk
MAX_POSITION_SIZE = 0.25  # 25% vốn tối đa
MIN_CONFIDENCE = 0.5      # Confidence tối thiểu

# Cấu hình Signal
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
```

## 📝 Ví dụ sử dụng

### Chạy phân tích với dữ liệu thực
```python
from main import SolanaQuantFund

fund = SolanaQuantFund(initial_capital=10000)

# Lấy dữ liệu từ API
market_data = {
    "prices": [...],  # Từ Coingecko
    "rsi": 28,        # Tính từ prices
    "active_wallets": {...},  # Từ Solscan
    ...
}

# Chạy phân tích
result = fund.run_daily_analysis(market_data)

# Đánh giá hiệu suất sau 1 ngày
fund.evaluate_performance(actual_price_change=0.05, dca_amount=100)
```

## 🔗 Tích hợp với Solana

### Lấy dữ liệu on-chain
```python
from solders.rpc.requests import GetTokenSupply
from solders.rpc.async_api import AsyncClient

async def get_solana_metrics():
    client = AsyncClient("https://api.mainnet-beta.solana.com")
    # Lấy dữ liệu on-chain
    ...
```

### Thực thi giao dịch
```python
from solders.transaction import Transaction
from solders.system_program import transfer

# Tạo lệnh DCA
tx = Transaction()
# ... thêm instruction
# ... ký và gửi
```

## 📚 Tài liệu thêm

- [Solana RPC API](https://docs.solana.com/api)
- [Solscan API](https://solscan.io/api-docs)
- [Coingecko API](https://www.coingecko.com/en/api)
- [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)

## ⚠️ Disclaimer

Hệ thống này là công cụ hỗ trợ quyết định, không phải lời khuyên đầu tư. Luôn kiểm tra kỹ trước khi thực thi giao dịch thực.

## 🤝 Đóng góp

Nếu bạn có ý tưởng cải tiến, vui lòng:
1. Tạo issue mô tả ý tưởng
2. Fork repo
3. Tạo pull request

---

**Phiên bản:** 0.1.0 (MVP)  
**Cập nhật lần cuối:** 2026-04-12
