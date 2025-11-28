"""
Risk Agent for ARION
Analyzes volatility, drawdowns, and risk spikes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class RiskAgent:
    """Detects and analyzes market risk through volatility and drawdown analysis"""
    
    def __init__(self, volatility_threshold: float = 0.3, drawdown_threshold: float = -0.15):
        """
        Initialize Risk Agent
        
        Args:
            volatility_threshold: Threshold for high volatility alert (annualized)
            drawdown_threshold: Threshold for significant drawdown alert
        """
        self.volatility_threshold = volatility_threshold
        self.drawdown_threshold = drawdown_threshold
        self.last_analysis = {}
        
    def analyze(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Analyze risk across portfolio
        
        Args:
            data: Dictionary mapping symbols to DataFrames with price data
            
        Returns:
            Dictionary containing risk analysis results
        """
        if not data:
            return self._empty_result()
        
        risk_scores = {}
        volatility_data = {}
        drawdown_data = {}
        alerts = []
        
        for symbol, df in data.items():
            if df.empty or 'Returns' not in df.columns:
                continue
                
            # Calculate current volatility
            recent_returns = df['Returns'].dropna().tail(20)
            if len(recent_returns) < 5:
                continue
                
            current_vol = recent_returns.std() * np.sqrt(252)
            volatility_data[symbol] = current_vol
            
            # Calculate current drawdown
            current_dd = df['Drawdown'].iloc[-1] if 'Drawdown' in df.columns else 0
            drawdown_data[symbol] = current_dd
            
            # Risk scoring (0-100)
            vol_score = min(100, (current_vol / self.volatility_threshold) * 50)
            dd_score = min(100, abs(current_dd / self.drawdown_threshold) * 50)
            risk_score = (vol_score + dd_score) / 2
            
            risk_scores[symbol] = risk_score
            
            # Generate alerts
            if current_vol > self.volatility_threshold:
                alerts.append({
                    'symbol': symbol,
                    'type': 'HIGH_VOLATILITY',
                    'severity': 'HIGH' if current_vol > self.volatility_threshold * 1.5 else 'MEDIUM',
                    'message': f'{symbol}: High volatility detected ({current_vol:.2%})',
                    'value': current_vol
                })
                
            if current_dd < self.drawdown_threshold:
                alerts.append({
                    'symbol': symbol,
                    'type': 'SIGNIFICANT_DRAWDOWN',
                    'severity': 'HIGH' if current_dd < self.drawdown_threshold * 1.5 else 'MEDIUM',
                    'message': f'{symbol}: Significant drawdown ({current_dd:.2%})',
                    'value': current_dd
                })
            
            # Detect volatility spikes (recent vol > historical average)
            if len(df) > 60:
                historical_vol = df['Returns'].iloc[:-20].std() * np.sqrt(252)
                if current_vol > historical_vol * 1.5:
                    alerts.append({
                        'symbol': symbol,
                        'type': 'VOLATILITY_SPIKE',
                        'severity': 'MEDIUM',
                        'message': f'{symbol}: Volatility spike detected (current: {current_vol:.2%} vs avg: {historical_vol:.2%})',
                        'value': current_vol / historical_vol
                    })
        
        # Calculate overall portfolio risk
        avg_risk_score = np.mean(list(risk_scores.values())) if risk_scores else 0
        max_risk_score = max(risk_scores.values()) if risk_scores else 0
        
        # Determine risk level
        risk_level = self._get_risk_level(avg_risk_score)
        
        self.last_analysis = {
            'overall_risk_score': avg_risk_score,
            'max_risk_score': max_risk_score,
            'risk_level': risk_level,
            'individual_scores': risk_scores,
            'volatility': volatility_data,
            'drawdowns': drawdown_data,
            'alerts': alerts,
            'confidence': self._calculate_confidence(data)
        }
        
        return self.last_analysis
    
    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to risk level"""
        if score < 20:
            return 'LOW'
        elif score < 50:
            return 'MEDIUM'
        elif score < 80:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _calculate_confidence(self, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate confidence in analysis based on data quality"""
        if not data:
            return 0.0
        
        # Confidence based on data availability and length
        total_points = 0
        valid_points = 0
        
        for df in data.values():
            total_points += 1
            if len(df) >= 60:  # At least 60 days of data
                valid_points += 1
            elif len(df) >= 20:  # At least 20 days
                valid_points += 0.5
        
        return valid_points / total_points if total_points > 0 else 0.0
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'overall_risk_score': 0,
            'max_risk_score': 0,
            'risk_level': 'UNKNOWN',
            'individual_scores': {},
            'volatility': {},
            'drawdowns': {},
            'alerts': [],
            'confidence': 0.0
        }
    
    def return_signal(self) -> str:
        """Return simple signal based on last analysis"""
        if not self.last_analysis:
            return "NO_DATA"
        
        risk_level = self.last_analysis.get('risk_level', 'UNKNOWN')
        
        if risk_level == 'CRITICAL':
            return "DANGER"
        elif risk_level == 'HIGH':
            return "CAUTION"
        elif risk_level == 'MEDIUM':
            return "WATCH"
        else:
            return "STABLE"
    
    def return_confidence(self) -> float:
        """Return confidence in last analysis"""
        return self.last_analysis.get('confidence', 0.0)


if __name__ == "__main__":
    # Test the risk agent
    import sys
    sys.path.append('..')
    from utils.fetch_data import DataFetcher
    
    fetcher = DataFetcher()
    data = fetcher.fetch_stock_data(['AAPL', 'TSLA', 'NVDA'], period='3mo')
    
    agent = RiskAgent()
    result = agent.analyze(data)
    
    print("Risk Analysis Results:")
    print(f"Overall Risk Score: {result['overall_risk_score']:.2f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Signal: {agent.return_signal()}")
    print(f"Confidence: {agent.return_confidence():.2%}")
    print(f"\nAlerts: {len(result['alerts'])}")
    for alert in result['alerts']:
        print(f"  - {alert['message']}")
