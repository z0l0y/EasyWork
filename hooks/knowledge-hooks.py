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

# Fix Windows I/O encoding — stdin/stdout default to GBK on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8")

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

# Topic classification: keyword-based auto-categorization of user questions.
# Rules are evaluated in order; first match wins. Default: "📖-其他"
TOPIC_RULES = [
    ("🧠-概念解释", ["是什么", "什么意思", "区别", "对比", "定义", "概念", "解释", "理解",
                     "介绍", "diff", "compare", "what is", "概述", "简介", "有啥区别",
                     "有什么不同", "区别是", "不同点"]),
    ("🐛-问题排查", ["bug", "error", "报错", "不工作", "失败", "出问题", "修复", "fix",
                     "排查", "debug", "坏了", "不对", "错误", "异常", "怎么没", "不更新",
                     "没反应", "不行", "有问题", "出不来"]),
    ("💻-代码实现", ["实现", "开发", "写代码", "添加功能", "创建", "生成", "implement",
                     "create", "build", "coding", "编写", "写一个", "帮我写", "代码"]),
    ("🔧-工具配置", ["安装", "配置", "setup", "install", "config", "部署", "deploy",
                     "环境", "插件", "plugin", "hook", "hooks", "mcp", "skill"]),
    ("📊-架构设计", ["设计", "架构", "重构", "architecture", "design", "refactor",
                     "结构", "模式", "pattern", "方案", "选型", "技术栈", "框架"]),
    ("🚀-性能优化", ["性能", "优化", "慢", "加速", "perf", "卡顿", "memory", "内存",
                     "CPU", "提速", "瓶颈", "吞吐"]),
]
TOPIC_DEFAULT = "📖-其他"

# Max age for a user message timestamp before it's considered stale (hours).
# Stop hook fires in real-time; user→reply rarely exceeds 2 hours.
MAX_EVENT_AGE_HOURS = 2

# Capture pause flag file — when present, Stop hook skips ALL capture
CAPTURE_PAUSE_FLAG = BUFFER_DIR / "capture-paused"

# No-capture marker — include this anywhere in a message to skip that turn
NO_CAPTURE_MARKER = "[nc]"

# Capture control phrases — toggle session-wide pause/resume
CAPTURE_PAUSE_PHRASES = ["暂停捕获", "暂停记录", "停止捕获", "停止记录", "pause capture"]
CAPTURE_RESUME_PHRASES = ["恢复捕获", "继续捕获", "恢复记录", "继续记录", "resume capture"]

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

    # ── 1. Check capture pause flag ──────────────────────────────────
    if _is_capture_paused():
        _log_stop("SKIP: capture is paused (flag file exists)")
        return

    # ── 2. Ensure SQLite DB exists ───────────────────────────────────
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
                        # Check for capture control commands (pause/resume)
                        ctrl = _check_capture_control(content)
                        if ctrl == "pause":
                            _set_capture_paused(True)
                            _log_stop(f"CAPTURE PAUSED: user said '{content[:60]}'")
                            return  # Skip this entire turn
                        elif ctrl == "resume":
                            _set_capture_paused(False)
                            _log_stop(f"CAPTURE RESUMED: user said '{content[:60]}'")
                            return  # Skip this entire turn

                        # Check for per-message [nc] marker
                        if _is_nocapture_marked(content):
                            _log_stop(f"SKIP [nc]: {content[:80]}")
                            return  # Skip this entire turn

                        msg_ts = msg_event.get("timestamp", "")
                        # Skip stale messages injected from old conversation context
                        # (e.g. /compact summaries that include historical user messages)
                        if _is_stale_timestamp(msg_ts):
                            _log_stop(f"SKIP stale user msg: ts={msg_ts}, preview={content[:80]}")
                            continue
                        latest_user = content
                        latest_user_ts = msg_ts
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
                _log_stop(f"FAIL: insert user turn: {result.stderr[:2000]}")

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
                _log_stop(f"FAIL: insert assistant turn: {result.stderr[:2000]}")

        # ── 5. Write qa-pair Markdown file (complete, no truncation) ──
        if latest_user and latest_assistant:
            _write_qa_pair(session_id, latest_user, latest_user_ts,
                           latest_assistant, latest_assistant_ts, duration)

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


def _utc_to_local(ts: str) -> str:
    """Convert UTC timestamp (Z suffix) to local ISO format."""
    if not ts:
        return ts
    try:
        dt_utc = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt_utc.astimezone().isoformat()
    except Exception:
        return ts


