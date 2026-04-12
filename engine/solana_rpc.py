"""
Solana RPC Client - Kết nối với Helius/QuickNode cho dữ liệu on-chain
"""
import os
import json
import requests
from typing import Dict, List, Optional

class SolanaRPC:
    """Client kết nối Solana RPC với hỗ trợ nhiều provider"""
    
    def __init__(self):
        self.helius_key = os.getenv("HELUS_API_KEY")
        self.quicknode_key = os.getenv("QUICKNODE_API_KEY")
        
        # Dùng Helius nếu có, nếu không dùng QuickNode
        if self.helius_key:
            self.endpoint = f"https://mainnet.helius-rpc.com/?api-key={self.helius_key}"
        elif self.quicknode_key:
            self.endpoint = f"https://{self.quicknode_key}.quiknode.pro/"
        else:
            raise ValueError("Không tìm thấy API key cho Helius hoặc QuickNode")
            
    def get_account_info(self, pubkey: str) -> Dict:
        """Lấy thông tin tài khoản"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [pubkey, {"encoding": "jsonParsed"}]
        }
        
        response = requests.post(self.endpoint, json=payload, timeout=10)
        return response.json()
    
    def get_block_production(self) -> Dict:
        """Lấy thông tin sản xuất block"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBlockProduction",
            "params": []
        }
        
        response = requests.post(self.endpoint, json=payload, timeout=10)
        return response.json()
    
    def get_recent_performance_samples(self) -> Dict:
        """Lấy mẫu hiệu suất gần đây (TPS, slot time, etc)"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getRecentPerformanceSamples",
            "params": [5]  # Lấy 5 mẫu gần nhất
        }
        
        response = requests.post(self.endpoint, json=payload, timeout=10)
        return response.json()
    
    def get_transaction(self, signature: str) -> Dict:
        """Lấy thông tin giao dịch"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
        }
        
        response = requests.post(self.endpoint, json=payload, timeout=10)
        return response.json()
    
    def get_supply(self) -> Dict:
        """Lấy thông tin cung cấp SOL"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSupply",
            "params": [{"excludeNonCirculatingAccountsList": True}]
        }
        
        response = requests.post(self.endpoint, json=payload, timeout=10)
        return response.json()
    
    def get_priority_fee_estimate(self) -> float:
        """
        Ước tính phí ưu tiên trung bình từ các giao dịch gần đây
        """
        # Lấy mẫu hiệu suất gần đây để ước tính phí
        perf_samples = self.get_recent_performance_samples()
        
        if 'result' in perf_samples and 'value' in perf_samples['result']:
            samples = perf_samples['result']['value']
            if samples:
                # Tính trung bình thời gian slot (ước lượng phí)
                avg_slot_time = sum(s.get('slotTime', 0) for s in samples) / len(samples)
                # Chuyển đổi thành phí ưu tiên (giả định mối quan hệ ngược)
                estimated_fee = max(0.000005, 0.001 / (avg_slot_time + 1))  # Giả định
                return estimated_fee
                
        return 0.000005  # Phí mặc định thấp
