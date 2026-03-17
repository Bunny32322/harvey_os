"""
Harvey OS – Strategic Engine (Orchestrator)
Ties together vector memory, leverage scoring, and the Brain
to produce a complete strategic analysis for any user situation.
"""

from core.brain import Brain
from core.memory import UserProfile
from core.leverage import LeverageScorer
from core import vector_store


_ENGINE_PROMPT = """\
You are Harvey OS. Analyze the following situation using all available context.

## Situation
{situation}

## Relevant Memories
{memories}

## User Profile
{profile}

## Current Leverage Score: {leverage}/10

Respond using the Harvey OS strategic format:

1. Situation Analysis
2. Power Map
3. Risk Score (1-10)
4. Strategic Options
5. Recommended Move
6. Long-Term Impact
"""


class StrategicEngine:
    """
    Orchestrates a full strategic analysis:
    1. Retrieve relevant vector memories
    2. Compute leverage score
    3. Inject user profile context
    4. Build structured prompt
    5. Send to Brain and return the response
    """

    def __init__(self, brain: Brain, profile: UserProfile, scorer: LeverageScorer):
        self.brain = brain
        self.profile = profile
        self.scorer = scorer

    def analyze(self, situation: str, financial_stability: float = 5.0) -> str:
        """Run the full strategic pipeline and return the AI's analysis."""
        # 1. Retrieve related memories
        memories = vector_store.search_memory(situation, top_k=3)
        memories_text = (
            "\n".join(f"• {m}" for m in memories) if memories else "No prior memories."
        )

        # 2. Compute leverage score
        leverage = self.scorer.score(financial_stability)

        # 3. Build the prompt
        prompt = _ENGINE_PROMPT.format(
            situation=situation,
            memories=memories_text,
            profile=self.profile.summary(),
            leverage=leverage,
        )

        # 4. Think
        response = self.brain.think(prompt)

        # 5. Store this situation as a new memory for future reference
        vector_store.add_memory(situation)

        return response
