"""
Price Forecasting using Machine Learning (XGBoost) v4.3.1
Tích hợp: Auto-Retraining, Drift Detection, Model Versioning
"""
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class PriceForecaster:
    """
    Dự báo xu hướng giá Solana với Auto-Retraining và Drift Detection
    """
    
    def __init__(self, model_dir: str = "models/"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Model config
        self.model = None
        self.model_version = 0
        self.last_train_date = None
        self.retrain_interval_days = 7  # Retrain mỗi 7 ngày
        self.drift_threshold = 0.03     # Nếu sai số > 3% thì retrain ngay
        
        # History tracking
        self.prediction_history = []  # Lưu các lần dự báo để tính drift
        self.model_registry = []      # Lưu version history
        
        # Load model cũ nếu có
        self._load_latest_model()

    def _load_latest_model(self):
        """Load model mới nhất từ disk nếu tồn tại"""
        latest_path = os.path.join(self.model_dir, "latest_model.pkl")
        if os.path.exists(latest_path):
            try:
                with open(latest_path, 'rb') as f:
                    state = pickle.load(f)
                self.model = state['model']
                self.model_version = state['version']
                self.last_train_date = state.get('train_date')
                self.prediction_history = state.get('prediction_history', [])
                print(f"✅ Loaded model v{self.model_version} (trained: {self.last_train_date})")
            except Exception as e:
                print(f"⚠️ Failed to load model: {e}. Starting fresh.")
                self._init_fresh_model()
        else:
            self._init_fresh_model()

    def _init_fresh_model(self):
        """Khởi tạo model mới"""
        self.model = XGBRegressor(n_estimators=200, learning_rate=0.03, max_depth=6, 
                                   subsample=0.8, colsample_bytree=0.8, random_state=42)
        self.model_version = 0
        self.last_train_date = None

    def _save_model(self, df_train: pd.DataFrame = None):
        """Lưu model và metadata"""
        self.model_version += 1
        self.last_train_date = datetime.now()
        
        # Save current model
        state = {
            'model': self.model,
            'version': self.model_version,
            'train_date': self.last_train_date,
            'prediction_history': self.prediction_history[-100:]  # Giữ 100 lần gần nhất
        }
        
        latest_path = os.path.join(self.model_dir, "latest_model.pkl")
        with open(latest_path, 'wb') as f:
            pickle.dump(state, f)
        
        # Save versioned backup
        version_path = os.path.join(self.model_dir, f"model_v{self.model_version}.pkl")
        with open(version_path, 'wb') as f:
            pickle.dump(state, f)
        
        # Update registry
        registry_entry = {
            'version': self.model_version,
            'train_date': self.last_train_date.isoformat(),
            'train_samples': len(df_train) if df_train is not None else 0,
            'mape': self._calculate_recent_mape()
        }
        self.model_registry.append(registry_entry)
        
        # Save registry
        registry_path = os.path.join(self.model_dir, "model_registry.pkl")
        with open(registry_path, 'wb') as f:
            pickle.dump(self.model_registry, f)
        
        print(f"💾 Saved model v{self.model_version}")

    def _calculate_recent_mape(self) -> float:
        """Tính Mean Absolute Percentage Error từ các dự báo gần nhất"""
        if not self.prediction_history:
            return 0.0
        recent = self.prediction_history[-30:]  # 30 lần gần nhất
        errors = [abs(p['error_pct']) for p in recent if 'error_pct' in p]
        return np.mean(errors) if errors else 0.0

    def prepare_features(self, df: pd.DataFrame):
        """Tạo các đặc trưng (features) cho mô hình"""
        data = df.copy()
        data['returns'] = data['close'].pct_change()
        data['rsi'] = self._calculate_rsi(data['close'])
        data['vol_change'] = data['volume'].pct_change()
        data['macd'] = self._calculate_macd(data['close'])
        data['atr'] = self._calculate_atr(data)
        
        # Target: % change của nến tiếp theo (t+1)
        data['target'] = data['close'].pct_change().shift(-1)
        return data.dropna()

    def train_and_predict(self, df: pd.DataFrame, force_retrain: bool = False) -> Dict:
        """
        Huấn luyện và dự báo với Auto-Retraining
        """
        data = self.prepare_features(df)
        if len(data) < 50:
            return {"status": "INSUFFICIENT_DATA", "min_required": 50}
        
        # 1. Kiểm tra có cần retrain không
        needs_retrain = self._should_retrain(force_retrain)
        
        if needs_retrain['should_retrain']:
            print(f"🔄 Auto-Retraining triggered: {needs_retrain['reason']}")
            self._train_model(data)
        
        # 2. Predict
        X = data[['close', 'returns', 'rsi', 'vol_change', 'macd', 'atr']]
        last_features = X.tail(1)
        
        if self.model is None:
            return {"status": "MODEL_NOT_TRAINED"}
        
        prediction = self.model.predict(last_features)[0]
        current_price = df['close'].iloc[-1]
        expected_change = prediction  # Target là pct_change
        
        predicted_price = current_price * (1 + expected_change)
        
        # 3. Lưu vào history để track drift
        self.prediction_history.append({
            'timestamp': datetime.now().isoformat(),
            'predicted_change': expected_change,
            'actual_change': None,  # Sẽ được update sau khi có giá thực
            'model_version': self.model_version
        })
        
        return {
            "status": "OK",
            "predicted_price": float(predicted_price),
            "expected_change_pct": float(expected_change * 100),
            "model_version": self.model_version,
            "last_train_date": self.last_train_date.isoformat() if self.last_train_date else None,
            "recent_mape": self._calculate_recent_mape() * 100,
            "needs_retrain": needs_retrain['should_retrain']
        }

    def update_prediction_accuracy(self, actual_change: float):
        """Cập nhật kết quả thực tế cho dự báo gần nhất để tính drift"""
        if self.prediction_history:
            last_pred = self.prediction_history[-1]
            last_pred['actual_change'] = actual_change
            predicted = last_pred['predicted_change']
            error_pct = abs(actual_change - predicted) / (abs(actual_change) + 1e-8)
            last_pred['error_pct'] = error_pct

    def _should_retrain(self, force: bool = False) -> Dict:
        """Kiểm tra có cần retrain không"""
        if force:
            return {"should_retrain": True, "reason": "FORCE_RETRAIN"}
        
        # 1. Chưa train lần nào
        if self.last_train_date is None:
            return {"should_retrain": True, "reason": "FIRST_TRAIN"}
        
        # 2. Đã quá interval
        days_since_train = (datetime.now() - self.last_train_date).days
        if days_since_train >= self.retrain_interval_days:
            return {
                "should_retrain": True, 
                "reason": f"RETRAIN_INTERVAL ({days_since_train} days >= {self.retrain_interval_days})"
            }
        
        # 3. Drift Detection - Nếu sai số gần đây quá cao
        recent_mape = self._calculate_recent_mape()
        if recent_mape > self.drift_threshold:
            return {
                "should_retrain": True,
                "reason": f"DRIFT_DETECTED (MAPE: {recent_mape:.2%} > {self.drift_threshold:.2%})"
            }
        
        return {"should_retrain": False, "reason": "MODEL_UP_TO_DATE"}

    def _train_model(self, data: pd.DataFrame):
        """Train model trên toàn bộ dữ liệu"""
        X = data[['close', 'returns', 'rsi', 'vol_change', 'macd', 'atr']]
        y = data['target']
        
        # Train-test split để đánh giá
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        self.model.fit(X_train, y_train)
        
        # Đánh giá
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        
        print(f"📊 Model v{self.model_version + 1} - Train MAE: {train_mae:.4f}, Test MAE: {test_mae:.4f}")
        
        # Save
        self._save_model(data)

    def get_model_registry(self) -> list:
        """Lấy danh sách các version model"""
        registry_path = os.path.join(self.model_dir, "model_registry.pkl")
        if os.path.exists(registry_path):
            with open(registry_path, 'rb') as f:
                return pickle.load(f)
        return self.model_registry

    def rollback_model(self, version: int):
        """Rollback về version cũ"""
        version_path = os.path.join(self.model_dir, f"model_v{version}.pkl")
        if os.path.exists(version_path):
            with open(version_path, 'rb') as f:
                state = pickle.load(f)
            self.model = state['model']
            self.model_version = state['version']
            self.last_train_date = state.get('train_date')
            print(f"⏪ Rolled back to model v{version}")
            
            # Save as latest
            self._save_model()
        else:
            print(f"❌ Model v{version} not found")

    def _calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        return macd

    def _calculate_atr(self, df, period=14):
        high = df['high'] if 'high' in df.columns else df['close'] * 1.02
        low = df['low'] if 'low' in df.columns else df['close'] * 0.98
        prev_close = df['close'].shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
