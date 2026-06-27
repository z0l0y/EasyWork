#!/usr/bin/env python3
"""
EasyWork Knowledge Base Hooks

Handles PostToolUse and SessionEnd events for automatic knowledge capture.

PostToolUse (high-frequency, must be fast):
  - Appends tool call event to per-session JSONL buffer
  - Only captures meaningful events (Read/Write/Edit/Bash/Grep/WebSearch/WebFetch)
  - Skips own hook calls to prevent infinite recursion
  - Target latency: <10ms

SessionEnd (low-frequency, can be heavier):
  - Reads the session buffer
  - Classifies events into domain/source/dimension
  - Writes structured knowledge entries via MCP (or direct file write as fallback)
  - Generates session handoff record
  - Dumps full conversation trace to knowledge/conversation/raw/
  - Cleans up buffer

Usage:
  python hooks/knowledge-hooks.py post-tool-use    # Called by PostToolUse hook
  python hooks/knowledge-hooks.py session-end       # Called by SessionEnd hook
"""

import json
import os
import sys
import re
from datetime import datetime, timezone
from pathlib import Path


# ─── Config ──────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUFFER_DIR = PROJECT_ROOT / "knowledge" / ".buffer"
RAW_DIR = PROJECT_ROOT / "knowledge" / "conversation" / "raw"
SESSIONS_DIR = PROJECT_ROOT / "knowledge" / "sessions"
MCP_SERVER_SCRIPT = PROJECT_ROOT / "skills" / "knowledge-base" / "mcp-server" / "server.py"

# Tools that trigger knowledge capture interest
INTERESTING_TOOLS = {"Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebSearch", "WebFetch"}

# File patterns worth tracking
INTERESTING_FILE_PATTERNS = [
    r"\.py$", r"\.js$", r"\.ts$", r"\.go$", r"\.java$", r"\.rs$",
    r"\.md$", r"\.yaml$", r"\.yml$", r"\.json$", r"\.toml$",
    r"SKILL\.md$", r"CLAUDE\.md$", r"README\.md$",
    r"src/", r"skills/", r"knowledge/", r"\.claude/",
]

# Tools that are "read-only" (source discovery)
READ_TOOLS = {"Read", "Grep", "Glob", "WebSearch", "WebFetch"}

# Tools that are "write" (knowledge production)
WRITE_TOOLS = {"Write", "Edit"}

# Tools that are "execute" (verification)
EXEC_TOOLS = {"Bash"}


# ─── Helpers ──────────────────────────────────────────────────────────

