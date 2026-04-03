"""
Harvey OS – Self-Improving Decision Learning (v2 – SQLite-backed)
Analyzes historical decisions to find patterns in successful strategies
and update future recommendations.
"""

from __future__ import annotations

import json
from datetime import datetime

from core.database import get_db


class DecisionLearner:
    """Mine past decisions for strategy patterns and success rates."""

    def __init__(self, decisions: list[dict] | None = None):
        self.decisions = decisions or []

    # ── analysis ────────────────────────────────────────────────────────
    def analyze(self, decisions: list[dict] | None = None) -> dict:
        """
        Analyze decisions and produce learning insights.
        Returns a dict with strategy_stats, avg_confidence, avg_score,
        top_strategies, and weak_strategies.
        """
        data = decisions or self.decisions
        if not data:
            return {"message": "No decisions to analyze yet."}

        # Group by strategy
        strategy_stats: dict[str, dict] = {}
        for d in data:
            strat = d.get("strategy_used", "Unknown")
            if strat not in strategy_stats:
                strategy_stats[strat] = {"count": 0, "total_score": 0, "total_conf": 0}
            strategy_stats[strat]["count"] += 1
            strategy_stats[strat]["total_score"] += d.get("score", 0)
            strategy_stats[strat]["total_conf"] += d.get("confidence_level", 0)

        # Compute averages
        for strat, stats in strategy_stats.items():
            c = stats["count"]
            stats["avg_score"] = round(stats["total_score"] / c, 2) if c else 0
            stats["avg_confidence"] = round(stats["total_conf"] / c, 2) if c else 0

        total = len(data)
        avg_score = round(sum(d.get("score", 0) for d in data) / total, 2)
        avg_conf = round(
            sum(d.get("confidence_level", 0) for d in data) / total, 2
        )

        # Rank strategies
        ranked = sorted(
            strategy_stats.items(), key=lambda x: x[1]["avg_score"], reverse=True
        )
        top = [s for s, _ in ranked[:3]]
        weak = [s for s, st in ranked if st["avg_score"] < 4]

        result = {
            "total_decisions": total,
            "avg_score": avg_score,
            "avg_confidence": avg_conf,
            "strategy_stats": strategy_stats,
            "top_strategies": top,
            "weak_strategies": weak,
            "timestamp": datetime.now().isoformat(),
        }

        # Persist insight to SQLite
        db = get_db()
        db.execute(
            "INSERT INTO learning_history (insights, created_at) VALUES (?, ?)",
            (json.dumps(result), result["timestamp"]),
        )
        db.commit()

        return result

    def summary(self, decisions: list[dict] | None = None) -> str:
        """Human-readable learning summary."""
        result = self.analyze(decisions)
        if "message" in result:
            return result["message"]

        lines = [
            f"**Total Decisions Analyzed:** {result['total_decisions']}",
            f"**Average Score:** {result['avg_score']}/10",
            f"**Average Confidence:** {result['avg_confidence']}/10",
            "",
            "**Top Strategies:**",
        ]
        for s in result["top_strategies"]:
            st = result["strategy_stats"][s]
            lines.append(f"  • {s} (avg score {st['avg_score']})")

        if result["weak_strategies"]:
            lines.append("\n**Weak Strategies (avg < 4):**")
            for s in result["weak_strategies"]:
                st = result["strategy_stats"][s]
                lines.append(f"  • {s} (avg score {st['avg_score']})")

        return "\n".join(lines)
