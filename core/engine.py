"""
Harvey OS – Strategic Engine (Orchestrator) v2
Ties together vector memory, episodic memory, leverage scoring,
and the Brain to produce a complete strategic analysis.
Now with conversation threading and richer context injection.
"""

from core.brain import Brain
from core.memory import UserProfile
from core.leverage import LeverageScorer
from core import vector_store
from core.episodic_memory import EpisodicMemory


_ENGINE_PROMPT = """\
You are Harvey OS. Analyze the following situation using all available context.

## Situation
{situation}

## Relevant Memories
{memories}

## Life Context
{episodic_context}

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
    2. Retrieve relevant episodic memories
    3. Compute leverage score
    4. Inject user profile context
    5. Build structured prompt
    6. Send to Brain (with optional thread) and return the response
    """

    def __init__(self, brain: Brain, profile: UserProfile, scorer: LeverageScorer):
        self.brain = brain
        self.profile = profile
        self.scorer = scorer
        self.episodes = EpisodicMemory()

    def analyze(
        self,
        situation: str,
        financial_stability: float = 5.0,
        thread_id: str | None = None,
    ) -> str:
        """Run the full strategic pipeline and return the AI's analysis."""
        # 1. Retrieve related vector memories (new API returns dicts)
        memory_results = vector_store.search_memory(situation, top_k=3)
        memories_text = (
            "\n".join(f"• {m['text']}" for m in memory_results)
            if memory_results
            else "No prior memories."
        )

        # 2. Retrieve episodic context
        episodic_context = self.episodes.build_context(query=situation)
        if not episodic_context:
            episodic_context = "No life events recorded yet."

        # 3. Compute leverage score
        leverage = self.scorer.score(financial_stability)

        # 4. Build the prompt
        prompt = _ENGINE_PROMPT.format(
            situation=situation,
            memories=memories_text,
            episodic_context=episodic_context,
            profile=self.profile.summary(),
            leverage=leverage,
        )

        # 5. Think (with thread if provided)
        response = self.brain.think(prompt, thread_id=thread_id)

        # 6. Store this situation as a new memory for future reference
        vector_store.add_memory(
            situation,
            source="strategic_engine",
            importance=6.0,
        )

        # 7. Record as an episodic event
        self.episodes.record(
            content=f"Strategic analysis requested: {situation[:200]}",
            category="decision",
            importance=6.0,
            emotion="determined",
            tags=["strategic_engine"],
        )

        return response
