"""
Harvey OS – Hybrid Brain (v2)
Routes prompts to a local LLM (LM Studio) or OpenAI depending on mode.
Now with conversation threading, episodic memory injection, and
automatic thread summarization.
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
from core.conversation_memory import ConversationMemory
from core.episodic_memory import EpisodicMemory


class Brain:
    """Hybrid AI brain with full memory integration."""

    def __init__(self, mode: str = "offline"):
        self.mode = mode  # "offline" or "online"
        self._system_prompt = get_system_prompt()
        self.memory = ConversationMemory()
        self.episodes = EpisodicMemory()

    # ── public API ──────────────────────────────────────────────────────

    def think(
        self,
        prompt: str,
        system_prompt: str | None = None,
        thread_id: str | None = None,
    ) -> str:
        """
        Send *prompt* to the active LLM and return the response text.

        If *thread_id* is provided:
        - Loads conversation history from that thread
        - Injects relevant episodic memories
        - Stores both the user message and AI response
        - Auto-summarizes the thread if it gets long

        An optional *system_prompt* overrides the default Harvey brain.
        """
        sys = system_prompt or self._system_prompt

        # Build message list
        messages: list[dict] = [{"role": "system", "content": sys}]

        # Inject episodic context into system prompt
        episodic_context = self.episodes.build_context(query=prompt, max_episodes=5)
        if episodic_context:
            messages.append({
                "role": "system",
                "content": episodic_context,
            })

        # Load conversation history if threaded
        if thread_id:
            context = self.memory.get_context(thread_id)
            messages.extend(context)

        # Add the current user message
        messages.append({"role": "user", "content": prompt})

        # Call LLM
        if self.mode == "offline":
            response = self._think_offline(messages)
        else:
            response = self._think_online(messages)

        # Store in thread if threaded
        if thread_id:
            self.memory.add_message(thread_id, "user", prompt)
            self.memory.add_message(thread_id, "assistant", response)

            # Auto-summarize if needed
            if self.memory.needs_summarization(thread_id):
                self._summarize_thread(thread_id)

        return response

    def start_thread(self, title: str = "Untitled", tag: str = "") -> str:
        """Convenience: start a new conversation thread. Returns thread_id."""
        return self.memory.start_thread(title=title, tag=tag)

    # ── private helpers ─────────────────────────────────────────────────

    def _think_offline(self, messages: list[dict]) -> str:
        """Call LM Studio's OpenAI-compatible local endpoint."""
        payload = {
            "model": LM_STUDIO_MODEL,
            "messages": messages,
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

    def _think_online(self, messages: list[dict]) -> str:
        """Call OpenAI API."""
        if not OPENAI_API_KEY:
            return "⚠️ OPENAI_API_KEY is not set. Add it to your .env file."
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            )
            return completion.choices[0].message.content
        except Exception as exc:
            return f"⚠️ Online brain error: {exc}"

    def _summarize_thread(self, thread_id: str) -> None:
        """Use the LLM to summarize a long conversation thread."""
        full_text = self.memory.get_summarization_text(thread_id)
        summary_prompt = (
            "Summarize the following conversation into a concise paragraph "
            "capturing the key topics, decisions made, and any unresolved items. "
            "Focus on strategic context that would be useful for future reference.\n\n"
            f"{full_text}"
        )
        messages = [
            {"role": "system", "content": "You are a concise summarizer."},
            {"role": "user", "content": summary_prompt},
        ]

        if self.mode == "offline":
            summary = self._think_offline(messages)
        else:
            summary = self._think_online(messages)

        if not summary.startswith("⚠️"):
            self.memory.update_summary(thread_id, summary)
