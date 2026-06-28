#!/usr/bin/env python3
"""
EasyWork Knowledge Store — SQLite + FTS5 backed conversation & knowledge storage.

Architecture (inspired by claude-mem, continuity-v2, am-memory):

  Stop hook        → per-turn Q&A  → turns table (REAL-TIME)
  PostToolUse hook → tool metadata → tool_calls table
  SessionEnd hook  → session close → sessions table update + facts promotion

Queryable via SQL:
  sqlite3 knowledge/conversation.db "SELECT * FROM turns WHERE content MATCH 'HBase'"
  sqlite3 knowledge/conversation.db "SELECT session_id, COUNT(*) FROM turns GROUP BY session_id"

Usage:
  python hooks/knowledge-store.py init              # Create DB + schema
  python hooks/knowledge-store.py turn <json>       # Insert a turn (Q&A pair)
  python hooks/knowledge-store.py tool-call <json>  # Insert a tool call record
  python hooks/knowledge-store.py session-end <json> # Mark session ended
  python hooks/knowledge-store.py search <query>     # FTS5 search
  python hooks/knowledge-store.py recent [N]         # Recent turns
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Fix Windows I/O encoding for emoji/Chinese — stdin/stdout default to GBK on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "knowledge" / "conversation.db"

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT,
    ended_at TEXT,
    domain TEXT DEFAULT 'development',
    tool_calls_count INTEGER DEFAULT 0,
    turn_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_sessions_ended ON sessions(ended_at);

-- Turns: per-turn Q&A pairs (INSERTED ON EVERY Stop HOOK)
CREATE TABLE IF NOT EXISTS turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    turn_number INTEGER NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    role TEXT NOT NULL CHECK(role IN ('user','assistant','system','tool')),
    content TEXT NOT NULL,
    duration_seconds REAL,
    content_preview TEXT GENERATED ALWAYS AS (substr(content, 1, 200)) STORED
);
CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id, turn_number);
CREATE INDEX IF NOT EXISTS idx_turns_timestamp ON turns(timestamp);
CREATE INDEX IF NOT EXISTS idx_turns_role ON turns(role);

-- FTS5 full-text index on turn content
CREATE VIRTUAL TABLE IF NOT EXISTS turns_fts USING fts5(
    content, role,
    content='turns', content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS turns_ai AFTER INSERT ON turns BEGIN
    INSERT INTO turns_fts(rowid, content, role)
    VALUES (new.rowid, new.content, new.role);
END;

CREATE TRIGGER IF NOT EXISTS turns_ad AFTER DELETE ON turns BEGIN
    INSERT INTO turns_fts(turns_fts, rowid, content, role)
    VALUES ('delete', old.rowid, old.content, old.role);
END;

-- Tool calls: per-tool-call instrumentation
CREATE TABLE IF NOT EXISTS tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    turn_number INTEGER,
    tool_name TEXT NOT NULL,
    file_paths TEXT,
    duration_ms INTEGER DEFAULT 0,
    timestamp TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_tool_session ON tool_calls(session_id);
CREATE INDEX IF NOT EXISTS idx_tool_name ON tool_calls(tool_name);

-- Facts: upgraded cross-session knowledge
CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL,
    dimension TEXT NOT NULL DEFAULT 'analysis',
    title TEXT NOT NULL,
    fact TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    tags TEXT DEFAULT '[]',
    source_session TEXT REFERENCES sessions(id),
    supersedes INTEGER REFERENCES facts(id),
    retracted INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_facts_domain ON facts(domain);
CREATE INDEX IF NOT EXISTS idx_facts_retracted ON facts(retracted);

-- FTS5 on facts
CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
    title, fact, domain,
    content='facts', content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
    INSERT INTO facts_fts(rowid, title, fact, domain)
    VALUES (new.rowid, new.title, new.fact, new.domain);
END;
"""


