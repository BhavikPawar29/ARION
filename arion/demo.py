"""
Quick Demo Script for ARION
Tests all components quickly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🧪 ARION Quick Demo")
print("=" * 60)

# Test 1: Data Fetcher
print("\n1️⃣ Testing Data Fetcher...")
try:
    from utils.fetch_data import DataFetcher
    fetcher = DataFetcher()
    data = fetcher.fetch_stock_data(['AAPL'], period='1mo')
    print(f"   ✅ Data fetched: {len(data)} symbols")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 2: Risk Agent
print("\n2️⃣ Testing Risk Agent...")
try:
    from agents.risk_agent import RiskAgent
    agent = RiskAgent()
    result = agent.analyze(data)
    print(f"   ✅ Risk Score: {result['overall_risk_score']:.1f}")
    print(f"   ✅ Signal: {agent.return_signal()}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 3: Forecast Agent
print("\n3️⃣ Testing Forecast Agent...")
try:
    from agents.forecast_agent import ForecastAgent
    agent = ForecastAgent()
    result = agent.analyze(data)
    print(f"   ✅ Sentiment: {result['market_sentiment']}")
    print(f"   ✅ Signal: {agent.return_signal()}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 4: Sentiment Agent
print("\n4️⃣ Testing Sentiment Agent...")
try:
    from agents.sentiment_agent import SentimentAgent
    news = fetcher.fetch_news(['AAPL'])
    agent = SentimentAgent()
    result = agent.analyze(news)
    print(f"   ✅ Sentiment: {result['overall_label']}")
    print(f"   ✅ Signal: {agent.return_signal()}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 5: Correlation Agent
print("\n5️⃣ Testing Correlation Agent...")
try:
    from agents.correlation_agent import CorrelationAgent
    data_multi = fetcher.fetch_stock_data(['AAPL', 'MSFT'], period='1mo')
    agent = CorrelationAgent()
    result = agent.analyze(data_multi)
    print(f"   ✅ Diversification: {result['diversification_score']:.1f}")
    print(f"   ✅ Signal: {agent.return_signal()}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 6: Full Engine
print("\n6️⃣ Testing ARION Engine...")
try:
    from core.engine import ARIONEngine
    engine = ARIONEngine(['AAPL', 'MSFT'])
    summary = engine.run(period='1mo')
    print(f"   ✅ Unified Risk Score: {summary['unified_risk_score']:.1f}")
    print(f"   ✅ Risk Level: {summary['risk_level']}")
    print(f"   ✅ Alerts: {len(summary['all_alerts'])}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("✅ Demo complete!")
print("\n💻 To launch the dashboard, run:")
print("   streamlit run dashboard/app.py")
print("=" * 60)
