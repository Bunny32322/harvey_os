"""
Harvey OS – Scenario Simulator
Generates three strategic approaches (aggressive, balanced, passive)
with predicted outcomes for a given situation.
"""

from core.brain import Brain


_SIMULATION_PROMPT = """\
You are a world-class strategic analyst.

Given the following situation, generate exactly THREE strategies and predict each outcome.

## Situation
{situation}

## User Context
{context}

Respond in this EXACT format:

### 1 · Aggressive Strategy
**Approach:** ...
**Predicted Outcome:** ...

### 2 · Balanced Strategy
**Approach:** ...
**Predicted Outcome:** ...

### 3 · Passive Strategy
**Approach:** ...
**Predicted Outcome:** ...

### Final Recommendation
State which strategy is optimal and why.
"""


class ScenarioSimulator:
    """Generate three strategy options for any decision scenario."""

    def __init__(self, brain: Brain):
        self.brain = brain

    def simulate(self, situation: str, context: str = "") -> str:
        """Return a structured multi-strategy analysis."""
        prompt = _SIMULATION_PROMPT.format(
            situation=situation,
            context=context or "No additional context provided.",
        )
        return self.brain.think(prompt)
