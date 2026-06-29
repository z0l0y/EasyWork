---
name: slash-cmd
description: >
  Claude Code 斜杠命令调度与技能管理。将 25 个技能映射为 /easywork:<name> 命名空间子命令，
  支持 Tab 自动补全、参数透传、git 上下文注入。维护命令索引表、创建/更新/删除命令文件、
  生成技能使用文档。用户输入 /easywork: 后 Tab 即可发现所有可用技能命令。
allowed-tools: Read, Write, Bash, Grep, Glob
model: sonnet
version: 3.0
capability:
  id: slash-cmd
  display_name: 命令调度
  emoji: "💻"
  category: orchestration
  tier: 2
  inputs:
    - { name: action, type: enum, required: true, description: "操作类型：list|create|update|delete|sync|docs" }
    - { name: skill_name, type: string, required: false, description: "目标技能名（create/update/delete 时必填）" }
  outputs:
    - { name: command_status, type: text, description: "命令操作结果（已创建/已更新/已删除/索引表）" }
  triggers: ["斜杠命令","slash command","命令管理","/easywork","更新命令","重建命令",
             "slash-cmd","command list","命令列表"]
  related_skills:
    - { skill: all, relationship: outbound, desc: "为所有 25 个技能生成 /easywork:<name> 子命令入口" }
  suggested_when:
    - "新增了一个 skill 需要注册斜杠命令"
    - "skill 的触发词/描述有变更需要同步到命令文件"
    - "用户想知道有哪些可用命令（/easywork:? 索引）"
    - "命令文件丢失/损坏需要重建"
  pipeline_placement:
    good_after: []
    good_before: []
  autonomous:
    callable_by_other: false
    requires_confirmation: true
    max_depth: 0
  risk_level: L0
---

# 💻 Slash Cmd（斜杠命令调度）

> 命令入口层 · v1.0 · 将 25 个技能映射为 `/easywork:<name>` 命名空间子命令

## 1. 定位

slash-cmd 是 EasyWork 技能体系的**命令入口层**。它不执行任何业务逻辑——只为每个技能提供一个 `/easywork:<name>` 斜杠命令，让用户像使用 Claude Code 内置命令一样快速调用技能。

```
用户输入 /easywork:radar → Claude Code 加载 .claude/commands/easywork/radar.md
  → 路由到 skills/tech-radar/SKILL.md → 执行技术雷达扫描
```

**与 fullchain-dev-workflow 的关系**：

| 维度 | slash-cmd | fullchain-dev-workflow |
|------|-----------|----------------------|
| 定位 | 命令入口层（快捷方式） | 运行时编排（智能路由） |
| 触发 | `/easywork:<name>` | 自然语言触发词 |
| 启动 | 直接定位到目标 SKILL.md | 意图解析 → 分类 → 裁剪 → 执行 |
| 适用 | 知道要调用哪个技能的熟练用户 | 不确定需要什么的新用户 / 复杂任务 |
| 开销 | 最小（跳过分类和闸门） | 完整（含分类确认 + 闸门） |

两者互补，互不替代。

### 命令系统架构

```
.claude/commands/easywork/
├── paper.md           → /easywork:paper      📖 论文阅读
├── project.md         → /easywork:project     📐 项目理解
├── trace.md           → /easywork:trace       🔬 代码追踪
├── radar.md           → /easywork:radar       🛰️ 技术雷达
├── coverage.md        → /easywork:coverage    🧪 测试覆盖
├── requirements.md    → /easywork:requirements 👁️ 需求理解
├── implement.md       → /easywork:implement   ✏️ 代码实现
├── review.md          → /easywork:review      🔍 代码审查
├── retro.md           → /easywork:retro       🧠 复盘分析
├── selfcheck.md       → /easywork:selfcheck   🥊 CTO 拷打
├── graph.md           → /easywork:graph       📊 架构可视化
├── sum.md             → /easywork:sum         📋 总结报告
├── checklist.md       → /easywork:checklist   ✅ 清单审计
├── article.md         → /easywork:article     📝 文档编写
├── quick.md            → /easywork:quick       ⚡ 快问快答
├── compare.md          → /easywork:compare     ⚖️ 技术选型对比
├── test.md             → /easywork:test         🔌 接口联调测试
├── knowledge.md        → /easywork:knowledge    📚 知识库管理
├── pipeline.md        → /easywork:pipeline    🔗 流水线编排
└── meta.md            → /easywork:meta        🌐 网状分析
```

