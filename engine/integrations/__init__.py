"""
QFD Integrations Module
====================
Merged features from:
- VectorBT: High-performance vectorized backtesting
- Freqtrade: Strategy framework, Hyperopt, Edge
- Hummingbot: Execution connectors, Market Making
- vn.py: Vietnam market data
"""
from engine.integrations.vectorbt_engine import VectorBTEngine
from engine.integrations.freqtrade_integration import (
    FreqtradeStrategy,
    FreqtradeHyperopt,
    FreqtradeEdge,
    FreqtradeBacktest
)
from engine.integrations.hummingbot_integration import (
    HummingbotConnector,
    PureMarketMaking,
    CrossExchangeMM,
    InventorySkew
)
from engine.integrations.vnpy_integration import (
    VietnamMarketData,
    VnStockData,
    IPSDataProvider,
    MarketIndex
)

__all__ = [
    # VectorBT
    "VectorBTEngine",
    
    # Freqtrade
    "FreqtradeStrategy",
    "FreqtradeHyperopt",
    "FreqtradeEdge",
    "FreqtradeBacktest",
    
    # Hummingbot
    "HummingbotConnector",
    "PureMarketMaking",
    "CrossExchangeMM",
    "InventorySkew",
    
    # vn.py
    "VietnamMarketData",
    "VnStockData",
    "IPSDataProvider",
    "MarketIndex",
]

__version__ = "4.4.0"
__integrations__ = [
    "vectorbt",
    "freqtrade", 
    "hummingbot",
    "vnpy"
]