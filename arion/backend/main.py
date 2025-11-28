"""
ARION - Autonomous Risk Intelligence & Optimization Network
Main entry point for command-line execution
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine import ARIONEngine


def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   █████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗                 ║
    ║  ██╔══██╗██╔══██╗██║██╔═══██╗████╗  ██║                 ║
    ║  ███████║██████╔╝██║██║   ██║██╔██╗ ██║                 ║
    ║  ██╔══██║██╔══██╗██║██║   ██║██║╚██╗██║                 ║
    ║  ██║  ██║██║  ██║██║╚██████╔╝██║ ╚████║                 ║
    ║  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝                 ║
    ║                                                           ║
    ║  Autonomous Risk Intelligence & Optimization Network     ║
    ║  Built to notice what others overlook.                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Default portfolio
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    print("\n📋 Default Portfolio:")
    print(f"   {', '.join(symbols)}")
    print("\n" + "=" * 60)
    
    # Create and run engine
    engine = ARIONEngine(symbols)
    summary = engine.run(period='3mo')
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 ARION ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"\n🎯 UNIFIED RISK SCORE: {summary['unified_risk_score']:.1f}/100")
    print(f"   Risk Level: {summary['risk_level']}")
    
    print(f"\n🤖 AGENT SIGNALS:")
    print(f"   Risk Agent:        {engine.risk_agent.return_signal()}")
    print(f"   Forecast Agent:    {engine.forecast_agent.return_signal()}")
    print(f"   Sentiment Agent:   {engine.sentiment_agent.return_signal()}")
    print(f"   Correlation Agent: {engine.correlation_agent.return_signal()}")
    print(f"   Advisory Agent:    {engine.advisory_agent.return_signal()}")
    
    print(f"\n⚠️  TOP ALERTS ({len(summary['all_alerts'])} total):")
    for i, alert in enumerate(summary['all_alerts'][:5], 1):
        print(f"   {i}. [{alert['severity']}] {alert['message']}")
    
    print(f"\n🎯 TOP RECOMMENDATIONS:")
    recommendations = summary['agent_results']['advisory']['recommendations']
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"   {i}. [{rec['category']}] {rec['recommendation']}")
        print(f"      → {rec['rationale']}")
    
    print(f"\n💡 ADVISORY SUMMARY:")
    print(f"   {summary['agent_results']['advisory']['summary']}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete!")
    print("\n💻 To view the interactive dashboard, run:")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
