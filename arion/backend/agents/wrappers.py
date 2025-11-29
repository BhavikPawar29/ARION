# backend/agents/wrappers.py
"""
Agent wrapper implementations for ARION.

Drop this file into: backend/agents/wrappers.py

Each wrapper wraps an "internal" agent object (from your engine) and
normalizes its outputs to:

{
  "prob": float,        # 0..1
  "severity": str,      # "low" | "medium" | "high"
  "message": str,       # brief human-friendly explanation
  "confidence": float,  # 0..1
  "meta": {...}         # optional extra data
}

Each wrapper implements BaseAgent interface:
- __init__(name)
- observe(market_state)
- get_signal()
- explain()
"""

import time
from typing import Any, Dict
from backend.core.agent_base import BaseAgent


def _parse_signal(raw: Any) -> Dict[str, Any]:
    """
    Robustly parse many possible internal signal shapes into normalized shape.
    Accepts:
      - dict-like with keys (prob, probability, score, severity, message, confidence)
      - string -> interpretable as a message (fallback)
      - object with methods .get_signal() / .return_signal()
    """
    # default empty signal
    out = {"prob": 0.0, "severity": "low", "message": "", "confidence": 0.0, "meta": {}}

    if raw is None:
        return out

    # if already in normalized shape
    if isinstance(raw, dict):
        # map common keys
        prob = raw.get("prob") or raw.get("probability") or raw.get("score") or raw.get("value") or 0.0
        try:
            prob = float(prob)
        except Exception:
            prob = 0.0

        out["prob"] = max(0.0, min(1.0, prob))
        out["severity"] = raw.get("severity") or raw.get("level") or raw.get("severity_level") or out["severity"]
        out["message"] = raw.get("message") or raw.get("note") or raw.get("explanation") or out["message"]
        conf = raw.get("confidence") or raw.get("conf") or raw.get("score_confidence")
        try:
            out["confidence"] = max(0.0, min(1.0, float(conf))) if conf is not None else (out["prob"] if out["prob"] else 0.5)
        except Exception:
            out["confidence"] = out["prob"] or 0.5
        # meta: anything else
        meta = {k: v for k, v in raw.items() if k not in ("prob","probability","score","value","severity","level","message","note","explanation","confidence","conf","score_confidence")}
        out["meta"] = meta
        return out

    # if raw is a string or can be str-ed
    try:
        s = str(raw)
        if s:
            out["message"] = s
            out["confidence"] = 0.5
            return out
    except Exception:
        pass

    # fallback
    return out


class GenericAgentWrapper(BaseAgent):
    """
    Generic wrapper that attempts to call common methods on the internal agent:
      - get_signal()
      - return_signal()
      - compute_signal()
      - run() / analyze()
    Use this when you want a one-size wrapper.
    """

    def __init__(self, internal_agent, name: str = None):
        super().__init__(name or getattr(internal_agent, "name", internal_agent.__class__.__name__))
        self._agent = internal_agent
        self._last_raw = None
        self._last_signal = {"prob": 0.0, "severity": "low", "message": "", "confidence": 0.0, "meta": {}}
        self._last_obs_time = None

    def observe(self, market_state: Dict[str, Any]) -> None:
        """
        Offer market_state to internal agent if it has an 'observe' or 'update' method.
        Then call the internal agent for a fresh signal if possible.
        """
        self._last_obs_time = time.time()
        try:
            if hasattr(self._agent, "observe"):
                # call agent.observe(...) if available
                try:
                    self._agent.observe(market_state)
                except TypeError:
                    # some observe may expect different signature; attempt without args
                    try:
                        self._agent.observe()
                    except Exception:
                        pass
            elif hasattr(self._agent, "update"):
                try:
                    self._agent.update(market_state)
                except Exception:
                    pass

            # Now try fetch signal using common method names
            for method in ("get_signal", "return_signal", "compute_signal", "signal", "analyze", "run"):
                if hasattr(self._agent, method):
                    try:
                        fn = getattr(self._agent, method)
                        raw = fn() if callable(fn) else getattr(self._agent, method)
                        self._last_raw = raw
                        self._last_signal = _parse_signal(raw)
                        return
                    except TypeError:
                        # maybe requires params; try with market_state
                        try:
                            raw = getattr(self._agent, method)(market_state)
                            self._last_raw = raw
                            self._last_signal = _parse_signal(raw)
                            return
                        except Exception:
                            continue
                    except Exception:
                        continue

            # If agent is a simple attribute-holder
            if hasattr(self._agent, "signal"):
                try:
                    raw = getattr(self._agent, "signal")
                    self._last_raw = raw
                    self._last_signal = _parse_signal(raw)
                    return
                except Exception:
                    pass

            # nothing else worked — fallback to str(agent)
            self._last_raw = str(self._agent)
            self._last_signal = _parse_signal(self._last_raw)

        except Exception as e:
            # In case the internal agent throws — keep a safe minimal signal
            self._last_raw = {"error": str(e)}
            self._last_signal = {"prob": 0.0, "severity": "low", "message": f"agent error: {e}", "confidence": 0.0, "meta": {"exception": str(e)}}

    def get_signal(self) -> Dict[str, Any]:
        return self._last_signal

    def explain(self) -> str:
        return f"{self.name}: {self._last_signal.get('message','no message')} (prob={self._last_signal.get('prob')}, conf={self._last_signal.get('confidence')})"


