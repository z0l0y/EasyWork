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

import hashlib
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

# Minimum activity thresholds to trigger MCP knowledge_store
MIN_EVENTS_FOR_STORE = 5
MIN_FILES_FOR_STORE = 3
# Dedup window: skip if same session flushed within this many seconds
DEDUP_WINDOW_SECONDS = 60
# Max transcript lines to read (avoid OOM on huge sessions)
MAX_TRANSCRIPT_LINES = 3000

# File patterns for domain classification
INTEGRATION_PATTERNS = re.compile(
    r"(api|test|curl|endpoint|接口|联调|mock|integration|e2e|契约)",
    re.IGNORECASE,
)
QUARTERLY_PATTERNS = re.compile(
    r"(okr|quarterly|季度|roadmap|战略|目标|planning|规划|里程碑)",
    re.IGNORECASE,
)

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
                    result["user_prompts"].append({
                        "ts": event.get("timestamp", ""),
                        "content": strip_ansi(content)[:2000],  # strip ANSI, then truncate
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
                    result["assistant_messages"].append({
                        "ts": event.get("timestamp", ""),
                        "content": strip_ansi(content)[:3000],
                        "stop_reason": msg.get("stop_reason", ""),
                    })

    except Exception as e:
        result["error"] = str(e)

    return result


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

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
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

    # ── 5. Write daily log ──────────────────────────────────────
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    daily_path = DAILY_DIR / f"{date_label}.md"

    # Format file lists
    def fmt_files(files: set, max_n: int = 15) -> str:
        sorted_files = sorted(files)
        lines = "\n".join(f"- `{f}`" for f in sorted_files[:max_n])
        if len(sorted_files) > max_n:
            lines += f"\n- ... 及其他 {len(sorted_files) - max_n} 个文件"
        return lines if lines else "（无）"

    # Format transcript excerpts
    def fmt_prompts(prompts: list[dict], max_n: int = 5) -> str:
        if not prompts:
            return "（未捕获到用户提问）"
        lines = []
        for p in prompts[-max_n:]:
            content = p["content"][:300].replace("\n", " ")
            lines.append(f"- 💬 {content}...")
        return "\n".join(lines)

    daily_entry = f"""---
session: {session_id}
domain: {domain}
date: {date_label}
---

## 📝 {date_label} — 会话记录

### 🔧 工具使用
- 总调用: {len(events)}
- Read: {tool_counts.get('Read', 0)} | Write/Edit: {tool_counts.get('Write', 0) + tool_counts.get('Edit', 0)}
- Bash: {tool_counts.get('Bash', 0)} | WebSearch: {tool_counts.get('WebSearch', 0)}
- 涉及文件: {len(all_files)} 个

### 📖 读取的文件
{fmt_files(read_files)}

### ✏️ 写入的文件
{fmt_files(written_files)}

### 💬 用户提问
{fmt_prompts(transcript_excerpt.get('user_prompts', []))}

### 📚 原始数据
`knowledge/conversation/raw/{date_str}/{session_id}.json`

---
"""

    # Append to daily log (multiple sessions can write to same day)
    with open(daily_path, "a", encoding="utf-8") as f:
        f.write(daily_entry)

    # ── 6. Write session handoff ────────────────────────────────
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
        )
        if result.returncode == 0:
            print(f"[knowledge-flush] MCP store: {result.stdout.strip()}", file=sys.stderr)
    except Exception:
        pass  # MCP store is best-effort; never fail the flush for it


# ─── CLI ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: python knowledge-flush.py <session_id> <transcript_path> <buffer_path>",
            file=sys.stderr,
        )
        sys.exit(1)

    flush(sys.argv[1], sys.argv[2], sys.argv[3])