def _sanitize_filename(text: str, max_len: int = 60) -> str:
    """Convert user prompt to a safe filename segment."""
    # Take first line
    title = text.split("\n")[0].strip()
    # Remove/replace unsafe characters
    safe = re.sub(r'[\\/:*?"<>|\r\n\t]', "-", title)
    # Collapse whitespace and dashes
    safe = re.sub(r"\s+", " ", safe).strip()
    safe = re.sub(r"-{2,}", "-", safe)
    # Truncate
    if len(safe) > max_len:
        safe = safe[:max_len]
    return safe or "untitled"


def _write_qa_pair(session_id: str, user_content: str, user_ts: str,
                   assistant_content: str, assistant_ts: str,
                   duration: float | None):
    """Write a full Q&A pair as a readable Markdown file. No truncation.
    Saves into a topic subdirectory (auto-classified from user prompt)."""
    try:
        qa_dir = PROJECT_ROOT / "knowledge" / "conversation" / "qa-pairs"
        # Convert UTC timestamps to local time for filename + display
        local_user_ts = _utc_to_local(user_ts)
        local_asst_ts = _utc_to_local(assistant_ts)
        if local_user_ts:
            try:
                dt_q = datetime.fromisoformat(local_user_ts)
                date_str = dt_q.strftime("%Y-%m-%d")
                time_str = dt_q.strftime("%H%M%S")
            except Exception:
                now = datetime.now(timezone.utc).astimezone()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H%M%S")
        else:
            now = datetime.now(timezone.utc).astimezone()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H%M%S")

        # Sanitize question for filename
        safe_title = _sanitize_filename(user_content)
        filename = f"{time_str}-{safe_title}.md"

        # Classify topic and save into topic subdirectory
        topic = _classify_topic(user_content)
        day_dir = qa_dir / date_str / topic
        day_dir.mkdir(parents=True, exist_ok=True)

        file_path = day_dir / filename
        # Skip if already exists (idempotent — may have been written by flush)
        if file_path.exists():
            return

        # Format duration
        if duration is not None:
            mins = int(duration // 60)
            secs = duration % 60
            dur_str = f"{mins}m {secs:.0f}s"
        else:
            dur_str = "N/A"

        # Write complete markdown file — FULL content, zero truncation
        content = f"""# {user_content[:200]}

> ⏱ 提问: {local_user_ts or user_ts or 'N/A'} | 回答: {local_asst_ts or assistant_ts or 'N/A'} | 耗时: {dur_str}
> 🔗 会话: {session_id[:12]}

{assistant_content}
"""
        file_path.write_text(content, encoding="utf-8")
        _log_stop(f"QA-PAIR: wrote {topic}/{filename}")

        # Rebuild daily log (topic-grouped structure — cannot simple-append)
        _rebuild_daily_log(date_str)

    except Exception as e:
        _log_stop(f"FAIL: write qa-pair: {e}")


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


def _is_nocapture_marked(content: str) -> bool:
    """Check if a user message contains the [nc] no-capture marker."""
    return NO_CAPTURE_MARKER in content


def _is_capture_paused() -> bool:
    """Check if session-wide capture is paused (flag file exists)."""
    return CAPTURE_PAUSE_FLAG.exists()


def _set_capture_paused(paused: bool) -> None:
    """Create or remove the capture-paused flag file."""
    CAPTURE_PAUSE_FLAG.parent.mkdir(parents=True, exist_ok=True)
    if paused:
        CAPTURE_PAUSE_FLAG.write_text("paused")
    else:
        CAPTURE_PAUSE_FLAG.unlink(missing_ok=True)


def _check_capture_control(content: str) -> str | None:
    """Detect if a user message is a capture control command.
    Returns 'pause', 'resume', or None."""
    for phrase in CAPTURE_PAUSE_PHRASES:
        if phrase in content:
            return "pause"
    for phrase in CAPTURE_RESUME_PHRASES:
        if phrase in content:
            return "resume"
    return None


def _classify_topic(user_content: str) -> str:
    """Classify a user question into a topic category based on keyword matching.
    Returns the topic directory name (e.g. '🧠-概念解释'), or '📖-其他' as default.
    """
    text = user_content.lower()
    for topic_dir, keywords in TOPIC_RULES:
        for kw in keywords:
            if kw.lower() in text:
                return topic_dir
    return TOPIC_DEFAULT


def _is_stale_timestamp(ts: str, max_age_hours: int = MAX_EVENT_AGE_HOURS) -> bool:
    """Check if a transcript event timestamp is too old to be a current-turn message.
    Returns True if the timestamp is more than max_age_hours before now (stale context injection).
    Returns False if the timestamp is recent or unparseable (safe default: accept it).
    """
    if not ts:
        return False  # No timestamp → can't judge, accept it
    try:
        from datetime import timezone as tz_mod
        event_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        now_dt = datetime.now(tz_mod.utc)
        age = (now_dt - event_dt).total_seconds()
        return age > max_age_hours * 3600
    except Exception:
        return False  # Unparseable timestamp → accept it (safe default)


def _rebuild_daily_log(date_str: str) -> None:
    """Rebuild the daily log from all qa-pair files in the date directory.
    Groups entries by topic, generates an overview table + per-topic sections.
    """
    try:
        daily_dir = PROJECT_ROOT / "knowledge" / "conversation" / "daily"
        qa_dir = PROJECT_ROOT / "knowledge" / "conversation" / "qa-pairs" / date_str
        daily_dir.mkdir(parents=True, exist_ok=True)

        if not qa_dir.exists():
            # No qa-pairs yet — write minimal daily log
            daily_path = daily_dir / f"{date_str}.md"
            daily_path.write_text(f"# 📝 {date_str} — 对话记录\n\n尚无非系统噪声的问答记录。\n", encoding="utf-8")
            return

        # Collect all qa-pair entries from topic subdirectories
        entries = []  # list of {topic, time_str, title, dur_str, rel_path, filename}
        for topic_dir in sorted(qa_dir.iterdir()):
            if not topic_dir.is_dir():
                continue
            topic_name = topic_dir.name
            for md_file in sorted(topic_dir.glob("*.md")):
                try:
                    text = md_file.read_text(encoding="utf-8")
                    lines = text.split("\n")
                    # Line 0: "# {title}"
                    title = lines[0][2:].strip() if lines[0].startswith("# ") else md_file.stem
                    # Line 2: "> ⏱ 提问: ... | 回答: ... | 耗时: Xm Ys"
                    dur_str = "N/A"
                    time_label = "N/A"
                    if len(lines) >= 3 and lines[2].startswith("> ⏱"):
                        meta = lines[2]
                        # Extract time: from "> ⏱ 提问: ..." take the first time
                        # or extract the local HH:MM from the filename (more reliable)
                        pass
                    # Extract time from filename: format is HHMMSS-title.md
                    fname = md_file.name
                    if len(fname) >= 6 and fname[:6].isdigit():
                        hh, mm, ss = fname[:2], fname[2:4], fname[4:6]
                        time_label = f"{hh}:{mm}:{ss}"
                    # Extract duration from metadata line
                    if len(lines) >= 3:
                        meta_line = lines[2]
                        dur_match = re.search(r"耗时:\s*(\d+m\s*\d+s|N/A)", meta_line)
                        if dur_match:
                            dur_str = dur_match.group(1)
                    # Build relative path from daily dir
                    rel_path = f"qa-pairs/{date_str}/{topic_name}/{fname}"
                    entries.append({
                        "topic": topic_name,
                        "time": time_label,
                        "title": title[:100],
                        "duration": dur_str,
                        "rel_path": rel_path,
                    })
                except Exception:
                    continue

        if not entries:
            daily_path = daily_dir / f"{date_str}.md"
            daily_path.write_text(f"# 📝 {date_str} — 对话记录\n\n尚无非系统噪声的问答记录。\n", encoding="utf-8")
            return

        # Sort entries by time
        entries.sort(key=lambda e: e["time"])

        # Group by topic
        grouped = {}
        for e in entries:
            grouped.setdefault(e["topic"], []).append(e)

        # Build overview row
        topic_order = [t[0] for t in TOPIC_RULES] + [TOPIC_DEFAULT]
        counts = {}
        for t in topic_order:
            counts[t] = len(grouped.get(t, []))
        total = sum(counts.values())

        overview_header = "| " + " | ".join(t.replace("📖-其他", "📖其他").replace("🧠-概念解释", "🧠概念").replace("🐛-问题排查", "🐛排查").replace("💻-代码实现", "💻实现").replace("🔧-工具配置", "🔧配置").replace("📊-架构设计", "📊架构").replace("🚀-性能优化", "🚀性能") for t in topic_order) + " | **总计** |"
        overview_sep = "|" + "|".join(":---:" for _ in range(len(topic_order) + 1)) + "|"
        overview_row = "| " + " | ".join(str(counts[t]) for t in topic_order) + f" | **{total}** |"

        # Build markdown
        md = f"""# 📝 {date_str} — 对话记录

## 📊 概览
{overview_header}
{overview_sep}
{overview_row}
"""
        # Per-topic sections
        for topic in topic_order:
            items = grouped.get(topic, [])
            if not items:
                continue
            md += f"\n## {topic}（{len(items)} 条）\n"
            md += "| # | 时间 | 提问 | 耗时 |\n"
            md += "|---|------|------|------|\n"
            for i, item in enumerate(items, 1):
                time_short = item["time"][:5] if len(item["time"]) >= 5 else item["time"]
                title_short = item["title"][:80].replace("|", "/")
                md += f"| {i} | {time_short} | [{title_short}]({item['rel_path']}) | {item['duration']} |\n"

        # Atomic write: temp file → rename (prevents corruption on concurrent access)
        daily_path = daily_dir / f"{date_str}.md"
        daily_tmp = daily_path.with_suffix(".tmp")
        daily_tmp.write_text(md, encoding="utf-8")
        daily_tmp.replace(daily_path)

    except Exception:
        pass  # Best-effort; never block main flow


def _migrate_flat_to_topic(date_str: str) -> int:
    """Migrate existing flat qa-pair files into topic subdirectories.
    Returns count of files migrated.
    """
    qa_dir = PROJECT_ROOT / "knowledge" / "conversation" / "qa-pairs" / date_str
    if not qa_dir.exists():
        return 0

    migrated = 0
    for md_file in sorted(qa_dir.glob("*.md")):
        if not md_file.is_file():
            continue
        try:
            text = md_file.read_text(encoding="utf-8")
            # Extract user content from first line: "# {title}"
            first_line = text.split("\n")[0]
            user_content = first_line[2:].strip() if first_line.startswith("# ") else first_line

            topic = _classify_topic(user_content)
            topic_dir = qa_dir / topic
            topic_dir.mkdir(parents=True, exist_ok=True)

            target = topic_dir / md_file.name
            if not target.exists():
                md_file.rename(target)
                migrated += 1
        except Exception:
            continue

    return migrated


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
            "Usage: python knowledge-hooks.py <command>\n"
            "\n  Hook commands (called by Claude Code):\n"
            "    session-start       Inject knowledge index into context\n"
            "    post-tool-use       Record tool usage to buffer\n"
            "    pre-compact         Safety net before context compaction\n"
            "    stop               Per-turn Q&A capture (user + assistant)\n"
            "    session-end         Spawn detached flush worker\n"
            "\n  User commands:\n"
            "    init                Bootstrap knowledge/ from template\n"
            "    capture-pause       Pause all knowledge capture (session-wide)\n"
            "    capture-resume      Resume knowledge capture\n"
            "    capture-status      Show current capture state",
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
    elif command == "capture-pause":
        _set_capture_paused(True)
        print("📚 知识捕获已暂停 — 后续对话不写入知识库")
    elif command == "capture-resume":
        _set_capture_paused(False)
        print("📚 知识捕获已恢复")
    elif command == "capture-status":
        if _is_capture_paused():
            print("📚 知识捕获状态: **已暂停** (恢复: `python hooks/knowledge-hooks.py capture-resume`)")
        else:
            print("📚 知识捕获状态: **正常** (暂停: `python hooks/knowledge-hooks.py capture-pause`)")
    elif command == "backup":
        import shutil
        backup_dir = sys.argv[2] if len(sys.argv) > 2 else str(PROJECT_ROOT / ".." / "EasyWork-backup")
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
        archive_name = f"easywork-knowledge-{now}.zip"
        archive_path = backup_path / archive_name
        knowledge_path = PROJECT_ROOT / "knowledge"
        if knowledge_path.exists():
            shutil.make_archive(str(archive_path.with_suffix("")), "zip", str(knowledge_path.parent), "knowledge")
            size_mb = archive_path.stat().st_size / (1024 * 1024)
            print(f"📚 知识库已备份到: {archive_path} ({size_mb:.1f} MB)")
        else:
            print("📚 知识库目录不存在，无需备份")
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
