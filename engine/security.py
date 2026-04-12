"""
Security Utils - Mã hóa và bảo mật API keys
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityManager:
    """Quản lý bảo mật API keys và thông tin nhạy cảm"""
    
    def __init__(self, password=None):
        self.password = password or os.getenv("SECURITY_PASSWORD", "default_password")
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)
    
    def _derive_key(self):
        """Derive encryption key from password"""
        salt = b'solana_dca_ai_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
    
    def encrypt(self, text):
        """Mã hóa text"""
        return self.fernet.encrypt(text.encode()).decode()
    
    def decrypt(self, encrypted_text):
        """Giải mã text"""
        return self.fernet.decrypt(encrypted_text.encode()).decode()
    
    def save_config_securely(self, config_data, filename="config_settings.json"):
        """Lưu config với API keys đã mã hóa"""
        encrypted_config = {}
        sensitive_keys = ["OPENAI_API_KEY", "GEMINI_API_KEY", "BINANCE_API_KEY", "OKX_API_KEY"]
        
        for key, value in config_data.items():
            if key in sensitive_keys and value:
                encrypted_config[key] = self.encrypt(value)
            else:
                encrypted_config[key] = value
        
        with open(filename, "w") as f:
            import json
            json.dump(encrypted_config, f, indent=4)
    
    def load_config_securely(self, filename="config_settings.json"):
        """Load config và giải mã API keys"""
        import json
        if not os.path.exists(filename):
            return {}
        
        with open(filename, "r") as f:
            encrypted_config = json.load(f)
        
        config_data = {}
        sensitive_keys = ["OPENAI_API_KEY", "GEMINI_API_KEY", "BINANCE_API_KEY", "OKX_API_KEY"]
        
        for key, value in encrypted_config.items():
            if key in sensitive_keys and value:
                try:
                    config_data[key] = self.decrypt(value)
                except:
                    config_data[key] = value  # Nếu không giải mã được, giữ nguyên
            else:
                config_data[key] = value
        
        return config_data