# Specific wrappers for clarity (they simply subclass GenericAgentWrapper,
# but you can extend them to add agent-specific normalization logic.)

class RiskAgentWrapper(GenericAgentWrapper):
    def __init__(self, internal_agent):
        super().__init__(internal_agent, name="RiskAgent")

    # Example override if you want special mapping:
    def get_signal(self):
        s = super().get_signal()
        # Example heuristic: if agent returns a volatility field, bump prob
        vol = s.get("meta", {}).get("volatility")
        if vol:
            try:
                v = float(vol)
                # scale to prob if in typical range
                s["prob"] = max(s["prob"], min(1.0, v / 100.0))
            except Exception:
                pass
        return s


class ForecastAgentWrapper(GenericAgentWrapper):
    def __init__(self, internal_agent):
        super().__init__(internal_agent, name="ForecastAgent")

    def get_signal(self):
        s = super().get_signal()
        # Map numeric forecast error to confidence if available
        err = s.get("meta", {}).get("forecast_error")
        if err is not None:
            try:
                e = float(err)
                s["confidence"] = max(0.0, min(1.0, 1.0 - min(1.0, e)))
            except Exception:
                pass
        return s


class SentimentAgentWrapper(GenericAgentWrapper):
    def __init__(self, internal_agent):
        super().__init__(internal_agent, name="SentimentAgent")

    def get_signal(self):
        s = super().get_signal()
        # If internal agent returns polarity, map to prob
        pol = s.get("meta", {}).get("polarity")
        if pol is not None:
            try:
                p = float(pol)  # -1..1
                # negative polarity increases risk prob
                prob = max(s["prob"], min(1.0, (1.0 - p) / 2.0))
                s["prob"] = prob
            except Exception:
                pass
        return s


class CorrelationAgentWrapper(GenericAgentWrapper):
    def __init__(self, internal_agent):
        super().__init__(internal_agent, name="CorrelationAgent")

    def get_signal(self):
        s = super().get_signal()
        # if meta contains 'corr_change' scale severity
        corr = s.get("meta", {}).get("corr_change")
        if corr is not None:
            try:
                c = float(corr)
                if abs(c) > 0.3:
                    s["severity"] = "medium"
                if abs(c) > 0.6:
                    s["severity"] = "high"
            except Exception:
                pass
        return s


class AdvisoryAgentWrapper(GenericAgentWrapper):
    def __init__(self, internal_agent):
        super().__init__(internal_agent, name="AdvisoryAgent")

    def get_signal(self):
        s = super().get_signal()
        # Ensure advisory returns some textual recommendation in message
        if not s.get("message"):
            recs = s.get("meta", {}).get("recommendations") or s.get("meta", {}).get("advice")
            if recs:
                s["message"] = recs if isinstance(recs, str) else str(recs)
        return s


# Export list for easy import
__all__ = [
    "GenericAgentWrapper",
    "RiskAgentWrapper",
    "ForecastAgentWrapper",
    "SentimentAgentWrapper",
    "CorrelationAgentWrapper",
    "AdvisoryAgentWrapper",
    "_parse_signal",
]
