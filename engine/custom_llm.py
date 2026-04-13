"""
Custom LLM Provider Manager
Cho phép người dùng thêm custom OpenAI-compatible endpoints
"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime

class CustomLLMManager:
    """
    Quản lý custom LLM providers
    Lưu config vào file
    """
    
    DEFAULT_CONFIG_FILE = "config_custom_models.json"
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.models = self._load()
    
    def _load(self) -> Dict:
        """Load config từ file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"custom_models": {}}
    
    def _save(self):
        """Save config xuống file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.models, f, indent=2)
    
    def add_model(self, 
               name: str,
               endpoint: str,
               api_key: str,
               model_name: str = "custom",
               metadata: Dict = None) -> bool:
        """
        Thêm custom model
        
        Args:
            name: Tên hiển thị (vd: "My Local LLM")
            endpoint: API URL (vd: "http://localhost:1234/v1")
            api_key: API key (để trống nếu không cần)
            model_name: Tên model trên endpoint
            metadata: Thông tin thêm
        
        Returns:
            True nếu thành công
        """
        if not name or not endpoint:
            return False
        
        self.models["custom_models"][name] = {
            "endpoint": endpoint.rstrip('/'),
            "api_key": api_key,
            "model_name": model_name,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        self._save()
        return True
    
    def update_model(self, name: str, **kwargs) -> bool:
        """Update custom model"""
        if name not in self.models["custom_models"]:
            return False
        
        for key, value in kwargs.items():
            if key in ["endpoint", "api_key", "model_name", "metadata"]:
                self.models["custom_models"][name][key] = value
        
        self._save()
        return True
    
    def remove_model(self, name: str) -> bool:
        """Xóa custom model"""
        if name in self.models["custom_models"]:
            del self.models["custom_models"][name]
            self._save()
            return True
        return False
    
    def get_model(self, name: str) -> Optional[Dict]:
        """Lấy thông tin model"""
        return self.models["custom_models"].get(name)
    
    def list_models(self) -> List[str]:
        """Danh sách model names"""
        return list(self.models["custom_models"].keys())
    
    def mark_used(self, name: str):
        """Đánh dấu đã sử dụng"""
        if name in self.models["custom_models"]:
            self.models["custom_models"][name]["last_used"] = datetime.now().isoformat()
            self._save()
    
    def get_all_for_config(self) -> Dict:
        """Lấy tất cả config cho dropdown trong UI"""
        result = {}
        for name, config in self.models["custom_models"].items():
            result[name] = {
                "endpoint": config["endpoint"],
                "api_key": config["api_key"],
                "model_name": config["model_name"]
            }
        return result


class CustomLLMClient:
    """Client gọi custom LLM endpoint"""
    
    def __init__(self, endpoint: str, api_key: str = None, model: str = "custom"):
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.model = model
    
    def chat(self, messages: List[Dict], temperature: float = 0.3, max_tokens: int = 1000) -> Dict:
        """Gọi chat completion"""
        import requests
        
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            resp = requests.post(
                f"{self.endpoint}/chat/completions",
                json=data,
                headers=headers,
                timeout=60
            )
            
            if resp.status_code == 200:
                result = resp.json()
                return {
                    "content": result["choices"][0]["message"]["content"],
                    "raw": result
                }
            else:
                return {"error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    def models(self) -> List[Dict]:
        """Lấy danh sách models"""
        import requests
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            resp = requests.get(
                f"{self.endpoint}/models",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json().get("data", [])
            return []
        except:
            return []


# Singleton instance
_custom_llm_manager = None

def get_custom_llm_manager() -> CustomLLMManager:
    global _custom_llm_manager
    if _custom_llm_manager is None:
        _custom_llm_manager = CustomLLMManager()
    return _custom_llm_manager