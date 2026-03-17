"""
Harvey OS – Psychological Pattern Analyzer
Scans reflections for recurring cognitive / emotional patterns.
"""

from __future__ import annotations

import re

# ── Pattern keyword maps ────────────────────────────────────────────────────
_PATTERN_KEYWORDS: dict[str, list[str]] = {
    "overthinking": [
        "overthink", "can't stop thinking", "spiral", "stuck in my head",
        "going in circles", "analysis paralysis", "ruminating",
    ],
    "conflict_avoidance": [
        "avoid conflict", "didn't say anything", "stayed quiet",
        "let it go", "didn't want to fight", "kept the peace",
        "backed down", "didn't push back",
    ],
    "emotional_reaction": [
        "lost my temper", "got angry", "emotional", "couldn't control",
        "reacted", "snapped", "frustrated", "blew up", "felt overwhelmed",
    ],
    "hesitation": [
        "hesitat", "couldn't decide", "waited too long", "missed the chance",
        "froze", "procrastinat", "delayed", "put off", "second-guessed",
    ],
}


class PatternAnalyzer:
    """Detect psychological patterns from free-text reflections."""

    def analyze(self, text: str) -> list[str]:
        """Return a list of detected pattern names in *text*."""
        lower = text.lower()
        detected: list[str] = []
        for pattern, keywords in _PATTERN_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                detected.append(pattern)
        return detected

    def analyze_many(self, reflections: list[str]) -> dict[str, int]:
        """Aggregate pattern counts across multiple reflections."""
        counts: dict[str, int] = {}
        for text in reflections:
            for p in self.analyze(text):
                counts[p] = counts.get(p, 0) + 1
        return counts

    def summary(self, reflections: list[str]) -> str:
        """Human-readable summary of detected patterns."""
        counts = self.analyze_many(reflections)
        if not counts:
            return "No dominant patterns detected yet."
        lines = [f"• **{k.replace('_', ' ').title()}** – detected {v} time(s)"
                 for k, v in sorted(counts.items(), key=lambda x: -x[1])]
        return "\n".join(lines)
