import json
import datetime
import os

class ReflectionEngine:
    """
    Bộ máy Tự phản biện cho Solana Quant Fund.
    Chịu trách nhiệm ghi lại quyết định, đánh giá kết quả và rút ra bài học.
    """
    def __init__(self, memory_dir="memory"):
        self.memory_dir = memory_dir
        self.diary_path = os.path.join(memory_dir, "INVESTMENT_DIARY.md")
        self.lessons_path = os.path.join(memory_dir, "LESSONS_LEARNED.md")
        
    def log_decision(self, decision, reason, amount, risk_assessment, data_sources):
        """Ghi lại quyết định DCA vào nhật ký"""
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = f"""
## Ngày: {date_str}
### Quyết định: {decision}
- **Lý do:** {reason}
- **Số tiền:** {amount}
- **Rủi ro:** {risk_assessment}
- **Dữ liệu sử dụng:** {data_sources}
- **Đánh giá sau 1 tuần:**
  - [ ] Hiệu quả: (Chưa đánh giá)
  - [ ] Sai sót: (Chưa đánh giá)
  - [ ] Cải tiến: (Chưa đánh giá)
"""
        with open(self.diary_path, "a", encoding="utf-8") as f:
            f.write(entry)
            
        return "Đã ghi nhận quyết định vào INVESTMENT_DIARY.md"

    def review_decision(self, date_str, outcome, mistakes, improvements):
        """Đánh giá lại quyết định sau một thời gian"""
        # Logic để cập nhật file MD (trong thực tế sẽ phức tạp hơn)
        # Tạm thời chỉ ghi thêm vào cuối file
        review = f"\n### Đánh giá cho quyết định ngày {date_str}\n- Hiệu quả: {outcome}\n- Sai sót: {mistakes}\n- Cải tiến: {improvements}\n"
        with open(self.diary_path, "a", encoding="utf-8") as f:
            f.write(review)
            
        # Tự động ghi vào bài học nếu có sai sót
        if mistakes:
            self._add_lesson(mistakes, improvements)
            
        return "Đã cập nhật đánh giá."

    def propose_improvements(self):
        """Phân tích nhật ký để đề xuất cải tiến kỹ thuật"""
        if not os.path.exists(self.lessons_path):
            return "Chưa có đủ dữ liệu để đề xuất."
            
        with open(self.lessons_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # AI logic phân tích keyword từ các bài học cũ
        proposals = []
        if "phí mạng" in content.lower():
            proposals.append("Tích hợp 'Jito Priority Fee' vào trọng số quyết định DCA (Ưu tiên: Cao)")
        if "sentiment" in content.lower():
            proposals.append("Sử dụng 'Twitter API v2' thay cho bộ lọc sentiment cơ bản (Ưu tiên: Trung bình)")
        if "rsi" in content.lower():
            proposals.append("Thêm chỉ báo 'Stochastic RSI' để bắt đáy chính xác hơn trong khung 4H (Ưu tiên: Cao)")
            
        return proposals

    def _add_lesson(self, situation, action_item):
        """Ghi nhận bài học mới"""
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        lesson_count = self._get_lesson_count() + 1
        
        entry = f"""
## {lesson_count}. Rút kinh nghiệm ({date_str})
- **Tình huống:** {situation}
- **Bài học & Cải tiến:** {action_item}
"""
        with open(self.lessons_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def _get_lesson_count(self):
        try:
            with open(self.lessons_path, "r", encoding="utf-8") as f:
                content = f.read()
                return content.count("##")
        except FileNotFoundError:
            return 0

# Test
if __name__ == "__main__":
    engine = ReflectionEngine("../memory")
    # engine.log_decision("Mua 10 SOL", "Giá giảm 15% trong 24h", "$1500", "Bắt dao rơi", "Coingecko, Binance")
