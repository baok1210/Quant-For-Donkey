"""
AI Brain - Multi-Provider LLM Integration with OAuth Support
Inspired by OpenClaw/ClawX OAuth implementation
"""
import os
import json
import secrets
import hashlib
import base64
import webbrowser
import http.server
import socketserver
import threading
import time
import requests
from typing import Dict, Optional, List
from urllib.parse import urlencode, parse_qs

from engine.custom_llm import CustomLLMManager, get_custom_llm_manager

class OAuthConfig:
    """OAuth configuration"""
    
    PROVIDER_CONFIGS = {
        "openai": {
            "name": "OpenAI (ChatGPT)",
            "auth_url": "https://auth.openai.com/oauth/authorize",
            "token_url": "https://auth.openai.com/oauth/token",
            "scopes": ["openid", "email", "profile"],
            "redirect_uri": "http://127.0.0.1:1455/callback"
        },
        "anthropic": {
            "name": "Anthropic (Claude)",
            "auth_url": "https://auth.anthropic.com/oauth/authorize",
            "token_url": "https://auth.anthropic.com/oauth/token",
            "scopes": ["openid", "email", "profile"],
            "redirect_uri": "http://127.0.0.1:1456/callback"
        },
        "google": {
            "name": "Google AI",
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "scopes": ["https://www.googleapis.com/auth/generative.language.tunner"],
            "redirect_uri": "http://127.0.0.1:1457/callback"
        }
    }
    
    @classmethod
    def get(cls, provider: str) -> Dict:
        return cls.PROVIDER_CONFIGS.get(provider, {})


