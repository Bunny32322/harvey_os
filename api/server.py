"""
Harvey OS – FastAPI Backend
REST API endpoints for mobile apps and external integrations.

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
from fastapi.responses import Response

from fastapi.middleware.cors import CORSMiddleware

# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Harvey OS API",
    description="Hybrid Strategic AI Command Center – REST API",
    version="1.0.0",
)

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for the requested demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / response models ──────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    situation: str
    mode: str = Field("offline", pattern="^(offline|online)$")
    financial_stability: float = Field(5.0, ge=0, le=10)

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


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"name": "Harvey OS API", "status": "operational"}


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """Run a full strategic analysis on the given situation."""
    brain = Brain(mode=req.mode)
    profile = UserProfile()
    scorer = LeverageScorer()
    engine = StrategicEngine(brain, profile, scorer)
    result = engine.analyze(req.situation, financial_stability=req.financial_stability)
    return {"analysis": result}


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
