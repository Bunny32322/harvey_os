"""
Harvey OS – Mobile API Client
Lightweight client for connecting mobile apps or external integrations
to the Harvey OS FastAPI backend.
"""

from __future__ import annotations

import requests


class HarveyClient:
    """HTTP client for the Harvey OS REST API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base}{path}"

    # ── Strategic Analysis ──────────────────────────────────────────────
    def analyze(
        self,
        situation: str,
        mode: str = "offline",
        financial_stability: float = 5.0,
    ) -> dict:
        """Run a full strategic analysis via the API."""
        resp = requests.post(
            self._url("/analyze"),
            json={
                "situation": situation,
                "mode": mode,
                "financial_stability": financial_stability,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()

    # ── Decisions ───────────────────────────────────────────────────────
    def log_decision(
        self,
        decision: str,
        strategy_used: str = "",
        confidence_level: int = 5,
        outcome: str = "",
        score: int = 0,
    ) -> dict:
        resp = requests.post(
            self._url("/decision"),
            json={
                "decision": decision,
                "strategy_used": strategy_used,
                "confidence_level": confidence_level,
                "outcome": outcome,
                "score": score,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def list_decisions(self) -> dict:
        resp = requests.get(self._url("/decision"), timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ── Habits ──────────────────────────────────────────────────────────
    def get_habits(self) -> dict:
        resp = requests.get(self._url("/habits"), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def update_habits(self, **kwargs) -> dict:
        resp = requests.put(self._url("/habits"), json=kwargs, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ── Profile ─────────────────────────────────────────────────────────
    def get_profile(self) -> dict:
        resp = requests.get(self._url("/profile"), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def update_profile(self, **kwargs) -> dict:
        resp = requests.put(self._url("/profile"), json=kwargs, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ── Reports ─────────────────────────────────────────────────────────
    def get_report(self, financial_stability: float = 5.0) -> dict:
        resp = requests.get(
            self._url("/report"),
            params={"financial_stability": financial_stability},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()

    def download_pdf(self, financial_stability: float = 5.0) -> bytes:
        """Download PDF report as bytes."""
        resp = requests.get(
            self._url("/report/pdf"),
            params={"financial_stability": financial_stability},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.content
