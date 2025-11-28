# 🛡️ ARION — Autonomous Risk Intelligence & Optimization Network

**Built to notice what others overlook.**

![ARION Banner](https://via.placeholder.com/1200x300/667eea/ffffff?text=ARION+-+Risk+Intelligence+System)

## 📌 What is ARION?

ARION is an **intelligent multi-agent AI system** designed to monitor financial portfolios, detect early signs of risk, and provide actionable recommendations for portfolio optimization.

### What ARION Stands For

- **A** — **Autonomous**: Runs continuously without human intervention
- **R** — **Risk**: Identifies financial market risks (volatility, drawdowns, correlation shifts)
- **I** — **Intelligence**: Generates insights, not just raw numbers
- **O** — **Optimization**: Recommends improvements to reduce risk and increase diversification
- **N** — **Network**: Multiple specialized AI agents working together

## 🎯 Key Features

### 🤖 Multi-Agent Architecture

ARION consists of 5 specialized AI agents:

1. **Risk Agent** — Analyzes volatility, drawdowns, and risk spikes
2. **Forecast Agent** — Predicts short-term price movements using ML
3. **Sentiment Agent** — Analyzes news headlines for market sentiment
4. **Correlation Agent** — Tracks asset correlations and diversification
5. **Advisory Agent** — Combines all outputs into actionable recommendations

### 📊 Unified Risk Score

ARION generates a **single risk score (0-100)** that combines:
- Volatility analysis (40% weight)
- Forecast sentiment (20% weight)
- News sentiment (20% weight)
- Correlation risk (20% weight)

### 🎨 Beautiful Dashboard

Premium Streamlit dashboard featuring:
- Real-time risk gauge
- Interactive price and volatility charts
- Alert notifications
- Actionable recommendations
- Agent confidence levels

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or navigate to the ARION directory:**
   ```bash
   cd arion
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys (optional)
   ```

### Running ARION

#### Option 1: Command Line Interface

```bash
python main.py
```

This will run a complete analysis and display results in the terminal.

#### Option 2: Interactive Dashboard (Recommended)

```bash
streamlit run dashboard/app.py
```

Then open your browser to `http://localhost:8501`

## 📁 Project Structure

```
arion/
├── data/                    # Data storage (auto-generated)
├── agents/                  # AI Agent implementations
│   ├── risk_agent.py       # Volatility & drawdown analysis
│   ├── forecast_agent.py   # ML-based forecasting
│   ├── sentiment_agent.py  # News sentiment analysis
│   ├── correlation_agent.py # Correlation tracking
│   └── advisory_agent.py   # Recommendation generation
├── core/
│   └── engine.py           # Main ARION orchestration engine
├── utils/
│   └── fetch_data.py       # Data fetching utilities
├── dashboard/
│   └── app.py              # Streamlit dashboard
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 How It Works

### 1. Data Collection

ARION fetches:
- Historical price data (Yahoo Finance)
- Current prices and metrics
- News headlines for sentiment analysis

### 2. Agent Analysis

Each agent processes the data independently:

- **Risk Agent**: Calculates volatility, identifies drawdowns, detects spikes
- **Forecast Agent**: Uses Linear Regression/Random Forest to predict movements
- **Sentiment Agent**: Analyzes headlines using VADER sentiment analysis
- **Correlation Agent**: Computes correlation matrix and diversification score

### 3. Unified Intelligence

The **Advisory Agent** combines all outputs to:
- Generate a unified risk score (0-100)
- Identify priority actions
- Provide specific recommendations
- Create human-readable summaries

### 4. Visualization

The dashboard displays:
- Risk score gauge with color-coded zones
- Price and volatility trends
- Active alerts by severity
- Actionable recommendations
- Agent confidence levels

## 📊 Risk Score Interpretation

| Score Range | Risk Level | Meaning |
|-------------|-----------|---------|
| 0-20 | **LOW** | Portfolio is stable with low volatility |
| 20-50 | **MEDIUM** | Moderate risk, monitor closely |
| 50-80 | **HIGH** | Elevated risk, consider reducing exposure |
| 80-100 | **CRITICAL** | Severe risk, immediate action recommended |

## 🎨 Dashboard Features

### Main Metrics
- **Unified Risk Score**: Overall portfolio risk (0-100)
- **Market Sentiment**: Bullish/Bearish/Neutral forecast
- **Diversification Score**: Portfolio correlation analysis
- **Active Alerts**: Number of risk warnings

### Visualizations
- **Risk Gauge**: Real-time risk level indicator
- **Risk Breakdown**: Component scores (volatility, correlation, etc.)
- **Price Trends**: Historical price movements
- **Volatility Trends**: Rolling volatility analysis

### Insights
- **Active Alerts**: Prioritized warnings (Critical → High → Medium → Low)
- **Recommendations**: Actionable advice with rationale
- **Current Prices**: Live market data
- **Agent Confidence**: Reliability scores for each agent

## 🔑 Configuration

### Portfolio Symbols

Edit in the dashboard sidebar or modify `main.py`:
```python
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
```

### Analysis Period

Choose from:
- `1mo` — 1 month
- `3mo` — 3 months (default)
- `6mo` — 6 months
- `1y` — 1 year

### API Keys (Optional)

ARION works out-of-the-box with Yahoo Finance (no API key required).

For enhanced features, add to `.env`:
```
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

## 🧪 Testing Individual Agents

Each agent can be tested independently:

```bash
# Test Risk Agent
python agents/risk_agent.py

# Test Forecast Agent
python agents/forecast_agent.py

# Test Sentiment Agent
python agents/sentiment_agent.py

# Test Correlation Agent
python agents/correlation_agent.py

# Test Advisory Agent
python agents/advisory_agent.py
```

## 📈 Example Output

```
🚀 ARION — Autonomous Risk Intelligence & Optimization Network
============================================================

📊 Fetching market data...
💰 Fetching current prices...
📰 Fetching news data...

🤖 Running ARION Agents...
  ⚠️  Risk Agent analyzing...
  📈 Forecast Agent predicting...
  💭 Sentiment Agent analyzing...
  🔗 Correlation Agent calculating...
  🎯 Advisory Agent generating recommendations...

✅ Analysis complete!
   Unified Risk Score: 45.3/100
   Risk Level: MEDIUM
   Total Alerts: 3

============================================================
📊 ARION ANALYSIS RESULTS
============================================================

🎯 UNIFIED RISK SCORE: 45.3/100
   Risk Level: MEDIUM

🤖 AGENT SIGNALS:
   Risk Agent:        WATCH
   Forecast Agent:    BULLISH
   Sentiment Agent:   NEUTRAL
   Correlation Agent: MODERATE_CORRELATION
   Advisory Agent:    MAINTAIN_CURRENT_STRATEGY

⚠️  TOP ALERTS (3 total):
   1. [MEDIUM] AAPL: High volatility detected (0.32)
   2. [MEDIUM] TSLA-NVDA: Correlation increased from 0.45 to 0.68
   3. [LOW] GOOGL: Strong positive sentiment detected (0.65)

🎯 TOP RECOMMENDATIONS:
   1. [MARKET_OUTLOOK] Favorable conditions for growth positions
      → Technical forecast and news sentiment both indicate upward momentum
   2. [DIVERSIFICATION] Portfolio shows good diversification
      → Diversification score (72.3/100) indicates low correlation risk
```

## 🛠️ Tech Stack

- **Python 3.8+**
- **Data**: yfinance, pandas, numpy
- **ML**: scikit-learn, xgboost
- **Sentiment**: vaderSentiment
- **Dashboard**: Streamlit, Plotly
- **APIs**: Yahoo Finance (primary), Alpha Vantage (optional), News API (optional)

## 🎓 Use Cases

### For Hackathons
- Demonstrates multi-agent AI architecture
- Real-time data processing
- ML-powered predictions
- Beautiful, interactive dashboard

### For Portfolio Management
- Early risk detection
- Diversification analysis
- Sentiment-driven insights
- Actionable recommendations

### For Learning
- Agent-based system design
- Financial data analysis
- ML model integration
- Dashboard development

## 🚧 Future Enhancements

- [ ] Real-time WebSocket data streaming
- [ ] More ML models (LSTM, Transformer)
- [ ] Options hedging recommendations
- [ ] Backtesting framework
- [ ] Email/SMS alert notifications
- [ ] Multi-portfolio support
- [ ] Custom risk thresholds
- [ ] Export reports (PDF/Excel)

## 📝 License

This project is open-source and available for educational and hackathon purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new agents
- Improve ML models
- Enhance the dashboard
- Add new data sources
- Fix bugs

## 📧 Contact

Built for hackathon demonstration purposes.

---

**ARION — Built to notice what others overlook.** 🛡️
