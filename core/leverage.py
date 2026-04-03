"""
Harvey OS – Leverage Score Engine (v2 – SQLite-backed)
Computes a composite 0–10 score reflecting the user's current strategic leverage.
"""

from __future__ import annotations

from core.database import get_db


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
    """Calculate and explain the user's leverage score (0–10). SQLite-backed."""

    def __init__(self):
        self.habits = self._load()

    def _load(self) -> dict:
        """Load habits from SQLite."""
        db = get_db()
        rows = db.execute("SELECT key, value FROM habits").fetchall()
        data = {r["key"]: r["value"] for r in rows}
        # Ensure all habit keys exist
        for k in _WEIGHTS:
            if k != "financial_stability":
                data.setdefault(k, 0)
        return data

    def save(self, habits: dict) -> None:
        """Persist updated habits to SQLite."""
        db = get_db()
        for key, value in habits.items():
            db.execute(
                """INSERT INTO habits (key, value, updated_at)
                   VALUES (?, ?, datetime('now'))
                   ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = datetime('now')""",
                (key, float(value), float(value)),
            )
        db.commit()
        self.habits = habits

    def score(self, financial_stability: float = 5.0) -> float:
        """
        Return a composite leverage score (0–10).
        *financial_stability* is supplied separately.
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
