#!/usr/bin/env python3
"""
EasyWork Knowledge Base Hooks — v2.0

Handles Claude Code lifecycle events for automatic knowledge capture.

Architecture (inspired by claude-memory-compiler + memory-mason):

  SessionStart  → injects knowledge index into context
  PostToolUse   → appends event to per-session buffer (session_id from hook JSON)
  PreCompact    → safety net: captures context before compaction discards it
  SessionEnd    → spawns detached knowledge-flush.py background worker

Key fixes over v1:
  - Uses hook event's `session_id` (not os.getpid()) → no PID fragmentation
  - Reads `transcript_path` to extract actual conversation content
  - Detached background flush (SessionEnd doesn't block)
  - Recursion guard: CLAUDE_INVOKED_BY env var
  - Deduplication: SHA-256 state tracking, 60s dedup window

Usage:
  python hooks/knowledge-hooks.py session-start    # SessionStart hook
  python hooks/knowledge-hooks.py post-tool-use    # PostToolUse hook
  python hooks/knowledge-hooks.py pre-compact      # PreCompact hook
  python hooks/knowledge-hooks.py session-end      # SessionEnd hook
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Fix Windows stdout encoding for emoji output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Windows: prevent console windows from popping up for subprocess calls
CREATE_NO_WINDOW = 0x08000000
WINDOWS_FLAGS = 0x00000200 | 0x00000008 | CREATE_NO_WINDOW  # CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS | CREATE_NO_WINDOW


# ─── Config ──────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "knowledge-template"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
BUFFER_DIR = KNOWLEDGE_DIR / ".buffer"
FLUSH_SCRIPT = PROJECT_ROOT / "hooks" / "knowledge-flush.py"
STORE_SCRIPT = PROJECT_ROOT / "hooks" / "knowledge-store.py"
STATE_DIR = BUFFER_DIR  # reuse buffer dir for state files
KNOWLEDGE_INDEX = KNOWLEDGE_DIR / "README.md"
MEMORY_FILE = PROJECT_ROOT / "MEMORY.md"

# Tools that trigger knowledge capture
INTERESTING_TOOLS = {"Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebSearch", "WebFetch"}

# File patterns worth tracking (must match at least one)
INTERESTING_FILE_PATTERNS = [
    r"\.py$", r"\.js$", r"\.ts$", r"\.go$", r"\.java$", r"\.rs$", r"\.swift$",
    r"\.md$", r"\.yaml$", r"\.yml$", r"\.json$", r"\.toml$",
    r"SKILL\.md$", r"CLAUDE\.md$", r"README\.md$",
    r"src/", r"skills/", r"knowledge/", r"\.claude/", r"hooks/",
]

# Read-only tools (source discovery)
READ_TOOLS = {"Read", "Grep", "Glob", "WebSearch", "WebFetch"}
# Write tools (knowledge production)
WRITE_TOOLS = {"Write", "Edit"}

# Max context to inject on SessionStart (characters)
MAX_SESSION_START_CONTEXT = 15000


# ─── Recursion Guard ──────────────────────────────────────────────────

def is_recursive() -> bool:
    """Check if this hook was called by our own flush worker (prevents infinite loops)."""
    return os.environ.get("CLAUDE_INVOKED_BY", "").startswith("knowledge_")


# ─── Session ID ───────────────────────────────────────────────────────

def get_session_id_from_event(event: dict) -> str:
    """
    Extract session_id from hook event JSON.
    Falls back to compound PID+timestamp if not available (older Claude Code versions).
    """
    sid = event.get("session_id", "")
    if sid:
        # Sanitize: remove path separators and non-alphanumeric chars
        return re.sub(r"[^\w\-]", "_", sid)[:64]
    # Fallback: PID + timestamp (compound key pattern from oh-my-claudecode)
    return f"pid-{os.getpid()}-{int(time.time() * 1000)}"


def get_buffer_path(session_id: str) -> Path:
    """Get the per-session JSONL buffer path."""
    BUFFER_DIR.mkdir(parents=True, exist_ok=True)
    return BUFFER_DIR / f"{session_id}.jsonl"


# ─── File Filtering ───────────────────────────────────────────────────

def is_interesting_read(file_path: str) -> bool:
    """Check if a file path is worth tracking."""
    if not file_path:
        return False
    for pattern in INTERESTING_FILE_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False


# ─── Detached Process Spawn ───────────────────────────────────────────

def spawn_detached(args: list[str]):
    """
    Spawn a fully detached background process.
    Windows: CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
    Unix: start_new_session=True
    """
    if sys.platform == "win32":
        # DETACHED_PROCESS = 0x00000008, CREATE_NEW_PROCESS_GROUP = 0x00000200
        flags = 0x00000200 | 0x00000008
        subprocess.Popen(
            args,
            creationflags=flags,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.Popen(
            args,
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


# ─── Init from Template ────────────────────────────────────────────────

def init_knowledge_dir() -> bool:
    """
    Bootstrap knowledge/ from knowledge-template/ if it doesn't exist.
    Called automatically by SessionStart. Can also be invoked manually:
      python hooks/knowledge-hooks.py init

    Returns True if init was performed, False if already exists.
    """
    if KNOWLEDGE_DIR.exists():
        return False

    if not TEMPLATE_DIR.exists():
        print(f"[knowledge-hooks] No template at {TEMPLATE_DIR}, skipping init", file=sys.stderr)
        return False

    print(f"[knowledge-hooks] Bootstrapping {KNOWLEDGE_DIR} from {TEMPLATE_DIR}...", file=sys.stderr)
    _copy_tree(TEMPLATE_DIR, KNOWLEDGE_DIR)
    print(f"[knowledge-hooks] Knowledge dir initialized.", file=sys.stderr)
    return True


def _copy_tree(src: Path, dst: Path):
    """Copy directory tree, skipping files that would contain user data."""
    import shutil
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        s = src / item.name
        d = dst / item.name
        if s.is_dir():
            _copy_tree(s, d)
        else:
            # Only copy structural files, never user data
            if item.name in ("_index.md", "README.md", ".gitkeep"):
                shutil.copy2(s, d)


# ─── SessionStart ────────────────────────────────────────────────────

def handle_session_start():
    """
    Injects knowledge context into each new session.
    Reads knowledge/README.md (index) + most recent daily log.
    Outputs JSON with `additionalContext` on stdout.

    Also auto-initializes knowledge/ from template if it doesn't exist.
    Pattern: claude-memory-compiler's session-start.py
    """
    if is_recursive():
        return

    # Auto-init knowledge/ from template on first run
    init_knowledge_dir()

    contexts = []

    # 1. Knowledge index
    if KNOWLEDGE_INDEX.exists():
        try:
            content = KNOWLEDGE_INDEX.read_text(encoding="utf-8")
            if len(content) > MAX_SESSION_START_CONTEXT // 2:
                # Truncate: keep first ~500 chars (overview) + last ~2000 (most recent entries)
                content = content[:500] + "\n\n... (中间省略) ...\n\n" + content[-2000:]
            contexts.append(f"## 知识库索引\n\n{content}")
        except Exception:
            pass

    # 2. Most recent daily log (if exists today)
    daily_dir = PROJECT_ROOT / "knowledge" / "conversation" / "daily"
    if daily_dir.exists():
        today = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
        today_log = daily_dir / f"{today}.md"
        if today_log.exists():
            try:
                content = today_log.read_text(encoding="utf-8")
                # Keep last ~3000 chars
                if len(content) > 3000:
                    content = content[-3000:]
                contexts.append(f"## 今日会话记录 (最后部分)\n\n{content}")
            except Exception:
                pass

    if contexts:
        combined = "\n\n---\n\n".join(contexts)
        # Output as structured JSON on stdout (Claude Code reads this as additionalContext)
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": combined[:MAX_SESSION_START_CONTEXT],
            }
        }
        print(json.dumps(output, ensure_ascii=False))
    else:
        # Minimal output — knowledge base is empty
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "📚 EasyWork 知识库已准备就绪。当前知识库为空，随会话自动积累。",
            }
        }
        print(json.dumps(output, ensure_ascii=False))


# ─── PostToolUse ─────────────────────────────────────────────────────

def handle_post_tool_use():
    """
    Called after every tool use. Appends event to per-session buffer.

    Key fix: uses session_id from hook event JSON (not os.getpid()),
    so all events from the same Claude Code session go to ONE buffer file.

    Input: stdin JSON from Claude Code hook
    """
    if is_recursive():
        return

    try:
        event = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = event.get("tool_name", "")
    if tool_name not in INTERESTING_TOOLS:
        return

    tool_input = event.get("tool_input", {})

    # Extract file paths from tool input
    file_paths = []
    if "file_path" in tool_input:
        file_paths.append(str(tool_input["file_path"]))
    if "pattern" in tool_input:
        file_paths.append(str(tool_input["pattern"]))
    if "paths" in tool_input and isinstance(tool_input["paths"], list):
        file_paths.extend(str(p) for p in tool_input["paths"])

    # Filter to interesting files only (for read tools)
    if tool_name in READ_TOOLS:
        if file_paths and not any(is_interesting_read(p) for p in file_paths):
            return

    # Get stable session_id from hook event (NOT os.getpid!)
    session_id = get_session_id_from_event(event)

    # Build event record
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "files": file_paths,
        "duration_ms": 0,  # not always available in PostToolUse
    }

    # Append to session buffer
    buffer_path = get_buffer_path(session_id)
    with open(buffer_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ─── PreCompact ──────────────────────────────────────────────────────

def handle_pre_compact():
    """
    Safety net: captures context before Claude Code auto-compacts the context window.
    Long sessions may trigger multiple compactions before SessionEnd — without this,
    intermediate context is lost.

    Pattern: claude-memory-compiler's pre-compact.py
    Guard: skips if transcript_path is empty (known Claude Code bug)
    """
    if is_recursive():
        return

    try:
        event = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    session_id = get_session_id_from_event(event)
    transcript_path = event.get("transcript_path", "")

    # Guard: skip if no transcript path (known CC bug #13668)
    if not transcript_path:
        return

    buffer_path = get_buffer_path(session_id)

    # Spawn detached flush for pre-compact (lighter: captures context before it's lost)
    env = os.environ.copy()
    env["CLAUDE_INVOKED_BY"] = "knowledge_compact"

    if sys.platform == "win32":
        subprocess.Popen(
            [sys.executable, str(FLUSH_SCRIPT), session_id, transcript_path, str(buffer_path)],
            creationflags=WINDOWS_FLAGS,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
    else:
        subprocess.Popen(
            [sys.executable, str(FLUSH_SCRIPT), session_id, transcript_path, str(buffer_path)],
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

    print(f"[knowledge-hooks] PreCompact: spawned flush for {session_id}", file=sys.stderr)


# ─── SessionEnd ──────────────────────────────────────────────────────

# ─── Stop (Per-Turn Capture) ──────────────────────────────────────────

def handle_stop():
    """
    Called when Claude finishes responding at the end of EACH turn.
    This is the per-turn capture mechanism — writes Q&A to SQLite IMMEDIATELY.

    Reads the transcript tail, extracts the latest user prompt + assistant response
    WITH their original event timestamps, and stores them as turns in SQLite.

    Pattern: claude-mem's Stop hook → SQLite per-turn insert
    """
    if is_recursive():
        return

    # ── 0. Parse hook event ──────────────────────────────────────────
    try:
        event = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        _log_stop("FAIL: cannot parse stdin JSON")
        return

    # Log full event keys for diagnostics (once per session)
    _log_stop(f"EVENT keys: {list(event.keys())} | stop_hook_active={event.get('stop_hook_active')}")

    session_id = get_session_id_from_event(event)
    transcript_path = event.get("transcript_path", "")

    if not transcript_path:
        _log_stop("SKIP: no transcript_path in event")
        return

    # ── 1. Ensure SQLite DB exists ───────────────────────────────────
    try:
        subprocess.run(
            [sys.executable, str(STORE_SCRIPT), "init"],
            capture_output=True, timeout=5,
            creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except Exception as e:
        _log_stop(f"FAIL: db init error: {e}")
        return

    # ── 2. Read transcript tail ──────────────────────────────────────
    tp = Path(transcript_path)
    if not tp.exists():
        _log_stop(f"SKIP: transcript not found: {transcript_path}")
        return

    # Track last-read position per session+transcript (avoid re-reading)
    # Keyed by session_id + transcript filename to detect transcript rotation after /compact
    transcript_key = tp.name.replace(".jsonl", "").replace(".json", "")
    cursor_path = STATE_DIR / f"{session_id}_{transcript_key}.cursor"
    last_pos = 0
    if cursor_path.exists():
        try:
            last_pos = int(cursor_path.read_text().strip())
        except Exception:
            last_pos = 0

    try:
        file_size = tp.stat().st_size
        # CRITICAL: if file_size < last_pos, the transcript was truncated (e.g. after /compact).
        # Reset cursor to 0 so we don't skip new content.
        if file_size < last_pos:
            _log_stop(f"RESET cursor: file_size({file_size}) < last_pos({last_pos}) — /compact detected")
            last_pos = 0
        if file_size <= last_pos:
            _log_stop(f"SKIP: no new content (file={file_size}, cursor={last_pos})")
            return  # No new content

        with open(tp, "r", encoding="utf-8") as f:
            f.seek(max(0, last_pos))
            new_content = f.read()

        # ── 3. Extract latest user prompt and assistant response ──────
        latest_user = None
        latest_user_ts = None
        latest_assistant = None
        latest_assistant_ts = None
        turn_number = 0

        for line in new_content.strip().split("\n"):
            if not line:
                continue
            try:
                msg_event = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg = msg_event.get("message", {})
            role = msg.get("role", "")

            if role == "user":
                content = msg.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text"
                    )
                if content and len(content) > 5:
                    # Skip system-injected messages (session summaries, local commands)
                    if not _is_system_noise(content):
                        latest_user = content
                        latest_user_ts = msg_event.get("timestamp", "")
                        turn_number = msg_event.get("turn_number", turn_number)

            elif role == "assistant":
                content = msg.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text"
                    )
                if content and len(content) > 10:
                    latest_assistant = content
                    latest_assistant_ts = msg_event.get("timestamp", "")
                    turn_number = msg_event.get("turn_number", turn_number)

        # ── 4. Compute duration & insert turns with precise event timestamps ─
        # Parse timestamps to calculate elapsed seconds between user prompt and assistant reply
        duration = _compute_duration(latest_user_ts, latest_assistant_ts)

        inserted = 0
        if latest_user:
            result = subprocess.run(
                [sys.executable, str(STORE_SCRIPT), "turn"],
                input=json.dumps({"session_id": session_id, "turn_number": turn_number,
                                  "role": "user", "content": latest_user,
                                  "timestamp": latest_user_ts or None},
                                 ensure_ascii=False),
                encoding="utf-8",
                capture_output=True, timeout=10,
                creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            if result.returncode == 0:
                inserted += 1
            else:
                _log_stop(f"FAIL: insert user turn: {result.stderr[:200]}")

        if latest_assistant:
            result = subprocess.run(
                [sys.executable, str(STORE_SCRIPT), "turn"],
                input=json.dumps({"session_id": session_id, "turn_number": turn_number + 1,
                                  "role": "assistant", "content": latest_assistant,
                                  "timestamp": latest_assistant_ts or None,
                                  "duration_seconds": duration},
                                 ensure_ascii=False),
                encoding="utf-8",
                capture_output=True, timeout=10,
                creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            if result.returncode == 0:
                inserted += 1
            else:
                _log_stop(f"FAIL: insert assistant turn: {result.stderr[:200]}")

        # Update cursor
        cursor_path.parent.mkdir(parents=True, exist_ok=True)
        cursor_path.write_text(str(file_size))

        _log_stop(f"OK: inserted {inserted} turns (T#{turn_number}), "
                  f"user_ts={latest_user_ts or 'N/A'}, asst_ts={latest_assistant_ts or 'N/A'}, "
                  f"cursor={file_size}")

    except Exception as e:
        _log_stop(f"ERROR: {e}")
        import traceback
        _log_stop(traceback.format_exc())


def _compute_duration(user_ts: str, assistant_ts: str) -> float | None:
    """Compute elapsed seconds between user prompt and assistant reply timestamps."""
    if not user_ts or not assistant_ts:
        return None
    try:
        # Timestamps from transcript are ISO format, possibly with timezone
        from datetime import datetime as dt
        t_user = dt.fromisoformat(user_ts.replace("Z", "+00:00"))
        t_asst = dt.fromisoformat(assistant_ts.replace("Z", "+00:00"))
        return (t_asst - t_user).total_seconds()
    except Exception:
        return None


def _log_stop(msg: str):
    """Write diagnostic log for Stop hook troubleshooting."""
    try:
        log_path = PROJECT_ROOT / "knowledge" / ".buffer" / "hook-debug.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).astimezone().isoformat()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def _is_system_noise(content: str) -> bool:
    """Filter out system-injected messages that aren't real user prompts."""
    noise_markers = [
        "<local-command-caveat>",
        "<command-name>",
        "<command-args>",
        "<local-command-stdout>",
        "This session is being continued from a previous conversation",
    ]
    return any(marker in content for marker in noise_markers)


