"""
Harvey OS – Decision Tracking Database
CRUD operations for data/decisions.json.
"""

import json
from datetime import datetime
from pathlib import Path

from config.settings import DECISIONS_FILE


class DecisionTracker:
    """Persist and query strategic decisions."""

    def __init__(self, path: Path | None = None):
        self.path = path or DECISIONS_FILE
        self.decisions: list[dict] = self._load()

    def _load(self) -> list[dict]:
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self.decisions, fh, indent=4, ensure_ascii=False)

    def add(
        self,
        decision: str,
        strategy_used: str,
        confidence_level: int,
        outcome: str = "",
        score: int = 0,
    ) -> dict:
        """Record a new decision entry and persist."""
        entry = {
            "id": len(self.decisions) + 1,
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "strategy_used": strategy_used,
            "confidence_level": confidence_level,
            "outcome": outcome,
            "score": score,
        }
        self.decisions.append(entry)
        self.save()
        return entry

    def update_outcome(self, decision_id: int, outcome: str, score: int) -> bool:
        """Update the outcome and score for an existing decision."""
        for d in self.decisions:
            if d.get("id") == decision_id:
                d["outcome"] = outcome
                d["score"] = score
                self.save()
                return True
        return False

    def list_all(self) -> list[dict]:
        return list(self.decisions)
