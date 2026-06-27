# EasyWork Knowledge Base MCP Server

> 为 Claude Code 提供知识库自动化能力：自动索引、语义搜索、去重检测、健康报告。

## 安装

```bash
cd skills/knowledge-base/mcp-server
pip install -r requirements.txt
```

## Claude Code 配置

在项目根目录的 `.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "easywork-knowledge": {
      "command": "python",
      "args": [
        "skills/knowledge-base/mcp-server/server.py",
        "--knowledge-dir",
        "knowledge"
      ],
      "env": {
        "EASYWORK_KNOWLEDGE_DIR": "knowledge"
      }
    }
  }
}
```

## MCP 工具清单

### knowledge_search

全文 + 标签搜索知识条目。

```
输入：query(关键词) + domain/source/dimension/tags(可选过滤) + limit(默认10)
输出：匹配条目列表（含相关度评分、标题、路径、标签）
```

### knowledge_context

根据当前任务描述智能检索相关知识。自动提取任务中的关键词进行搜索。

```
输入：task_description("支付模块 token 验证逻辑") + limit(默认5)
输出：相关条目摘要 + 上下文文本（可直接注入 Agent 上下文）
```

### knowledge_store

创建/更新知识条目。自动生成 ID、写入 Markdown、更新索引。

```
输入：domain + source + dimension + title + content + tags/related/source_files/source_urls(可选)
输出：条目 ID + 存储路径
```

### knowledge_stats

知识库统计信息。

```
输出：总条目数 / 领域分布 / 来源分布 / 维度分布 / 状态分布 / 过期条目列表
```

### knowledge_maintenance

知识库维护操作。

```
输入：action(detect_duplicates/find_stale/suggest_consolidation/full_report) + dry_run(默认true)
输出：建议操作列表（去重/归档/合并）
```

## 手动测试

```bash
# 搜索知识
python server.py --mode cli --tool knowledge_search --args '{"query":"支付"}'

# 查看统计
python server.py --mode cli --tool knowledge_stats

# 维护报告
python server.py --mode cli --tool knowledge_maintenance --args '{"action":"full_report"}'
```

## 架构

```
Agent 读取代码/文档
        │
        ▼
    触发规则检测
    (CLAUDE.md §知识库自动触发规则)
        │
        ├── MCP 可用 → MCP Tool: knowledge_context / knowledge_store
        │               → server.py 自动索引 + 去重 + 双向链接
        │
        └── MCP 不可用 → Agent 手动读写 knowledge/ 目录的 Markdown 文件
                        → 手动更新 _index.md
```

## 索引机制

- **启动时**：全量扫描 `knowledge/` 下所有 `.md` 文件，解析 frontmatter
- **每次工具调用时**：增量重建索引（捕获外部变更）
- **索引结构**：title_index / tag_index / domain_index（全部内存，百万级条目 <100MB）
- **搜索算法**：关键词匹配 + 标签匹配 + 领域匹配（加权评分排序）