# ─── SessionEnd ──────────────────────────────────────────────────────

def handle_session_end():
    """
    Called at session termination. Spawns detached knowledge-flush.py to do the
    heavy lifting (read buffer + transcript → raw dump + daily log + handoff).

    Returns immediately — the flush runs in background.
    """
    if is_recursive():
        return

    try:
        event = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    session_id = get_session_id_from_event(event)
    transcript_path = event.get("transcript_path", "")
    buffer_path = get_buffer_path(session_id)

    # Check if buffer has content before spawning
    if not buffer_path.exists():
        print(f"[knowledge-hooks] SessionEnd: no buffer for {session_id}, skipping flush",
              file=sys.stderr)
        return

    # Spawn detached flush worker
    env = os.environ.copy()
    env["CLAUDE_INVOKED_BY"] = "knowledge_flush"

    if sys.platform == "win32":
        subprocess.Popen(
            [sys.executable, str(FLUSH_SCRIPT), session_id, transcript_path, str(buffer_path)],
            creationflags=WINDOWS_FLAGS,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
    else:
        subprocess.Popen(
            [sys.executable, str(FLUSH_SCRIPT), session_id, transcript_path, str(buffer_path)],
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

    print(f"[knowledge-hooks] SessionEnd: spawned flush for {session_id}", file=sys.stderr)


# ─── CLI ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python knowledge-hooks.py <session-start|post-tool-use|pre-compact|stop|session-end|init>",
            file=sys.stderr,
        )
        sys.exit(1)

    command = sys.argv[1]

    if command == "session-start":
        handle_session_start()
    elif command == "post-tool-use":
        handle_post_tool_use()
    elif command == "pre-compact":
        handle_pre_compact()
    elif command == "stop":
        handle_stop()
    elif command == "session-end":
        handle_session_end()
    elif command == "init":
        ok = init_knowledge_dir()
        print(f"Knowledge dir {'initialized' if ok else 'already exists'}")
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
