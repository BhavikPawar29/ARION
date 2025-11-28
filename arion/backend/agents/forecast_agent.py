"""
Forecast Agent for ARION
Predicts short-term price movements using ML models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings

warnings.filterwarnings('ignore')


class ForecastAgent:
    """Predicts short-term market movements using machine learning"""
    
    def __init__(self, forecast_days: int = 5, model_type: str = 'linear'):
        """
        Initialize Forecast Agent
        
        Args:
            forecast_days: Number of days to forecast ahead
            model_type: Type of model to use ('linear' or 'random_forest')
        """
        self.forecast_days = forecast_days
        self.model_type = model_type
        self.last_analysis = {}
        
    def analyze(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate forecasts for all symbols
        
        Args:
            data: Dictionary mapping symbols to DataFrames with price data
            
        Returns:
            Dictionary containing forecast results
        """
        if not data:
            return self._empty_result()
        
        forecasts = {}
        trends = {}
        confidences = {}
        
        for symbol, df in data.items():
            if df.empty or len(df) < 30:
                continue
            
            try:
                # Prepare features
                features_df = self._prepare_features(df)
                
                if features_df.empty:
                    continue
                
                # Train model and predict
                prediction, confidence, trend = self._train_and_predict(features_df)
                
                forecasts[symbol] = {
                    'predicted_return': prediction,
                    'predicted_direction': 'UP' if prediction > 0 else 'DOWN' if prediction < 0 else 'FLAT',
                    'confidence': confidence,
                    'trend': trend
                }
                
                trends[symbol] = trend
                confidences[symbol] = confidence
                
            except Exception as e:
                print(f"Error forecasting {symbol}: {str(e)}")
                continue
        
        # Calculate overall market sentiment
        if forecasts:
            avg_prediction = np.mean([f['predicted_return'] for f in forecasts.values()])
            bullish_count = sum(1 for f in forecasts.values() if f['predicted_direction'] == 'UP')
            bearish_count = sum(1 for f in forecasts.values() if f['predicted_direction'] == 'DOWN')
            
            if bullish_count > bearish_count:
                market_sentiment = 'BULLISH'
            elif bearish_count > bullish_count:
                market_sentiment = 'BEARISH'
            else:
                market_sentiment = 'NEUTRAL'
        else:
            avg_prediction = 0
            market_sentiment = 'UNKNOWN'
        
        self.last_analysis = {
            'forecasts': forecasts,
            'market_sentiment': market_sentiment,
            'average_prediction': avg_prediction,
            'confidence': np.mean(list(confidences.values())) if confidences else 0.0
        }
        
        return self.last_analysis
    
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML model"""
        features_df = df.copy()
        
        # Technical indicators
        features_df['SMA_5'] = features_df['Close'].rolling(window=5).mean()
        features_df['SMA_10'] = features_df['Close'].rolling(window=10).mean()
        features_df['SMA_20'] = features_df['Close'].rolling(window=20).mean()
        
        # Price momentum
        features_df['Momentum_5'] = features_df['Close'].pct_change(5)
        features_df['Momentum_10'] = features_df['Close'].pct_change(10)
        
        # Volatility
        features_df['Vol_5'] = features_df['Returns'].rolling(window=5).std()
        features_df['Vol_20'] = features_df['Returns'].rolling(window=20).std()
        
        # Volume indicators
        features_df['Volume_SMA'] = features_df['Volume'].rolling(window=20).mean()
        features_df['Volume_Ratio'] = features_df['Volume'] / features_df['Volume_SMA']
        
        # RSI-like indicator
        delta = features_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, 1)
        features_df['RSI'] = 100 - (100 / (1 + rs))
        
        # Target: next day return
        features_df['Target'] = features_df['Close'].pct_change().shift(-1)
        
        # Drop NaN values
        features_df = features_df.dropna()
        
        return features_df
    
    def _train_and_predict(self, features_df: pd.DataFrame) -> Tuple[float, float, str]:
        """Train model and make prediction"""
        # Feature columns
        feature_cols = ['SMA_5', 'SMA_10', 'SMA_20', 'Momentum_5', 'Momentum_10', 
                       'Vol_5', 'Vol_20', 'Volume_Ratio', 'RSI']
        
        # Prepare training data
        X = features_df[feature_cols].iloc[:-5]  # Exclude last 5 days for validation
        y = features_df['Target'].iloc[:-5]
        
        # Prepare prediction data (most recent)
        X_pred = features_df[feature_cols].iloc[-1:].values
        
        # Train model
        if self.model_type == 'random_forest':
            model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
        else:
            model = LinearRegression()
        
        model.fit(X, y)
        
        # Make prediction
        prediction = model.predict(X_pred)[0]
        
        # Calculate confidence based on recent accuracy
        if len(features_df) > 10:
            X_recent = features_df[feature_cols].iloc[-10:-1]
            y_recent = features_df['Target'].iloc[-10:-1]
            recent_pred = model.predict(X_recent)
            
            # Direction accuracy
            correct_direction = sum((recent_pred > 0) == (y_recent > 0))
            confidence = correct_direction / len(y_recent)
        else:
            confidence = 0.5
        
        # Determine trend
        sma_5 = features_df['SMA_5'].iloc[-1]
        sma_20 = features_df['SMA_20'].iloc[-1]
        
        if sma_5 > sma_20 * 1.02:
            trend = 'UPTREND'
        elif sma_5 < sma_20 * 0.98:
            trend = 'DOWNTREND'
        else:
            trend = 'SIDEWAYS'
        
        return prediction, confidence, trend
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'forecasts': {},
            'market_sentiment': 'UNKNOWN',
            'average_prediction': 0,
            'confidence': 0.0
        }
    
    def return_signal(self) -> str:
        """Return simple signal based on last analysis"""
        if not self.last_analysis:
            return "NO_DATA"
        
        sentiment = self.last_analysis.get('market_sentiment', 'UNKNOWN')
        
        if sentiment == 'BULLISH':
            return "BULLISH"
        elif sentiment == 'BEARISH':
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def return_confidence(self) -> float:
        """Return confidence in last analysis"""
        return self.last_analysis.get('confidence', 0.0)


if __name__ == "__main__":
    # Test the forecast agent
    import sys
    sys.path.append('..')
    from utils.fetch_data import DataFetcher
    
    fetcher = DataFetcher()
    data = fetcher.fetch_stock_data(['AAPL', 'MSFT', 'GOOGL'], period='3mo')
    
    agent = ForecastAgent()
    result = agent.analyze(data)
    
    print("Forecast Results:")
    print(f"Market Sentiment: {result['market_sentiment']}")
    print(f"Signal: {agent.return_signal()}")
    print(f"Confidence: {agent.return_confidence():.2%}")
    print("\nIndividual Forecasts:")
    for symbol, forecast in result['forecasts'].items():
        print(f"  {symbol}: {forecast['predicted_direction']} ({forecast['predicted_return']:.2%}) - {forecast['trend']}")
