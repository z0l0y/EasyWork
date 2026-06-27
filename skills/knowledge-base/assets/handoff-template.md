---
dimension: reference
domain: {{DOMAIN}}
source: derived
status: stable
created: {{TIMESTAMP}}
session: {{SESSION_ID}}
tags: [handoff, {{TAGS}}]
---

# 会话交接 — {{DATE}}

## ✅ 已完成

{{#each completed}}
- {{this}}
{{/each}}

## 🛑 停在

{{当前进度——下一步该做什么，下一个 Agent 从这里开始}}

## 📋 关键决策

{{#each decisions}}
- **{{decision}}**：选择 {{chosen}} 而非 {{alternatives}}，因为 {{reason}}
{{/each}}

## 🔓 打开事项

{{#each open_threads}}
- {{this}}（预期解决时间：{{when}}）
{{/each}}

## 📁 涉及文件

{{#each files}}
- `{{path}}` — {{change_type}}：{{description}}
{{/each}}

## 📚 知识沉淀

本次会话新增/更新的知识条目：
{{#each knowledge_entries}}
- [{{id}}]({{path}}) — {{title}}
{{/each}}

## 🔗 继续方式

下一个 Agent / 会话：
1. 读 `MEMORY.md` 了解知识库索引
2. 读 `knowledge/sessions/{{session_id}}.md`（本文件）了解上次停在哪儿
3. 搜索相关知识条目：`{{suggested_queries}}`
4. 从 `{{next_action}}` 继续
