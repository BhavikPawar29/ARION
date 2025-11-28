"""
Advisory Agent for ARION
Combines all agent outputs and provides actionable recommendations
"""

import numpy as np
from typing import Dict, List


class AdvisoryAgent:
    """Generates actionable recommendations based on all agent outputs"""
    
    def __init__(self):
        """Initialize Advisory Agent"""
        self.last_analysis = {}
        
    def analyze(self, 
                risk_analysis: Dict,
                forecast_analysis: Dict,
                sentiment_analysis: Dict,
                correlation_analysis: Dict) -> Dict:
        """
        Generate recommendations based on all agent outputs
        
        Args:
            risk_analysis: Output from Risk Agent
            forecast_analysis: Output from Forecast Agent
            sentiment_analysis: Output from Sentiment Agent
            correlation_analysis: Output from Correlation Agent
            
        Returns:
            Dictionary containing advisory recommendations
        """
        recommendations = []
        priority_actions = []
        risk_factors = []
        
        # Extract key metrics
        risk_level = risk_analysis.get('risk_level', 'UNKNOWN')
        risk_score = risk_analysis.get('overall_risk_score', 0)
        market_sentiment = forecast_analysis.get('market_sentiment', 'UNKNOWN')
        sentiment_label = sentiment_analysis.get('overall_label', 'NEUTRAL')
        sentiment_score = sentiment_analysis.get('overall_score', 0)
        corr_risk = correlation_analysis.get('risk_level', 'UNKNOWN')
        avg_correlation = correlation_analysis.get('average_correlation', 0)
        diversification = correlation_analysis.get('diversification_score', 0)
        
        # Analyze risk situation
        if risk_level in ['HIGH', 'CRITICAL']:
            risk_factors.append('High portfolio volatility detected')
            priority_actions.append({
                'action': 'REDUCE_EXPOSURE',
                'priority': 'HIGH',
                'reason': f'Risk level is {risk_level}',
                'details': 'Consider reducing position sizes or taking profits on volatile assets'
            })
            
            recommendations.append({
                'category': 'RISK_MANAGEMENT',
                'recommendation': 'Reduce overall portfolio exposure',
                'rationale': f'Current risk score ({risk_score:.1f}) indicates elevated volatility',
                'urgency': 'HIGH'
            })
        
        # Analyze forecast and sentiment alignment
        if market_sentiment == 'BEARISH' and sentiment_label == 'NEGATIVE':
            risk_factors.append('Bearish forecast aligned with negative sentiment')
            priority_actions.append({
                'action': 'DEFENSIVE_POSITIONING',
                'priority': 'HIGH',
                'reason': 'Both technical and sentiment indicators are negative',
                'details': 'Consider defensive sectors or hedging strategies'
            })
            
            recommendations.append({
                'category': 'MARKET_OUTLOOK',
                'recommendation': 'Adopt defensive positioning',
                'rationale': 'Technical forecast and news sentiment both indicate downward pressure',
                'urgency': 'HIGH'
            })
        elif market_sentiment == 'BULLISH' and sentiment_label == 'POSITIVE':
            recommendations.append({
                'category': 'MARKET_OUTLOOK',
                'recommendation': 'Favorable conditions for growth positions',
                'rationale': 'Technical forecast and news sentiment both indicate upward momentum',
                'urgency': 'LOW'
            })
        elif market_sentiment != sentiment_label:
            risk_factors.append('Divergence between technical and sentiment signals')
            recommendations.append({
                'category': 'MARKET_OUTLOOK',
                'recommendation': 'Exercise caution - mixed signals detected',
                'rationale': f'Technical forecast ({market_sentiment}) diverges from sentiment ({sentiment_label})',
                'urgency': 'MEDIUM'
            })
        
        # Analyze correlation risk
        if corr_risk == 'HIGH':
            risk_factors.append('High correlation reduces diversification benefit')
            priority_actions.append({
                'action': 'IMPROVE_DIVERSIFICATION',
                'priority': 'MEDIUM',
                'reason': f'Average correlation is {avg_correlation:.2f}',
                'details': 'Add uncorrelated assets or reduce exposure to correlated positions'
            })
            
            recommendations.append({
                'category': 'DIVERSIFICATION',
                'recommendation': 'Improve portfolio diversification',
                'rationale': f'Current diversification score ({diversification:.1f}/100) is low',
                'urgency': 'MEDIUM'
            })
        elif diversification > 70:
            recommendations.append({
                'category': 'DIVERSIFICATION',
                'recommendation': 'Portfolio shows good diversification',
                'rationale': f'Diversification score ({diversification:.1f}/100) indicates low correlation risk',
                'urgency': 'LOW'
            })
        
        # Check for specific alert combinations
        risk_alerts = risk_analysis.get('alerts', [])
        sentiment_alerts = sentiment_analysis.get('alerts', [])
        corr_alerts = correlation_analysis.get('alerts', [])
        
        # High volatility + negative sentiment = strong warning
        high_vol_alerts = [a for a in risk_alerts if a['type'] in ['HIGH_VOLATILITY', 'VOLATILITY_SPIKE']]
        neg_sent_alerts = [a for a in sentiment_alerts if a['type'] == 'NEGATIVE_SENTIMENT']
        
        if high_vol_alerts and neg_sent_alerts:
            priority_actions.append({
                'action': 'RISK_REVIEW',
                'priority': 'CRITICAL',
                'reason': 'Combination of high volatility and negative sentiment',
                'details': 'Immediate review of portfolio risk exposure recommended'
            })
        
        # Generate overall recommendation
        overall_recommendation = self._generate_overall_recommendation(
            risk_level, market_sentiment, sentiment_label, corr_risk
        )
        
        # Calculate confidence
        confidences = [
            risk_analysis.get('confidence', 0),
            forecast_analysis.get('confidence', 0),
            sentiment_analysis.get('confidence', 0),
            correlation_analysis.get('confidence', 0)
        ]
        overall_confidence = np.mean([c for c in confidences if c > 0])
        
        self.last_analysis = {
            'overall_recommendation': overall_recommendation,
            'priority_actions': sorted(priority_actions, key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}[x['priority']]),
            'recommendations': recommendations,
            'risk_factors': risk_factors,
            'confidence': overall_confidence,
            'summary': self._generate_summary(risk_level, market_sentiment, sentiment_label, diversification)
        }
        
        return self.last_analysis
    
    def _generate_overall_recommendation(self, risk_level: str, market_sentiment: str, 
                                        sentiment_label: str, corr_risk: str) -> str:
        """Generate overall portfolio recommendation"""
        # Critical risk always takes precedence
        if risk_level == 'CRITICAL':
            return 'REDUCE_RISK_IMMEDIATELY'
        
        # High risk with negative signals
        if risk_level == 'HIGH' and (market_sentiment == 'BEARISH' or sentiment_label == 'NEGATIVE'):
            return 'DEFENSIVE_STANCE'
        
        # High risk but positive signals
        if risk_level == 'HIGH':
            return 'MONITOR_CLOSELY'
        
        # Medium risk with negative signals
        if risk_level == 'MEDIUM' and market_sentiment == 'BEARISH' and sentiment_label == 'NEGATIVE':
            return 'CAUTIOUS_APPROACH'
        
        # Low risk with positive signals
        if risk_level == 'LOW' and market_sentiment == 'BULLISH' and sentiment_label == 'POSITIVE':
            return 'FAVORABLE_CONDITIONS'
        
        # Default
        return 'MAINTAIN_CURRENT_STRATEGY'
    
    def _generate_summary(self, risk_level: str, market_sentiment: str, 
                         sentiment_label: str, diversification: float) -> str:
        """Generate human-readable summary"""
        summary_parts = []
        
        # Risk assessment
        if risk_level in ['HIGH', 'CRITICAL']:
            summary_parts.append(f"Portfolio is experiencing {risk_level.lower()} volatility.")
        else:
            summary_parts.append(f"Portfolio risk is currently {risk_level.lower()}.")
        
        # Market outlook
        if market_sentiment == 'BEARISH' and sentiment_label == 'NEGATIVE':
            summary_parts.append("Both technical and sentiment indicators suggest downward pressure.")
        elif market_sentiment == 'BULLISH' and sentiment_label == 'POSITIVE':
            summary_parts.append("Both technical and sentiment indicators suggest positive momentum.")
        else:
            summary_parts.append(f"Technical outlook is {market_sentiment.lower()} while sentiment is {sentiment_label.lower()}.")
        
        # Diversification
        if diversification > 70:
            summary_parts.append("Portfolio shows good diversification.")
        elif diversification < 40:
            summary_parts.append("Portfolio diversification could be improved.")
        
        return " ".join(summary_parts)
    
    def return_signal(self) -> str:
        """Return simple signal based on last analysis"""
        if not self.last_analysis:
            return "NO_DATA"
        
        return self.last_analysis.get('overall_recommendation', 'UNKNOWN')
    
    def return_confidence(self) -> float:
        """Return confidence in last analysis"""
        return self.last_analysis.get('confidence', 0.0)


