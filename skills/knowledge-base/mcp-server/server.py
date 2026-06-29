"""
EasyWork Knowledge Base MCP Server

Provides MCP tools for automated knowledge base management:
- knowledge_search: Full-text + tag search across all knowledge entries
- knowledge_store: Create/update knowledge entries with auto-indexing
- knowledge_context: Get relevant knowledge for a task description
- knowledge_stats: Entry counts, domain distribution, staleness report
- knowledge_maintenance: Dedup, archive, consolidate

Usage:
    python server.py --knowledge-dir /path/to/EasyWork/knowledge
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# ─── Config integration (v3.0) ────────────────────────────────────
_HOOKS_PATH = Path(__file__).resolve().parent.parent.parent.parent / "hooks"
if str(_HOOKS_PATH) not in sys.path:
    sys.path.insert(0, str(_HOOKS_PATH))


def _get_domain_config():
    """Load domain configuration from .easywork/config.json."""
    try:
        from config import get_domains
        return get_domains()
    except Exception:
        return [
            {"id": "integration", "name": "联调需求", "description": "API联调",
             "keywords": ["api", "test", "curl", "endpoint"]},
            {"id": "development", "name": "开发需求", "description": "Feature开发",
             "keywords": []},
            {"id": "quarterly-o", "name": "季度O", "description": "战略目标",
             "keywords": ["okr", "quarterly", "季度"]},
        ]


def _build_dir_map() -> dict:
    """Build dir_map dynamically from config domains."""
    return {d["id"]: f"domain/{d['id']}" for d in _get_domain_config()}


def _build_domain_enum() -> list:
    """Build domain enum list for MCP tool schemas."""
    return [d["id"] for d in _get_domain_config()] + [""]

# MCP SDK availability flag
HAS_MCP = False
try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationCapabilities
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    pass


# ─── Indexer ────────────────────────────────────────────────────────

class KnowledgeIndexer:
    """Indexes and searches knowledge entries in the knowledge/ directory."""

    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = Path(knowledge_dir)
        self._ensure_init()
        self.entries: dict[str, dict] = {}
        self.tag_index: dict[str, list[str]] = {}
        self.domain_index: dict[str, list[str]] = {}
        self.title_index: dict[str, str] = {}
        self._reindex()

    def _ensure_init(self):
        """Auto-init knowledge/ from template if it doesn't exist."""
        if self.knowledge_dir.exists():
            return
        template_dir = self.knowledge_dir.parent / "knowledge-template"
        if not template_dir.exists():
            return
        import shutil

        def _copy(src: Path, dst: Path):
            dst.mkdir(parents=True, exist_ok=True)
            for item in src.iterdir():
                s = src / item.name
                d = dst / item.name
                if s.is_dir():
                    _copy(s, d)
                elif item.name in ("_index.md", "README.md", ".gitkeep"):
                    shutil.copy2(s, d)

        _copy(template_dir, self.knowledge_dir)

    def _reindex(self):
        """Rebuild all indexes from disk."""
        self.entries.clear()
        self.tag_index.clear()
        self.domain_index.clear()
        self.title_index.clear()

        if not self.knowledge_dir.exists():
            return

        for md_file in self.knowledge_dir.rglob("*.md"):
            # Skip _index.md and README.md (they are indexes, not entries)
            if md_file.name == "_index.md" or md_file.name == "README.md":
                continue

            try:
                entry = self._parse_entry(md_file)
                if entry:
                    entry["_path"] = str(md_file.relative_to(self.knowledge_dir))
                    eid = entry.get("id", md_file.stem)
                    self.entries[eid] = entry

                    # Tag index
                    for tag in entry.get("tags", []):
                        self.tag_index.setdefault(tag, []).append(eid)

                    # Domain index
                    domain = entry.get("domain", "unknown")
                    self.domain_index.setdefault(domain, []).append(eid)

                    # Title index
                    title = entry.get("title", "")
                    if title:
                        self.title_index[eid] = title
            except Exception:
                continue

    def _parse_entry(self, filepath: Path) -> dict | None:
        """Parse a knowledge entry markdown file, extracting frontmatter and title."""
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            return None

        # Extract YAML frontmatter
        fm = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_text = parts[1]
                fm = self._parse_simple_yaml(fm_text)

        # Extract title (first # heading)
        title = ""
        body = parts[2] if len(parts) >= 3 else content
        for line in body.split("\n"):
            m = re.match(r"^#\s+(.+)", line)
            if m:
                title = m.group(1).strip()
                break

        if not fm:
            return None

        return {
            "id": fm.get("id", filepath.stem),
            "title": title or fm.get("title", filepath.stem),
            "domain": fm.get("domain", "unknown"),
            "source": fm.get("source", "unknown"),
            "dimension": fm.get("dimension", "unknown"),
            "status": fm.get("status", "draft"),
            "created": fm.get("created", ""),
            "updated": fm.get("updated", ""),
            "session": fm.get("session", ""),
            "tags": self._parse_tags(fm.get("tags", [])),
            "related": self._parse_tags(fm.get("related", [])),
            "source_files": self._parse_tags(fm.get("source_files", [])),
            "source_urls": self._parse_tags(fm.get("source_urls", [])),
        }

    @staticmethod
    def _parse_simple_yaml(text: str) -> dict[str, Any]:
        """Parse a simplified YAML frontmatter (only top-level scalar/list fields)."""
        result = {}
        current_key = None
        current_list = []

        for line in text.split("\n"):
            # List item
            m = re.match(r"^\s+-\s+(.+)", line)
            if m and current_key:
                current_list.append(m.group(1).strip().strip('"').strip("'"))
                continue

            # Key-value
            m = re.match(r"^(\w[\w_]*)\s*:\s*(.*)", line)
            if m:
                # Save previous list
                if current_key and current_list:
                    result[current_key] = current_list
                    current_list = []

                key = m.group(1)
                value = m.group(2).strip()

                if value in ("true", "false"):
                    result[key] = value == "true"
                elif value == "" or value == "[]":
                    current_key = key
                    current_list = []
                elif value.startswith("[") and value.endswith("]"):
                    result[key] = KnowledgeIndexer._parse_tags(value)
                else:
                    result[key] = value.strip('"').strip("'")
                    current_key = None
            else:
                if current_key and current_list:
                    result[current_key] = current_list
                    current_list = []
                current_key = None

        # Save last list
        if current_key and current_list:
            result[current_key] = current_list

        return result

    @staticmethod
    def _parse_tags(value) -> list[str]:
        """Parse tags from various formats."""
        if isinstance(value, list):
            return [str(v).strip() for v in value]
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1]
                return [t.strip().strip('"').strip("'") for t in inner.split(",") if t.strip()]
            return [value]
        return []

    def search(
        self,
        query: str = "",
        domain: str = "",
        source: str = "",
        dimension: str = "",
        tags: list[str] | None = None,
        status: str = "",
        limit: int = 10,
    ) -> list[dict]:
        """Search knowledge entries with multiple filters."""
        results = []

        query_lower = query.lower() if query else ""

        for eid, entry in self.entries.items():
            # Domain filter
            if domain and entry.get("domain") != domain:
                continue
            # Source filter
            if source and entry.get("source") != source:
                continue
            # Dimension filter
            if dimension and entry.get("dimension") != dimension:
                continue
            # Status filter
            if status and entry.get("status") != status:
                continue
            # Tag filter (ANY match)
            if tags:
                entry_tags = entry.get("tags", [])
                if not any(t in entry_tags for t in tags):
                    continue

            # Text query: match against title, tags, domain
            if query_lower:
                title = entry.get("title", "").lower()
                entry_tags = [t.lower() for t in entry.get("tags", [])]
                entry_domain = entry.get("domain", "").lower()

                score = 0
                if query_lower in title:
                    score += 10
                if any(query_lower in t for t in entry_tags):
                    score += 5
                if query_lower in entry_domain:
                    score += 3

                if score == 0:
                    continue
            else:
                score = 1

            results.append({
                "id": eid,
                "title": entry.get("title", ""),
                "domain": entry.get("domain", ""),
                "source": entry.get("source", ""),
                "dimension": entry.get("dimension", ""),
                "status": entry.get("status", ""),
                "tags": entry.get("tags", []),
                "created": entry.get("created", ""),
                "updated": entry.get("updated", ""),
                "path": entry.get("_path", ""),
                "relevance": score,
            })

        # Sort by relevance descending
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]

    def get_stats(self) -> dict:
        """Generate knowledge base statistics."""
        total = len(self.entries)
        by_domain: dict[str, int] = {}
        by_source: dict[str, int] = {}
        by_dimension: dict[str, int] = {}
        by_status: dict[str, int] = {}
        stale_entries: list[dict] = []
        now = datetime.now()

        for eid, entry in self.entries.items():
            domain = entry.get("domain", "unknown")
            source = entry.get("source", "unknown")
            dimension = entry.get("dimension", "unknown")
            status = entry.get("status", "draft")

            by_domain[domain] = by_domain.get(domain, 0) + 1
            by_source[source] = by_source.get(source, 0) + 1
            by_dimension[dimension] = by_dimension.get(dimension, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1

            # Staleness check
            updated_str = entry.get("updated", "")
            if updated_str:
                try:
                    updated = datetime.fromisoformat(re.sub(r'[+-]\d{2}:\d{2}$', '', updated_str))
                    days_since = (now - updated).days
                    if days_since > 90:
                        stale_entries.append({
                            "id": eid,
                            "title": entry.get("title", ""),
                            "days_since_update": days_since,
                        })
                    elif entry.get("domain") == "integration" and days_since > 7:
                        stale_entries.append({
                            "id": eid,
                            "title": entry.get("title", ""),
                            "days_since_update": days_since,
                        })
                except ValueError:
                    pass

        return {
            "total": total,
            "by_domain": by_domain,
            "by_source": by_source,
            "by_dimension": by_dimension,
            "by_status": by_status,
            "stale_count": len(stale_entries),
            "stale_entries": stale_entries[:20],
            "indexed_at": now.isoformat(),
        }

    def find_duplicates(self, threshold: float = 0.7) -> list[dict]:
        """Find potential duplicate entries by title similarity."""
        duplicates = []
        titles = [(eid, entry.get("title", "")) for eid, entry in self.entries.items()]

        for i, (id1, t1) in enumerate(titles):
            for id2, t2 in titles[i + 1 :]:
                sim = _title_similarity(t1, t2)
                if sim >= threshold:
                    duplicates.append({
                        "entry_a": id1,
                        "entry_b": id2,
                        "title_a": t1,
                        "title_b": t2,
                        "similarity": round(sim, 2),
                    })

        return duplicates


def _title_similarity(a: str, b: str) -> float:
    """Simple word-overlap similarity."""
    if not a or not b:
        return 0.0
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


# ─── MCP Server ─────────────────────────────────────────────────────

class KnowledgeMCPServer:
    """MCP Server wrapping the KnowledgeIndexer."""

    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = Path(knowledge_dir)
        self.indexer = KnowledgeIndexer(knowledge_dir)

    def get_tools(self) -> list[dict]:
        """Return MCP tool definitions."""
        return [
            {
                "name": "knowledge_search",
                "description": "搜索知识库条目。支持全文关键词 + 领域/来源/维度/标签过滤。返回匹配条目列表（含相关度评分）。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词（匹配标题、标签、领域）",
                        },
                        "domain": {
                            "type": "string",
                            "enum": _build_domain_enum(),
                            "description": "领域过滤。可用领域见 .easywork/config.json",
                        },
                        "source": {
                            "type": "string",
                            "enum": ["inner", "outer", "derived", ""],
                            "description": "来源过滤：inner(用户提供) / outer(Agent搜索) / derived(Agent推导)",
                        },
                        "dimension": {
                            "type": "string",
                            "enum": ["prompt", "output", "analysis", "reference", "decision", ""],
                            "description": "维度过滤",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签列表（任一匹配即返回）",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["draft", "stable", "archived", ""],
                            "description": "状态过滤",
                        },
                        "limit": {
                            "type": "integer",
                            "default": 10,
                            "description": "返回条数上限",
                        },
                    },
                },
            },
            {
                "name": "knowledge_context",
                "description": "根据当前任务描述，智能检索相关知识。自动提取任务中的关键词进行搜索，返回最相关的知识条目摘要。用于新任务启动前的知识检索。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "当前任务描述（模块名/API路径/功能名/技术问题）",
                        },
                        "limit": {
                            "type": "integer",
                            "default": 5,
                            "description": "返回条数上限",
                        },
                    },
                    "required": ["task_description"],
                },
            },
            {
                "name": "knowledge_store",
                "description": "写入一条知识到知识库。自动生成 ID、写入 Markdown 文件（含 frontmatter）、更新索引。支持新创建和更新已有条目。去重检测自动触发。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "enum": [d["id"] for d in _get_domain_config()],
                            "description": "领域（必填）。可用领域见 .easywork/config.json",
                        },
                        "source": {
                            "type": "string",
                            "enum": ["inner", "outer", "derived"],
                            "description": "来源（必填）",
                        },
                        "dimension": {
                            "type": "string",
                            "enum": ["prompt", "output", "analysis", "reference", "decision"],
                            "description": "维度（必填）",
                        },
                        "title": {
                            "type": "string",
                            "description": "知识条目标题（一句话概括）",
                        },
                        "content": {
                            "type": "string",
                            "description": "知识内容（Markdown 格式，含 背景/核心内容/ETR证据链/时效性）",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签列表",
                        },
                        "related": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "关联知识条目 ID 列表",
                        },
                        "source_files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "源文件路径列表（如 src/auth/login.go:45-89）",
                        },
                        "source_urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "源 URL 列表",
                        },
                        "session": {
                            "type": "string",
                            "description": "会话标识符",
                        },
                        "entry_id": {
                            "type": "string",
                            "description": "指定 ID（更新已有条目时使用，不指定则自动生成）",
                        },
                    },
                    "required": ["domain", "source", "dimension", "title", "content"],
                },
            },
            {
                "name": "knowledge_stats",
                "description": "获取知识库统计信息：总条目数、领域分布、来源分布、维度分布、状态分布、过期条目列表。",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "knowledge_maintenance",
                "description": "知识库维护操作：去重检测、归档过期条目、升级碎片为模式。返回建议操作列表（需人工确认后执行）。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["detect_duplicates", "find_stale", "suggest_consolidation", "full_report"],
                            "description": "维护操作类型",
                        },
                        "dry_run": {
                            "type": "boolean",
                            "default": True,
                            "description": "是否为演习模式（true=仅报告不修改，false=执行变更）",
                        },
                    },
                    "required": ["action"],
                },
            },
        ]

    def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Handle tool call and return result as JSON string."""
        # Re-index before any operation to catch external changes
        self.indexer._reindex()

        if tool_name == "knowledge_search":
            return self._search(arguments)
        elif tool_name == "knowledge_context":
            return self._context(arguments)
        elif tool_name == "knowledge_store":
            return self._store(arguments)
        elif tool_name == "knowledge_stats":
            return self._stats(arguments)
        elif tool_name == "knowledge_maintenance":
            return self._maintenance(arguments)
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"}, ensure_ascii=False)

    def _search(self, args: dict) -> str:
        results = self.indexer.search(
            query=args.get("query", ""),
            domain=args.get("domain", ""),
            source=args.get("source", ""),
            dimension=args.get("dimension", ""),
            tags=args.get("tags"),
            status=args.get("status", ""),
            limit=args.get("limit", 10),
        )
        return json.dumps({
            "found": len(results),
            "results": results,
        }, ensure_ascii=False, indent=2)

    def _context(self, args: dict) -> str:
        task = args.get("task_description", "")

        # Extract keywords: module names, API paths, technology names
        keywords = []
        # Module/file paths: src/xxx, auth, payment, etc.
        for m in re.finditer(r"(?:src/)?(\w+(?:/\w+)*)", task):
            keywords.append(m.group(1).split("/")[-1])
        # API paths: /api/v1/xxx
        for m in re.finditer(r"(/[\w/-]+)", task):
            keywords.append(m.group(1))
        # Capitalized terms: JWT, OAuth, SQL, etc.
        for m in re.finditer(r"\b([A-Z]{2,}|\w+)\b", task):
            w = m.group(1).lower()
            if w not in ("the", "and", "for", "with", "that", "this", "from", "what", "how", "why", "when", "帮我", "一下", "这个"):
                keywords.append(w)

        all_results = []
        seen = set()
        for kw in keywords[:8]:  # Limit to 8 keywords
            results = self.indexer.search(query=kw, limit=3)
            for r in results:
                if r["id"] not in seen:
                    seen.add(r["id"])
                    all_results.append(r)

        limit = args.get("limit", 5)
        all_results.sort(key=lambda x: x["relevance"], reverse=True)

        # Generate context summary
        context_text = ""
        for r in all_results[:limit]:
            context_text += f"- [{r['id']}] **{r['title']}** ({r['domain']}/{r['dimension']}) — tags: {', '.join(r['tags'])}\n"

        if not context_text:
            context_text = "无相关知识条目。建议完成当前任务后将分析结果沉淀到知识库。\n"

        return json.dumps({
            "task": task,
            "keywords_extracted": keywords[:8],
            "found": len(all_results),
            "context_summary": context_text,
            "results": all_results[:limit],
        }, ensure_ascii=False, indent=2)

    def _store(self, args: dict) -> str:
        domain = args["domain"]
        source = args["source"]
        dimension = args["dimension"]
        title = args["title"]
        content = args["content"]
        tags = args.get("tags", [])
        related = args.get("related", [])
        source_files = args.get("source_files", [])
        source_urls = args.get("source_urls", [])
        session = args.get("session", "")
        entry_id = args.get("entry_id", "")

        now = datetime.now(timezone.utc).astimezone()
        date_str = now.strftime("%Y%m%d")
        timestamp = now.isoformat()

        # Generate ID if not provided
        if not entry_id:
            # Find next sequence number
            existing = [eid for eid in self.indexer.entries if eid.startswith(f"kb-{date_str}-")]
            seq = 1
            while f"kb-{date_str}-{seq:03d}" in existing:
                seq += 1
            entry_id = f"kb-{date_str}-{seq:03d}"

        # Determine target directory (v3.0: config-driven, not hardcoded)
        dir_map = _build_dir_map()
        if dimension == "decision":
            target_dir = "decisions"
        elif source == "inner":
            target_dir = "source/inner"
        elif source == "outer":
            target_dir = "source/outer"
        elif dimension in ("prompt",):
            target_dir = "conversation/prompts"
        elif dimension in ("output",):
            target_dir = "conversation/outputs"
        else:
            target_dir = dir_map.get(domain, "domain/development")

        # Build frontmatter
        fm = f"""---