## 2. 命令索引

### 2.1 学习类（learning）

| 命令 | 技能 | 描述 | 常用参数示例 |
|------|------|------|-------------|
| `/easywork:paper` | read-paper | 论文阅读→十段报告（速览/背景/方法/实验/局限/分享） | `https://arxiv.org/abs/...` |
| `/easywork:project` | read-project | 项目架构理解（结构→模块→依赖→技术栈） | `src/` / 模块名 |
| `/easywork:trace` | trace-code | 函数调用链追踪（入口→路径→分支→数据流） | `handlePayment` / `src/api/order.ts` |
| `/easywork:radar` | tech-radar | 技术动态扫描（点/面/体三级粒度） | `深扫 MCP 协议` / `全面深扫 AI Agent` |
| `/easywork:coverage` | test-coverage | 测试覆盖率分析（五维覆盖+盲区检测） | `src/payment/` |

### 2.2 开发类（development）

| 命令 | 技能 | 描述 | 常用参数示例 |
|------|------|------|-------------|
| `/easywork:requirements` | read-requirements | 五要素需求说明+完成定义+可追溯矩阵 | 需求描述或用户故事 |
| `/easywork:implement` | code-implement | 需求文档→代码变更（文件清单+原因+影响面） | `实现用户登录接口` |
| `/easywork:review` | code-review | 七维度代码审查（反合理化+供应链检查） | `src/auth/` / PR 描述 |
| `/easywork:retro` | talk-retro | 5-Whys 根因分析+Trade-offs+工程规范 | `为什么支付模块反复出bug` |
| `/easywork:selfcheck` | self-check | 四阶段 CTO 盘问+认知缺口+汇报就绪 | 代码改动描述 |
| `/easywork:graph` | graph-fullchain | Mermaid 架构图+节点对照表 | `支付系统架构` |
| `/easywork:sum` | sum-session | 六要素总结（背景→发现→问题→解决→效果→展望） | 总结主题 |

### 2.3 质量类（quality）

| 命令 | 技能 | 描述 | 常用参数示例 |
|------|------|------|-------------|
| `/easywork:checklist` | checklist | 开发清单审计（Pre-flight 就绪+Audit 交付） | `开发前检查` / `交付检查` |
| `/easywork:test` | api-test | 接口联调测试——全覆盖用例/预期结果/错误码映射/MySQL5.7 SQL/Redis/MQ | `POST /api/user` / `帮我测这个接口` |

### 2.4 内容类（content）

| 命令 | 技能 | 描述 | 常用参数示例 |
|------|------|------|-------------|
| `/easywork:article` | article-write | Agent 输出→格式化 Markdown 文档（6 种模板） | `把刚才的分析写成技术报告` |
| `/easywork:quick` | quick-answer | 快问快答——答案先行/要点为辅/展开按需 | `tldr` / `说重点` |
| `/easywork:compare` | tech-compare | 技术方案选型对比——六阶段战略决策框架 | `对比 A 和 B` / `技术选型` |
| `/easywork:knowledge` | knowledge-base | 知识库管理——沉淀/检索/维护/交接，跨 Agent 复用知识 | `查知识库` / `整理知识库` |

### 2.5 编排类（orchestration）

| 命令 | 模式 | 描述 | 常用参数示例 |
|------|------|------|-------------|
| `/easywork:pipeline` | 🔗 线模式 | 7 条内置流水线+动态 DAG 编排 | `先理解项目架构，再追踪支付模块调用链` |
| `/easywork:meta` | 🌐 网模式 | Meta-Orchestrator 自治扩散+深度分析 | `支付模块能不能扛住双11` |

