import ccxt
import os

class ExchangeConnector:
    """Kết nối Binance/OKX để lấy dữ liệu thực tế cho AI Online"""
    
    def __init__(self, exchange_id="binance"):
        self.exchange_id = exchange_id
        # Dùng thông tin từ .env
        apiKey = os.getenv(f"{exchange_id.upper()}_API_KEY")
        secret = os.getenv(f"{exchange_id.upper()}_SECRET_KEY")
        
        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': apiKey,
            'secret': secret,
            'enableRateLimit': True,
        })

    def get_realtime_data(self, symbol="SOL/USDT"):
        """Lấy dữ liệu nến, orderbook thực tế"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=24)
            orderbook = self.exchange.fetch_order_book(symbol)
            
            return {
                "price": ticker['last'],
                "change_24h": ticker['percentage'],
                "volume": ticker['quoteVolume'],
                "ohlcv": ohlcv,
                "bids": orderbook['bids'][:5],
                "asks": orderbook['asks'][:5]
            }
        except Exception as e:
            return {"error": str(e)}

    def execute_trade(self, symbol, side, amount):
        """Thực thi lệnh thật trên sàn"""
        # return self.exchange.create_order(symbol, 'market', side, amount)
        return f"Simulated {side} order for {amount} {symbol} on {self.exchange_id}"
