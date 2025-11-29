from core import engine

from backend.agents.wrappers import (
    RiskAgentWrapper,
    ForecastAgentWrapper,
    SentimentAgentWrapper,
    CorrelationAgentWrapper,
    AdvisoryAgentWrapper,
)

# assume engine is your ARIONEngine instance
risk_wrapper = RiskAgentWrapper(engine.risk_agent)
forecast_wrapper = ForecastAgentWrapper(engine.forecast_agent)
sentiment_wrapper = SentimentAgentWrapper(engine.sentiment_agent)
corr_wrapper = CorrelationAgentWrapper(engine.correlation_agent)
advisory_wrapper = AdvisoryAgentWrapper(engine.advisory_agent)

agents = [risk_wrapper, forecast_wrapper, sentiment_wrapper, corr_wrapper, advisory_wrapper]