## 3. 使用指南

### 3.1 发现命令

- **Tab 补全**：输入 `/easywork:` 然后按 Tab，自动列出所有 21 个子命令
- **命令列表**：输入 `/easywork:?` 或说"命令列表"查看完整索引
- **模糊查找**：输入 `/easywork:rad` 然后 Tab 补全为 `/easywork:radar`

### 3.2 带参数调用

```
/easywork:radar MCP 协议              → 点模式，聚焦 MCP 协议深扫
/easywork:checklist 开发前检查         → Pre-flight 就绪检查
/easywork:article 把刚才的分析写成报告  → report 模板，内容来自上一步输出
/easywork:pipeline 先理解项目，再追踪支付模块 → DAG 编排
```

### 3.3 何时用命令 vs 自然语言

| 场景 | 用命令 | 用自然语言 |
|------|--------|-----------|
| 知道具体要哪个技能 | ✅ `/easywork:radar` | |
| 不确定需要什么 | | ✅ "帮我分析一下这个技术的趋势" |
| 需要多步编排 | ✅ `/easywork:pipeline` | ✅ "先理解项目架构，再追踪调用链" |
| 复杂模糊需求 | | ✅ "这个支付系统能不能扛住双11" |
| 快速单步调用 | ✅ `/easywork:paper URL` | |

## 4. 命令文件规范

### 4.1 模板格式

每个 `.claude/commands/easywork/<name>.md` 文件遵循以下模板：

```markdown
---
description: "{emoji} {中文名}——{一句话描述}"
argument-hint: "[额外参数/上下文]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/{skill-id}/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
```

### 4.2 字段说明

| 字段 | 必须 | 说明 |
|------|------|------|
| `description` | ✅ | `/help` 和自动补全时展示的命令说明。≤60 字符，以动词开头 |
| `argument-hint` | ✅ | 自动补全时的参数提示 |
| `disable-model-invocation` | ✅ | 设为 `true`——子命令不注入 system prompt，仅在手动输入时加载 |
| `allowed-tools` | ✅ | 限制命令可用的工具范围 |
| `$ARGUMENTS` | — | 用户输入的额外参数，透传给技能 |
| `!` 注入 | — | 命令加载时执行 bash 并嵌入输出（git 上下文自动注入） |

### 4.3 生成规则

- 文件名 = 技能 ID 的简写（`tech-radar` → `radar.md`，`read-paper` → `paper.md`）
- 文件名不使用完整 skill-id（避免过长：`/easywork:read-requirements` vs `/easywork:requirements`）
- pipeline 和 meta 例外——它们是模式入口，不是单技能

## 5. 维护流程

### 5.1 新增技能 → 生成命令

```
1. 确认技能已注册到 skill-graph-orchestration.md §5.2
2. 确定命令文件名（技能 ID 简写）
3. 确定分类（learning / development / quality / content）
4. 按模板生成 .claude/commands/easywork/<name>.md
5. 更新本文档 §2 命令索引表
6. 更新 SKILLS.md 技能目录总览
7. Git commit："feat: add /easywork:<name> slash command for {skill-name}"
```

### 5.2 删除技能 → 移除命令

```
1. 删除 .claude/commands/easywork/<name>.md
2. 从本文档 §2 命令索引表中移除该行
3. 从 SKILLS.md 中移除该行
4. Git commit："feat: remove /easywork:<name> slash command"
```

### 5.3 更新技能 → 同步命令

```
1. 仅触发词/描述变更 → 无需修改命令文件（命令文件只做路由）
2. skill-id 变更 → 更新命令文件中的 skills/{skill-id}/SKILL.md 路径
3. 技能分类变更 → 更新本文档 §2 中的分类
```

### 5.4 批量重建

