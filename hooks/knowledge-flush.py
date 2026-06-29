#!/usr/bin/env python3
"""
EasyWork Knowledge Flush Worker (detached background process)

Spawned by SessionEnd/PreCompact hooks. Reads the per-session event buffer and
transcript, produces structured knowledge artifacts, then cleans up.

This runs in a FULLY DETACHED background process so it never blocks the hook.
Inspired by claude-memory-compiler's flush.py and memory-mason's capture pipeline.

Architecture:
  knowledge/.buffer/{session_id}.jsonl  ─┐
  transcript_path (JSONL)               ─┤  Inputs
  state.json (dedup tracker)            ─┘
       │
       ▼
  knowledge-flush.py
       │
       ├── knowledge/conversation/raw/{date}/{session_id}.json   (Layer 0, 7-day TTL)
       ├── knowledge/conversation/daily/{date}.md                (human-readable daily log)
       ├── knowledge/sessions/{date}-{session_id}.md             (session handoff)
       └── (attempts MCP knowledge_store for substantial sessions)

Usage (internal — called by knowledge-hooks.py):
  python hooks/knowledge-flush.py <session_id> <transcript_path> <buffer_path>
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ─── Config ──────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "knowledge" / "conversation" / "raw"
DAILY_DIR = PROJECT_ROOT / "knowledge" / "conversation" / "daily"
SESSIONS_DIR = PROJECT_ROOT / "knowledge" / "sessions"
STATE_FILE = PROJECT_ROOT / "knowledge" / ".buffer" / "state.json"
MCP_SERVER_SCRIPT = PROJECT_ROOT / "skills" / "knowledge-base" / "mcp-server" / "server.py"

MAX_EVENT_AGE_HOURS = 2

# No-capture marker — skip messages containing this (synced with knowledge-hooks.py)
NO_CAPTURE_MARKER = "[nc]"

# Minimum activity thresholds to trigger MCP knowledge_store
MIN_EVENTS_FOR_STORE = 5
MIN_FILES_FOR_STORE = 3
# Dedup window: skip if same session flushed within this many seconds
DEDUP_WINDOW_SECONDS = 60
# Max transcript lines to read (avoid OOM on huge sessions)
MAX_TRANSCRIPT_LINES = 10000
# Max content length for raw dump (generous -- qa-pairs/ has complete full text)
MAX_CONTENT_LENGTH = 100000
# Raw dump TTL: delete JSON files older than this many days
RAW_TTL_DAYS = 7

# ─── Config-driven helpers (v3.0: user-configurable via .easywork/config.json) ───


def _get_topic_rules():
    """Return topic rules from config, cached."""
    try:
        from hooks.config import get_topic_rules as cfg_rules
        return cfg_rules()
    except Exception:
        return [
            ("🧠-概念解释", ["是什么", "什么意思", "区别", "对比", "定义", "概念", "解释", "理解", "介绍", "diff", "compare", "what is", "概述", "简介", "有啥区别"]),
            ("🐛-问题排查", ["bug", "error", "报错", "不工作", "失败", "出问题", "修复", "fix", "排查", "debug", "错误", "异常"]),
            ("💻-代码实现", ["实现", "开发", "写代码", "添加功能", "创建", "生成", "implement", "create", "build", "编写", "代码"]),
            ("🔧-工具配置", ["安装", "配置", "setup", "install", "config", "部署", "deploy", "环境", "插件", "plugin", "hook", "mcp", "skill"]),
            ("📊-架构设计", ["设计", "架构", "重构", "architecture", "design", "refactor", "结构", "模式", "pattern", "方案", "选型", "技术栈", "框架"]),
            ("🚀-性能优化", ["性能", "优化", "慢", "加速", "perf", "卡顿", "memory", "内存", "CPU", "提速", "瓶颈", "吞吐"]),
        ]


def _get_topic_default():
    try:
        from hooks.config import get_topic_default
        return get_topic_default()
    except Exception:
        return "📖-其他"


def _is_kb_enabled():
    try:
        from hooks.config import is_knowledge_enabled
        return is_knowledge_enabled()
    except Exception:
        return True


def classify_domain(file_paths: list[str]) -> str:
    """Classify domain from file paths touched, using config-driven keyword matching."""
    try:
        from hooks.config import get_domains
        domains = get_domains()
    except Exception:
        return "development"
    combined = " ".join(file_paths).lower()
    for domain in domains:
        for kw in domain.get("keywords", []):
            if kw.lower() in combined:
                return domain["id"]
    return domains[0]["id"] if domains else "development"

# ANSI escape sequence regex (strips terminal control characters from transcript)
# Covers: CSI sequences (\x1b[...m), OSC sequences, cursor movements, etc.
ANSI_ESCAPE_RE = re.compile(
    r"\x1b\[[0-9;]*[a-zA-Z]|"    # CSI: \x1b[0m, \x1b[2m, \x1b[1;32m, etc.
    r"\x1b\][^\x07]*\x07|"       # OSC: \x1b]0;title\x07
    r"\x1b[PX^_].*?\x1b\\\\|"     # DCS/SOS/PM/APC strings
    r"\x1b\[[0-9;]*[\x40-\x7e]",  # More CSI variants
)


# ─── Helpers ──────────────────────────────────────────────────────────

def strip_ansi(text: str) -> str:
    """
    Strip ANSI escape sequences from text.
    These come from terminal output in Claude Code transcripts (dim/bold/color codes).
    Without this, raw dumps contain garbled characters like \x1b[2m...\x1b[22m.

    Reference: ECMA-48 / ISO 6429 control functions
    """
    if not text:
        return text
    return ANSI_ESCAPE_RE.sub("", text)


def classify_domain(file_paths: list[str]) -> str:
    """Classify domain from file paths touched."""
    combined = " ".join(file_paths).lower()
    if INTEGRATION_PATTERNS.search(combined):
        return "integration"
    if QUARTERLY_PATTERNS.search(combined):
        return "quarterly-o"
    return "development"


def should_skip_dedup(session_id: str) -> bool:
    """Check if this session was already flushed recently (dedup)."""
    try:
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            last_flush = state.get("last_flush", {})
            if session_id in last_flush:
                elapsed = time.time() - last_flush[session_id]
                if elapsed < DEDUP_WINDOW_SECONDS:
                    return True
    except Exception:
        pass
    return False


def mark_flushed(session_id: str):
    """Record flush timestamp for dedup."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    state.setdefault("last_flush", {})[session_id] = time.time()
    # Prune entries older than 7 days
    cutoff = time.time() - 7 * 86400
    state["last_flush"] = {
        k: v for k, v in state.get("last_flush", {}).items() if v > cutoff
    }
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def read_transcript_excerpt(transcript_path: str, max_lines: int = MAX_TRANSCRIPT_LINES) -> dict:
    """
    Read the conversation transcript and extract key content.
    Returns structured excerpt: user prompts, assistant messages, tool call summary.
    """
    result = {
        "user_prompts": [],
        "assistant_messages": [],
        "tool_call_summary": {},
        "total_lines": 0,
        "excerpted": False,
    }

    tp = Path(transcript_path)
    if not tp.exists():
        return result

    try:
        lines = []
        with open(tp, "r", encoding="utf-8") as f:
            for line in f:
                lines.append(line.strip())

        result["total_lines"] = len(lines)
        if len(lines) > max_lines:
            lines = lines[-max_lines:]
            result["excerpted"] = True

        prev_role = None
        for line in lines:
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg = event.get("message", {})
            role = msg.get("role", "")

            if role == "user":
                content = msg.get("content", "")
                if isinstance(content, list):
                    # Extract text from structured content blocks
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                    content = " ".join(text_parts)
                if content and len(content) > 10:
                    if not _is_system_noise(content):
                        result["user_prompts"].append({
                            "ts": event.get("timestamp", ""),
                            "content": strip_ansi(content)[:MAX_CONTENT_LENGTH],
                        })

            elif role == "assistant":
                content = msg.get("content", "")
                if isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                    content = " ".join(text_parts)
                if content and len(content) > 20:
                    entry = {
                        "ts": event.get("timestamp", ""),
                        "content": strip_ansi(content)[:MAX_CONTENT_LENGTH],
                        "stop_reason": msg.get("stop_reason", ""),
                    }
                    # CRITICAL: merge consecutive assistant events (streaming chunks).
                    # The last event in a group contains the FULL response; earlier ones
                    # are partial chunks. Replace the previous entry instead of appending.
                    if prev_role == "assistant" and result["assistant_messages"]:
                        result["assistant_messages"][-1] = entry
                    else:
                        result["assistant_messages"].append(entry)

            prev_role = role

    except Exception as e:
        result["error"] = str(e)

    return result


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


def _sanitize_filename(text: str, max_len: int = 60) -> str:
    """Convert user prompt to a safe filename segment."""
    title = text.split("\n")[0].strip()
    safe = re.sub(r'[\\/:*?"<>|\r\n\t]', "-", title)
    safe = re.sub(r"\s+", " ", safe).strip()
    safe = re.sub(r"-{2,}", "-", safe)
    if len(safe) > max_len:
        safe = safe[:max_len]
    return safe or "untitled"


def _classify_topic(user_content: str) -> str:
    """Classify a user question into a topic category based on keyword matching."""
    text = user_content.lower()
    for topic_dir, keywords in _get_topic_rules():
        for kw in keywords:
            if kw.lower() in text:
                return topic_dir
    return _get_topic_default()


def _is_stale_timestamp(ts: str, max_age_hours: int = MAX_EVENT_AGE_HOURS) -> bool:
    """Check if a transcript event timestamp is too old to be a current-turn message."""
    if not ts:
        return False
    try:
        event_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        now_dt = datetime.now(timezone.utc)
        age = (now_dt - event_dt).total_seconds()
        return age > max_age_hours * 3600
    except Exception:
        return False


def _rebuild_daily_log(date_str: str) -> None:
    """Rebuild the daily log from all qa-pair files in the date directory.
    Groups entries by topic, generates an overview table + per-topic sections.
    (synced with knowledge-hooks.py)"""
    try:
        daily_dir = PROJECT_ROOT / "knowledge" / "conversation" / "daily"
        qa_dir = PROJECT_ROOT / "knowledge" / "conversation" / "qa-pairs" / date_str
        daily_dir.mkdir(parents=True, exist_ok=True)

        if not qa_dir.exists():
            daily_path = daily_dir / f"{date_str}.md"
            daily_path.write_text(f"# 📝 {date_str} — 对话记录\n\n尚无非系统噪声的问答记录。\n", encoding="utf-8")
            return

        entries = []
        for topic_dir in sorted(qa_dir.iterdir()):
            if not topic_dir.is_dir():
                continue
            topic_name = topic_dir.name
            for md_file in sorted(topic_dir.glob("*.md")):
                try:
                    text = md_file.read_text(encoding="utf-8")
                    lines = text.split("\n")
                    title = lines[0][2:].strip() if lines[0].startswith("# ") else md_file.stem
                    fname = md_file.name
                    time_label = "N/A"
                    if len(fname) >= 6 and fname[:6].isdigit():
                        hh, mm, ss = fname[:2], fname[2:4], fname[4:6]
                        time_label = f"{hh}:{mm}:{ss}"
                    dur_str = "N/A"
                    if len(lines) >= 3:
                        meta_line = lines[2]
                        dur_match = re.search(r"耗时:\s*(\d+m\s*\d+s|N/A)", meta_line)
                        if dur_match:
                            dur_str = dur_match.group(1)
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

        entries.sort(key=lambda e: e["time"])
        grouped = {}
        for e in entries:
            grouped.setdefault(e["topic"], []).append(e)

        topic_order = [t[0] for t in _get_topic_rules()] + [_get_topic_default()]
        counts = {}
        for t in topic_order:
            counts[t] = len(grouped.get(t, []))
        total = sum(counts.values())

        overview_header = "| " + " | ".join(
            t.replace("📖-其他", "📖其他").replace("🧠-概念解释", "🧠概念").replace("🐛-问题排查", "🐛排查")
             .replace("💻-代码实现", "💻实现").replace("🔧-工具配置", "🔧配置")
             .replace("📊-架构设计", "📊架构").replace("🚀-性能优化", "🚀性能")
            for t in topic_order) + " | **总计** |"
        overview_sep = "|" + "|".join(":---:" for _ in range(len(topic_order) + 1)) + "|"
        overview_row = "| " + " | ".join(str(counts[t]) for t in topic_order) + f" | **{total}** |"

        md = f"""# 📝 {date_str} — 对话记录

## 📊 概览
{overview_header}
{overview_sep}
{overview_row}
"""
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

        daily_path = daily_dir / f"{date_str}.md"
        # Atomic write: temp file → rename (prevents corruption on concurrent access)
        daily_tmp = daily_path.with_suffix(".tmp")
        daily_tmp.write_text(md, encoding="utf-8")
        daily_tmp.replace(daily_path)
    except Exception:
        pass


def _cleanup_raw_dumps():
    """Delete raw dump JSON files older than RAW_TTL_DAYS."""
    try:
        import time as time_mod
        raw_dir = PROJECT_ROOT / "knowledge" / "conversation" / "raw"
        if not raw_dir.exists():
            return
        cutoff = time_mod.time() - RAW_TTL_DAYS * 86400
        deleted = 0
        for date_dir in raw_dir.iterdir():
            if not date_dir.is_dir():
                continue
            for json_file in date_dir.glob("*.json"):
                try:
                    if json_file.stat().st_mtime < cutoff:
                        json_file.unlink()
                        deleted += 1
                except OSError:
                    continue
            try:
                date_dir.rmdir()
            except OSError:
                pass
        if deleted:
            print(f"[knowledge-flush] Raw TTL cleanup: deleted {deleted} stale dumps",
                  file=sys.stderr)
    except Exception:
        pass


def _is_nocapture_marked(content: str) -> bool:
    """Check if a user message contains the [nc] no-capture marker."""
    return NO_CAPTURE_MARKER in content


def _generate_qa_pairs(transcript_excerpt: dict, date_str: str) -> list[dict]:
    """
    Generate qa-pair Markdown files from transcript excerpt (backup path).
    Skips files that already exist (written by Stop hook).
    Skips user prompts with stale timestamps (injected from old context).
    Saves into topic subdirectories.
    Returns list of dicts for daily log index table.
    """
    user_prompts = transcript_excerpt.get("user_prompts", [])
    assistant_messages = transcript_excerpt.get("assistant_messages", [])

    if not user_prompts or not assistant_messages:
        return []

    qa_dir = PROJECT_ROOT / "knowledge" / "conversation" / "qa-pairs" / date_str

    # Filter out interrupted/incomplete assistant messages
    valid_assistant = []
    for a in assistant_messages:
        ac = a.get("content", "")
        if "[Request interrupted by user" in ac:
            continue
        if len(ac) < 20:
            continue
        valid_assistant.append(a)

    rows = []
    asst_idx = 0
    for i, user in enumerate(user_prompts):
        user_content = user.get("content", "")
        user_ts = user.get("ts", "")

        if not user_content:
            continue

        # Skip messages marked with [nc] (no-capture)
        if _is_nocapture_marked(user_content):
            continue

        # Skip user prompts with stale timestamps (>2h old — injected from context)
        if _is_stale_timestamp(user_ts):
            continue

        # Find matching assistant response (timestamp must be after user timestamp)
        while asst_idx < len(valid_assistant):
            asst = valid_assistant[asst_idx]
            asst_ts = asst.get("ts", "")
            if user_ts and asst_ts:
                try:
                    t_u = datetime.fromisoformat(user_ts.replace("Z", "+00:00"))
                    t_a = datetime.fromisoformat(asst_ts.replace("Z", "+00:00"))
                    if t_a >= t_u:
                        break
                except Exception:
                    break
            else:
                break
            asst_idx += 1

        if asst_idx >= len(valid_assistant):
            break  # No more assistant responses

        asst = valid_assistant[asst_idx]
        asst_content = asst.get("content", "")
        asst_ts = asst.get("ts", "")
        asst_idx += 1

        if not user_content or not asst_content:
            continue

        # Compute filename
        if user_ts:
            try:
                dt_q = datetime.fromisoformat(user_ts.replace("Z", "+00:00"))
                dt_local = dt_q.astimezone()
                time_str = dt_local.strftime("%H%M%S")
            except Exception:
                time_str = "000000"
        else:
            time_str = "000000"

        safe_title = _sanitize_filename(user_content)
        filename = f"{time_str}-{safe_title}.md"

        # Classify topic and save into topic subdirectory
        topic = _classify_topic(user_content)
        topic_dir = qa_dir / topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        file_path = topic_dir / filename

        # Compute duration
        dur_str = "N/A"
        if user_ts and asst_ts:
            try:
                t_u = datetime.fromisoformat(user_ts.replace("Z", "+00:00"))
                t_a = datetime.fromisoformat(asst_ts.replace("Z", "+00:00"))
                dur = (t_a - t_u).total_seconds()
                if dur >= 0:
                    mins = int(dur // 60)
                    secs = dur % 60
                    dur_str = f"{mins}m {secs:.0f}s"
            except Exception:
                pass

        # Skip if qa-pair already exists (Stop hook wrote it)
        if not file_path.exists():
            content = f"""# {user_content[:200]}

> ⏱ 提问: {user_ts or 'N/A'} | 回答: {asst_ts or 'N/A'} | 耗时: {dur_str}

{asst_content}
"""
            try:
                file_path.write_text(content, encoding="utf-8")
            except Exception:
                pass

        # Build index row
        time_label = time_str[:2] + ":" + time_str[2:4] + ":" + time_str[4:6] if time_str != "000000" else "N/A"
        question_short = user_content[:80].replace("\n", " ")
        rows.append({
            "n": i + 1,
            "time": time_label,
            "question": question_short,
            "duration": dur_str,
            "file": filename,
            "topic": topic,
        })

    return rows


def count_tool_usage(events: list[dict]) -> dict:
    """Count tool usage from buffer events."""
    counts = {}
    for e in events:
        tool = e.get("tool", "unknown")
        counts[tool] = counts.get(tool, 0) + 1
    return counts


# ─── Main Flush Logic ─────────────────────────────────────────────────

def flush(session_id: str, transcript_path: str, buffer_path: str):
    """
    Main flush pipeline:
    1. Read buffer events
    2. Read transcript excerpt
    3. Write raw dump (Layer 0)
    4. Write daily log
    5. Write session handoff
    6. Try MCP store (if activity warrants)
    7. Clean buffer
    """
    if not _is_kb_enabled():
        Path(buffer_path).unlink(missing_ok=True)
        return

    # ── 0. Dedup check ──────────────────────────────────────────
    if should_skip_dedup(session_id):
        print(f"[knowledge-flush] Skipping {session_id}: already flushed within {DEDUP_WINDOW_SECONDS}s",
              file=sys.stderr)
        # Still clean buffer
        Path(buffer_path).unlink(missing_ok=True)
        return

    # ── 1. Read buffer ──────────────────────────────────────────
    events = []
    bp = Path(buffer_path)
    if bp.exists():
        with open(bp, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    if not events:
        print(f"[knowledge-flush] No events in buffer for {session_id}", file=sys.stderr)
        bp.unlink(missing_ok=True)
        return

    # ── 2. Read transcript ──────────────────────────────────────
    transcript_excerpt = read_transcript_excerpt(transcript_path) if transcript_path else {}

    # ── 3. Analyze ──────────────────────────────────────────────
    tool_counts = count_tool_usage(events)
    all_files: set[str] = set()
    read_files: set[str] = set()
    written_files: set[str] = set()
    total_duration_ms = 0

    for e in events:
        files = e.get("files", [])
        for f in files:
            all_files.add(f)
            if e.get("tool") in {"Read", "Grep", "Glob", "WebSearch", "WebFetch"}:
                read_files.add(f)
            elif e.get("tool") in {"Write", "Edit"}:
                written_files.add(f)
        total_duration_ms += e.get("duration_ms", 0)

    domain = classify_domain(list(all_files))

    now = datetime.now(timezone.utc).astimezone()
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.isoformat()
    date_label = now.strftime("%Y-%m-%d")

    # ── 4. Write raw dump (Layer 0, 7-day TTL) ──────────────────
    raw_session_dir = RAW_DIR / date_str
    raw_session_dir.mkdir(parents=True, exist_ok=True)

    raw_dump = {
        "session_id": session_id,
        "flushed_at": timestamp,
        "domain": domain,
        "tool_stats": {
            "total_calls": len(events),
            "by_tool": tool_counts,
            "files_read": len(read_files),
            "files_written": len(written_files),
            "total_files_touched": len(all_files),
            "total_duration_ms": total_duration_ms,
        },
        "transcript": {
            "user_prompts": transcript_excerpt.get("user_prompts", [])[-20:],
            "assistant_messages": transcript_excerpt.get("assistant_messages", [])[-10:],
            "total_lines": transcript_excerpt.get("total_lines", 0),
            "excerpted": transcript_excerpt.get("excerpted", False),
        },
        "events": events,
    }

    raw_path = raw_session_dir / f"{session_id}.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_dump, f, ensure_ascii=False, indent=2)

    # ── 5. Generate qa-pair files from transcript (backup for Stop hook) ──
    qa_rows = _generate_qa_pairs(transcript_excerpt, date_str)

    # ── 6. Append session stats to daily log ──
    # Stats go AFTER the Q&A index (which is rebuilt from qa-pairs/ by Stop hook)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    daily_path = DAILY_DIR / f"{date_label}.md"

    # Format file lists
    def fmt_files(files: set, max_n: int = 12) -> str:
        sorted_files = sorted(files)
        lines = "\n".join(f"- `{f}`" for f in sorted_files[:max_n])
        if len(sorted_files) > max_n:
            lines += f"\n- ... 及其他 {len(sorted_files) - max_n} 个文件"
        return lines if lines else "（无）"

    _rebuild_daily_log(date_str)

    stats_entry = f"""

### 🔧 会话 {session_id[:12]} 统计
- 工具调用: {len(events)} | Read: {tool_counts.get('Read', 0)} | Write/Edit: {tool_counts.get('Write', 0) + tool_counts.get('Edit', 0)}
- Bash: {tool_counts.get('Bash', 0)} | WebSearch: {tool_counts.get('WebSearch', 0)}
- 涉及文件: {len(all_files)} 个
- 读取: {fmt_files(read_files)}
- 写入: {fmt_files(written_files)}

---
"""

    with open(daily_path, "a", encoding="utf-8") as f:
        f.write(stats_entry)

    # ── 7. Write session handoff ────────────────────────────────
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    read_summary = fmt_files(read_files)
    write_summary = fmt_files(written_files)

    handoff_content = f"""---
dimension: reference
domain: {domain}
source: derived
status: stable
created: {timestamp}
session: {session_id}
tags: [handoff, auto-generated]
---

# 会话交接 — {date_label}

## ✅ 工具调用统计

| 指标 | 值 |
|------|-----|
| 总工具调用 | {len(events)} |
| Read | {tool_counts.get('Read', 0)} |
| Write/Edit | {tool_counts.get('Write', 0) + tool_counts.get('Edit', 0)} |
| Bash | {tool_counts.get('Bash', 0)} |
| Grep/Glob | {tool_counts.get('Grep', 0) + tool_counts.get('Glob', 0)} |
| WebSearch/WebFetch | {tool_counts.get('WebSearch', 0) + tool_counts.get('WebFetch', 0)} |

## 📁 涉及文件

### 读取 ({len(read_files)} 个)
{read_summary}

### 写入 ({len(written_files)} 个)
{write_summary}

## 📚 原始数据

完整事件日志 + 对话摘要：`knowledge/conversation/raw/{date_str}/{session_id}.json`
每日日志：`knowledge/conversation/daily/{date_label}.md`

## 🔗 继续方式

下一个 Agent / 会话：
1. 读 `MEMORY.md` 了解知识库索引
2. 读本文件了解本次会话统计
3. 需要详细事件时读原始数据文件
"""

    handoff_path = SESSIONS_DIR / f"{date_label}-{session_id}.md"
    with open(handoff_path, "w", encoding="utf-8") as f:
        f.write(handoff_content)

    # ── 7. Try MCP knowledge_store ──────────────────────────────
    if len(events) >= MIN_EVENTS_FOR_STORE and len(all_files) >= MIN_FILES_FOR_STORE:
        _try_mcp_store(domain, list(all_files), tool_counts, len(events), session_id)

    # ── 8. Cleanup ──────────────────────────────────────────────
    _cleanup_raw_dumps()
    bp.unlink(missing_ok=True)
    mark_flushed(session_id)

    print(
        f"[knowledge-flush] Session {session_id}: "
        f"{len(events)} events, {len(all_files)} files, "
        f"domain={domain}, raw={raw_path.name}, daily={daily_path.name}",
        file=sys.stderr,
    )


def _try_mcp_store(domain: str, all_files: list[str], tool_counts: dict, total_events: int, session_id: str):
    """Try MCP knowledge_store. Falls back silently on failure."""
    try:
        files_str = ", ".join(sorted(all_files)[:10])
        title = f"会话自动沉淀：{len(all_files)} 个文件，{total_events} 次工具调用"

        content = f"""## 背景
本次会话自动捕获。涉及 {len(all_files)} 个文件，{total_events} 次工具调用。

## 工具使用
- Read: {tool_counts.get('Read', 0)}
- Write/Edit: {tool_counts.get('Write', 0) + tool_counts.get('Edit', 0)}
- Bash: {tool_counts.get('Bash', 0)}
- Grep/Glob: {tool_counts.get('Grep', 0) + tool_counts.get('Glob', 0)}
- WebSearch: {tool_counts.get('WebSearch', 0)}

## 涉及文件（前 10 个）
{files_str}

## ETR
- **E**: 工具调用日志已保存到 knowledge/conversation/raw/
- **T**: 基于文件路径和工具类型自动分类领域
- **R**: 自动分类可能不准确，建议人工复查
"""

        # CREATE_NO_WINDOW = 0x08000000 on Windows
        win_flags = 0x08000000 if sys.platform == "win32" else 0
        result = subprocess.run(
            [
                sys.executable,
                str(MCP_SERVER_SCRIPT),
                "--mode", "cli",
                "--tool", "knowledge_store",
                "--args", json.dumps({
                    "domain": domain,
                    "source": "derived",
                    "dimension": "analysis",
                    "title": title,
                    "content": content,
                    "tags": all_files[:5],
                    "source_files": all_files[:10],
                    "session": session_id,
                }),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=win_flags,
        )
        if result.returncode == 0:
            print(f"[knowledge-flush] MCP store: {result.stdout.strip()}", file=sys.stderr)
        else:
            print(f"[knowledge-flush] MCP store failed (rc={result.returncode}): {result.stderr[:500]}",
                  file=sys.stderr)
    except FileNotFoundError:
        print("[knowledge-flush] MCP store skipped: Python/mcp not available", file=sys.stderr)
    except Exception as e:
        print(f"[knowledge-flush] MCP store error: {e}", file=sys.stderr)


# ─── CLI ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: python knowledge-flush.py <session_id> <transcript_path> <buffer_path>",
            file=sys.stderr,
        )
        sys.exit(1)

    flush(sys.argv[1], sys.argv[2], sys.argv[3])
