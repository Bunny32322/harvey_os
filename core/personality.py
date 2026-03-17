"""
Harvey OS – Personality Modes
Adjusts AI prompting style based on selected strategic personality.
"""

from __future__ import annotations

# ── Personality mode definitions ────────────────────────────────────────────
MODES: dict[str, dict[str, str]] = {
    "Strategic": {
        "label": "♟️ Strategic",
        "description": "Balanced long-game analysis with calculated risk-taking.",
        "prompt_modifier": (
            "Adopt a strategic mindset. Think multiple moves ahead. "
            "Weigh risks against long-term positioning. Be calculated "
            "and methodical in your analysis."
        ),
    },
    "Aggressive": {
        "label": "🔥 Aggressive",
        "description": "High-conviction, bold moves, maximise leverage immediately.",
        "prompt_modifier": (
            "Adopt an aggressive mindset. Prioritize bold, decisive action. "
            "Identify the highest-leverage move and recommend it with conviction. "
            "Minimize hesitation and maximize momentum."
        ),
    },
    "Diplomatic": {
        "label": "🤝 Diplomatic",
        "description": "Relationship-aware, consensus-building, minimize friction.",
        "prompt_modifier": (
            "Adopt a diplomatic mindset. Prioritize relationships and alliances. "
            "Find win-win solutions where possible. Minimize unnecessary conflict "
            "while protecting the user's core interests."
        ),
    },
    "Long-Term": {
        "label": "🏗️ Long-Term",
        "description": "5-year horizon thinking, compounding advantages, patience.",
        "prompt_modifier": (
            "Adopt a long-term architect mindset. Evaluate every option against "
            "a 5-year horizon. Prioritize compounding advantages, sustainable "
            "growth, and structural positioning over short-term wins."
        ),
    },
}


def get_personality_prompt(mode: str) -> str:
    """Return the prompt modifier for the given personality *mode*."""
    entry = MODES.get(mode, MODES["Strategic"])
    return entry["prompt_modifier"]


def list_modes() -> list[str]:
    """Return the available personality mode names."""
    return list(MODES.keys())


def get_mode_info(mode: str) -> dict[str, str]:
    """Return label + description for a mode."""
    return MODES.get(mode, MODES["Strategic"])
