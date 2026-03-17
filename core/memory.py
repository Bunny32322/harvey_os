"""
Harvey OS – User Profile Memory
Loads and saves the user's profile (career, finance, relationships,
detected patterns, and daily reflections) to data/memory.json.
"""

import json
from pathlib import Path

from config.settings import MEMORY_FILE

# ── Default profile structure ──────────────────────────────────────────────
_DEFAULT_PROFILE: dict = {
    "career_position": "",
    "financial_status": "",
    "relationship_status": "",
    "patterns": [],
    "reflections": [],
}


class UserProfile:
    """Read / write the user's strategic profile."""

    def __init__(self, path: Path | None = None):
        self.path = path or MEMORY_FILE
        self.data: dict = self._load()

    # ── persistence ─────────────────────────────────────────────────────
    def _load(self) -> dict:
        """Load profile from disk, falling back to defaults."""
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            # Ensure all keys exist (forward-compat)
            for key, val in _DEFAULT_PROFILE.items():
                data.setdefault(key, val)
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return dict(_DEFAULT_PROFILE)

    def save(self) -> None:
        """Persist profile to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=4, ensure_ascii=False)

    # ── accessors ───────────────────────────────────────────────────────
    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value) -> None:
        self.data[key] = value

    def add_reflection(self, text: str) -> None:
        """Append a daily reflection entry."""
        self.data.setdefault("reflections", []).append(text)
        self.save()

    def add_pattern(self, pattern: str) -> None:
        """Record a detected psychological pattern (unique)."""
        patterns = self.data.setdefault("patterns", [])
        if pattern not in patterns:
            patterns.append(pattern)
            self.save()

    def summary(self) -> str:
        """Return a compact text summary suitable for prompt injection."""
        return (
            f"Career: {self.data.get('career_position', 'N/A')}\n"
            f"Finance: {self.data.get('financial_status', 'N/A')}\n"
            f"Relationships: {self.data.get('relationship_status', 'N/A')}\n"
            f"Detected Patterns: {', '.join(self.data.get('patterns', [])) or 'None'}"
        )
