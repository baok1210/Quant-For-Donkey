"""
On-chain Data - Lấy dữ liệu TVL, DEX Volume, Active Wallets từ Solana
"""
import requests
from typing import Dict
from datetime import datetime

class OnChainAnalyzer:
    """Phân tích dữ liệu on-chain Solana"""
    
    def __init__(self):
        self.defillama_api = "https://api.llama.fi"
        self.solscan_api = "https://public-api.solscan.io"
        
    def get_solana_tvl(self) -> Dict:
        """
        Lấy Total Value Locked (TVL) của Solana từ DefiLlama
        """
        try:
            url = f"{self.defillama_api}/tvl/solana"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                tvl = response.json()
                return {
                    "tvl_usd": tvl,
                    "source": "defillama",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"tvl_usd": 0, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"tvl_usd": 0, "error": str(e)}
    
    def get_dex_volume_24h(self) -> Dict:
        """
        Lấy khối lượng giao dịch DEX 24h trên Solana
        """
        try:
            # DefiLlama DEX API
            url = f"{self.defillama_api}/overview/dexs/solana"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                volume_24h = data.get("total24h", 0)
                
                return {
                    "dex_volume_24h": volume_24h,
                    "source": "defillama",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"dex_volume_24h": 0, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"dex_volume_24h": 0, "error": str(e)}
    
    def get_active_addresses(self) -> Dict:
        """
        Lấy số lượng địa chỉ hoạt động trên Solana
        """
        try:
            # Solscan API
            url = f"{self.solscan_api}/chaininfo"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "active_addresses": data.get("activeAddresses", 0),
                    "tps": data.get("currentTPS", 0),
                    "source": "solscan",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"active_addresses": 0, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"active_addresses": 0, "error": str(e)}
    
    def get_whale_movements(self, threshold_sol=10000) -> Dict:
        """
        Theo dõi giao dịch lớn (whale movements)
        """
        try:
            # Solscan API - Recent transactions
            url = f"{self.solscan_api}/transaction/last"
            params = {"limit": 50}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                transactions = response.json()
                
                whale_txs = []
                for tx in transactions:
                    amount = tx.get("lamport", 0) / 1e9  # Convert to SOL
                    if amount >= threshold_sol:
                        whale_txs.append({
                            "amount_sol": amount,
                            "signature": tx.get("txHash", ""),
                            "timestamp": tx.get("blockTime", 0)
                        })
                
                return {
                    "whale_count": len(whale_txs),
                    "total_whale_volume": sum(tx["amount_sol"] for tx in whale_txs),
                    "transactions": whale_txs[:10],  # Top 10
                    "source": "solscan"
                }
            else:
                return {"whale_count": 0, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"whale_count": 0, "error": str(e)}
    
    def get_network_health(self) -> Dict:
        """
        Đánh giá sức khỏe mạng Solana
        """
        try:
            url = f"{self.solscan_api}/chaininfo"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tps = data.get("currentTPS", 0)
                
                # Đánh giá health dựa trên TPS
                if tps > 2000:
                    health = "EXCELLENT"
                elif tps > 1000:
                    health = "GOOD"
                elif tps > 500:
                    health = "MODERATE"
                else:
                    health = "CONGESTED"
                
                return {
                    "health": health,
                    "tps": tps,
                    "block_height": data.get("blockHeight", 0),
                    "epoch": data.get("epoch", 0),
                    "source": "solscan"
                }
            else:
                return {"health": "UNKNOWN", "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"health": "UNKNOWN", "error": str(e)}
    
    def get_comprehensive_metrics(self) -> Dict:
        """
        Lấy tất cả metrics on-chain
        """
        tvl = self.get_solana_tvl()
        dex_volume = self.get_dex_volume_24h()
        active_addresses = self.get_active_addresses()
        whale_movements = self.get_whale_movements()
        network_health = self.get_network_health()
        
        return {
            "tvl": tvl,
            "dex_volume": dex_volume,
            "active_addresses": active_addresses,
            "whale_movements": whale_movements,
            "network_health": network_health,
            "timestamp": datetime.now().isoformat()
        }
