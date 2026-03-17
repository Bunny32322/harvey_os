"""
Harvey OS – Leverage Score Engine
Computes a composite 0–10 score reflecting the user's current strategic leverage.
"""

import json
from pathlib import Path

from config.settings import HABITS_FILE

# ── Weight mapping (total = 1.0) ───────────────────────────────────────────
_WEIGHTS = {
    "learning_hours": 0.20,
    "deep_work_hours": 0.25,
    "networking_actions": 0.15,
    "workout": 0.20,
    "financial_stability": 0.20,
}

# Maximum expected daily values used for normalisation
_MAX_VALUES = {
    "learning_hours": 5,
    "deep_work_hours": 8,
    "networking_actions": 5,
    "workout": 2,
    "financial_stability": 10,
}


class LeverageScorer:
    """Calculate and explain the user's leverage score (0–10)."""

    def __init__(self, habits_path: Path | None = None):
        self.path = habits_path or HABITS_FILE
        self.habits = self._load()

    def _load(self) -> dict:
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            return {k: 0 for k in _WEIGHTS}

    def save(self, habits: dict) -> None:
        """Persist updated habits to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(habits, fh, indent=4)
        self.habits = habits

    def score(self, financial_stability: float = 5.0) -> float:
        """
        Return a composite leverage score (0–10).
        *financial_stability* is supplied separately (not in habits.json).
        """
        values = {**self.habits, "financial_stability": financial_stability}
        total = 0.0
        for key, weight in _WEIGHTS.items():
            raw = float(values.get(key, 0))
            normalised = min(raw / _MAX_VALUES.get(key, 1), 1.0)
            total += normalised * weight
        return round(total * 10, 2)

    def breakdown(self, financial_stability: float = 5.0) -> dict[str, float]:
        """Return per-dimension scores (each 0–10)."""
        values = {**self.habits, "financial_stability": financial_stability}
        out = {}
        for key in _WEIGHTS:
            raw = float(values.get(key, 0))
            normalised = min(raw / _MAX_VALUES.get(key, 1), 1.0)
            out[key] = round(normalised * 10, 2)
        return out
