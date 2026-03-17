"""
Harvey OS – Trajectory Prediction
Predicts 1-year, 3-year, and 5-year outcomes (best / worst case)
based on leverage score, habits, and career data.
"""

from core.brain import Brain
from core.leverage import LeverageScorer
from core.memory import UserProfile


_TRAJECTORY_PROMPT = """\
You are a strategic futurist and life-trajectory analyst.

Based on the following data, predict realistic outcomes at three time horizons.

## Current Leverage Score: {score}/10

## Leverage Breakdown
{breakdown}

## Habits
{habits}

## User Profile
{profile}

Respond in this EXACT format:

### 1-Year Forecast
**Best Case:** ...
**Worst Case:** ...

### 3-Year Forecast
**Best Case:** ...
**Worst Case:** ...

### 5-Year Forecast
**Best Case:** ...
**Worst Case:** ...

### Key Inflection Points
List the 3 most critical decisions / habits that will determine trajectory.
"""


class TrajectoryPredictor:
    """Forecast future outcomes using current data and the Brain."""

    def __init__(self, brain: Brain):
        self.brain = brain

    def predict(
        self,
        profile: UserProfile,
        scorer: LeverageScorer,
        financial_stability: float = 5.0,
    ) -> str:
        """Generate a structured trajectory forecast."""
        score = scorer.score(financial_stability)
        breakdown = scorer.breakdown(financial_stability)
        breakdown_text = "\n".join(
            f"• {k.replace('_', ' ').title()}: {v}/10" for k, v in breakdown.items()
        )
        habits_text = "\n".join(
            f"• {k.replace('_', ' ').title()}: {v}"
            for k, v in scorer.habits.items()
        )
        prompt = _TRAJECTORY_PROMPT.format(
            score=score,
            breakdown=breakdown_text,
            habits=habits_text,
            profile=profile.summary(),
        )
        return self.brain.think(prompt)
