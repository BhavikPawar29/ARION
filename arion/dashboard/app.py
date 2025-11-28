"""
ARION Dashboard - Streamlit Application
Beautiful, premium risk intelligence dashboard
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import ARIONEngine

# Page configuration
st.set_page_config(
    page_title="ARION - Risk Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 700;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .alert-card {
        background: rgba(255, 59, 48, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #ff3b30;
        margin: 10px 0;
    }
    
    .recommendation-card {
        background: rgba(52, 199, 89, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #34c759;
        margin: 10px 0;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    div[data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'engine' not in st.session_state:
    st.session_state.engine = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=ARION", use_column_width=True)
    st.markdown("### 🛡️ Risk Intelligence System")
    st.markdown("---")
    
    # Symbol input
    st.markdown("#### Portfolio Configuration")
    default_symbols = "AAPL,MSFT,GOOGL,TSLA,NVDA"
    symbols_input = st.text_area(
        "Stock Symbols (comma-separated)",
        value=default_symbols,
        height=100
    )
    
    symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
    
    # Time period
    period = st.selectbox(
        "Analysis Period",
        options=['1mo', '3mo', '6mo', '1y'],
        index=1
    )
    
    st.markdown("---")
    
    # Run analysis button
    if st.button("🚀 Run Analysis"):
        with st.spinner("Running ARION analysis..."):
            try:
                engine = ARIONEngine(symbols)
                summary = engine.run(period=period)
                
                st.session_state.engine = engine
                st.session_state.summary = summary
                st.session_state.last_update = datetime.now()
                
                st.success("✅ Analysis complete!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Last update time
    if st.session_state.last_update:
        st.markdown("---")
        st.markdown(f"**Last Update:**")
        st.markdown(f"{st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("---")
    st.markdown("### About ARION")
    st.markdown("""
    **A**utonomous  
    **R**isk  
    **I**ntelligence &  
    **O**ptimization  
    **N**etwork
    
    Built to notice what others overlook.
    """)

# Main content
st.title("🛡️ ARION Risk Intelligence Dashboard")
st.markdown("### Built to notice what others overlook")

if st.session_state.summary is None:
    # Welcome screen
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>⚠️ Risk Detection</h3>
            <p>Real-time volatility and drawdown monitoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Forecasting</h3>
            <p>ML-powered price movement predictions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Advisory</h3>
            <p>Actionable recommendations for your portfolio</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("👈 Configure your portfolio in the sidebar and click 'Run Analysis' to get started.")
    
else:
    summary = st.session_state.summary
    engine = st.session_state.engine
    
    # Top metrics row
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_score = summary['unified_risk_score']
        risk_level = summary['risk_level']
        
        # Color based on risk level
        if risk_level == 'CRITICAL':
            delta_color = "inverse"
        elif risk_level == 'HIGH':
            delta_color = "inverse"
        else:
            delta_color = "normal"
        
        st.metric(
            label="Unified Risk Score",
            value=f"{risk_score:.1f}/100",
            delta=risk_level,
            delta_color=delta_color
        )
    
    with col2:
        market_sentiment = summary['agent_results']['forecast']['market_sentiment']
        st.metric(
            label="Market Sentiment",
            value=market_sentiment,
            delta=engine.forecast_agent.return_signal()
        )
    
    with col3:
        diversification = summary['agent_results']['correlation']['diversification_score']
        st.metric(
            label="Diversification Score",
            value=f"{diversification:.1f}/100",
            delta="Good" if diversification > 60 else "Improve"
        )
    
    with col4:
        alert_count = len(summary['all_alerts'])
        st.metric(
            label="Active Alerts",
            value=alert_count,
            delta=f"{sum(1 for a in summary['all_alerts'] if a['severity'] in ['HIGH', 'CRITICAL'])} High Priority"
        )
    
    # Risk Score Gauge
    st.markdown("---")
    st.markdown("### 📊 Risk Assessment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "ARION Risk Score", 'font': {'size': 24, 'color': 'white'}},
            delta={'reference': 50, 'increasing': {'color': "#ff3b30"}, 'decreasing': {'color': "#34c759"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#667eea"},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 2,
                'bordercolor': "white",
                'steps': [
                    {'range': [0, 20], 'color': 'rgba(52, 199, 89, 0.3)'},
                    {'range': [20, 50], 'color': 'rgba(255, 204, 0, 0.3)'},
                    {'range': [50, 80], 'color': 'rgba(255, 149, 0, 0.3)'},
                    {'range': [80, 100], 'color': 'rgba(255, 59, 48, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "white", 'family': "Inter"},
            height=300
        )
        
        st.plotly_chart(fig, use_column_width=True)
    
    with col2:
        st.markdown("#### Risk Breakdown")
        
        risk_components = {
            'Volatility': summary['agent_results']['risk']['overall_risk_score'],
            'Correlation': 75 if summary['agent_results']['correlation']['risk_level'] == 'HIGH' else 50 if summary['agent_results']['correlation']['risk_level'] == 'MEDIUM' else 25,
            'Sentiment': 70 if summary['agent_results']['sentiment']['overall_label'] == 'NEGATIVE' else 30,
            'Forecast': 70 if summary['agent_results']['forecast']['market_sentiment'] == 'BEARISH' else 30
        }
        
        fig = go.Figure(data=[
            go.Bar(
                y=list(risk_components.keys()),
                x=list(risk_components.values()),
                orientation='h',
                marker=dict(
                    color=list(risk_components.values()),
                    colorscale='RdYlGn_r',
                    showscale=False
                ),
                text=[f"{v:.0f}" for v in risk_components.values()],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "white"},
            xaxis={'range': [0, 100], 'showgrid': False},
            yaxis={'showgrid': False},
            height=300,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_column_width=True)
    
    # Portfolio Performance
    st.markdown("---")
    st.markdown("### 📈 Portfolio Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price chart
        if engine.market_data:
            # Combine all price data
            price_data = []
            for symbol, df in engine.market_data.items():
                temp_df = df[['Close']].copy()
                temp_df['Symbol'] = symbol
                temp_df['Date'] = temp_df.index
                price_data.append(temp_df)
            
            if price_data:
                combined_df = pd.concat(price_data)
                
                fig = px.line(
                    combined_df,
                    x='Date',
                    y='Close',
                    color='Symbol',
                    title='Price Trends'
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "white"},
                    xaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.1)'},
                    yaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.1)'},
                    height=400
                )
                
                st.plotly_chart(fig, use_column_width=True)
    
    with col2:
        # Volatility chart
        if engine.market_data:
            vol_data = []
            for symbol, df in engine.market_data.items():
                if 'Volatility' in df.columns:
                    temp_df = df[['Volatility']].copy()
                    temp_df['Symbol'] = symbol
                    temp_df['Date'] = temp_df.index
                    vol_data.append(temp_df)
            
            if vol_data:
                combined_vol = pd.concat(vol_data)
                
                fig = px.line(
                    combined_vol,
                    x='Date',
                    y='Volatility',
                    color='Symbol',
                    title='Volatility Trends'
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "white"},
                    xaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.1)'},
                    yaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.1)'},
                    height=400
                )
                
                st.plotly_chart(fig, use_column_width=True)
    
    # Alerts and Recommendations
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚠️ Active Alerts")
        
        alerts = summary['all_alerts'][:10]
        
        if alerts:
            for alert in alerts:
                severity = alert.get('severity', 'LOW')
                message = alert.get('message', '')
                
                if severity in ['CRITICAL', 'HIGH']:
                    st.markdown(f"""
                    <div class="alert-card">
                        <strong>[{severity}]</strong> {message}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"[{severity}] {message}")
        else:
            st.success("✅ No alerts at this time")
    
    with col2:
        st.markdown("### 🎯 Recommendations")
        
        recommendations = summary['agent_results']['advisory']['recommendations'][:5]
        
        if recommendations:
            for rec in recommendations:
                category = rec.get('category', '')
                recommendation = rec.get('recommendation', '')
                rationale = rec.get('rationale', '')
                
                st.markdown(f"""
                <div class="recommendation-card">
                    <strong>{category}</strong><br>
                    {recommendation}<br>
                    <small style="opacity: 0.7;">{rationale}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific recommendations at this time")
    
    # Current Prices
    st.markdown("---")
    st.markdown("### 💰 Current Prices")
    
    if summary['current_prices']:
        price_df = pd.DataFrame(summary['current_prices']).T
        price_df = price_df[['price', 'change_percent', 'volume', 'sector']]
        price_df.columns = ['Price', 'Change %', 'Volume', 'Sector']
        price_df['Change %'] = price_df['Change %'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(price_df, use_column_width=True)
    
    # Agent Confidence
    st.markdown("---")
    st.markdown("### 🤖 Agent Confidence Levels")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_conf = engine.risk_agent.return_confidence()
        st.metric("Risk Agent", f"{risk_conf:.0%}")
    
    with col2:
        forecast_conf = engine.forecast_agent.return_confidence()
        st.metric("Forecast Agent", f"{forecast_conf:.0%}")
    
    with col3:
        sentiment_conf = engine.sentiment_agent.return_confidence()
        st.metric("Sentiment Agent", f"{sentiment_conf:.0%}")
    
    with col4:
        corr_conf = engine.correlation_agent.return_confidence()
        st.metric("Correlation Agent", f"{corr_conf:.0%}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.7;">
    <p>ARION — Autonomous Risk Intelligence & Optimization Network</p>
    <p>Built to notice what others overlook.</p>
</div>
""", unsafe_allow_html=True)
