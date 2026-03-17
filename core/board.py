"""
Harvey OS – Board of Directors Mode
Simulates a panel of five AI personas, each analyzing the same situation
through a different strategic lens, then synthesises their perspectives.
"""

from __future__ import annotations

from core.brain import Brain

# ── Persona definitions ────────────────────────────────────────────────────
PERSONAS: dict[str, str] = {
    "The Closer": (
        "You are The Closer. You focus on winning. You identify the fastest "
        "path to closing a deal, securing a position, or ending a negotiation "
        "in the user's favor. Be direct, assertive, and results-oriented."
    ),
    "The Psychologist": (
        "You are The Psychologist. You analyze the emotional and psychological "
        "dimensions of the situation. Identify hidden motivations, blind spots, "
        "and interpersonal dynamics. Offer insight into people's behavior."
    ),
    "The Economist": (
        "You are The Economist. You evaluate the situation from a financial "
        "and resource-allocation perspective. Quantify opportunity costs, ROI, "
        "and long-term financial impact."
    ),
    "The Risk Manager": (
        "You are The Risk Manager. You identify every risk, vulnerability, "
        "and downside scenario. Rank risks by probability and severity. "
        "Recommend mitigation strategies."
    ),
    "The Architect": (
        "You are The Architect. You think in systems and structures. Design "
        "long-term frameworks, processes, and strategic architectures that "
        "create compounding advantages over time."
    ),
}

_SYNTHESIS_PROMPT = """\
You are Harvey OS, the chief strategist.

Five advisors have analyzed the following situation:

{situation}

Here are their individual analyses:

{analyses}

Synthesize all perspectives into a single, decisive strategic recommendation.
Use this structure:

1. Situation Analysis
2. Power Map
3. Risk Score (1-10)
4. Strategic Options
5. Recommended Move
6. Long-Term Impact
"""


class BoardOfDirectors:
    """Run a multi-persona advisory panel and produce a synthesis."""

    def __init__(self, brain: Brain):
        self.brain = brain

    def convene(self, situation: str) -> dict[str, str]:
        """
        Each persona analyzes *situation* independently.
        Returns a dict mapping persona name → analysis text,
        plus a "Synthesis" key with the final combined recommendation.
        """
        results: dict[str, str] = {}

        # Collect individual analyses
        for name, system_prompt in PERSONAS.items():
            prompt = (
                f"Analyze the following situation from your unique perspective:\n\n"
                f"{situation}"
            )
            results[name] = self.brain.think(prompt, system_prompt=system_prompt)

        # Build synthesis
        analyses_text = "\n\n---\n\n".join(
            f"**{name}:**\n{text}" for name, text in results.items()
        )
        synthesis = self.brain.think(
            _SYNTHESIS_PROMPT.format(situation=situation, analyses=analyses_text)
        )
        results["Synthesis"] = synthesis
        return results
