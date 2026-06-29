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
    """Built-in defaults matching v3.0 multi-role domains."""
    return {
        "version": 1,
        "knowledge": {
            "enabled": True,
            "domains": [
                {"id": "backend", "name": "后端开发", "emoji": "💻", "description": "API/服务端/数据库相关开发", "keywords": ["api", "接口", "数据库", "server", "后端", "服务", "rpc", "rest", "sql", "并发", "缓存", "队列", "docker", "k8s", "微服务"], "ttl_days": 30},
                {"id": "frontend", "name": "前端开发", "emoji": "🎨", "description": "UI/交互/客户端渲染", "keywords": ["组件", "css", "react", "vue", "组件", "页面", "ui", "样式", "渲染", "前端", "浏览器", "响应式", "web", "html", "animation"], "ttl_days": 30},
                {"id": "data", "name": "数据工程", "emoji": "📊", "description": "数据处理/ETL/分析", "keywords": ["数据", "etl", "pipeline", "spark", "sql", "数据仓库", "分析", "报表", "清洗", "flink"], "ttl_days": 60},
                {"id": "devops", "name": "DevOps", "emoji": "🔧", "description": "CI/CD/部署/基础设施", "keywords": ["部署", "ci", "cd", "docker", "k8s", "kubernetes", "jenkins", "基础设施", "监控", "运维", "terraform"], "ttl_days": 30},
                {"id": "mobile", "name": "移动开发", "emoji": "📱", "description": "iOS/Android/跨端移动开发", "keywords": ["ios", "android", "flutter", "react native", "移动端", "app", "小程序", "swift", "kotlin"], "ttl_days": 30},
                {"id": "design", "name": "设计", "emoji": "🎯", "description": "UI/UX设计/产品设计", "keywords": ["设计", "design", "figma", "ux", "原型", "交互设计", "视觉", "设计系统", "组件库", "design system"], "ttl_days": 90},
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
