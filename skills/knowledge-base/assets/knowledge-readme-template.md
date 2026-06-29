# 📚 EasyWork 知识库

> L1 总索引 · 始终加载 · 只存指针不存内容
> 最后更新：{{LAST_UPDATE}} | 总条目数：{{TOTAL_ENTRIES}}

## 领域目录

> 领域由 `.easywork/config.json` → `knowledge.domains` 动态定义。以下为初始化时的占位表——实际内容由 config 驱动。

| 领域 | 路径 | 条目数 | 说明 |
|------|------|--------|------|
{{DOMAIN_TABLE_ROWS}}

## 来源目录

| 来源 | 路径 | 条目数 | 说明 |
|------|------|--------|------|
| 📥 Inner | [source/inner/](source/inner/_index.md) | {{N}} | 用户提供的材料（代码/文档/需求） |
| 🌐 Outer | [source/outer/](source/outer/_index.md) | {{N}} | Agent 搜索的外部资料（GitHub/论文/博客） |

## 会话目录

| 维度 | 路径 | 条目数 | 说明 |
|------|------|--------|------|
| ❓ Prompts | [conversation/prompts/](conversation/prompts/_index.md) | {{N}} | 用户提问归档 |
| 💬 Outputs | [conversation/outputs/](conversation/outputs/_index.md) | {{N}} | Agent 回答归档 |

## 代码分析

| 模块 | 路径 | 条目数 | 最后分析 |
|------|------|--------|---------|
{{CODE_MODULES_TABLE}}

## 架构决策

| ID | 标题 | 日期 | 状态 |
|----|------|------|------|
{{DECISIONS_TABLE}}

## 会话交接

最近交接记录：[sessions/](sessions/_index.md) — 共 {{N}} 条

## 快速检索

- 查领域知识：搜索 `domain/{domain-id}/` 下的 `_index.md`（domain 由 config 定义）
- 查模块分析：搜索 `code/` 下的模块名
- 查技术决策：搜索 `decisions/DEC-*.md`
- 查历史提问：搜索 `conversation/prompts/` 下的日期或标签
- 查上次停在哪儿：读最近一条 `sessions/*.md`

> **使用原则**：本级索引只存指针。如需加载具体知识内容，按路径进入 L2 目录。