当命令文件大面积损坏或需要统一升级格式时：

```
说"重建命令"或"更新命令"
  → Agent 加载本 SKILL.md
  → 读取 skill-graph-orchestration.md §5.2 技能注册表
  → 逐个检查/生成命令文件
  → 报告：{N} 个已存在且正确 / {M} 个新建 / {K} 个已更新
```

## 6. 与技能注册表的映射

命令文件 ↔ 技能注册表（`skill-graph-orchestration.md` §5.2）的对应关系：

| 命令文件 | 技能注册表中的行 |
|---------|----------------|
| `paper.md` | 📖 read-paper | learning |
| `project.md` | 📐 read-project | learning |
| `trace.md` | 🔬 trace-code | learning |
| `radar.md` | 🛰️ tech-radar | learning |
| `coverage.md` | 🧪 test-coverage | learning |
| `requirements.md` | 👁️ read-requirements | development |
| `implement.md` | ✏️ code-implement | development |
| `review.md` | 🔍 code-review | development |
| `retro.md` | 🧠 talk-retro | development |
| `selfcheck.md` | 🥊 self-check | development |
| `graph.md` | 📊 graph-fullchain | development |
| `sum.md` | 📋 sum-session | development |
| `checklist.md` | ✅ checklist | quality |
| `article.md` | 📝 article-write | content |
| `quick.md` | ⚡ quick-answer | content |
| `compare.md` | ⚖️ tech-compare | development |
| `test.md` | 🔌 api-test | quality |
| `knowledge.md` | 📚 knowledge-base | infrastructure |
| `pipeline.md` | — | 线模式入口 |
| `meta.md` | — | 网模式入口 |

## 7. SKILLS.md 生成

`skills/slash-cmd/assets/SKILLS.md` 是面向用户的技能目录总览文档。生成规则：
- 按类别分组（learning / development / quality / content / orchestration）
- 每行：命令 + 技能 ID + 一句话描述 + 常用示例
- 底部附流水线组合示例
- 更新触发：技能增删时同步更新

## 8. 反模式

- ❌ **不要把业务逻辑放进命令文件**——命令文件只做路由（"加载并执行 SKILL.md"）。业务逻辑维护在技能 SKILL.md 中。命令文件超过 30 行就是反模式。
- ❌ **不要为同一个技能创建多个命令名**——一个技能只有一个命令入口。如果技能有子模式（如 tech-radar 的点/面/体），由技能内部的触发词判断，不需要 `/easywork:radar-point`、`/easywork:radar-surface` 等。
- ❌ **不要忘记更新命令索引表**——新增/删除命令后必须同步更新本文档 §2 和 SKILLS.md。过期的索引表比没有索引表更糟糕。
- ❌ **不要在命令文件中写死执行逻辑**——如"执行以下 5 个步骤：1.搜索 2.分析..."。这些步骤定义在目标技能的 SKILL.md 中。命令文件重复定义会导致维护灾难——改技能逻辑却忘了改命令文件。
- ❌ **不要把 `disable-model-invocation` 设为 `false`**——21 个子命令如果全部注入 system prompt，每轮浪费 ~600 tokens。命令是给用户手动输入的，不需要模型自动调用。
- ❌ **不要用完整 skill-id 做命令名**——`/easywork:read-requirements` 太长。简写为 `/easywork:requirements`。命令名是快捷方式，不是标识符。
- ❌ **不要把 pipeline 和 meta 当普通技能**——它们是模式入口（线模式/网模式），不是单技能。用 `skills/fullchain-dev-workflow/SKILL.md` 的线/网模式执行，不需要单独的技能 SKILL.md。
- ❌ **不要跳过 git 上下文注入**——`!` 注入让命令自动感知当前分支和状态。去掉它，用户每次都要手动描述上下文。

## 9. 版本历史

- v1.0 (2026-06-27)：包含 21 个子命令（19 技能 + pipeline + meta），命名空间架构，命令索引表，维护流程，8 条反模式。
