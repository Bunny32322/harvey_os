"""
Harvey OS – Episodic Memory
Stores and retrieves life events with importance weighting, emotional
tagging, temporal indexing, and automatic decay of old unimportant
memories.

This is qualitatively different from vector memory:
- Vector memory: raw text chunks for semantic retrieval
- Episodic memory: structured life events with metadata for reasoning

Think of it as Harvey's long-term autobiographical memory about the user.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from core.database import get_db


# ── Emotion vocabulary ─────────────────────────────────────────────────────
EMOTIONS = [
    "neutral", "triumphant", "confident", "motivated", "calm",
    "stressed", "anxious", "frustrated", "angry", "sad",
    "confused", "hesitant", "overwhelmed", "determined", "hopeful",
]

# ── Category vocabulary ────────────────────────────────────────────────────
CATEGORIES = [
    "general", "career", "financial", "relationship", "health",
    "learning", "decision", "conflict", "achievement", "setback",
    "insight", "goal", "milestone",
]


class EpisodicMemory:
    """
    Structured life-event memory with importance, emotion, and temporal decay.

    Key features:
    - Events scored by importance (1-10)
    - Emotional tagging for mood correlation
    - Category-based filtering
    - Automatic decay: low-importance old events are pruned
    - Temporal queries: "what happened this week" vs "this year"
    """

    # Events below this importance that are older than DECAY_DAYS get pruned
    DECAY_IMPORTANCE_THRESHOLD = 3.0
    DECAY_DAYS = 90

    # ── Record ─────────────────────────────────────────────────────────

    def record(
        self,
        content: str,
        category: str = "general",
        importance: float = 5.0,
        emotion: str = "neutral",
        tags: list[str] | None = None,
    ) -> int:
        """
        Record a life event / episode.

        Args:
            content:    Description of what happened
            category:   One of CATEGORIES
            importance: 1.0 (trivial) to 10.0 (life-changing)
            emotion:    Emotional state during the event
            tags:       Optional freeform tags

        Returns:
            The episode ID.
        """
        # Validate
        importance = max(1.0, min(10.0, importance))
        if category not in CATEGORIES:
            category = "general"
        if emotion not in EMOTIONS:
            emotion = "neutral"

        # Calculate decay date for low-importance events
        decay_at = None
        if importance < self.DECAY_IMPORTANCE_THRESHOLD:
            decay_at = (
                datetime.now() + timedelta(days=self.DECAY_DAYS)
            ).isoformat()

        tags_json = json.dumps(tags or [])
        now = datetime.now().isoformat()

        db = get_db()
        cursor = db.execute(
            """INSERT INTO episodes
               (content, category, importance, emotion, tags, created_at, decay_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (content, category, importance, emotion, tags_json, now, decay_at),
        )
        db.commit()
        return cursor.lastrowid

    # ── Recall ─────────────────────────────────────────────────────────

    def recall(
        self,
        query: str | None = None,
        category: str | None = None,
        min_importance: float = 0.0,
        days_back: int | None = None,
        emotion: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """
        Recall episodes matching the given filters.

        Args:
            query:          Text search (LIKE match)
            category:       Filter by category
            min_importance: Minimum importance threshold
            days_back:      Only episodes from the last N days
            emotion:        Filter by emotion
            limit:          Max results

        Returns:
            List of episode dicts, newest first.
        """
        conditions: list[str] = []
        params: list = []

        if query:
            conditions.append("content LIKE ?")
            params.append(f"%{query}%")

        if category:
            conditions.append("category = ?")
            params.append(category)

        if min_importance > 0:
            conditions.append("importance >= ?")
            params.append(min_importance)

        if days_back:
            cutoff = (datetime.now() - timedelta(days=days_back)).isoformat()
            conditions.append("created_at >= ?")
            params.append(cutoff)

        if emotion:
            conditions.append("emotion = ?")
            params.append(emotion)

        where = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)

        db = get_db()
        rows = db.execute(
            f"""SELECT * FROM episodes
                WHERE {where}
                ORDER BY created_at DESC
                LIMIT ?""",
            params,
        ).fetchall()

        results = []
        for r in rows:
            d = dict(r)
            d["tags"] = json.loads(d.get("tags", "[]"))
            results.append(d)
        return results

    def recall_important(self, limit: int = 10) -> list[dict]:
        """Get the most important episodes ever recorded."""
        return self.recall(min_importance=7.0, limit=limit)

    def recall_recent(self, days: int = 7, limit: int = 20) -> list[dict]:
        """Get episodes from the last N days."""
        return self.recall(days_back=days, limit=limit)

    def recall_by_emotion(self, emotion: str, limit: int = 10) -> list[dict]:
        """Get episodes that had a specific emotional state."""
        return self.recall(emotion=emotion, limit=limit)

    # ── Context building (for LLM injection) ───────────────────────────

    def build_context(
        self,
        query: str | None = None,
        max_episodes: int = 5,
    ) -> str:
        """
        Build a text block of relevant episodes suitable for
        injection into LLM context.

        Strategy: Mix recent + high-importance + query-relevant episodes.
        """
        episodes: list[dict] = []
        seen_ids: set[int] = set()

        def _add(eps: list[dict]) -> None:
            for e in eps:
                if e["id"] not in seen_ids and len(episodes) < max_episodes:
                    episodes.append(e)
                    seen_ids.add(e["id"])

        # 1. Query-relevant episodes
        if query:
            _add(self.recall(query=query, limit=3))

        # 2. High-importance recent episodes
        _add(self.recall(min_importance=7.0, days_back=30, limit=3))

        # 3. Most recent episodes
        _add(self.recall_recent(days=7, limit=3))

        if not episodes:
            return ""

        lines: list[str] = ["[Life Context / Episodic Memory]"]
        for e in episodes:
            date = e["created_at"][:10]
            imp = "⭐" * int(e["importance"] // 2)
            lines.append(
                f"• [{date}] ({e['category']}, {e['emotion']}) {imp} {e['content']}"
            )
        return "\n".join(lines)

    # ── Decay / Pruning ────────────────────────────────────────────────

    def prune(self) -> int:
        """
        Delete episodes past their decay date.
        Only low-importance episodes get decay dates, so important
        memories are preserved forever.

        Returns the number of pruned episodes.
        """
        now = datetime.now().isoformat()
        db = get_db()
        cursor = db.execute(
            "DELETE FROM episodes WHERE decay_at IS NOT NULL AND decay_at < ?",
            (now,),
        )
        db.commit()
        return cursor.rowcount

    # ── Stats ──────────────────────────────────────────────────────────

    def stats(self) -> dict:
        """Return episodic memory statistics."""
        db = get_db()
        total = db.execute("SELECT COUNT(*) as cnt FROM episodes").fetchone()["cnt"]
        avg_imp = db.execute(
            "SELECT COALESCE(AVG(importance), 0) as avg FROM episodes"
        ).fetchone()["avg"]

        # Category breakdown
        cats = db.execute(
            """SELECT category, COUNT(*) as cnt
               FROM episodes GROUP BY category
               ORDER BY cnt DESC"""
        ).fetchall()

        # Emotion breakdown
        emotions = db.execute(
            """SELECT emotion, COUNT(*) as cnt
               FROM episodes GROUP BY emotion
               ORDER BY cnt DESC"""
        ).fetchall()

        return {
            "total_episodes": total,
            "average_importance": round(avg_imp, 2),
            "categories": {r["category"]: r["cnt"] for r in cats},
            "emotions": {r["emotion"]: r["cnt"] for r in emotions},
        }

    def summary(self) -> str:
        """Human-readable summary of episodic memory."""
        s = self.stats()
        if s["total_episodes"] == 0:
            return "No life events recorded yet."

        lines = [
            f"**Total Episodes:** {s['total_episodes']}",
            f"**Average Importance:** {s['average_importance']}/10",
        ]

        if s["categories"]:
            lines.append("\n**Categories:**")
            for cat, cnt in s["categories"].items():
                lines.append(f"  • {cat.title()}: {cnt}")

        if s["emotions"]:
            lines.append("\n**Emotional Distribution:**")
            for emo, cnt in s["emotions"].items():
                lines.append(f"  • {emo.title()}: {cnt}")

        return "\n".join(lines)
