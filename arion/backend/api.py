import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.engine import ARIONEngine

app = FastAPI(title="ARION API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_summary.json")

def load_sample():
    if os.path.exists(SAMPLE_PATH):
        with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/risk")
def get_risk(symbols: str = "AAPL,MSFT,GOOGL,TSLA,NVDA", period: str = "3mo"):
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    try:
        engine = ARIONEngine(symbol_list)
        summary = engine.run(period=period)
        # shape response
        resp = {
            "unified_risk_score": summary.get("unified_risk_score"),
            "risk_level": summary.get("risk_level"),
            "agent_signals": {
                "risk_agent": engine.risk_agent.return_signal(),
                "forecast_agent": engine.forecast_agent.return_signal(),
                "sentiment_agent": engine.sentiment_agent.return_signal(),
                "correlation_agent": engine.correlation_agent.return_signal(),
                "advisory_agent": engine.advisory_agent.return_signal(),
            },
            "agent_results": summary.get("agent_results", {}),
            "all_alerts": summary.get("all_alerts", []),
        }
        # also save a copy as last-known-good for fallback
        os.makedirs(os.path.dirname(SAMPLE_PATH), exist_ok=True)
        with open(SAMPLE_PATH, "w", encoding="utf-8") as f:
            json.dump(resp, f, indent=2)
        return resp

    except Exception as e:
        # log on server
        import traceback, sys
        print("⚠️ ARION engine failed, returning sample data. Reason:", e, file=sys.stderr)
        traceback.print_exc()
        sample = load_sample()
        if sample:
            return sample
        # last resort — return minimal shape so frontend doesn't crash
        return {
            "unified_risk_score": None,
            "risk_level": "unknown",
            "agent_signals": {},
            "agent_results": {},
            "all_alerts": [],
            "error": str(e)
        }
