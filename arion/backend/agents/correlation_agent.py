"""
Correlation Agent for ARION
Tracks asset correlations and detects correlation risk
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class CorrelationAgent:
    """Analyzes correlations between assets and detects correlation risk"""
    
    def __init__(self, high_correlation_threshold: float = 0.7):
        """
        Initialize Correlation Agent
        
        Args:
            high_correlation_threshold: Threshold for high correlation alert
        """
        self.high_correlation_threshold = high_correlation_threshold
        self.last_analysis = {}
        
    def analyze(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Analyze correlations across portfolio
        
        Args:
            data: Dictionary mapping symbols to DataFrames with price data
            
        Returns:
            Dictionary containing correlation analysis results
        """
        if not data or len(data) < 2:
            return self._empty_result()
        
        # Create returns matrix
        returns_dict = {}
        for symbol, df in data.items():
            if 'Returns' in df.columns and not df['Returns'].empty:
                returns_dict[symbol] = df['Returns']
        
        if len(returns_dict) < 2:
            return self._empty_result()
        
        # Align all series to same dates
        returns_df = pd.DataFrame(returns_dict).dropna()
        
        if returns_df.empty or len(returns_df) < 20:
            return self._empty_result()
        
        # Calculate correlation matrix
        corr_matrix = returns_df.corr()
        
        # Calculate rolling correlation (recent vs historical)
        recent_window = min(20, len(returns_df) // 3)
        recent_corr = returns_df.tail(recent_window).corr()
        
        # Find high correlations
        high_correlations = []
        correlation_increases = []
        
        symbols = list(corr_matrix.columns)
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                sym1, sym2 = symbols[i], symbols[j]
                corr_value = corr_matrix.loc[sym1, sym2]
                recent_corr_value = recent_corr.loc[sym1, sym2]
                
                # Check for high correlation
                if abs(corr_value) > self.high_correlation_threshold:
                    high_correlations.append({
                        'pair': f'{sym1}-{sym2}',
                        'correlation': corr_value,
                        'type': 'positive' if corr_value > 0 else 'negative'
                    })
                
                # Check for correlation increase
                if len(returns_df) > 60:
                    historical_corr = returns_df.iloc[:-recent_window].corr().loc[sym1, sym2]
                    if abs(recent_corr_value) > abs(historical_corr) + 0.2:
                        correlation_increases.append({
                            'pair': f'{sym1}-{sym2}',
                            'recent': recent_corr_value,
                            'historical': historical_corr,
                            'change': recent_corr_value - historical_corr
                        })
        
        # Calculate average correlation
        upper_triangle = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        avg_correlation = upper_triangle.stack().mean()
        
        # Calculate diversification score (lower correlation = better diversification)
        diversification_score = max(0, 100 * (1 - abs(avg_correlation)))
        
        # Generate alerts
        alerts = []
        
        if abs(avg_correlation) > self.high_correlation_threshold:
            alerts.append({
                'type': 'HIGH_PORTFOLIO_CORRELATION',
                'severity': 'HIGH',
                'message': f'Portfolio shows high average correlation ({avg_correlation:.2f})',
                'value': avg_correlation
            })
        
        for corr_increase in correlation_increases:
            alerts.append({
                'type': 'CORRELATION_INCREASE',
                'severity': 'MEDIUM',
                'message': f'{corr_increase["pair"]}: Correlation increased from {corr_increase["historical"]:.2f} to {corr_increase["recent"]:.2f}',
                'value': corr_increase['change']
            })
        
        # Determine risk level
        if abs(avg_correlation) > 0.8:
            risk_level = 'HIGH'
        elif abs(avg_correlation) > 0.6:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        self.last_analysis = {
            'correlation_matrix': corr_matrix.to_dict(),
            'average_correlation': avg_correlation,
            'diversification_score': diversification_score,
            'high_correlations': high_correlations,
            'correlation_increases': correlation_increases,
            'risk_level': risk_level,
            'alerts': alerts,
            'confidence': self._calculate_confidence(returns_df)
        }
        
        return self.last_analysis
    
    def _calculate_confidence(self, returns_df: pd.DataFrame) -> float:
        """Calculate confidence based on data quality"""
        if returns_df.empty:
            return 0.0
        
        # Confidence based on number of observations
        n_obs = len(returns_df)
        
        if n_obs >= 60:
            return 1.0
        elif n_obs >= 30:
            return 0.8
        elif n_obs >= 20:
            return 0.6
        else:
            return 0.4
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'correlation_matrix': {},
            'average_correlation': 0,
            'diversification_score': 0,
            'high_correlations': [],
            'correlation_increases': [],
            'risk_level': 'UNKNOWN',
            'alerts': [],
            'confidence': 0.0
        }
    
    def return_signal(self) -> str:
        """Return simple signal based on last analysis"""
        if not self.last_analysis:
            return "NO_DATA"
        
        risk_level = self.last_analysis.get('risk_level', 'UNKNOWN')
        
        if risk_level == 'HIGH':
            return "HIGH_CORRELATION"
        elif risk_level == 'MEDIUM':
            return "MODERATE_CORRELATION"
        else:
            return "WELL_DIVERSIFIED"
    
    def return_confidence(self) -> float:
        """Return confidence in last analysis"""
        return self.last_analysis.get('confidence', 0.0)


if __name__ == "__main__":
    # Test the correlation agent
    import sys
    sys.path.append('..')
    from utils.fetch_data import DataFetcher
    
    fetcher = DataFetcher()
    data = fetcher.fetch_stock_data(['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'], period='3mo')
    
    agent = CorrelationAgent()
    result = agent.analyze(data)
    
    print("Correlation Analysis Results:")
    print(f"Average Correlation: {result['average_correlation']:.2f}")
    print(f"Diversification Score: {result['diversification_score']:.2f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Signal: {agent.return_signal()}")
    print(f"Confidence: {agent.return_confidence():.2%}")
    print(f"\nHigh Correlations: {len(result['high_correlations'])}")
    for corr in result['high_correlations'][:5]:
        print(f"  {corr['pair']}: {corr['correlation']:.2f}")
    print(f"\nAlerts: {len(result['alerts'])}")
    for alert in result['alerts']:
        print(f"  - {alert['message']}")
