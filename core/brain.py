"""
Harvey OS – Hybrid Brain
Routes prompts to a local LLM (LM Studio) or OpenAI depending on mode.
"""

import requests
from openai import OpenAI

from config.settings import (
    LM_STUDIO_URL,
    LM_STUDIO_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    get_system_prompt,
)


class Brain:
    """Hybrid AI brain that can operate offline (LM Studio) or online (OpenAI)."""

    def __init__(self, mode: str = "offline"):
        self.mode = mode  # "offline" or "online"
        self._system_prompt = get_system_prompt()

    # ── public API ──────────────────────────────────────────────────────
    def think(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Send *prompt* to the active LLM and return the response text.
        An optional *system_prompt* overrides the default Harvey brain.
        """
        sys = system_prompt or self._system_prompt
        if self.mode == "offline":
            return self._think_offline(prompt, sys)
        return self._think_online(prompt, sys)

    # ── private helpers ─────────────────────────────────────────────────
    def _think_offline(self, prompt: str, system_prompt: str) -> str:
        """Call LM Studio's OpenAI-compatible local endpoint."""
        payload = {
            "model": LM_STUDIO_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
        }
        try:
            resp = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            return (
                "⚠️ LM Studio is not reachable at "
                f"{LM_STUDIO_URL}. Make sure it is running."
            )
        except Exception as exc:
            return f"⚠️ Offline brain error: {exc}"

    def _think_online(self, prompt: str, system_prompt: str) -> str:
        """Call OpenAI API."""
        if not OPENAI_API_KEY:
            return "⚠️ OPENAI_API_KEY is not set. Add it to your .env file."
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2048,
            )
            return completion.choices[0].message.content
        except Exception as exc:
            return f"⚠️ Online brain error: {exc}"