def get_session_id() -> str:
    """Generate a stable session ID from timestamp + PID."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    pid = os.getpid()
    return f"{date_str}-{pid}"


def get_buffer_path() -> Path:
    """Get the per-session JSONL buffer path."""
    BUFFER_DIR.mkdir(parents=True, exist_ok=True)
    return BUFFER_DIR / f"{get_session_id()}.jsonl"


def is_interesting_read(file_path: str) -> bool:
    """Check if a file path is worth tracking."""
    if not file_path:
        return False
    for pattern in INTERESTING_FILE_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False


def classify_domain(file_paths: list[str], tool_name: str) -> str:
    """Classify the domain based on file paths and tool."""
    combined = " ".join(file_paths).lower()

    # Integration testing patterns
    if re.search(r"(api|test|curl|endpoint|接口|联调|mock)", combined):
        return "integration"

    # Quarterly OKR patterns
    if re.search(r"(okr|quarterly|季度|roadmap|战略|目标|planning)", combined):
        return "quarterly-o"

    # Everything else is development
    return "development"


# ─── PostToolUse ─────────────────────────────────────────────────────

def handle_post_tool_use():
    """
    Called after every tool use. Reads event JSON from stdin, appends to buffer.

    Input format (stdin JSON):
    {
      "tool_name": "Read",
      "tool_input": {"file_path": "src/auth.go", ...},
      "tool_output": "...",
      "duration_ms": 150
    }
    """
    try:
        event = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = event.get("tool_name", "")
    if tool_name not in INTERESTING_TOOLS:
        return

    tool_input = event.get("tool_input", {})

    # Extract file paths
    file_paths = []
    if "file_path" in tool_input:
        file_paths.append(str(tool_input["file_path"]))
    if "pattern" in tool_input:
        file_paths.append(str(tool_input["pattern"]))
    if "paths" in tool_input and isinstance(tool_input["paths"], list):
        file_paths.extend(str(p) for p in tool_input["paths"])

    # Filter to interesting files only
    if tool_name in READ_TOOLS:
        if file_paths and not any(is_interesting_read(p) for p in file_paths):
            return  # Skip uninteresting reads (e.g., reading /dev/null, temp files)

    # Build event record
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "files": file_paths,
        "duration_ms": event.get("duration_ms", 0),
        # Don't store tool_output in buffer (too large, privacy)
    }

    # Append to buffer
    buffer_path = get_buffer_path()
    with open(buffer_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ─── SessionEnd ──────────────────────────────────────────────────────

def handle_session_end():
    """
    Called at session end. Reads buffer, writes knowledge entries, cleans up.

    This does the heavy lifting:
    1. Read JSONL buffer
    2. Classify by domain
    3. Write to knowledge/conversation/raw/ (full dump)
    4. Generate session handoff
    5. Clean buffer
    """
    session_id = get_session_id()
    buffer_path = get_buffer_path()

    if not buffer_path.exists():
        print(f"[knowledge-hooks] No buffer found for session {session_id}", file=sys.stderr)
        # Still write a minimal handoff
        _write_minimal_handoff(session_id)
        return

    # Read buffer
    events = []
    with open(buffer_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not events:
        _write_minimal_handoff(session_id)
        buffer_path.unlink(missing_ok=True)
        return

    # ── Analysis ──────────────────────────────────────────────

    # Count tool usage
    tool_counts = {}
    all_files = set()
    read_files = set()
    written_files = set()
    total_duration_ms = 0

    for e in events:
        tool = e.get("tool", "")
        tool_counts[tool] = tool_counts.get(tool, 0) + 1
        files = e.get("files", [])
        for f in files:
            all_files.add(f)
            if e["tool"] in READ_TOOLS:
                read_files.add(f)
            elif e["tool"] in WRITE_TOOLS:
                written_files.add(f)
        total_duration_ms += e.get("duration_ms", 0)

    # Classify domain
    domain = classify_domain(list(all_files), "")

    # ── 1. Raw conversation dump ───────────────────────────────

    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    raw_session_dir = RAW_DIR / date_str
    raw_session_dir.mkdir(parents=True, exist_ok=True)

    raw_dump = {
        "session_id": session_id,
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "domain": domain,
        "tool_stats": {
            "total_calls": len(events),
            "by_tool": tool_counts,
            "files_read": len(read_files),
            "files_written": len(written_files),
            "total_files_touched": len(all_files),
            "total_duration_ms": total_duration_ms,
        },
        "events": events,
    }

    raw_path = raw_session_dir / f"{session_id}.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_dump, f, ensure_ascii=False, indent=2)

    # ── 2. Session handoff ─────────────────────────────────────

    read_summary = "\n".join(f"- `{f}`" for f in sorted(read_files)[:20])
    write_summary = "\n".join(f"- `{f}`" for f in sorted(written_files)[:20])
    if len(read_files) > 20:
        read_summary += f"\n- ... 及其他 {len(read_files) - 20} 个文件"
    if len(written_files) > 20:
        write_summary += f"\n- ... 及其他 {len(written_files) - 20} 个文件"

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    date_label = now.strftime("%Y-%m-%d")

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
| WebSearch | {tool_counts.get('WebSearch', 0)} |

## 📁 涉及文件

### 读取 ({len(read_files)} 个)
{read_summary if read_summary else '（无）'}

### 写入 ({len(written_files)} 个)
{write_summary if write_summary else '（无）'}

## 📚 原始数据

完整事件日志：`knowledge/conversation/raw/{date_str}/{session_id}.json`

## 🔗 继续方式

下一个 Agent / 会话：
1. 读 `MEMORY.md` 了解知识库索引
2. 读本文件了解本次会话统计
3. 需要详细事件时读原始数据文件
"""

    handoff_path = SESSIONS_DIR / f"{date_label}-{session_id}.md"
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    with open(handoff_path, "w", encoding="utf-8") as f:
        f.write(handoff_content)

    # ── 3. Try MCP knowledge_store for key findings ────────────

    # Only trigger MCP store if there was substantial activity
    if len(events) >= 5 and len(all_files) >= 3:
        _try_mcp_store(domain, all_files, tool_counts, len(events))

    # ── 4. Cleanup ─────────────────────────────────────────────

    buffer_path.unlink(missing_ok=True)

    print(
        f"[knowledge-hooks] Session {session_id} ended: "
        f"{len(events)} tool calls, {len(all_files)} files, "
        f"domain={domain}, raw={raw_path.name}",
        file=sys.stderr,
    )


def _write_minimal_handoff(session_id: str):
    """Write a minimal handoff when no buffer exists."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    date_label = now.strftime("%Y-%m-%d")

    content = f"""---
dimension: reference
domain: unknown
source: derived
status: stable
created: {timestamp}
session: {session_id}
tags: [handoff, auto-generated, minimal]
---

# 会话交接 — {date_label}

## 统计

无工具调用记录（会话无文件操作或 buffer 未生成）。

## 继续方式

下一个 Agent / 会话：读 `MEMORY.md` 了解知识库索引。
"""

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    handoff_path = SESSIONS_DIR / f"{date_label}-{session_id}.md"
    with open(handoff_path, "w", encoding="utf-8") as f:
        f.write(content)


def _try_mcp_store(domain: str, all_files: set, tool_counts: dict, total_events: int):
    """Try to store a knowledge entry via MCP. Falls back to direct file write."""
    try:
        import subprocess

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
                    "tags": list(all_files)[:5],
                    "source_files": list(all_files)[:10],
                    "session": get_session_id(),
                }),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print(f"[knowledge-hooks] MCP store: {result.stdout.strip()}", file=sys.stderr)
        else:
            print(f"[knowledge-hooks] MCP store failed: {result.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"[knowledge-hooks] MCP store error: {e}", file=sys.stderr)


# ─── CLI ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python knowledge-hooks.py <post-tool-use|session-end>", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "post-tool-use":
        handle_post_tool_use()
    elif command == "session-end":
        handle_session_end()
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
