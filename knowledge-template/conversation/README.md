# 📝 SQLite Conversation Store

> 每轮对话实时写入 · FTS5 全文检索 · 纯本地 · 零依赖

## 数据库文件

```
knowledge/conversation.db
```

一个 SQLite 文件，WAL 模式，包含所有对话历史 + 工具调用记录 + 长期知识事实。

## 快速开始

```bash
# 看总体统计
python hooks/knowledge-store.py summary

# 浏览最近 20 轮对话（表格视图）
python hooks/knowledge-store.py browse

# 只看用户提问
python hooks/knowledge-store.py browse 20 user

# 只看 Agent 回答
python hooks/knowledge-store.py browse 20 assistant

# 查看某条对话的完整内容
python hooks/knowledge-store.py turn-detail 42

# 全文搜索（FTS5）
python hooks/knowledge-store.py search "技术选型"

# 查看数据库表结构
python hooks/knowledge-store.py schema

# 某个会话的统计
python hooks/knowledge-store.py stats <session_id>
```

## 表结构

```
turns               ← 每轮对话（用户提问 + Agent 回答）
├── id              AUTOINCREMENT
├── session_id      会话 UUID
├── turn_number     轮次序号
├── timestamp       时间戳
├── role            user / assistant / system / tool
├── content         完整文本
└── content_preview 前 200 字符（自动生成）

turns_fts           ← FTS5 全文索引（自动同步）
    MATCH '关键词'  → BM25 排序结果

sessions            ← 会话元数据
├── id              会话 UUID
├── started_at      开始时间
├── ended_at        结束时间
├── domain          领域分类
├── tool_calls_count 工具调用总数
└── turn_count      对话轮数

tool_calls          ← 工具调用记录
├── session_id      所属会话
├── tool_name       工具名（Read/Bash/Write...）
├── file_paths      涉及文件
└── duration_ms     耗时

facts               ← 升级后的长期知识
├── domain          领域
├── dimension       维度（analysis/decision/pattern）
├── fact            知识内容
├── confidence      置信度（0-1）
└── retracted       是否已撤回
```

## SQL 查询示例

如果你有 `sqlite3` CLI：

```bash
sqlite3 knowledge/conversation.db
```

```sql
-- 最近 10 轮对话
SELECT timestamp, role, substr(content,1,100) FROM turns ORDER BY id DESC LIMIT 10;

-- 搜索包含"HBase"的对话
SELECT snippet(turns_fts, 1, '**', '**', '...', 40) FROM turns_fts WHERE turns_fts MATCH 'HBase';

-- 今天的对话
SELECT * FROM turns WHERE date(timestamp) = date('now');

-- 按会话统计
SELECT session_id, COUNT(*) as turns FROM turns GROUP BY session_id;

-- 所有活跃会话
SELECT * FROM sessions WHERE ended_at IS NULL;
```

如果没有 `sqlite3` CLI（Windows 常见情况），用 Python 一行查询：

```bash
python -c "import sqlite3; conn=sqlite3.connect('knowledge/conversation.db'); conn.row_factory=sqlite3.Row; [print(dict(r)) for r in conn.execute('SELECT * FROM turns LIMIT 5').fetchall()]"
```

## 写入机制

| 触发 | 写入 | 时机 |
|------|------|------|
| **Stop hook** | turns 表（Q&A 全文） | 每轮 Agent 回复结束 |
| **PostToolUse hook** | buffer JSONL | 每次工具调用后 |
| **SessionEnd hook** | tool_calls 表 + sessions 更新 | 会话退出时 |

## 隐私说明

- `knowledge/conversation.db` 已被 `.gitignore` 排除，不会提交到 Git
- 数据库纯本地，无网络传输
- 对话内容完全由你控制——删除 `knowledge/` 目录即可清除所有记录