class AIBrain:
    """
    Multi-provider AI Brain with OAuth and API Key support
    """
    
    # OpenRouter models - 300+ models from 50+ providers
    OPENROUTER_MODELS = [
        # Top tier (best performers)
        "openai/gpt-5.4", "openai/gpt-5.4-pro", "anthropic/claude-sonnet-4.6",
        "anthropic/claude-opus-4.6", "google/gemini-2.5-pro", "google/gemini-3.1-pro-preview",
        
        # Mid tier (best value)
        "openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-sonnet-4.5",
        "anthropic/claude-haiku-4.5", "google/gemini-2.5-flash", "google/gemini-3-flash-preview",
        
        # Budget tier
        "openai/gpt-4o-mini", "google/gemini-2.0-flash-lite", "google/gemini-3.1-flash-lite",
        "anthropic/claude-haiku-4", "meta-llama/llama-3.3-70b-instruct",
        
        # Free tier
        "deepseek/deepseek-r1", "qwen/qwen3-235b-a22b", "x-ai/grok-3-mini",
        
        # Specialized
        "mistralai/codestral-2508", "moonshotai/kimi-k2-thinking", "perplexity/sonar",
        "google/gemini-2.5-flash-lite", "nvidia/llama-3.1-nemotron-70b-instruct",
        
        # Chinese models
        "minimax/minimax-m2.5", "x-ai/grok-3", "deepseek/deepseek-v3.1",
    ]
    
    PROVIDERS = {
        "openai": {
            "name": "OpenAI (GPT)",
            "models": ["gpt-5.4", "gpt-5.4-pro", "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "api_key_env": "OPENAI_API_KEY",
            "oauth_client_id_env": "OPENAI_OAUTH_CLIENT_ID",
            "oauth_client_secret_env": "OPENAI_OAUTH_CLIENT_SECRET"
        },
        "anthropic": {
            "name": "Claude (Anthropic)",
            "models": ["claude-sonnet-4.6", "claude-opus-4.6", "claude-haiku-4.5"],
            "api_key_env": "ANTHROPIC_API_KEY",
            "oauth_client_id_env": "ANTHROPIC_OAUTH_CLIENT_ID",
            "oauth_client_secret_env": "ANTHROPIC_OAUTH_CLIENT_SECRET"
        },
        "google": {
            "name": "Google Gemini",
            "models": ["gemini-2.5-pro", "gemini-3.1-pro-preview", "gemini-2.5-flash", "gemini-3.1-flash-lite"],
            "api_key_env": "GEMINI_API_KEY",
            "oauth_client_id_env": "GOOGLE_OAUTH_CLIENT_ID",
            "oauth_client_secret_env": "GOOGLE_OAUTH_CLIENT_SECRET"
        },
        "openrouter": {
            "name": "OpenRouter (300+ models)",
            "models": OPENROUTER_MODELS,
            "api_key_env": "OPENROUTER_API_KEY",
            "endpoint": "https://openrouter.ai/api/v1/chat/completions"
        },
        "deepseek": {
            "name": "DeepSeek",
            "models": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
            "api_key_env": "DEEPSEEK_API_KEY"
        },
        "together": {
            "name": "Together AI",
            "models": ["Llama-3.3-70B", "Qwen-72B", "Mixtral-8x7B"],
            "api_key_env": "TOGETHER_API_KEY"
        },
        "groq": {
            "name": "Groq",
            "models": ["llama-3.3-70b", "mixtral-8x7b", "qwen-2.5-72b"],
            "api_key_env": "GROQ_API_KEY"
        },
        "qwen": {
            "name": "Qwen (Alibaba)",
            "models": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen3-235b-a22b"],
            "api_key_env": "QWEN_API_KEY"
        },
        "custom": {
            "name": "Custom LLM (my models)",
            "models": ["custom"],
            "is_custom_manager": True
        }
    }
    
    def __init__(self, 
                 provider: str = "openai", 
                 model: str = None,
                 api_key: str = None,
                 oauth_client_id: str = None,
                 oauth_client_secret: str = None,
                 custom_endpoint: str = None,
                 custom_model_name: str = None):
        
        self.provider = provider.lower()
        self.custom_endpoint = custom_endpoint
        self.custom_model_name = custom_model_name
        self.client = None
        
        # Handle custom provider - load from CustomLLMManager
        if self.provider == "custom":
            self._init_custom_custom(model, api_key)
            return
        
        config = self.PROVIDERS.get(self.provider, self.PROVIDERS["custom"])
        self.model = model or config["models"][0]
        
        # Priority: 1. OAuth (param), 2. API key (param), 3. Env vars
        if oauth_client_id:
            self.auth_type = "oauth"
            self.oauth_client_id = oauth_client_id
            self.oauth_client_secret = oauth_client_secret
            self.api_key = None
        elif api_key:
            self.auth_type = "api_key"
            self.api_key = api_key
        else:
            self.api_key = os.getenv(config.get("api_key_env", ""))
            self.oauth_client_id = os.getenv(config.get("oauth_client_id_env", ""))
            self.oauth_client_secret = os.getenv(config.get("oauth_client_secret_env", ""))
            
            if self.oauth_client_id:
                self.auth_type = "oauth"
            elif self.api_key:
                self.auth_type = "api_key"
            else:
                self.auth_type = None
        
        self.access_token = None
        self._init_client()
    
    def _init_custom_custom(self, model: str, api_key: str = None):
        """Init custom provider from CustomLLMManager"""
        manager = get_custom_llm_manager()
        
        # Get specific model or first one
        if model:
            config = manager.get_model(model)
        else:
            models = manager.list_models()
            config = manager.get_model(models[0]) if models else None
        
        if config:
            self.model = config.get("model_name", "custom")
            self.custom_endpoint = config.get("endpoint")
            self.api_key = api_key or config.get("api_key", "")
            self.custom_model_name = model or model
            manager.mark_used(model or "")
            
            from engine.custom_llm import CustomLLMClient
            self.client = CustomLLMClient(
                endpoint=self.custom_endpoint,
                api_key=self.api_key,
                model=self.model
            )
            self.auth_type = "api_key"
        else:
            self.auth_type = None
            self.client = None
    
    def _init_client(self):
        if self.provider == "openai" and self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except:
                self.client = None
        elif self.provider == "anthropic" and self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except:
                self.client = None
        elif self.provider == "google" and self.api_key:
            try:
                from google import genai
                genai.configure(api_key=self.api_key)
                self.client = genai
            except:
                self.client = None
        elif self.provider == "openrouter" and self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            except:
                self.client = None
        elif self.provider == "deepseek" and self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            except:
                self.client = None
        elif self.provider == "together" and self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.together.ai/v1"
                )
            except:
                self.client = None
        elif self.provider == "groq" and self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
            except:
                self.client = None
        else:
            self.client = None
    
    def get_oauth_url(self) -> str:
        """Get OAuth authorization URL"""
        if not self.oauth_client_id:
            raise ValueError("OAuth client ID not set")
        
        config = OAuthConfig.get(self.provider)
        if not config:
            raise ValueError(f"OAuth not supported for {self.provider}")
        
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        
        self._oauth_state = secrets.token_urlsafe(16)
        self._code_verifier = code_verifier
        
        params = {
            "client_id": self.oauth_client_id,
            "redirect_uri": config["redirect_uri"],
            "response_type": "code",
            "scope": " ".join(config.get("scopes", [])),
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": self._oauth_state
        }
        
        return f"{config['auth_url']}?{urlencode(params)}"
    
    def start_oauth_browser(self):
        """Open browser for OAuth login"""
        url = self.get_oauth_url()
        webbrowser.open(url)
        print(f"OAuth URL opened: {url}")
        print("After login, paste the callback URL here")
    
    def exchange_token(self, code: str) -> bool:
        """Exchange code for token"""
        config = OAuthConfig.get(self.provider)
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.oauth_client_id,
            "client_secret": self.oauth_client_secret,
            "code": code,
            "code_verifier": self._code_verifier,
            "redirect_uri": config.get("redirect_uri")
        }
        
        try:
            response = requests.post(
                config["token_url"],
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            result = response.json()
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                self.api_key = result["access_token"]
                self.auth_type = "oauth"
                self._init_client()
                return True
            return False
        except Exception as e:
            print(f"Token exchange error: {e}")
            return False
    
    def analyze_market(self, market_data: dict, investment_diary: str = "") -> dict:
        """Analyze market data"""
        # Handle custom provider
        if self.provider == "custom" and self.client:
            return self._call_custom(prompt)
        
        if not self.client and not self.api_key:
            return {
                "recommendation": "HOLD",
                "confidence": 0.5,
                "reasoning": "No provider configured"
            }
        
        prompt = self._build_prompt(market_data, investment_diary)
        
        if self.provider in ["openai", "openrouter", "deepseek", "together", "groq"]:
            return self._call_openai(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.provider == "google":
            return self._call_google(prompt)
        return {"recommendation": "HOLD", "confidence": 0.5, "error": "Provider not supported"}
    
    def _call_custom(self, prompt: str) -> dict:
        """Call custom LLM"""
        try:
            messages = [{"role": "user", "content": prompt}]
            resp = self.client.chat(messages)
            if "error" in resp:
                return {"recommendation": "HOLD", "confidence": 0.5, "error": resp["error"]}
            content = resp.get("content", "")
            try:
                return json.loads(content)
            except:
                return {"raw": content}
        except Exception as e:
            return {"recommendation": "HOLD", "confidence": 0.5, "error": str(e)}
    
    def _build_prompt(self, market_data: dict, diary: str) -> str:
        return f"""Phân tích và trả JSON:

 market_data: {json.dumps(market_data)}
 diary: {diary[:500]}

JSON: {{"recommendation": "BUY|HOLD|SELL", "confidence": 0.0-1.0, "reasoning": "...", "allocation": "100%|50%|25%|0%", "risk": "LOW|MED|HIGH"}}"""
    
    def _call_openai(self, prompt: str) -> dict:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            return {"recommendation": "HOLD", "confidence": 0.5, "error": str(e)}
    
    def _call_anthropic(self, prompt: str) -> dict:
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system="Trả JSON.",
                messages=[{"role": "user", "content": prompt}]
            )
            return {"raw": resp.content[0].text}
        except Exception as e:
            return {"recommendation": "HOLD", "confidence": 0.5, "error": str(e)}
    
    def _call_google(self, prompt: str) -> dict:
        try:
            model = self.client.GenerativeModel(self.model)
            resp = model.generate_content(prompt)
            text = resp.text
            start, end = text.find('{'), text.rfind('}')
            if start >= 0:
                return json.loads(text[start:end+1])
            return {"raw": text}
        except Exception as e:
            return {"recommendation": "HOLD", "confidence": 0.5, "error": str(e)}
    
    @staticmethod
    def list_providers() -> dict:
        return {k: v["name"] for k, v in AIBrain.PROVIDERS.items()}
    
    @staticmethod
    def list_custom_models() -> List[str]:
        """Danh sách custom models"""
        return get_custom_llm_manager().list_models()
    
    @staticmethod
    def add_custom_model(name: str, endpoint: str, api_key: str, model_name: str = "custom") -> bool:
        """Thêm custom model"""
        return get_custom_llm_manager().add_model(name, endpoint, api_key, model_name)
    
    @staticmethod
    def remove_custom_model(name: str) -> bool:
        """Xóa custom model"""
        return get_custom_llm_manager().remove_model(name)
    
    @staticmethod
    def check_configured() -> dict:
        """Check which providers are configured"""
        result = {}
        for p, c in AIBrain.PROVIDERS.items():
            if c.get("is_custom_manager"):
                custom_models = get_custom_llm_manager().list_models()
                result[p] = {"name": c["name"], "configured": len(custom_models) > 0, "models": custom_models}
            else:
                api_key = os.getenv(c.get("api_key_env", ""))
                oauth_id = os.getenv(c.get("oauth_client_id_env", ""))
                result[p] = {"name": c["name"], "api_key": bool(api_key), "oauth": bool(oauth_id)}
        return result