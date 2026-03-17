"""
Harvey OS – Configuration & Settings
Manages mode switching, API endpoints, and project paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Project Paths ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
SYSTEM_PROMPT_FILE = PROJECT_ROOT / "harvey_brain.txt"

# ── AI Mode ────────────────────────────────────────────────────────────────
# "offline" → LM Studio local server | "online" → OpenAI API
MODE = os.getenv("HARVEY_MODE", "offline")

# ── LM Studio (Offline) ───────────────────────────────────────────────────
LM_STUDIO_URL = os.getenv(
    "LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions"
)
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "local-model")

# ── OpenAI (Online) ───────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── Embedding Model ───────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ── Data File Paths ────────────────────────────────────────────────────────
MEMORY_FILE = DATA_DIR / "memory.json"
HABITS_FILE = DATA_DIR / "habits.json"
DECISIONS_FILE = DATA_DIR / "decisions.json"
VECTOR_INDEX_FILE = DATA_DIR / "vector.index"
VECTOR_STORE_FILE = DATA_DIR / "vector_store.pkl"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
LEARNING_FILE = DATA_DIR / "learning_history.json"

# ── Assets ─────────────────────────────────────────────────────────────────
ASSETS_DIR = PROJECT_ROOT / "assets"
STYLES_CSS = ASSETS_DIR / "styles.css"


def get_system_prompt() -> str:
    """Load the Harvey OS system prompt from harvey_brain.txt."""
    try:
        return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return (
            "You are Harvey OS. You think five moves ahead. "
            "You prioritize leverage over emotion. "
            "You analyze power dynamics and give structured strategic advice."
        )
