"""
Harvey OS – FastAPI Backend (v2)
REST API endpoints for mobile apps and external integrations.
Now with conversation threading, episodic memory, and data migration.

Run with:  uvicorn api.server:app --reload
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from core.brain import Brain
from core.memory import UserProfile
from core.leverage import LeverageScorer
from core.scoring import DecisionTracker
from core.engine import StrategicEngine
from core.reporting import ReportEngine
from core.conversation_memory import ConversationMemory
from core.episodic_memory import EpisodicMemory, EMOTIONS, CATEGORIES
from core import vector_store
from core.database import migrate_json_to_sqlite
from fastapi.responses import Response

from fastapi.middleware.cors import CORSMiddleware

# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Harvey OS API",
    description="Hybrid Strategic AI Command Center – REST API v2",
    version="2.0.0",
)

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / response models ──────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    situation: str
    mode: str = Field("offline", pattern="^(offline|online)$")
    financial_stability: float = Field(5.0, ge=0, le=10)
    thread_id: str | None = None  # Optional: continue in an existing thread

class ChatRequest(BaseModel):
    message: str
    mode: str = Field("offline", pattern="^(offline|online)$")
    thread_id: str | None = None  # If None, creates a new thread

class DecisionRequest(BaseModel):
    decision: str
    strategy_used: str = ""
    confidence_level: int = Field(5, ge=1, le=10)
    outcome: str = ""
    score: int = Field(0, ge=0, le=10)

class HabitsRequest(BaseModel):
    deep_work_hours: float = 0
    learning_hours: float = 0
    workout: float = 0
    networking_actions: int = 0

class ProfileRequest(BaseModel):
    career_position: str = ""
    financial_status: str = ""
    relationship_status: str = ""

class EpisodeRequest(BaseModel):
    content: str
    category: str = "general"
    importance: float = Field(5.0, ge=1, le=10)
    emotion: str = "neutral"
    tags: list[str] = []

class ThreadStartRequest(BaseModel):
    title: str = "Untitled"
    tag: str = ""


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"name": "Harvey OS API", "version": "2.0.0", "status": "operational"}


# ── Strategic Analysis ─────────────────────────────────────────────────────

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """Run a full strategic analysis on the given situation."""
    brain = Brain(mode=req.mode)
    profile = UserProfile()
    scorer = LeverageScorer()
    engine = StrategicEngine(brain, profile, scorer)

    # Auto-create thread if not provided
    thread_id = req.thread_id
    if not thread_id:
        thread_id = brain.start_thread(title="Strategic Analysis", tag="analysis")

    result = engine.analyze(
        req.situation,
        financial_stability=req.financial_stability,
        thread_id=thread_id,
    )
    return {"analysis": result, "thread_id": thread_id}


# ── Chat (Threaded Conversation) ──────────────────────────────────────────

@app.post("/chat")
def chat(req: ChatRequest):
    """Send a message in a conversation thread. Creates a new thread if needed."""
    brain = Brain(mode=req.mode)

    thread_id = req.thread_id
    if not thread_id:
        thread_id = brain.start_thread(title="Chat", tag="chat")

    response = brain.think(req.message, thread_id=thread_id)
    return {
        "response": response,
        "thread_id": thread_id,
    }


# ── Conversation Threads ──────────────────────────────────────────────────

@app.post("/threads")
def create_thread(req: ThreadStartRequest):
    """Create a new conversation thread."""
    memory = ConversationMemory()
    thread_id = memory.start_thread(title=req.title, tag=req.tag)
    return {"thread_id": thread_id}


@app.get("/threads")
def list_threads(limit: int = 50):
    """List all conversation threads."""
    memory = ConversationMemory()
    return {"threads": memory.list_threads(limit=limit)}


@app.get("/threads/{thread_id}")
def get_thread(thread_id: str):
    """Get a thread with all its messages."""
    memory = ConversationMemory()
    thread = memory.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    messages = memory.get_messages(thread_id)
    return {"thread": thread, "messages": messages}


@app.delete("/threads/{thread_id}")
def delete_thread(thread_id: str):
    """Delete a thread and all its messages."""
    memory = ConversationMemory()
    memory.delete_thread(thread_id)
    return {"deleted": True}


@app.get("/threads/stats/overview")
def thread_stats():
    """Get conversation statistics."""
    memory = ConversationMemory()
    return {"stats": memory.stats()}


# ── Episodic Memory ───────────────────────────────────────────────────────

@app.post("/episodes")
def record_episode(req: EpisodeRequest):
    """Record a life event / episode."""
    episodes = EpisodicMemory()
    episode_id = episodes.record(
        content=req.content,
        category=req.category,
        importance=req.importance,
        emotion=req.emotion,
        tags=req.tags,
    )
    return {"episode_id": episode_id}


@app.get("/episodes")
def list_episodes(
    category: str | None = None,
    emotion: str | None = None,
    min_importance: float = 0.0,
    days_back: int | None = None,
    limit: int = 20,
):
    """Query episodic memories with filters."""
    episodes = EpisodicMemory()
    results = episodes.recall(
        category=category,
        emotion=emotion,
        min_importance=min_importance,
        days_back=days_back,
        limit=limit,
    )
    return {"episodes": results}


@app.get("/episodes/important")
def important_episodes(limit: int = 10):
    """Get the most important life events."""
    episodes = EpisodicMemory()
    return {"episodes": episodes.recall_important(limit=limit)}


@app.get("/episodes/recent")
def recent_episodes(days: int = 7, limit: int = 20):
    """Get recent episodes."""
    episodes = EpisodicMemory()
    return {"episodes": episodes.recall_recent(days=days, limit=limit)}


@app.get("/episodes/stats")
def episode_stats():
    """Get episodic memory statistics."""
    episodes = EpisodicMemory()
    return {"stats": episodes.stats()}


@app.post("/episodes/prune")
def prune_episodes():
    """Prune decayed low-importance old memories."""
    episodes = EpisodicMemory()
    pruned = episodes.prune()
    return {"pruned_count": pruned}


@app.get("/episodes/categories")
def episode_categories():
    """List available episode categories."""
    return {"categories": CATEGORIES}


@app.get("/episodes/emotions")
def episode_emotions():
    """List available emotions."""
    return {"emotions": EMOTIONS}


# ── Vector Memory ──────────────────────────────────────────────────────────

@app.get("/memories")
def list_memories(limit: int = 50):
    """List all vector memories."""
    return {"memories": vector_store.get_all_memories(limit=limit)}


@app.get("/memories/search")
def search_memories(query: str, top_k: int = 5):
    """Semantic search for memories."""
    results = vector_store.search_memory(query, top_k=top_k)
    return {"results": results}


@app.get("/memories/count")
def memory_count():
    """Get vector memory count."""
    return {"count": vector_store.memory_count()}


# ── Decisions ──────────────────────────────────────────────────────────────

@app.post("/decision")
def log_decision(req: DecisionRequest):
    """Log a strategic decision."""
    tracker = DecisionTracker()
    entry = tracker.add(
        decision=req.decision,
        strategy_used=req.strategy_used,
        confidence_level=req.confidence_level,
        outcome=req.outcome,
        score=req.score,
    )
    return {"decision": entry}


@app.get("/decision")
def list_decisions():
    """List all tracked decisions."""
    tracker = DecisionTracker()
    return {"decisions": tracker.list_all()}


# ── Habits ─────────────────────────────────────────────────────────────────

@app.get("/habits")
def get_habits():
    """Get current habits data."""
    scorer = LeverageScorer()
    return {"habits": scorer.habits, "leverage_score": scorer.score()}


@app.put("/habits")
def update_habits(req: HabitsRequest):
    """Update habits data."""
    scorer = LeverageScorer()
    new_habits = {
        "deep_work_hours": req.deep_work_hours,
        "learning_hours": req.learning_hours,
        "workout": req.workout,
        "networking_actions": req.networking_actions,
    }
    scorer.save(new_habits)
    return {"habits": new_habits, "leverage_score": scorer.score()}


# ── Profile ────────────────────────────────────────────────────────────────

@app.get("/profile")
def get_profile():
    """Get user profile."""
    profile = UserProfile()
    return {"profile": profile.data}


@app.put("/profile")
def update_profile(req: ProfileRequest):
    """Update user profile fields."""
    profile = UserProfile()
    profile.set("career_position", req.career_position)
    profile.set("financial_status", req.financial_status)
    profile.set("relationship_status", req.relationship_status)
    profile.save()
    return {"profile": profile.data}


# ── Reports ────────────────────────────────────────────────────────────────

@app.get("/report")
def generate_report(financial_stability: float = 5.0):
    """Generate a performance report (JSON + markdown)."""
    engine = ReportEngine()
    md = engine.generate_markdown(financial_stability)
    return {"report_markdown": md}


@app.get("/report/pdf")
def generate_pdf_report(financial_stability: float = 5.0):
    """Generate and return a PDF performance report."""
    engine = ReportEngine()
    pdf_bytes = engine.generate_pdf(financial_stability)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=harvey_os_report.pdf"},
    )


# ── Migration ──────────────────────────────────────────────────────────────

@app.post("/admin/migrate")
def run_migration():
    """One-time: migrate existing JSON data into SQLite."""
    counts = migrate_json_to_sqlite()
    # Also migrate FAISS vectors to ChromaDB
    faiss_count = vector_store.migrate_from_faiss()
    counts["vector_memories"] = faiss_count
    return {"migrated": counts}
