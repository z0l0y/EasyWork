#!/usr/bin/env python3
"""
EasyWork Shared Config Reader — v3.0

Reads .easywork/config.json and provides typed accessors for all hook scripts
and the MCP server. If config.json does not exist, returns built-in defaults
matching old v2.x behavior (backward compatible).

Usage:
  from config import load_config, is_knowledge_enabled, get_domains, get_topic_rules
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / ".easywork" / "config.json"

# ─── Cache ──────────────────────────────────────────────────────────

_config_cache = None
_config_mtime = 0


def load_config(force: bool = False) -> dict:
    """Load config from .easywork/config.json. Cached in memory, re-reads on file change."""
    global _config_cache, _config_mtime

    if not force and _config_cache is not None:
        try:
            if CONFIG_PATH.exists():
                current_mtime = CONFIG_PATH.stat().st_mtime
                if current_mtime <= _config_mtime:
                    return _config_cache
        except OSError:
            pass

    if CONFIG_PATH.exists():
        try:
            raw = CONFIG_PATH.read_text(encoding="utf-8")
            _config_cache = json.loads(raw)
            _config_mtime = CONFIG_PATH.stat().st_mtime
            return _config_cache
        except (json.JSONDecodeError, OSError) as e:
            sys.stderr.write(f"[config] Failed to parse {CONFIG_PATH}: {e}\n")
            sys.stderr.write("[config] Falling back to built-in defaults.\n")

    _config_cache = _default_config()
    _config_mtime = 0
    return _config_cache


def _default_config() -> dict:
    """Built-in defaults matching old v2.x behavior (integration/development/quarterly-o)."""
    return {
        "version": 1,
        "knowledge": {
            "enabled": True,
            "domains": [
                {"id": "integration", "name": "联调需求", "emoji": "🔌", "description": "单个API/接口的联调、测试、验证", "keywords": ["api", "test", "curl", "endpoint", "接口", "联调", "mock", "integration", "e2e", "契约"], "ttl_days": 7},
                {"id": "development", "name": "开发需求", "emoji": "🚀", "description": "Feature开发、模块重构、技术改进", "keywords": [], "ttl_days": 90},
                {"id": "quarterly-o", "name": "季度O", "emoji": "🎯", "description": "跨Sprint战略目标", "keywords": ["okr", "quarterly", "季度", "roadmap", "战略", "目标", "planning", "规划", "里程碑"], "ttl_days": 365},
            ],
            "data_dir": "knowledge",
        },
        "topic_rules": {
            "rules": [
                {"category": "概念解释", "emoji": "🧠", "keywords": ["是什么", "什么意思", "区别", "对比", "定义", "概念", "解释", "理解", "介绍", "diff", "compare", "what is", "概述", "简介", "有啥区别"]},
                {"category": "问题排查", "emoji": "🐛", "keywords": ["bug", "error", "报错", "不工作", "失败", "出问题", "修复", "fix", "排查", "debug", "错误", "异常"]},
                {"category": "代码实现", "emoji": "💻", "keywords": ["实现", "开发", "写代码", "添加功能", "创建", "生成", "implement", "create", "build", "编写", "代码"]},
                {"category": "工具配置", "emoji": "🔧", "keywords": ["安装", "配置", "setup", "install", "config", "部署", "deploy", "环境", "插件", "plugin", "hook", "mcp", "skill"]},
                {"category": "架构设计", "emoji": "📊", "keywords": ["设计", "架构", "重构", "architecture", "design", "refactor", "结构", "模式", "pattern", "方案", "选型", "技术栈", "框架"]},
                {"category": "性能优化", "emoji": "🚀", "keywords": ["性能", "优化", "慢", "加速", "perf", "卡顿", "memory", "内存", "CPU", "提速", "瓶颈", "吞吐"]},
            ],
            "default_category": "其他",
            "default_emoji": "📖",
        },
        "paths": {"skills": "skills/", "tools": "tools/"},
        "workflow": {"comment_language": "chinese", "report_type": "engineering_record", "output_backend": "local_html"},
    }


# ─── Public API ────────────────────────────────────────────────────

def is_knowledge_enabled() -> bool:
    cfg = load_config()
    return cfg.get("knowledge", {}).get("enabled", True)


def get_domains() -> list:
    cfg = load_config()
    return cfg.get("knowledge", {}).get("domains", [])


def get_domain_ids() -> list:
    return [d["id"] for d in get_domains()]


def get_domain_default() -> str:
    ids = get_domain_ids()
    return ids[0] if ids else "development"


def get_topic_rules() -> list:
    """Return topic rules as list of (emoji-category, keywords_list) tuples."""
    cfg = load_config()
    rules = cfg.get("topic_rules", {}).get("rules", [])
    return [(f"{r['emoji']}-{r['category']}", r["keywords"]) for r in rules]


def get_topic_default() -> str:
    cfg = load_config()
    rules = cfg.get("topic_rules", {})
    return f"{rules.get('default_emoji', '📖')}-{rules.get('default_category', '其他')}"


def get_data_dir() -> str:
    cfg = load_config()
    return cfg.get("knowledge", {}).get("data_dir", "knowledge")


def get_skills_path() -> str:
    cfg = load_config()
    return cfg.get("paths", {}).get("skills", "skills/")


def get_tools_path() -> str:
    cfg = load_config()
    return cfg.get("paths", {}).get("tools", "tools/")


def get_risk_patterns() -> list:
    cfg = load_config()
    return cfg.get("risk", {}).get("high_risk_patterns", [])


def get_workflow_default(key: str, fallback=None):
    cfg = load_config()
    return cfg.get("workflow", {}).get(key, fallback)
