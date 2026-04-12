#!/usr/bin/env python3
"""
Demo: Real-time SOL Price Streaming
Kết nối Solana RPC và hiển thị giá SOL real-time
"""

import asyncio
import json
import time
from datetime import datetime
from engine.price_stream import SolanaPriceStream, PriceAggregator
from engine.market_data_manager import MarketDataManager

async def demo_price_stream():
    """Demo real-time price streaming"""
    print("🚀 Bắt đầu stream giá SOL real-time...")
    print("=" * 50)
    
    # Khởi tạo price stream
    price_stream = SolanaPriceStream()
    price_aggregator = PriceAggregator()
    market_manager = MarketDataManager()
    
    print("🔗 Kết nối tới Solana RPC...")
    print("📊 Đang lấy dữ liệu giá SOL real-time...")
    print("-" * 50)
    
    # Lấy giá hiện tại
    current_price = price_stream.get_current_price()
    print(f"💰 Giá SOL hiện tại: ${current_price.get('price', 0):.2f}")
    print(f"📊 Nguồn dữ liệu: {current_price.get('source', 'unknown')}")
    
    # Lấy giá từ nhiều nguồn
    print("\n📈 So sánh giá từ các sàn:")
    all_prices = price_aggregator.fetch_all_prices()
    for source, price in all_prices.items():
        if price:
            print(f"  {source.upper()}: ${price:.2f}")
    
    # Lấy giá trung bình
    avg_price = price_aggregator.get_average_price()
    print(f"\n📊 Giá trung bình: ${avg_price:.2f}")
    
    # Demo stream giá real-time (mô phỏng)
    print("\n🎯 Bắt đầu stream giá real-time (nhấn Ctrl+C để dừng)...")
    print("=" * 50)
    
    try:
        for i in range(10):  # Demo 10 lần cập nhật
            # Lấy giá mới
            current_price = price_stream.get_current_price()
            price = current_price.get('price', 0)
            
            # Lấy dữ liệu thị trường đầy đủ
            market_data = market_manager.get_realtime_market_data()
            
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
            print(f"💰 SOL/USD: ${price:.2f}")
            print(f"📊 Tín hiệu: {market_data.get('signals', {}).get('signal', 'N/A')}")
            print(f"📈 Score: {market_data.get('signals', {}).get('score', 0):.2f}")
            print(f"📊 Sentiment: {market_data.get('sentiment', {}).get('combined_sentiment', 0):.2f}")
            print("-" * 40)
            
            await asyncio.sleep(5)  # Cập nhật mỗi 5 giây
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Dừng stream...")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

async def demo_market_data():
    """Demo toàn bộ dữ liệu thị trường"""
    print("\n" + "="*50)
    print("📊 DEMO: Market Data Manager")
    print("="*50)
    
    manager = MarketDataManager()
    
    # Lấy dữ liệu thị trường đầy đủ
    print("\n🔄 Đang lấy dữ liệu thị trường...")
    market_data = manager.get_realtime_market_data()
    
    if market_data:
        print("✅ Dữ liệu thị trường:")
        print(f"  • Giá SOL: ${market_data.get('price', {}).get('average', 0):.2f}")
        print(f"  • Tín hiệu: {market_data.get('signals', {}).get('signal', 'N/A')}")
        print(f"  • Score: {market_data.get('signals', {}).get('score', 0):.2f}")
        print(f"  • Risk Environment: {market_data.get('macro', {}).get('risk_environment', 'N/A')}")
        print(f"  • Network Health: {market_data.get('onchain', {}).get('network_health', 'N/A')}")
        print(f"  • Sentiment: {market_data.get('sentiment', {}).get('combined_sentiment', 0):.2f}")
    else:
        print("❌ Không thể lấy dữ liệu thị trường")

async def main():
    """Chạy demo chính"""
    print("🚀 SOLANA REAL-TIME PRICE STREAMING DEMO")
    print("=" * 50)
    
    # Demo 1: Price Streaming
    print("\n1. 🎯 DEMO 1: Real-time Price Streaming")
    print("-" * 40)
    await demo_price_stream()
    
    # Demo 2: Market Data
    print("\n\n2. 📊 DEMO 2: Market Data Integration")
    print("-" * 40)
    await demo_market_data()
    
    print("\n" + "="*50)
    print("✅ Demo hoàn tất!")
    print("Các API endpoints đã được kích hoạt:")
    print("  • Real-time price streaming")
    print("  • Market data aggregation")
    print("  • On-chain data analysis")
    print("  • Sentiment analysis")
    print("  • Signal generation")
    print("\n🎯 Hệ thống sẵn sàng cho giao dịch real-time!")

if __name__ == "__main__":
    asyncio.run(main())