def get_conn() -> sqlite3.Connection:
    """Get a SQLite connection with WAL mode and optimized settings."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create database and all tables if they don't exist. Also runs migrations."""
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        # Migrations: add columns that may not exist in older databases
        _migrate_add_column(conn, "turns", "duration_seconds", "REAL")
        conn.commit()
        print(f"[knowledge-store] Database initialized at {DB_PATH}", file=sys.stderr)
    finally:
        conn.close()


def _migrate_add_column(conn: sqlite3.Connection, table: str, column: str, col_type: str):
    """Add a column if it doesn't already exist (idempotent migration)."""
    existing = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


def ensure_session(session_id: str) -> None:
    """Ensure a session row exists (idempotent)."""
    conn = get_conn()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO sessions (id, started_at) VALUES (?, ?)",
            (session_id, datetime.now(timezone.utc).astimezone().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def insert_turn(session_id: str, turn_number: int, role: str, content: str, timestamp: str = None, duration_seconds: float = None) -> int:
    """Insert a single conversation turn. Returns turn rowid.

    If timestamp is provided, use it (from transcript event).
    If duration_seconds is provided, store it (for assistant turns: elapsed since user prompt).
    Otherwise use current local time.
    """
    ensure_session(session_id)
    conn = get_conn()
    try:
        # Use provided timestamp if available, otherwise current local time
        ts = timestamp or datetime.now(timezone.utc).astimezone().isoformat()
        cursor = conn.execute(
            "INSERT INTO turns (session_id, turn_number, timestamp, role, content, duration_seconds) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, turn_number, ts, role, content, duration_seconds),
        )
        # Update session turn count
        conn.execute(
            "UPDATE sessions SET turn_count = turn_count + 1 WHERE id = ?",
            (session_id,),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def insert_tool_call(
    session_id: str, tool_name: str, file_paths: str = "",
    duration_ms: int = 0, turn_number: int = 0,
) -> int:
    """Insert a tool call record."""
    ensure_session(session_id)
    conn = get_conn()
    try:
        cursor = conn.execute(
            "INSERT INTO tool_calls (session_id, turn_number, tool_name, file_paths, duration_ms) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id, turn_number, tool_name, file_paths, duration_ms),
        )
        conn.execute(
            "UPDATE sessions SET tool_calls_count = tool_calls_count + 1 WHERE id = ?",
            (session_id,),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def end_session(session_id: str) -> None:
    """Mark a session as ended."""
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE sessions SET ended_at = ? WHERE id = ? AND ended_at IS NULL",
            (datetime.now(timezone.utc).astimezone().isoformat(), session_id),
        )
        conn.commit()
    finally:
        conn.close()


def search(query: str, limit: int = 20) -> list[dict]:
    """FTS5 search across turns."""
    conn = get_conn()
    try:
        # FTS5 search with external content table (reads content from turns table)
        rows = conn.execute(
            "SELECT t.id, t.session_id, t.turn_number, t.timestamp, t.role, "
            "t.content_preview "
            "FROM turns t "
            "JOIN turns_fts fts ON t.rowid = fts.rowid "
            "WHERE turns_fts MATCH ? "
            "ORDER BY rank "
            "LIMIT ?",
            (query, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.OperationalError:
        # FTS5 query syntax error — fall back to LIKE
        rows = conn.execute(
            "SELECT id, session_id, turn_number, timestamp, role, content_preview "
            "FROM turns WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def recent_turns(limit: int = 10) -> list[dict]:
    """Get the most recent turns."""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, session_id, turn_number, timestamp, role, duration_seconds, content_preview "
            "FROM turns ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_full(query: str, limit: int = 10) -> list[dict]:
    """FTS5 search across turns — returns FULL content (not just preview)."""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT t.id, t.session_id, t.turn_number, t.timestamp, t.role, "
            "t.duration_seconds, t.content "
            "FROM turns t "
            "JOIN turns_fts fts ON t.rowid = fts.rowid "
            "WHERE turns_fts MATCH ? "
            "ORDER BY rank "
            "LIMIT ?",
            (query, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.OperationalError:
        rows = conn.execute(
            "SELECT id, session_id, turn_number, timestamp, role, duration_seconds, content "
            "FROM turns WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_schema() -> list[str]:
    """Return CREATE TABLE statements for all user tables."""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts_%' ORDER BY name"
        ).fetchall()
        return [r[0] for r in rows if r[0]]
    finally:
        conn.close()


def get_summary() -> dict:
    """Overall knowledge base summary."""
    conn = get_conn()
    try:
        sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        sessions_active = conn.execute("SELECT COUNT(*) FROM sessions WHERE ended_at IS NULL").fetchone()[0]
        turns = conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
        user_turns = conn.execute("SELECT COUNT(*) FROM turns WHERE role='user'").fetchone()[0]
        assistant_turns = conn.execute("SELECT COUNT(*) FROM turns WHERE role='assistant'").fetchone()[0]
        tool_calls = conn.execute("SELECT COUNT(*) FROM tool_calls").fetchone()[0]
        facts = conn.execute("SELECT COUNT(*) FROM facts WHERE retracted=0").fetchone()[0]
        return {
            "sessions": {"total": sessions, "active": sessions_active},
            "turns": {"total": turns, "user": user_turns, "assistant": assistant_turns},
            "tool_calls": tool_calls,
            "facts": facts,
        }
    finally:
        conn.close()


def get_turn_detail(turn_id: int) -> dict | None:
    """Get a single turn with full content."""
    conn = get_conn()
    try:
        r = conn.execute(
            "SELECT id, session_id, turn_number, timestamp, role, duration_seconds, content FROM turns WHERE id=?",
            (turn_id,),
        ).fetchone()
        return dict(r) if r else None
    finally:
        conn.close()


def browse_turns(limit: int = 20, role: str = "") -> list[dict]:
    """Browse recent turns in a human-readable format."""
    conn = get_conn()
    try:
        if role in ("user", "assistant"):
            rows = conn.execute(
                "SELECT id, session_id, turn_number, timestamp, role, duration_seconds, content_preview "
                "FROM turns WHERE role = ? ORDER BY id DESC LIMIT ?",
                (role, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, session_id, turn_number, timestamp, role, duration_seconds, content_preview "
                "FROM turns ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def session_stats(session_id: str) -> dict:
    """Get stats for a session."""
    conn = get_conn()
    try:
        s = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not s:
            return {}
        turns = conn.execute(
            "SELECT role, COUNT(*) as cnt FROM turns WHERE session_id = ? GROUP BY role",
            (session_id,),
        ).fetchall()
        tools = conn.execute(
            "SELECT tool_name, COUNT(*) as cnt FROM tool_calls WHERE session_id = ? GROUP BY tool_name",
            (session_id,),
        ).fetchall()
        return {
            "session": dict(s),
            "turns_by_role": {r["role"]: r["cnt"] for r in turns},
            "tools_by_name": {r["tool_name"]: r["cnt"] for r in tools},
        }
    finally:
        conn.close()


# ─── CLI ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python knowledge-store.py <command> [args]\n"
            "\n  User commands:\n"
            "    init              Create database and all tables\n"
            "    schema            Show table schema (CREATE statements)\n"
            "    summary           Overall stats (sessions/turns/facts)\n"
            "    browse   [N] [role]  Browse last N turns (default: 20)\n"
            "    turn-detail <id>   Show full content of a turn\n"
            "    search   <query>  FTS5 full-text search (previews)\n"
            "    search-full <query> [N]  FTS5 search with FULL content\n"
            "    recent   [N]      Recent turns (JSON, default: 10)\n"
            "    stats    <id>     Session stats\n"
            "\n  Internal commands (called by hooks):\n"
            "    turn <json>       Insert a turn\n"
            "    tool-call <json>  Insert a tool call\n"
            "    session-end <json> Mark session ended",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        init_db()

    elif cmd == "schema":
        statements = get_schema()
        for s in statements:
            print(f"{s};\n")

    elif cmd == "summary":
        s = get_summary()
        print(f"[Knowledge Base Summary]")
        print(f"  Sessions:   {s['sessions']['total']} total ({s['sessions']['active']} active)")
        print(f"  Turns:      {s['turns']['total']} total ({s['turns']['user']} user, {s['turns']['assistant']} assistant)")
        print(f"  Tool calls: {s['tool_calls']}")
        print(f"  Facts:      {s['facts']}")

    elif cmd == "browse":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        role = sys.argv[3] if len(sys.argv) > 3 else ""
        rows = browse_turns(limit, role)
        if not rows:
            print("(no turns in database)")
            sys.exit(0)
        print(f"{'ID':<6} {'Session':<12} {'T#':<4} {'Role':<10} {'Time':<26} {'⏱':>6} {'Preview':<48}")
        print("-" * 114)
        for r in rows:
            sid_short = r.get("session_id", "")[:12]
            ts = r.get("timestamp", "")[:25] if r.get("timestamp") else ""
            dur = r.get("duration_seconds")
            dur_str = f"{dur:.0f}s" if dur else "-"
            preview = r.get("content_preview", "")[:46] or "(no preview)"
            print(f"{r['id']:<6} {sid_short:<12} {r.get('turn_number',0):<4} {r['role']:<10} {ts:<26} {dur_str:>6} {preview:<48}")

    elif cmd == "turn-detail":
        if len(sys.argv) < 3:
            print("Usage: python knowledge-store.py turn-detail <id>", file=sys.stderr)
            sys.exit(1)
        detail = get_turn_detail(int(sys.argv[2]))
        if detail:
            print(f"=== Turn #{detail['id']} ===")
            print(f"Session:    {detail['session_id']}")
            print(f"Turn #:     {detail['turn_number']}")
            print(f"Role:       {detail['role']}")
            print(f"Timestamp:  {detail['timestamp']}")
            if detail.get("duration_seconds"):
                mins = int(detail["duration_seconds"] // 60)
                secs = detail["duration_seconds"] % 60
                print(f"Duration:   {mins}m {secs:.0f}s ({detail['duration_seconds']:.1f}s)")
            print(f"Content:\n{detail['content']}")
        else:
            print(f"Turn {sys.argv[2]} not found.")

    elif cmd == "turn":
        data = json.loads(sys.stdin.read())
        rid = insert_turn(
            data["session_id"],
            data.get("turn_number", 0),
            data["role"],
            data["content"],
            data.get("timestamp"),  # optional: event time from transcript
            data.get("duration_seconds"),  # optional: elapsed time (assistant turns)
        )
        print(rid)

    elif cmd == "tool-call":
        data = json.loads(sys.stdin.read())
        rid = insert_tool_call(
            data["session_id"],
            data["tool_name"],
            data.get("file_paths", ""),
            data.get("duration_ms", 0),
            data.get("turn_number", 0),
        )
        print(rid)

    elif cmd == "session-end":
        data = json.loads(sys.stdin.read())
        end_session(data.get("session_id", ""))
        print("ok")

    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        results = search(query)
        # Use ensure_ascii to avoid Windows GBK encoding issues with emoji
        print(json.dumps(results, ensure_ascii=True, indent=2))

    elif cmd == "search-full":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        results = search_full(query, limit)
        for r in results:
            dur = r.get("duration_seconds")
            dur_str = f" ({dur:.0f}s)" if dur else ""
            print(f"{'='*70}")
            print(f"[#{r['id']}] {r['role']} | {r['timestamp']}{dur_str}")
            print(f"{'='*70}")
            print(r.get("content", "(no content)"))
            print()

    elif cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        results = recent_turns(limit)
        print(json.dumps(results, ensure_ascii=True, indent=2))

    elif cmd == "stats":
        sid = sys.argv[2] if len(sys.argv) > 2 else ""
        results = session_stats(sid)
        print(json.dumps(results, ensure_ascii=True, indent=2))

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
