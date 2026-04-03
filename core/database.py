"""
Harvey OS – SQLite Database Layer
Central database for all persistent storage. Replaces scattered JSON files
with a unified, queryable, transactional data store.
"""

from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

from config.settings import DATA_DIR

DB_PATH = DATA_DIR / "harvey_os.db"


def _get_connection() -> sqlite3.Connection:
    """Create a connection with WAL mode and foreign keys enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# Module-level connection (thread-safe with WAL mode)
_conn: sqlite3.Connection | None = None


def get_db() -> sqlite3.Connection:
    """Return the singleton database connection."""
    global _conn
    if _conn is None:
        _conn = _get_connection()
        _initialize_schema(_conn)
    return _conn


@contextmanager
def transaction():
    """Context manager for transactional writes."""
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise


def _initialize_schema(conn: sqlite3.Connection) -> None:
    """Create all tables if they don't exist."""
    conn.executescript("""

    -- ── User Profile ──────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS profile (
        key         TEXT PRIMARY KEY,
        value       TEXT NOT NULL,
        updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Habits ────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS habits (
        key         TEXT PRIMARY KEY,
        value       REAL NOT NULL DEFAULT 0,
        updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Decisions ─────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS decisions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        decision        TEXT NOT NULL,
        strategy_used   TEXT DEFAULT '',
        confidence_level INTEGER DEFAULT 5,
        outcome         TEXT DEFAULT '',
        score           INTEGER DEFAULT 0,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Reflections ───────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS reflections (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        content     TEXT NOT NULL,
        patterns    TEXT DEFAULT '[]',   -- JSON array of detected patterns
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Detected Patterns (aggregate) ─────────────────────────────────
    CREATE TABLE IF NOT EXISTS patterns (
        name        TEXT PRIMARY KEY,
        count       INTEGER NOT NULL DEFAULT 1,
        first_seen  TEXT NOT NULL DEFAULT (datetime('now')),
        last_seen   TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Conversation Threads ──────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS threads (
        id          TEXT PRIMARY KEY,   -- UUID
        title       TEXT DEFAULT 'Untitled',
        summary     TEXT DEFAULT '',
        tag         TEXT DEFAULT '',
        created_at  TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Messages (within threads) ─────────────────────────────────────
    CREATE TABLE IF NOT EXISTS messages (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id   TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
        role        TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
        content     TEXT NOT NULL,
        tokens_est  INTEGER DEFAULT 0,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_messages_thread
        ON messages(thread_id, created_at);

    -- ── Episodic Memory ───────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS episodes (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        content     TEXT NOT NULL,
        category    TEXT DEFAULT 'general',
        importance  REAL NOT NULL DEFAULT 5.0,   -- 1-10
        emotion     TEXT DEFAULT 'neutral',
        tags        TEXT DEFAULT '[]',            -- JSON array
        created_at  TEXT NOT NULL DEFAULT (datetime('now')),
        decay_at    TEXT                          -- Nullable; when to forget
    );
    CREATE INDEX IF NOT EXISTS idx_episodes_importance
        ON episodes(importance DESC);
    CREATE INDEX IF NOT EXISTS idx_episodes_created
        ON episodes(created_at DESC);

    -- ── Learning History ──────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS learning_history (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        insights    TEXT NOT NULL,   -- JSON blob
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Conversation Log (legacy compat) ──────────────────────────────
    CREATE TABLE IF NOT EXISTS conversation_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input  TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        tag         TEXT DEFAULT '',
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    """)


# ── Migration helpers ──────────────────────────────────────────────────────

def migrate_json_to_sqlite() -> dict[str, int]:
    """
    One-time migration: read existing JSON files and import into SQLite.
    Returns counts of migrated records per table.
    """
    counts: dict[str, int] = {}

    db = get_db()

    # ── Profile ────────────────────────────────────────────────────────
    memory_file = DATA_DIR / "memory.json"
    if memory_file.exists():
        try:
            data = json.loads(memory_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                n = 0
                for key, value in data.items():
                    if key in ("patterns", "reflections"):
                        continue  # Handle separately
                    db.execute(
                        "INSERT OR IGNORE INTO profile (key, value) VALUES (?, ?)",
                        (key, str(value)),
                    )
                    n += 1

                # Migrate patterns
                for p in data.get("patterns", []):
                    db.execute(
                        "INSERT OR IGNORE INTO patterns (name) VALUES (?)", (p,)
                    )

                # Migrate reflections
                for r in data.get("reflections", []):
                    db.execute(
                        "INSERT OR IGNORE INTO reflections (content) VALUES (?)",
                        (r,),
                    )
                    n += 1

                counts["profile"] = n
        except (json.JSONDecodeError, Exception):
            pass

    # ── Habits ─────────────────────────────────────────────────────────
    habits_file = DATA_DIR / "habits.json"
    if habits_file.exists():
        try:
            data = json.loads(habits_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                n = 0
                for key, value in data.items():
                    db.execute(
                        "INSERT OR IGNORE INTO habits (key, value) VALUES (?, ?)",
                        (key, float(value)),
                    )
                    n += 1
                counts["habits"] = n
        except (json.JSONDecodeError, Exception):
            pass

    # ── Decisions ──────────────────────────────────────────────────────
    decisions_file = DATA_DIR / "decisions.json"
    if decisions_file.exists():
        try:
            data = json.loads(decisions_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                n = 0
                for d in data:
                    db.execute(
                        """INSERT OR IGNORE INTO decisions
                           (decision, strategy_used, confidence_level,
                            outcome, score, created_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            d.get("decision", ""),
                            d.get("strategy_used", ""),
                            d.get("confidence_level", 5),
                            d.get("outcome", ""),
                            d.get("score", 0),
                            d.get("timestamp", datetime.now().isoformat()),
                        ),
                    )
                    n += 1
                counts["decisions"] = n
        except (json.JSONDecodeError, Exception):
            pass

    # ── Conversations ──────────────────────────────────────────────────
    convos_file = DATA_DIR / "conversations.json"
    if convos_file.exists():
        try:
            data = json.loads(convos_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                n = 0
                for c in data:
                    db.execute(
                        """INSERT OR IGNORE INTO conversation_log
                           (user_input, ai_response, tag, created_at)
                           VALUES (?, ?, ?, ?)""",
                        (
                            c.get("user", ""),
                            c.get("ai", ""),
                            c.get("tag", ""),
                            c.get("timestamp", datetime.now().isoformat()),
                        ),
                    )
                    n += 1
                counts["conversations"] = n
        except (json.JSONDecodeError, Exception):
            pass

    # ── Learning History ───────────────────────────────────────────────
    learning_file = DATA_DIR / "learning_history.json"
    if learning_file.exists():
        try:
            data = json.loads(learning_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                n = 0
                for entry in data:
                    db.execute(
                        "INSERT INTO learning_history (insights, created_at) VALUES (?, ?)",
                        (
                            json.dumps(entry),
                            entry.get("timestamp", datetime.now().isoformat()),
                        ),
                    )
                    n += 1
                counts["learning_history"] = n
        except (json.JSONDecodeError, Exception):
            pass

    db.commit()
    return counts
