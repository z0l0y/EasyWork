# EasyWork Memory Index

> L1 知识库索引 · 始终加载 · 只存指针不存内容 · 更新：2026-06-27

## 项目知识

- [知识库总索引](knowledge/README.md) — 领域/来源/会话三维索引
- 领域定义见 `.easywork/config.json` → `knowledge.domains`（用户自定义，不再硬编码）

## 代码分析

- [代码分析索引](knowledge/code/_index.md) — 模块结构/调用链/依赖分析记录
- 按模块检索：`knowledge/code/{module}/`

## 外部资料

- [用户材料](knowledge/source/inner/_index.md) — 用户提供的代码/文档/需求（只读）
- [Agent 搜索](knowledge/source/outer/_index.md) — GitHub/论文/博客搜索结果

## 决策记录

- [ADR 索引](knowledge/decisions/_index.md) — 架构决策记录（MADR v4.0）

## 会话记录

- [用户提问](knowledge/conversation/prompts/_index.md) — Prompt 归档（了解用户关注什么）
- [Agent 回答](knowledge/conversation/outputs/_index.md) — Output 归档（了解 Agent 怎么答的）
- [会话交接](knowledge/sessions/_index.md) — Handoff 记录（上次停在哪儿）

## 快速链接

- [EasyWork 快速参考](QUICKREF.md)
- [CHANGELOG](CHANGELOG.md)
- [README](README.md)
- [贡献指南](CONTRIBUTING.md)
- [故障排除](TROUBLESHOOTING.md)

## 使用方式

- **查知识**：说"查知识库" → Agent 检索相关知识
- **沉淀知识**：Agent 完成分析后自动写入，或说"沉淀一下"
- **整理知识库**：说"整理知识库" → Agent 去重/合并/归档
- **会话交接**：会话结束时自动触发

> **原则**：此文件只存指针。知识内容在 `knowledge/` 目录下的 L2 文件中。
