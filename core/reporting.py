"""
Harvey OS – Reporting Engine
Generates weekly / monthly reports with leverage trends, habit consistency,
decision success rate, psychological patterns, and improvement suggestions.
Supports PDF export via reportlab.
"""

from __future__ import annotations

import io
from datetime import datetime

from core.leverage import LeverageScorer
from core.memory import UserProfile
from core.psychology import PatternAnalyzer
from core.scoring import DecisionTracker
from core.learning import DecisionLearner


class ReportEngine:
    """Build structured performance reports."""

    def __init__(
        self,
        profile: UserProfile | None = None,
        scorer: LeverageScorer | None = None,
        tracker: DecisionTracker | None = None,
    ):
        self.profile = profile or UserProfile()
        self.scorer = scorer or LeverageScorer()
        self.tracker = tracker or DecisionTracker()
        self.analyzer = PatternAnalyzer()
        self.learner = DecisionLearner()

    # ── markdown report ─────────────────────────────────────────────────
    def generate_markdown(self, financial_stability: float = 5.0) -> str:
        """Return a full markdown report string."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lev = self.scorer.score(financial_stability)
        bd = self.scorer.breakdown(financial_stability)

        decisions = self.tracker.list_all()
        reflections = self.profile.get("reflections", [])
        patterns_summary = self.analyzer.summary(reflections)
        learning_summary = self.learner.summary(decisions)

        bd_lines = "\n".join(
            f"| {k.replace('_', ' ').title()} | {v}/10 |" for k, v in bd.items()
        )

        habits = self.scorer.habits
        habit_lines = "\n".join(
            f"| {k.replace('_', ' ').title()} | {v} |" for k, v in habits.items()
        )

        report = f"""# 📊 Harvey OS – Performance Report
**Generated:** {now}

---

## Leverage Score: {lev}/10

| Dimension | Score |
|-----------|-------|
{bd_lines}

---

## Habit Snapshot

| Habit | Value |
|-------|-------|
{habit_lines}

---

## Decision Analysis

**Total decisions tracked:** {len(decisions)}

{learning_summary}

---

## Psychological Patterns

{patterns_summary}

---

## Recommendations

- Focus on dimensions scoring below 5/10
- Review weak strategies and adjust approach
- Address recurring psychological patterns
- Increase habits that compound leverage
"""
        return report

    # ── PDF export ──────────────────────────────────────────────────────
    def generate_pdf(self, financial_stability: float = 5.0) -> bytes:
        """Return the report as PDF bytes (uses reportlab)."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        )

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "HarveyTitle", parent=styles["Title"],
            textColor=HexColor("#c9a84c"), fontSize=22,
        )
        heading_style = ParagraphStyle(
            "HarveyH2", parent=styles["Heading2"],
            textColor=HexColor("#c9a84c"), fontSize=14,
        )
        body_style = styles["BodyText"]

        story: list = []

        # Title
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        story.append(Paragraph("Harvey OS – Performance Report", title_style))
        story.append(Paragraph(f"Generated: {now}", body_style))
        story.append(Spacer(1, 12))

        # Leverage
        lev = self.scorer.score(financial_stability)
        bd = self.scorer.breakdown(financial_stability)
        story.append(Paragraph(f"Leverage Score: {lev}/10", heading_style))
        table_data = [["Dimension", "Score"]]
        for k, v in bd.items():
            table_data.append([k.replace("_", " ").title(), f"{v}/10"])
        t = Table(table_data, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#c9a84c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#000000")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#444444")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        # Habits
        story.append(Paragraph("Habit Snapshot", heading_style))
        habits = self.scorer.habits
        h_data = [["Habit", "Value"]]
        for k, v in habits.items():
            h_data.append([k.replace("_", " ").title(), str(v)])
        ht = Table(h_data, hAlign="LEFT")
        ht.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#c9a84c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#000000")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#444444")),
        ]))
        story.append(ht)
        story.append(Spacer(1, 12))

        # Decisions
        decisions = self.tracker.list_all()
        story.append(Paragraph(f"Decisions Tracked: {len(decisions)}", heading_style))
        learning = self.learner.summary(decisions)
        for line in learning.split("\n"):
            clean = line.replace("**", "").strip()
            if clean:
                story.append(Paragraph(clean, body_style))
        story.append(Spacer(1, 12))

        # Patterns
        reflections = self.profile.get("reflections", [])
        story.append(Paragraph("Psychological Patterns", heading_style))
        pat_summary = self.analyzer.summary(reflections)
        for line in pat_summary.split("\n"):
            clean = line.replace("**", "").replace("•", "–").strip()
            if clean:
                story.append(Paragraph(clean, body_style))

        doc.build(story)
        return buf.getvalue()
