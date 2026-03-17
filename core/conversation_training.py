"""
Harvey OS – Conversation Training
Analyze past conversations to extract decision patterns, psychological
patterns, recurring problems, and strategic tendencies.
Stores conversation history in data/conversations.json and feeds
extracted insights into vector memory.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from config.settings import DATA_DIR
from core.psychology import PatternAnalyzer
from core import vector_store

CONVERSATIONS_FILE = DATA_DIR / "conversations.json"


class ConversationTrainer:
    """Mine past conversations for strategic insights."""

    def __init__(self):
        self.conversations: list[dict] = self._load()
        self.analyzer = PatternAnalyzer()

    # ── persistence ─────────────────────────────────────────────────────
    def _load(self) -> list[dict]:
        try:
            with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self) -> None:
        CONVERSATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as fh:
            json.dump(self.conversations, fh, indent=4, ensure_ascii=False)

    # ── record ──────────────────────────────────────────────────────────
    def add_conversation(self, user_input: str, ai_response: str, tag: str = "") -> None:
        """Log a conversation turn."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "ai": ai_response,
            "tag": tag,
        }
        self.conversations.append(entry)
        self.save()

    # ── analysis ────────────────────────────────────────────────────────
    def extract_insights(self) -> dict:
        """
        Process all stored conversations and extract:
        - decision patterns
        - psychological patterns
        - recurring problems (keywords)
        - strategic tendencies
        Returns a summary dict and adds key insights to vector memory.
        """
        if not self.conversations:
            return {"message": "No conversations to analyze."}

        all_user_text = [c["user"] for c in self.conversations]
        all_ai_text = [c["ai"] for c in self.conversations]

        # Psychological patterns from user messages
        psych_counts = self.analyzer.analyze_many(all_user_text)

        # Recurring problem keywords
        problem_keywords = [
            "stuck", "don't know", "confused", "struggling", "problem",
            "challenge", "difficult", "worried", "stressed", "failing",
        ]
        recurring: dict[str, int] = {}
        for text in all_user_text:
            lower = text.lower()
            for kw in problem_keywords:
                if kw in lower:
                    recurring[kw] = recurring.get(kw, 0) + 1

        # Strategic tendencies (from AI responses)
        tendency_keywords = {
            "aggressive": ["bold", "aggressive", "maximum leverage", "decisive"],
            "diplomatic": ["negotiate", "compromise", "relationship", "consensus"],
            "analytical": ["analyze", "data", "metrics", "quantify"],
            "cautious": ["careful", "risk", "protect", "conservative"],
        }
        tendencies: dict[str, int] = {}
        for text in all_ai_text:
            lower = text.lower()
            for tendency, keywords in tendency_keywords.items():
                if any(kw in lower for kw in keywords):
                    tendencies[tendency] = tendencies.get(tendency, 0) + 1

        # Add key insights to vector memory
        if psych_counts:
            top_pattern = max(psych_counts, key=psych_counts.get)
            vector_store.add_memory(
                f"[Conversation Training] Dominant psychological pattern: "
                f"{top_pattern} (detected {psych_counts[top_pattern]} times)"
            )
        if tendencies:
            top_tendency = max(tendencies, key=tendencies.get)
            vector_store.add_memory(
                f"[Conversation Training] Dominant strategic tendency: "
                f"{top_tendency} (observed {tendencies[top_tendency]} times)"
            )

        return {
            "total_conversations": len(self.conversations),
            "psychological_patterns": psych_counts,
            "recurring_problems": recurring,
            "strategic_tendencies": tendencies,
            "timestamp": datetime.now().isoformat(),
        }

    def summary(self) -> str:
        """Human-readable training report."""
        result = self.extract_insights()
        if "message" in result:
            return result["message"]

        lines = [f"**Conversations Analyzed:** {result['total_conversations']}"]

        if result["psychological_patterns"]:
            lines.append("\n**Psychological Patterns:**")
            for p, c in sorted(result["psychological_patterns"].items(), key=lambda x: -x[1]):
                lines.append(f"  • {p.replace('_', ' ').title()}: {c} occurrence(s)")

        if result["recurring_problems"]:
            lines.append("\n**Recurring Problem Themes:**")
            for kw, c in sorted(result["recurring_problems"].items(), key=lambda x: -x[1]):
                lines.append(f"  • \"{kw}\": {c} mention(s)")

        if result["strategic_tendencies"]:
            lines.append("\n**Strategic Tendencies in Responses:**")
            for t, c in sorted(result["strategic_tendencies"].items(), key=lambda x: -x[1]):
                lines.append(f"  • {t.title()}: {c} occurrence(s)")

        return "\n".join(lines)
