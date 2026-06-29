# 📚 知识库初始化脚本

> 本文件描述了 Agent 首次初始化知识库的流程。
> 触发词："初始化知识库" / "创建知识库" / "init knowledge base"

## 初始化步骤

### Step 1: 创建目录结构

```
knowledge/
├── README.md                    ← L1 总索引
├── domain/                      ← 子目录按 .easywork/config.json → knowledge.domains 动态创建
│   ├── {domain-1}/
│   │   └── _index.md
│   ├── {domain-2}/
│   │   └── _index.md
│   └── ...
├── source/
│   ├── inner/
│   │   └── _index.md
│   └── outer/
│       └── _index.md
├── conversation/
│   ├── prompts/
│   │   └── _index.md
│   └── outputs/
│       └── _index.md
├── code/
│   └── _index.md
├── decisions/
│   └── _index.md
└── sessions/
    └── _index.md
```

### Step 2: 生成各目录的 _index.md

按 `assets/index-template.md` 模板，生成空的索引文件。

### Step 3: 生成 knowledge/README.md

按 `assets/knowledge-readme-template.md` 模板，填充初始统计数据（均为 0）。

### Step 4: 生成 CLAUDE.md（如不存在）

如果项目根目录无 CLAUDE.md，按以下模板创建：

```markdown
# CLAUDE.md

## 项目概述
{EasyWork 项目一句话描述}

## 构建与运行
- 本项目为 Claude Code Skills 集合，无编译步骤
- Skill 文件位于 `skills/` 目录
- 斜杠命令位于 `.claude/commands/easywork/`

## 架构概览
- `skills/` — 18+ 技能定义（每个技能一个 SKILL.md）
- `skills/fullchain-dev-workflow/SKILL.md` — 编排中枢
- `.claude/commands/easywork/` — 斜杠命令入口
- `knowledge/` — Agent 知识库（L2 内容层）

## 编码规范
- Skill 文件使用 YAML frontmatter + Markdown
- 中文为主要文档语言
- Emoji 作为技能唯一视觉标识符

## 知识库
详见 `MEMORY.md`（知识库索引）和 `knowledge/README.md`（知识库总索引）。
```

### Step 5: 生成 MEMORY.md（如不存在）

按以下格式创建（L1 索引，只存指针）：

```markdown
# EasyWork Memory Index

> L1 知识库索引 · 始终加载 · 只存指针不存内容 · 更新：{date}

## 项目知识
- [知识库总索引](knowledge/README.md) — 领域/来源/会话三维索引
- 领域链接由 `.easywork/config.json` → `knowledge.domains` 动态生成

## 代码分析
- [代码分析索引](knowledge/code/_index.md) — 模块分析记录

## 决策记录
- [ADR 索引](knowledge/decisions/_index.md) — 架构决策记录

## 会话记录
- [用户提问](knowledge/conversation/prompts/_index.md) — Prompt 归档
- [Agent 回答](knowledge/conversation/outputs/_index.md) — Output 归档
- [会话交接](knowledge/sessions/_index.md) — Handoff 记录

## 快速链接
- [EasyWork 快速参考](QUICKREF.md)
- [CHANGELOG](CHANGELOG.md)
- [贡献指南](CONTRIBUTING.md)
```

### Step 6: 验证

初始化完成后，检查：
- [ ] 所有目录已创建
- [ ] 所有 `_index.md` 已生成（包含有效 YAML 但条目数为 0）
- [ ] `knowledge/README.md` 已生成
- [ ] `CLAUDE.md` 已生成（或确认已存在）
- [ ] `MEMORY.md` 已生成（或确认已存在）

### Step 7: 报告

```
📚 知识库初始化完成

目录结构：{N} 个目录，{M} 个索引文件
CLAUDE.md：{已创建/已存在}
MEMORY.md：{已创建/已存在}
knowledge/README.md：已创建

→ 知识库已就绪。Agent 将在后续工作中自动沉淀知识。
```
