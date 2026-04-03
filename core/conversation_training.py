"""
Harvey OS – Conversation Training (v2 – SQLite-backed)
Analyze past conversations to extract decision patterns, psychological
patterns, recurring problems, and strategic tendencies.
"""

from __future__ import annotations

from datetime import datetime

from core.database import get_db
from core.psychology import PatternAnalyzer
from core import vector_store


class ConversationTrainer:
    """Mine past conversations for strategic insights (SQLite-backed)."""

    def __init__(self):
        self.analyzer = PatternAnalyzer()
        self.conversations: list[dict] = self._load()

    # ── persistence ─────────────────────────────────────────────────────
    def _load(self) -> list[dict]:
        """Load conversation log from SQLite."""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM conversation_log ORDER BY created_at ASC"
        ).fetchall()
        return [
            {
                "timestamp": r["created_at"],
                "user": r["user_input"],
                "ai": r["ai_response"],
                "tag": r["tag"],
            }
            for r in rows
        ]

    # ── record ──────────────────────────────────────────────────────────
    def add_conversation(self, user_input: str, ai_response: str, tag: str = "") -> None:
        """Log a conversation turn."""
        db = get_db()
        now = datetime.now().isoformat()
        db.execute(
            """INSERT INTO conversation_log (user_input, ai_response, tag, created_at)
               VALUES (?, ?, ?, ?)""",
            (user_input, ai_response, tag, now),
        )
        db.commit()

        entry = {
            "timestamp": now,
            "user": user_input,
            "ai": ai_response,
            "tag": tag,
        }
        self.conversations.append(entry)

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
                f"{top_pattern} (detected {psych_counts[top_pattern]} times)",
                source="conversation_training",
                importance=7.0,
            )
        if tendencies:
            top_tendency = max(tendencies, key=tendencies.get)
            vector_store.add_memory(
                f"[Conversation Training] Dominant strategic tendency: "
                f"{top_tendency} (observed {tendencies[top_tendency]} times)",
                source="conversation_training",
                importance=7.0,
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
