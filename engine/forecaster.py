"""
Price Forecasting using Machine Learning (XGBoost)
"""
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

class PriceForecaster:
    """Dự báo xu hướng giá Solana trong 24h tới"""
    
    def __init__(self):
        self.model = XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=5)

    def prepare_features(self, df: pd.DataFrame):
        """Tạo các đặc trưng (features) cho mô hình"""
        data = df.copy()
        data['returns'] = data['close'].pct_change()
        data['rsi'] = self._calculate_rsi(data['close'])
        data['vol_change'] = data['volume'].pct_change()
        
        # Target: Giá đóng cửa của nến tiếp theo (t+1)
        data['target'] = data['close'].shift(-1)
        return data.dropna()

    def train_and_predict(self, df: pd.DataFrame):
        """Huấn luyện và dự báo nến tiếp theo"""
        data = self.prepare_features(df)
        if len(data) < 50: return None
        
        X = data[['close', 'returns', 'rsi', 'vol_change']]
        y = data['target']
        
        # Train model
        self.model.fit(X[:-1], y[:-1]) # Train trên dữ liệu cũ
        
        # Predict nến tiếp theo
        last_features = X.tail(1)
        prediction = self.model.predict(last_features)[0]
        
        current_price = df['close'].iloc[-1]
        expected_change = (prediction - current_price) / current_price
        
        return {
            "predicted_price": float(prediction),
            "expected_change_pct": float(expected_change),
            "confidence_score": 0.85 # Mock confidence
        }

    def _calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
