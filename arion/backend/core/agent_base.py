# backend/core/agent_base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def observe(self, market_state: Dict[str, Any]) -> None:
        """Update internal state from market_state (called each cycle)."""
        pass

    @abstractmethod
    def get_signal(self) -> Dict[str, Any]:
        """
        Return a dict with:
        {
          "prob": float,         # 0..1 probability of risk
          "severity": "low|med|high",
          "message": str,        # short explanation
          "confidence": float    # 0..1
        }
        """
        pass

    def explain(self) -> str:
        """Human-friendly explanation (optional override)."""
        sig = self.get_signal()
        return f"{self.name}: {sig.get('message','')}"
