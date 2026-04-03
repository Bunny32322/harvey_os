"""
Harvey OS – Conversation Memory (Threaded)
Full conversation threading with context management, automatic
summarization, and cross-thread recall.

This is the core "Harvey remembers everything" system.
"""

from __future__ import annotations

import uuid
import json
from datetime import datetime

from core.database import get_db, transaction


# ── Rough token estimator (1 token ≈ 4 chars) ─────────────────────────────
def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class ConversationMemory:
    """
    Manages threaded conversations with smart context windowing.

    Key features:
    - Each conversation is a "thread" with a UUID
    - Messages stored with role, content, and token estimates
    - Smart context window: recent messages + thread summary
    - Cross-thread search via semantic matching
    - Auto-summarization when threads grow long
    """

    MAX_CONTEXT_TOKENS = 6000  # Max tokens to inject as context
    SUMMARY_THRESHOLD = 20    # Summarize after this many messages

    # ── Thread lifecycle ───────────────────────────────────────────────

    def start_thread(self, title: str = "Untitled", tag: str = "") -> str:
        """Create a new conversation thread. Returns thread_id (UUID)."""
        thread_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        db = get_db()
        db.execute(
            "INSERT INTO threads (id, title, tag, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (thread_id, title, tag, now, now),
        )
        db.commit()
        return thread_id

    def list_threads(self, limit: int = 50) -> list[dict]:
        """List recent threads, newest first."""
        db = get_db()
        rows = db.execute(
            """SELECT id, title, summary, tag, created_at, updated_at,
                      (SELECT COUNT(*) FROM messages WHERE thread_id = threads.id) AS msg_count
               FROM threads
               ORDER BY updated_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_thread(self, thread_id: str) -> dict | None:
        """Get thread metadata."""
        db = get_db()
        row = db.execute(
            "SELECT * FROM threads WHERE id = ?", (thread_id,)
        ).fetchone()
        return dict(row) if row else None

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its messages (cascade)."""
        db = get_db()
        db.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
        db.commit()
        return True

    # ── Message management ─────────────────────────────────────────────

    def add_message(
        self,
        thread_id: str,
        role: str,
        content: str,
    ) -> int:
        """
        Add a message to a thread.
        role: 'user', 'assistant', or 'system'
        Returns the message id.
        """
        tokens = _estimate_tokens(content)
        now = datetime.now().isoformat()
        db = get_db()
        cursor = db.execute(
            """INSERT INTO messages (thread_id, role, content, tokens_est, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (thread_id, role, content, tokens, now),
        )
        # Update thread's updated_at
        db.execute(
            "UPDATE threads SET updated_at = ? WHERE id = ?",
            (now, thread_id),
        )
        db.commit()

        msg_id = cursor.lastrowid

        # Auto-title the thread from the first user message
        thread = self.get_thread(thread_id)
        if thread and thread["title"] == "Untitled" and role == "user":
            # Use the first ~80 chars as title
            title = content[:80].strip()
            if len(content) > 80:
                title += "…"
            db.execute(
                "UPDATE threads SET title = ? WHERE id = ?",
                (title, thread_id),
            )
            db.commit()

        return msg_id

    def get_messages(
        self,
        thread_id: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict]:
        """Get messages in a thread, oldest first."""
        db = get_db()
        if limit:
            rows = db.execute(
                """SELECT * FROM messages WHERE thread_id = ?
                   ORDER BY created_at ASC LIMIT ? OFFSET ?""",
                (thread_id, limit, offset),
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT * FROM messages WHERE thread_id = ?
                   ORDER BY created_at ASC""",
                (thread_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def message_count(self, thread_id: str) -> int:
        """Count messages in a thread."""
        db = get_db()
        row = db.execute(
            "SELECT COUNT(*) as cnt FROM messages WHERE thread_id = ?",
            (thread_id,),
        ).fetchone()
        return row["cnt"] if row else 0

    # ── Smart Context Window ───────────────────────────────────────────

    def get_context(
        self,
        thread_id: str,
        max_tokens: int | None = None,
    ) -> list[dict]:
        """
        Build a context window for the LLM.

        Strategy:
        1. If total tokens < max, return all messages
        2. If too long, return:  [summary] + [recent N messages]

        Returns list of dicts with 'role' and 'content'.
        """
        max_tok = max_tokens or self.MAX_CONTEXT_TOKENS
        all_msgs = self.get_messages(thread_id)

        if not all_msgs:
            return []

        # Calculate total tokens
        total = sum(m["tokens_est"] for m in all_msgs)

        if total <= max_tok:
            return [{"role": m["role"], "content": m["content"]} for m in all_msgs]

        # Need to truncate: use summary + recent messages
        thread = self.get_thread(thread_id)
        context: list[dict] = []

        # Add thread summary as system context if available
        if thread and thread.get("summary"):
            context.append({
                "role": "system",
                "content": f"[Previous conversation summary]: {thread['summary']}",
            })
            used = _estimate_tokens(thread["summary"])
        else:
            used = 0

        # Fill from the end (most recent messages first)
        recent: list[dict] = []
        for m in reversed(all_msgs):
            msg_tokens = m["tokens_est"]
            if used + msg_tokens > max_tok:
                break
            recent.insert(0, {"role": m["role"], "content": m["content"]})
            used += msg_tokens

        context.extend(recent)
        return context

    # ── Thread Summarization ───────────────────────────────────────────

    def update_summary(self, thread_id: str, summary: str) -> None:
        """Store a summary for the thread (called after LLM summarization)."""
        db = get_db()
        db.execute(
            "UPDATE threads SET summary = ? WHERE id = ?",
            (summary, thread_id),
        )
        db.commit()

    def needs_summarization(self, thread_id: str) -> bool:
        """Check if thread has grown past the summarization threshold."""
        count = self.message_count(thread_id)
        thread = self.get_thread(thread_id)
        # Re-summarize every SUMMARY_THRESHOLD messages
        return count > self.SUMMARY_THRESHOLD and (
            not thread or not thread.get("summary")
        )

    def get_summarization_text(self, thread_id: str) -> str:
        """Get the full thread text for summarization by the LLM."""
        msgs = self.get_messages(thread_id)
        lines: list[str] = []
        for m in msgs:
            prefix = "User" if m["role"] == "user" else "Harvey OS"
            lines.append(f"{prefix}: {m['content']}")
        return "\n\n".join(lines)

    # ── Cross-Thread Search ────────────────────────────────────────────

    def search_messages(self, query: str, limit: int = 10) -> list[dict]:
        """
        Basic text search across all messages.
        For semantic search, use the vector store.
        """
        db = get_db()
        rows = db.execute(
            """SELECT m.*, t.title as thread_title
               FROM messages m
               JOIN threads t ON m.thread_id = t.id
               WHERE m.content LIKE ?
               ORDER BY m.created_at DESC
               LIMIT ?""",
            (f"%{query}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_recent_context_across_threads(
        self, limit: int = 5
    ) -> list[dict]:
        """Get the most recent messages across all threads for global context."""
        db = get_db()
        rows = db.execute(
            """SELECT m.role, m.content, t.title as thread_title, m.created_at
               FROM messages m
               JOIN threads t ON m.thread_id = t.id
               ORDER BY m.created_at DESC
               LIMIT ?""",
            (limit * 2,),  # Get pairs
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Statistics ─────────────────────────────────────────────────────

    def stats(self) -> dict:
        """Return conversation statistics."""
        db = get_db()
        thread_count = db.execute("SELECT COUNT(*) as cnt FROM threads").fetchone()["cnt"]
        msg_count = db.execute("SELECT COUNT(*) as cnt FROM messages").fetchone()["cnt"]
        total_tokens = db.execute(
            "SELECT COALESCE(SUM(tokens_est), 0) as total FROM messages"
        ).fetchone()["total"]

        return {
            "total_threads": thread_count,
            "total_messages": msg_count,
            "total_tokens_estimated": total_tokens,
        }