id: {entry_id}
domain: {domain}
source: {source}
dimension: {dimension}
status: stable
created: {timestamp}
updated: {timestamp}
"""
        if session:
            fm += f"session: {session}\n"
        if tags:
            fm += f"tags: [{', '.join(tags)}]\n"
        else:
            fm += "tags: []\n"
        if related:
            fm += f"related: [{', '.join(related)}]\n"
        else:
            fm += "related: []\n"
        if source_files:
            fm += f"source_files: [{', '.join(source_files)}]\n"
        else:
            fm += "source_files: []\n"
        if source_urls:
            fm += f"source_urls: [{', '.join(source_urls)}]\n"
        else:
            fm += "source_urls: []\n"

        fm += "---\n\n"

        # Build full markdown
        full_content = fm + f"# {title}\n\n{content}\n"

        # Write file
        target_path = self.knowledge_dir / target_dir / f"{entry_id}.md"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(full_content, encoding="utf-8")

        # Update _index.md
        self._update_index(target_dir, entry_id, title, "stable", date_str, tags)

        # Update related entries (bidirectional link)
        for rel_id in related:
            self._add_related_link(rel_id, entry_id)

        # Re-index
        self.indexer._reindex()

        return json.dumps({
            "status": "stored",
            "id": entry_id,
            "path": str(target_path.relative_to(self.knowledge_dir)),
            "duplicate_check": "none",
        }, ensure_ascii=False, indent=2)

    def _update_index(self, target_dir: str, entry_id: str, title: str, status: str, date_str: str, tags: list[str]):
        """Update the _index.md file for the target directory."""
        index_path = self.knowledge_dir / target_dir / "_index.md"
        if not index_path.exists():
            return

        content = index_path.read_text(encoding="utf-8")
        tag_str = " ".join(f"#{t}" for t in tags[:5])

        new_row = f"| {entry_id} | {title} | {status} | {date_str} | {date_str} | {tag_str} |\n"

        # Insert after the table header (find the first "|---" line, then find next empty line)
        lines = content.split("\n")
        inserted = False
        for i, line in enumerate(lines):
            if line.startswith("|---"):
                # Find next line that starts with "|" after the separator
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("| —"):
                        lines.insert(j + 1, new_row.rstrip("\n"))
                        inserted = True
                        break
                    elif lines[j].startswith("|"):
                        # Insert before first existing row
                        lines.insert(j, new_row.rstrip("\n"))
                        inserted = True
                        break
                    elif lines[j].strip() == "":
                        # Empty line after separator - insert here
                        lines.insert(j + 1, new_row.rstrip("\n"))
                        inserted = True
                        break
                break

        if inserted:
            index_path.write_text("\n".join(lines), encoding="utf-8")

    def _add_related_link(self, target_id: str, new_id: str):
        """Add bidirectional link to a related entry."""
        # Search for the target entry file
        for eid, entry in self.indexer.entries.items():
            if eid == target_id and "_path" in entry:
                filepath = self.knowledge_dir / entry["_path"]
                if filepath.exists():
                    content = filepath.read_text(encoding="utf-8")
                    # Check if link already exists
                    if new_id not in content:
                        content = content.replace(
                            "related: [", f"related: [{new_id}, "
                        ).replace("related: []", f"related: [{new_id}]")
                        filepath.write_text(content, encoding="utf-8")
                break

    def _stats(self, args: dict) -> str:
        stats = self.indexer.get_stats()
        return json.dumps(stats, ensure_ascii=False, indent=2)

    def _maintenance(self, args: dict) -> str:
        action = args.get("action", "full_report")
        dry_run = args.get("dry_run", True)

        if action == "detect_duplicates":
            dups = self.indexer.find_duplicates()
            return json.dumps({
                "action": "detect_duplicates",
                "dry_run": dry_run,
                "duplicates_found": len(dups),
                "duplicates": dups,
            }, ensure_ascii=False, indent=2)

        elif action == "find_stale":
            stats = self.indexer.get_stats()
            return json.dumps({
                "action": "find_stale",
                "stale_count": stats["stale_count"],
                "stale_entries": stats["stale_entries"],
                "suggestion": "建议归档 >90天未更新的条目，复查 >7天的 integration 条目",
            }, ensure_ascii=False, indent=2)

        elif action == "suggest_consolidation":
            # Find tags with >=3 entries → suggest consolidation
            suggestions = []
            for tag, eids in self.indexer.tag_index.items():
                if len(eids) >= 3:
                    suggestions.append({
                        "tag": tag,
                        "entry_count": len(eids),
                        "entries": eids,
                        "suggestion": f"标签 #{tag} 下有 {len(eids)} 条碎片化知识，建议合并为一条综合条目",
                    })
            return json.dumps({
                "action": "suggest_consolidation",
                "suggestions": suggestions,
            }, ensure_ascii=False, indent=2)

        elif action == "full_report":
            stats = self.indexer.get_stats()
            dups = self.indexer.find_duplicates()
            suggestions = []
            for tag, eids in self.indexer.tag_index.items():
                if len(eids) >= 3:
                    suggestions.append({
                        "tag": tag,
                        "entry_count": len(eids),
                        "entries": eids,
                    })

            return json.dumps({
                "action": "full_report",
                "dry_run": dry_run,
                "stats": stats,
                "duplicates": dups[:10],
                "consolidation_suggestions": suggestions,
                "summary": (
                    f"总条目: {stats['total']} | "
                    f"活跃: {stats['by_status'].get('stable', 0)} | "
                    f"草稿: {stats['by_status'].get('draft', 0)} | "
                    f"归档: {stats['by_status'].get('archived', 0)} | "
                    f"过期: {stats['stale_count']} | "
                    f"疑似重复: {len(dups)}"
                ),
            }, ensure_ascii=False, indent=2)

        return json.dumps({"error": f"Unknown action: {action}"}, ensure_ascii=False)


# ─── Stdio Mode (for Claude Code MCP) ───────────────────────────────

async def run_mcp_stdio(knowledge_dir: str):
    """Run as MCP stdio server for Claude Code integration."""
    if not HAS_MCP:
        print("MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
        sys.exit(1)

    server = Server("easywork-knowledge")
    kb = KnowledgeMCPServer(knowledge_dir)

    @server.list_tools()
    async def handle_list_tools():
        tools = kb.get_tools()
        return [Tool(**t) for t in tools]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        result = kb.call_tool(name, arguments)
        return [TextContent(type="text", text=result)]

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationCapabilities(
                sampling=None,
                experimental=None,
                roots=None,
            ),
            NotificationOptions(),
        )


# ─── CLI ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EasyWork Knowledge Base MCP Server")
    parser.add_argument(
        "--knowledge-dir",
        default=os.environ.get("EASYWORK_KNOWLEDGE_DIR", str(Path(__file__).parent.parent.parent.parent / "knowledge")),
        help="Path to knowledge/ directory",
    )
    parser.add_argument("--mode", choices=["mcp", "cli"], default="mcp", help="Run mode")
    parser.add_argument("--tool", help="CLI mode: tool name to call")
    parser.add_argument("--args", default="{}", help="CLI mode: JSON arguments for the tool")

    args = parser.parse_args()

    if args.mode == "cli":
        # CLI mode for testing
        kb = KnowledgeMCPServer(args.knowledge_dir)
        tool_args = json.loads(args.args)
        result = kb.call_tool(args.tool, tool_args)
        print(result)
    else:
        # MCP mode
        import asyncio
        asyncio.run(run_mcp_stdio(args.knowledge_dir))
