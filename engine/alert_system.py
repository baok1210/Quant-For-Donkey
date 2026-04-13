"""
Real-time Alert System (v4.3.2)
Gửi cảnh báo qua Telegram, Discord khi có sự kiện quan trọng
"""
import requests
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

class AlertLevel(Enum):
    """Mức độ cảnh báo"""
    INFO = "ℹ️"
    SUCCESS = "✅"
    WARNING = "⚠️"
    CRITICAL = "🚨"

class AlertSystem:
    """Hệ thống cảnh báo thời gian thực"""
    
    def __init__(self, telegram_token: str = None, telegram_chat_id: str = None,
                 discord_webhook: str = None):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.discord_webhook = discord_webhook
        self.alert_history = []

    def send_alert(self, title: str, message: str, level: AlertLevel = AlertLevel.INFO,
                   channels: list = None) -> Dict:
        """
        Gửi cảnh báo đến các kênh được chỉ định
        channels: ["telegram", "discord"] hoặc None (gửi tất cả)
        """
        if channels is None:
            channels = []
            if self.telegram_token and self.telegram_chat_id:
                channels.append("telegram")
            if self.discord_webhook:
                channels.append("discord")
        
        results = {}
        timestamp = datetime.now().isoformat()
        
        # Lưu vào history
        self.alert_history.append({
            "timestamp": timestamp,
            "title": title,
            "message": message,
            "level": level.name,
            "channels": channels
        })
        
        # Gửi Telegram
        if "telegram" in channels and self.telegram_token and self.telegram_chat_id:
            results["telegram"] = self._send_telegram(title, message, level)
        
        # Gửi Discord
        if "discord" in channels and self.discord_webhook:
            results["discord"] = self._send_discord(title, message, level)
        
        return {
            "status": "sent",
            "timestamp": timestamp,
            "results": results
        }

    def _send_telegram(self, title: str, message: str, level: AlertLevel) -> Dict:
        """Gửi cảnh báo qua Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            text = f"{level.value} **{title}**\n\n{message}\n\n__{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}__"
            
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            resp = requests.post(url, json=payload, timeout=5)
            return {
                "status": "success" if resp.status_code == 200 else "failed",
                "code": resp.status_code
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _send_discord(self, title: str, message: str, level: AlertLevel) -> Dict:
        """Gửi cảnh báo qua Discord"""
        try:
            embed = {
                "title": f"{level.value} {title}",
                "description": message,
                "color": self._get_color_code(level),
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "Quant for Donkey Alert System"}
            }
            
            payload = {"embeds": [embed]}
            resp = requests.post(self.discord_webhook, json=payload, timeout=5)
            
            return {
                "status": "success" if resp.status_code == 204 else "failed",
                "code": resp.status_code
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_color_code(self, level: AlertLevel) -> int:
        """Lấy mã màu cho Discord embed"""
        colors = {
            AlertLevel.INFO: 3447003,      # Blue
            AlertLevel.SUCCESS: 3066993,   # Green
            AlertLevel.WARNING: 15105570,  # Orange
            AlertLevel.CRITICAL: 15158332  # Red
        }
        return colors.get(level, 3447003)

    def alert_liquidation_cascade(self, symbol: str, intensity: float, zones: list):
        """Cảnh báo khi phát hiện Liquidation Cascade"""
        message = f"""
**Symbol:** {symbol}
**Intensity:** {intensity:.1f}x normal
**Zones Affected:** {len(zones)} zones
**Action:** ⚠️ REDUCE POSITION or HOLD

Liquidation cascade detected! Consider reducing exposure.
"""
        return self.send_alert(
            title=f"🌊 Liquidation Cascade - {symbol}",
            message=message,
            level=AlertLevel.CRITICAL
        )

    def alert_order_flow_signal(self, symbol: str, signal: str, confidence: float):
        """Cảnh báo khi Order Flow phát hiện tín hiệu mạnh"""
        level = AlertLevel.WARNING if signal == "BEARISH" else AlertLevel.SUCCESS
        message = f"""
**Symbol:** {symbol}
**Signal:** {signal}
**Confidence:** {confidence:.1%}

Order Flow analysis detected a strong {signal} signal.
"""
        return self.send_alert(
            title=f"🌊 Order Flow Signal - {signal}",
            message=message,
            level=level
        )

    def alert_model_retrain(self, model_version: int, reason: str, mape: float):
        """Cảnh báo khi XGBoost model được retrain"""
        message = f"""
**Model Version:** v{model_version}
**Reason:** {reason}
**Recent MAPE:** {mape:.2%}

Price forecasting model has been retrained with latest data.
"""
        return self.send_alert(
            title=f"🤖 Model Retrained - v{model_version}",
            message=message,
            level=AlertLevel.INFO
        )

    def alert_portfolio_rebalance(self, trades: list, total_value: float):
        """Cảnh báo khi Portfolio được rebalance"""
        trades_str = "\n".join([f"  • {t['action']} {t['amount']:.2f} {t['asset']} (${t['value_usd']:.2f})" 
                               for t in trades[:5]])
        
        message = f"""
**Total Portfolio Value:** ${total_value:,.2f}
**Trades Executed:** {len(trades)}

{trades_str}
{"..." if len(trades) > 5 else ""}

Portfolio rebalanced to target weights.
"""
        return self.send_alert(
            title=f"📊 Portfolio Rebalanced",
            message=message,
            level=AlertLevel.SUCCESS
        )

    def alert_dca_opportunity(self, symbol: str, timing_score: float, reasons: list):
        """Cảnh báo khi có cơ hội DCA tốt"""
        reasons_str = "\n".join([f"  ✓ {r}" for r in reasons])
        
        message = f"""
**Symbol:** {symbol}
**Timing Score:** {timing_score:.2f}
**Reasons:**
{reasons_str}

Excellent DCA opportunity detected!
"""
        return self.send_alert(
            title=f"💰 DCA Opportunity - {symbol}",
            message=message,
            level=AlertLevel.SUCCESS
        )

    def alert_risk_limit_breach(self, limit_type: str, current: float, limit: float):
        """Cảnh báo khi vượt quá giới hạn rủi ro"""
        message = f"""
**Limit Type:** {limit_type}
**Current:** {current:.2%}
**Limit:** {limit:.2%}

Risk limit has been breached! Trading is temporarily disabled.
"""
        return self.send_alert(
            title=f"🛑 Risk Limit Breached",
            message=message,
            level=AlertLevel.CRITICAL
        )

    def get_alert_history(self, limit: int = 50) -> list:
        """Lấy lịch sử cảnh báo"""
        return self.alert_history[-limit:]
