"""
Core Engine for ARION
Orchestrates all agents and combines their outputs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List
import numpy as np
from utils.fetch_data import DataFetcher
from agents.risk_agent import RiskAgent
from agents.forecast_agent import ForecastAgent
from agents.sentiment_agent import SentimentAgent
from agents.correlation_agent import CorrelationAgent
from agents.advisory_agent import AdvisoryAgent


class ARIONEngine:
    """
    Main ARION Engine
    Coordinates all agents and generates unified risk intelligence
    """
    
    def __init__(self, symbols: List[str]):
        """
        Initialize ARION Engine
        
        Args:
            symbols: List of stock symbols to monitor
        """
        self.symbols = symbols
        
        # Initialize data fetcher
        self.data_fetcher = DataFetcher()
        
        # Initialize agents
        self.risk_agent = RiskAgent()
        self.forecast_agent = ForecastAgent()
        self.sentiment_agent = SentimentAgent()
        self.correlation_agent = CorrelationAgent()
        self.advisory_agent = AdvisoryAgent()
        
        # Storage for results
        self.market_data = {}
        self.current_prices = {}
        self.news_data = {}
        self.agent_results = {}
        self.unified_score = 0
        
    def fetch_all_data(self, period: str = '3mo') -> bool:
        """
        Fetch all required data
        
        Args:
            period: Time period for historical data
            
        Returns:
            True if data was successfully fetched
        """
        try:
            print("📊 Fetching market data...")
            self.market_data = self.data_fetcher.fetch_stock_data(self.symbols, period=period)
            
            print("💰 Fetching current prices...")
            self.current_prices = self.data_fetcher.fetch_current_prices(self.symbols)
            
            print("📰 Fetching news data...")
            self.news_data = self.data_fetcher.fetch_news(self.symbols)
            
            return len(self.market_data) > 0
            
        except Exception as e:
            print(f"❌ Error fetching data: {str(e)}")
            return False
    
    def run_all_agents(self) -> Dict:
        """
        Run all agents and collect results
        
        Returns:
            Dictionary containing all agent results
        """
        print("\n🤖 Running ARION Agents...")
        
        # Run Risk Agent
        print("  ⚠️  Risk Agent analyzing...")
        risk_result = self.risk_agent.analyze(self.market_data)
        
        # Run Forecast Agent
        print("  📈 Forecast Agent predicting...")
        forecast_result = self.forecast_agent.analyze(self.market_data)
        
        # Run Sentiment Agent
        print("  💭 Sentiment Agent analyzing...")
        sentiment_result = self.sentiment_agent.analyze(self.news_data)
        
        # Run Correlation Agent
        print("  🔗 Correlation Agent calculating...")
        correlation_result = self.correlation_agent.analyze(self.market_data)
        
        # Run Advisory Agent
        print("  🎯 Advisory Agent generating recommendations...")
        advisory_result = self.advisory_agent.analyze(
            risk_result, forecast_result, sentiment_result, correlation_result
        )
        
        self.agent_results = {
            'risk': risk_result,
            'forecast': forecast_result,
            'sentiment': sentiment_result,
            'correlation': correlation_result,
            'advisory': advisory_result
        }
        
        return self.agent_results
    
    def calculate_unified_risk_score(self) -> float:
        """
        Calculate unified ARION risk score (0-100)
        
        Combines:
        - Risk Agent score (40% weight)
        - Forecast sentiment (20% weight)
        - News sentiment (20% weight)
        - Correlation risk (20% weight)
        
        Returns:
            Unified risk score (0-100)
        """
        if not self.agent_results:
            return 0
        
        # Extract component scores
        risk_score = self.agent_results['risk'].get('overall_risk_score', 0)
        
        # Convert forecast to risk score (bearish = high risk)
        forecast_sentiment = self.agent_results['forecast'].get('market_sentiment', 'NEUTRAL')
        if forecast_sentiment == 'BEARISH':
            forecast_score = 70
        elif forecast_sentiment == 'BULLISH':
            forecast_score = 30
        else:
            forecast_score = 50
        
        # Convert sentiment to risk score (negative = high risk)
        sentiment_label = self.agent_results['sentiment'].get('overall_label', 'NEUTRAL')
        sentiment_score_raw = self.agent_results['sentiment'].get('overall_score', 0)
        if sentiment_label == 'NEGATIVE':
            sentiment_score = 50 + abs(sentiment_score_raw) * 50
        elif sentiment_label == 'POSITIVE':
            sentiment_score = 50 - sentiment_score_raw * 50
        else:
            sentiment_score = 50
        
        # Convert correlation to risk score (high correlation = high risk)
        corr_risk_level = self.agent_results['correlation'].get('risk_level', 'UNKNOWN')
        if corr_risk_level == 'HIGH':
            correlation_score = 75
        elif corr_risk_level == 'MEDIUM':
            correlation_score = 50
        else:
            correlation_score = 25
        
        # Weighted combination
        unified_score = (
            risk_score * 0.40 +
            forecast_score * 0.20 +
            sentiment_score * 0.20 +
            correlation_score * 0.20
        )
        
        self.unified_score = min(100, max(0, unified_score))
        
        return self.unified_score
    
    def get_risk_level(self) -> str:
        """Get risk level based on unified score"""
        if self.unified_score < 20:
            return 'LOW'
        elif self.unified_score < 50:
            return 'MEDIUM'
        elif self.unified_score < 80:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def get_all_alerts(self) -> List[Dict]:
        """Collect all alerts from all agents"""
        all_alerts = []
        
        if not self.agent_results:
            return all_alerts
        
        # Collect alerts from each agent
        for agent_name, result in self.agent_results.items():
            if agent_name == 'advisory':
                continue
            
            alerts = result.get('alerts', [])
            for alert in alerts:
                alert['source'] = agent_name
                all_alerts.append(alert)
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        all_alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'LOW'), 3))
        
        return all_alerts
    
    def get_summary(self) -> Dict:
        """Get complete ARION summary"""
        return {
            'unified_risk_score': self.unified_score,
            'risk_level': self.get_risk_level(),
            'symbols': self.symbols,
            'current_prices': self.current_prices,
            'agent_results': self.agent_results,
            'all_alerts': self.get_all_alerts(),
            'portfolio_metrics': self.data_fetcher.calculate_portfolio_metrics(self.market_data)
        }
    
    def run(self, period: str = '3mo') -> Dict:
        """
        Run complete ARION analysis
        
        Args:
            period: Time period for historical data
            
        Returns:
            Complete analysis summary
        """
        print("🚀 ARION — Autonomous Risk Intelligence & Optimization Network")
        print("=" * 60)
        
        # Fetch data
        if not self.fetch_all_data(period):
            print("❌ Failed to fetch data")
            return {}
        
        # Run agents
        self.run_all_agents()
        
        # Calculate unified score
        print("\n📊 Calculating unified risk score...")
        self.calculate_unified_risk_score()
        
        # Get summary
        summary = self.get_summary()
        
        print(f"\n✅ Analysis complete!")
        print(f"   Unified Risk Score: {self.unified_score:.1f}/100")
        print(f"   Risk Level: {self.get_risk_level()}")
        print(f"   Total Alerts: {len(self.get_all_alerts())}")
        
        return summary


if __name__ == "__main__":
    # Test the engine
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    engine = ARIONEngine(symbols)
    summary = engine.run(period='3mo')
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"\nUnified Risk Score: {summary['unified_risk_score']:.1f}/100")
    print(f"Risk Level: {summary['risk_level']}")
    
    print(f"\nAgent Signals:")
    print(f"  Risk: {engine.risk_agent.return_signal()}")
    print(f"  Forecast: {engine.forecast_agent.return_signal()}")
    print(f"  Sentiment: {engine.sentiment_agent.return_signal()}")
    print(f"  Correlation: {engine.correlation_agent.return_signal()}")
    print(f"  Advisory: {engine.advisory_agent.return_signal()}")
    
    print(f"\nTop Alerts:")
    for alert in summary['all_alerts'][:5]:
        print(f"  [{alert['severity']}] {alert['message']}")
    
    print(f"\nTop Recommendations:")
    for rec in summary['agent_results']['advisory']['recommendations'][:3]:
        print(f"  - {rec['recommendation']}")
