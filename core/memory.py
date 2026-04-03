"""
Harvey OS – User Profile Memory (v2 – SQLite-backed)
Loads and saves the user's profile (career, finance, relationships,
detected patterns, and daily reflections) to the SQLite database.
Falls back gracefully if DB is unavailable.
"""

from __future__ import annotations

import json
from pathlib import Path

from core.database import get_db


# ── Default profile fields ─────────────────────────────────────────────────
_DEFAULT_FIELDS = {
    "career_position": "",
    "financial_status": "",
    "relationship_status": "",
}


class UserProfile:
    """Read / write the user's strategic profile (SQLite-backed)."""

    def __init__(self):
        self.data: dict = self._load()

    # ── persistence ─────────────────────────────────────────────────────
    def _load(self) -> dict:
        """Load profile from SQLite."""
        db = get_db()
        rows = db.execute("SELECT key, value FROM profile").fetchall()
        data = {r["key"]: r["value"] for r in rows}
        # Ensure all default keys exist
        for key, val in _DEFAULT_FIELDS.items():
            data.setdefault(key, val)
        # Load patterns
        pattern_rows = db.execute(
            "SELECT name FROM patterns ORDER BY last_seen DESC"
        ).fetchall()
        data["patterns"] = [r["name"] for r in pattern_rows]
        # Load recent reflections
        reflection_rows = db.execute(
            "SELECT content FROM reflections ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        data["reflections"] = [r["content"] for r in reversed(reflection_rows)]
        return data

    def save(self) -> None:
        """Persist profile to SQLite."""
        db = get_db()
        for key, value in self.data.items():
            if key in ("patterns", "reflections"):
                continue  # Handled by their own tables
            db.execute(
                """INSERT INTO profile (key, value, updated_at)
                   VALUES (?, ?, datetime('now'))
                   ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = datetime('now')""",
                (key, str(value), str(value)),
            )
        db.commit()

    # ── accessors ───────────────────────────────────────────────────────
    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value) -> None:
        self.data[key] = value

    def add_reflection(self, text: str) -> None:
        """Append a daily reflection entry."""
        db = get_db()
        db.execute(
            "INSERT INTO reflections (content) VALUES (?)",
            (text,),
        )
        db.commit()
        self.data.setdefault("reflections", []).append(text)

    def add_pattern(self, pattern: str) -> None:
        """Record a detected psychological pattern."""
        db = get_db()
        db.execute(
            """INSERT INTO patterns (name, count, first_seen, last_seen)
               VALUES (?, 1, datetime('now'), datetime('now'))
               ON CONFLICT(name) DO UPDATE SET
                   count = count + 1,
                   last_seen = datetime('now')""",
            (pattern,),
        )
        db.commit()
        if pattern not in self.data.get("patterns", []):
            self.data.setdefault("patterns", []).append(pattern)

    def get_reflections(self, limit: int = 50) -> list[str]:
        """Get reflections from DB."""
        db = get_db()
        rows = db.execute(
            "SELECT content FROM reflections ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [r["content"] for r in reversed(rows)]

    def get_pattern_counts(self) -> dict[str, int]:
        """Get all patterns with their detection counts."""
        db = get_db()
        rows = db.execute(
            "SELECT name, count FROM patterns ORDER BY count DESC"
        ).fetchall()
        return {r["name"]: r["count"] for r in rows}

    def summary(self) -> str:
        """Return a compact text summary suitable for prompt injection."""
        patterns_list = self.data.get("patterns", [])
        return (
            f"Career: {self.data.get('career_position', 'N/A')}\n"
            f"Finance: {self.data.get('financial_status', 'N/A')}\n"
            f"Relationships: {self.data.get('relationship_status', 'N/A')}\n"
            f"Detected Patterns: {', '.join(patterns_list) or 'None'}"
        )