if __name__ == "__main__":
    # Test the advisory agent
    import sys
    sys.path.append('..')
    from utils.fetch_data import DataFetcher
    from agents.risk_agent import RiskAgent
    from agents.forecast_agent import ForecastAgent
    from agents.sentiment_agent import SentimentAgent
    from agents.correlation_agent import CorrelationAgent
    
    # Fetch data
    fetcher = DataFetcher()
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    data = fetcher.fetch_stock_data(symbols, period='3mo')
    news = fetcher.fetch_news(symbols)
    
    # Run all agents
    risk_agent = RiskAgent()
    forecast_agent = ForecastAgent()
    sentiment_agent = SentimentAgent()
    correlation_agent = CorrelationAgent()
    
    risk_result = risk_agent.analyze(data)
    forecast_result = forecast_agent.analyze(data)
    sentiment_result = sentiment_agent.analyze(news)
    correlation_result = correlation_agent.analyze(data)
    
    # Get advisory
    advisory_agent = AdvisoryAgent()
    result = advisory_agent.analyze(risk_result, forecast_result, sentiment_result, correlation_result)
    
    print("Advisory Results:")
    print(f"\nOverall Recommendation: {result['overall_recommendation']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"\nSummary: {result['summary']}")
    print(f"\nPriority Actions ({len(result['priority_actions'])}):")
    for action in result['priority_actions']:
        print(f"  [{action['priority']}] {action['action']}: {action['details']}")
    print(f"\nRecommendations ({len(result['recommendations'])}):")
    for rec in result['recommendations'][:3]:
        print(f"  - {rec['recommendation']} ({rec['category']})")
