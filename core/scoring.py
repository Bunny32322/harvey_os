"""
Harvey OS – Decision Tracking (v2 – SQLite-backed)
CRUD operations for strategic decisions.
"""

from __future__ import annotations

from datetime import datetime

from core.database import get_db


class DecisionTracker:
    """Persist and query strategic decisions (SQLite-backed)."""

    def __init__(self):
        pass  # DB is initialized by database module

    def add(
        self,
        decision: str,
        strategy_used: str = "",
        confidence_level: int = 5,
        outcome: str = "",
        score: int = 0,
    ) -> dict:
        """Record a new decision entry and persist."""
        db = get_db()
        cursor = db.execute(
            """INSERT INTO decisions
               (decision, strategy_used, confidence_level, outcome, score, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (decision, strategy_used, confidence_level, outcome, score,
             datetime.now().isoformat()),
        )
        db.commit()

        entry = {
            "id": cursor.lastrowid,
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "strategy_used": strategy_used,
            "confidence_level": confidence_level,
            "outcome": outcome,
            "score": score,
        }
        return entry

    def update_outcome(self, decision_id: int, outcome: str, score: int) -> bool:
        """Update the outcome and score for an existing decision."""
        db = get_db()
        cursor = db.execute(
            "UPDATE decisions SET outcome = ?, score = ? WHERE id = ?",
            (outcome, score, decision_id),
        )
        db.commit()
        return cursor.rowcount > 0

    def list_all(self) -> list[dict]:
        """List all decisions."""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM decisions ORDER BY created_at ASC"
        ).fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "timestamp": r["created_at"],
                "decision": r["decision"],
                "strategy_used": r["strategy_used"],
                "confidence_level": r["confidence_level"],
                "outcome": r["outcome"],
                "score": r["score"],
            })
        return results

    def get(self, decision_id: int) -> dict | None:
        """Get a single decision by ID."""
        db = get_db()
        row = db.execute(
            "SELECT * FROM decisions WHERE id = ?", (decision_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "timestamp": row["created_at"],
            "decision": row["decision"],
            "strategy_used": row["strategy_used"],
            "confidence_level": row["confidence_level"],
            "outcome": row["outcome"],
            "score": row["score"],
        }

    def count(self) -> int:
        """Count total decisions."""
        db = get_db()
        return db.execute("SELECT COUNT(*) as cnt FROM decisions").fetchone()["cnt"]
