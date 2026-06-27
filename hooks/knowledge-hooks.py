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


# ─── Config ──────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "knowledge-template"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
BUFFER_DIR = KNOWLEDGE_DIR / ".buffer"
FLUSH_SCRIPT = PROJECT_ROOT / "hooks" / "knowledge-flush.py"
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
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
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
        flags = 0x00000200 | 0x00000008
        subprocess.Popen(
            [sys.executable, str(FLUSH_SCRIPT), session_id, transcript_path, str(buffer_path)],
            creationflags=flags,
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
        flags = 0x00000200 | 0x00000008
        subprocess.Popen(
            [sys.executable, str(FLUSH_SCRIPT), session_id, transcript_path, str(buffer_path)],
            creationflags=flags,
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
            "Usage: python knowledge-hooks.py <session-start|post-tool-use|pre-compact|session-end>",
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
    elif command == "session-end":
        handle_session_end()
    elif command == "init":
        ok = init_knowledge_dir()
        print(f"Knowledge dir {'initialized' if ok else 'already exists'}")
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
