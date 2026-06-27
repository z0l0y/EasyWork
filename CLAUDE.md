# CLAUDE.md

> L1 薄路由 · 始终加载 · 项目规范与架构概览

## 项目概述

EasyWork 是一个 Claude Code 技能生态系统，提供 19 个专业技能 + 流水线编排 + 网状自治分析。覆盖从需求理解、代码实现、审查、测试、复盘到 CTO 拷打的完整研发生命周期。

## 构建与运行

- 本项目为 Claude Code Skills 集合，无编译/构建步骤
- Skill 文件位于 `skills/` 目录，每个技能一个 `SKILL.md`
- 斜杠命令位于 `.claude/commands/easywork/`（21 条命令）
- 编排中枢：`skills/fullchain-dev-workflow/SKILL.md`
- 快速参考：`QUICKREF.md`

## 架构概览

```
EasyWork/
├── CLAUDE.md                 ← 本文件（L1 路由，始终加载）
├── MEMORY.md                 ← 知识库索引（指针列表）
├── QUICKREF.md               ← 30 秒快速参考
├── skills/                   ← 19 个技能定义
│   ├── fullchain-dev-workflow/  ← 编排中枢（任务分类+步骤裁剪+闸门系统）
│   ├── knowledge-base/          ← 知识库管理（跨切面能力）
│   └── ...                      ← 其余 17 个技能
├── .claude/commands/easywork/ ← 21 条斜杠命令入口
└── knowledge/                 ← 知识库内容层（L2）
```

## 编码规范

- **Skill 文件**：YAML frontmatter + Markdown，中文为主要文档语言
- **Emoji** 作为技能唯一视觉标识符（不可重复使用）
- **铁律系统**：40 条全局铁律（编排中枢 §2-3），风险 L0-L4 五级分类
- **ETR 证据标准**：所有关键结论必须含 Evidence/Thinking/Risk 三元组
- **命令文件**：`disable-model-invocation: true`，仅做路由不做业务逻辑

## 技能调用方式

1. **自然语言**：说触发词（如"技术选型"、"帮我测接口"）
2. **斜杠命令**：`/easywork:<name>`（如 `/easywork:radar`）
3. **编排中枢**：说"用 EasyWork" 走完整 10 步流程

## 知识库

- **L1 索引**：`MEMORY.md`（始终加载，只存指针）
- **L2 内容**：`knowledge/` 目录（按需加载）
- **知识沉淀**：Agent 阅读代码/文档后自动写入知识库
- **会话交接**：每次会话结束自动写交接记录到 `knowledge/sessions/`
