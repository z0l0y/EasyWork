---
name: knowledge-base
description: >
  Agent 知识库管理与沉淀（v2.0：SQLite + Stop Hook 每轮实时写入）。
  按领域模型（联调需求/开发需求/季度O）组织，区分来源（用户提供 inner / Agent 搜索 outer）
  和会话维度（用户提问 prompt / Agent 回答 output）。
  跨上下文、跨 Agent 对话复用，避免每次重读资料，节省 token 和时间。
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
model: sonnet
version: 2.0
capability:
  id: knowledge-base
  display_name: 知识库管理
  emoji: "📚"
  category: infrastructure
  tier: 2
  inputs:
    - { name: action, type: enum, required: true, description: "操作类型：capture|retrieve|maintain|init|handoff" }
    - { name: domain, type: enum, required: false, description: "领域：integration|development|quarterly-o" }
    - { name: query, type: string, required: false, description: "检索查询或维护范围" }
  outputs:
    - { name: knowledge_entry, type: markdown, description: "结构化知识条目（含 frontmatter）" }
    - { name: retrieval_result, type: markdown, description: "检索结果摘要 + 相关条目列表" }
    - { name: maintenance_report, type: markdown, description: "维护报告（去重/合并/归档/升级统计）" }
  triggers:
    - "知识库"
    - "knowledge base"
    - "查知识库"
    - "沉淀知识"
    - "整理知识库"
    - "我的知识库"
    - "知识管理"
    - "写入知识库"
    - "检索知识"
    - "knowledge management"
    - "kb"
  related_skills:
    - { skill: all, relationship: outbound, desc: "所有技能完成工作后可将产出沉淀到知识库（跨切面能力）" }
    - { skill: sum-session, relationship: inbound, desc: "SUM 的六要素总结可自动沉淀为知识条目" }
    - { skill: tech-compare, relationship: inbound, desc: "技术选型的决策过程应作为 ADR 沉淀" }
    - { skill: talk-retro, relationship: inbound, desc: "复盘结论应升级为长期知识" }
    - { skill: self-check, relationship: inbound, desc: "CTO 拷打暴露的认知缺口可标记为待补充知识" }
    - { skill: slash-cmd, relationship: inbound, desc: "知识库结构变更时需同步更新命令和索引" }
  suggested_when:
    - "用户提供了需要长期保留的材料（代码仓库/需求文档/技术规范）"
    - "Agent 阅读了大量代码并形成了理解——需要沉淀避免下次重读"
    - "完成了一个功能/接口/季度目标——需要归档知识"
    - "跨会话/跨 Agent 工作时——先查知识库看有没有已有分析"
    - "用户说'记住这个' / '下次别忘了' / '保存到知识库'"
    - "新会话开始——先检索知识库了解项目背景"
  pipeline_placement:
    good_after: [read-project, read-paper, trace-code, tech-radar, sum-session]
    good_before: [code-implement, code-review, tech-compare, self-check]
  autonomous:
    callable_by_other: true
    requires_confirmation: false
    max_depth: 1
  risk_level: L0
---

# 📚 Knowledge Base（知识库管理）

> Agent 知识沉淀与复用层 · v2.0 · Stop Hook 每轮实时写入 · SQLite + FTS5 全文检索 · Markdown 可读备份 · 跨上下文复用

## 0. 存储架构（v2.0）

```
每轮对话 → Stop hook → SQLite (实时，per-turn)
   │                      ├── turns 表 (用户提问 + Agent 回答)
   │                      ├── turns_fts (FTS5 全文索引)
   │                      └── sessions 表 (会话元数据)
   │
工具调用 → PostToolUse hook → buffer (JSONL)
   │
会话结束 → SessionEnd hook → flush worker
   ├── raw dump (JSON, 7天TTL)
   ├── daily log (Markdown, 人类可读)
   └── session handoff (Markdown, 会话交接)
```

**查询方式**：
```bash
python hooks/knowledge-store.py search "HBase"      # FTS5 全文搜索
python hooks/knowledge-store.py recent 20            # 最近 20 轮对话
python hooks/knowledge-store.py stats <session_id>    # 会话统计
sqlite3 knowledge/conversation.db "SELECT * FROM turns WHERE content MATCH '技术选型'"
```

## 1. 为什么需要知识库

```
现状（无知识库）：
  每次新会话 → Agent 重新读代码 → 重新读文档 → 重新搜索 →
  重新理解项目结构 → 重新分析依赖关系 →
  产出结果 → 对话结束 → 全部丢失 →
  下次会话 → 重新读代码 → 重新读文档 → ...

痛点量化：
  - 每次新会话浪费 2000-5000 tokens 重新理解项目
  - 跨 Agent 对话时母 Agent 的中间分析结果子 Agent 看不到
  - 用户每次都要重新提供材料（代码/文档/需求）
  - 无法追溯"这个结论是怎么来的"（证据链丢失）
  - 同一个模块被分析 5 次，每次得出相似的结论
```

**知识库要解决的问题**：

| 问题 | 解决方案 |
|------|---------|
| 每次重读代码 | 代码分析结果沉淀为结构化知识条目，下次直接检索 |
| 材料重复提供 | 用户提供的材料标记为 inner source，永久保存引用 |
| 分析过程丢失 | Agent 分析过程（推理链/证据链）完整记录 |
| 跨 Agent 不可见 | 知识库是所有 Agent 共享的单一事实源 |
| 无法追溯 | 每个知识条目含来源标注 + 创建时间 + 关联条目 |
| 组织混乱 | 领域模型（联调/开发/季度O）+ 来源维度 + 会话维度三维分类 |

---

## 1. 知识架构

### 1.0 核心策略：全部沉淀 → 定时巡检清理 → 总结归纳汇总

**不是选择性地存，而是先全部存，再定期清理。**

```
你的每次对话
  │
  ├── PostToolUse hook（每次工具调用后自动触发）
  │     → 写入 knowledge/.buffer/{session-id}.jsonl
  │     → 只记录元数据（工具名/文件路径/耗时），不存输出内容
  │
  ├── SessionEnd hook（会话结束时自动触发，100% 保证）
  │     → 读 buffer → 写 raw dump（knowledge/conversation/raw/）
  │     → 写 session handoff（knowledge/sessions/）
  │     → 清理 buffer
  │
  └── 你说"整理知识库"（定时巡检清理）
        → 扫描 raw/ → 去重 → 提取关键问答 → 写入 prompts/ + outputs/
        → 扫描 raw/ → 识别模式 → 合并碎片 → 升级到 domain/
        → 清理 raw/ 中超过 7 天的旧文件
        → 输出清理报告：合并 X 条 / 升级 Y 条 / 清理 Z 条
```

**四层会话存储**：

```
knowledge/conversation/
├── raw/           ← Layer 0：全量原始转储（7 天 TTL，自动生成，不经筛选）
│   └── {YYYYMMDD}/
│       └── {session-id}.json    ← 完整的工具调用事件日志
├── prompts/       ← Layer 1：提取的用户提问（清理后，手动/半自动策展）
│   └── {date}-{topic}.md
├── outputs/       ← Layer 1：提取的 Agent 回答（清理后，手动/半自动策展）
│   └── {date}-{topic}.md
├── sessions/      ← Layer 2：会话交接记录（自动生成，每次会话结束）
│   └── {date}-{session-id}.md
└── patterns/      ← Layer 3：从碎片中升级的模式知识（定期清理时生成）
    └── {tag}-pattern.md        ← 同一标签 ≥3 条碎片 → 合并为综合条目
```

### 1.1 三层渐进披露（L1→L2→L3）

```
L1 — 薄索引（始终加载，<200 行）
  ├── CLAUDE.md           ← 项目规范 + 构建命令 + 架构概览（Agent 入口）
  ├── MEMORY.md            ← 知识库索引（指针列表，不存内容）
  └── knowledge/README.md  ← 知识库总索引（domain/source/conversation 三级目录）
  
L2 — 领域知识（按需加载）
  └── knowledge/
      ├── domain/          ← 按项目需求领域组织
      │   ├── integration/     ← 联调需求（短期，API 级）
      │   ├── development/     ← 开发需求（中期，Feature 级）
      │   └── quarterly-o/     ← 季度 OKR（长期，战略级）
      ├── source/          ← 按来源类型组织
      │   ├── inner/           ← 用户提供的材料（代码/文档/需求）
      │   └── outer/           ← Agent 搜索的外部资料
      ├── conversation/    ← 按会话维度组织
      │   ├── raw/             ← 🆕 Layer 0：全量原始转储（7 天 TTL）
      │   ├── prompts/         ← 🆕 Layer 1：提取的用户提问
      │   ├── outputs/         ← 🆕 Layer 1：提取的 Agent 回答
      │   └── patterns/        ← 🆕 Layer 3：升级的模式知识
      ├── code/            ← 代码分析知识
      ├── decisions/       ← 架构决策记录（ADR）
      └── sessions/        ← 会话交接记录

L3 — 深度分析（可选，大项目启用）
  └── 语义检索 + 知识图谱（未来：向量化 + 实体关系图）
```

**核心原则**：L1 只存指针，L2 存内容，L3 存关系。加载 L1 成本恒定（<200 行），L2 按需加载。

### 1.2 知识条目格式

每个知识条目是一个 Markdown 文件，必须包含 YAML frontmatter：

```yaml
---
id: kb-20260627-001
domain: development              # integration | development | quarterly-o
source: inner                    # inner | outer | derived
dimension: analysis              # prompt | output | analysis | reference | decision
status: stable                   # draft | stable | archived
created: 2026-06-27T14:30:00+08:00
updated: 2026-06-27T14:30:00+08:00
session: 2026-06-27-session-01
tags: [payment, auth, token, performance]
related: [kb-20260625-003, kb-20260626-007]
source_files: [src/auth/login.go, src/auth/token.go]
source_urls: []
evidence: [ETR 三元组——证据/推理/风险]
---

# {标题——一句话概括本条知识的核心发现}

## 背景
{为什么产生这条知识——什么任务/什么问题触发的}

## 核心内容
{知识的实质内容——分析结论/代码理解/决策理由/问题解答}

## 证据链
- **E (Evidence)**：{证据——代码位置/测试输出/日志/数据对比}
- **T (Thinking)**：{推理——从现象到结论的逻辑链}
- **R (Risk)** ：{风险——未覆盖/边界/假设/时效性}

## 关联
- 前置知识：{kb-xxx}
- 后续知识：{kb-yyy}
- 矛盾知识：{如有，标注冲突及解决}

## 时效性
- 基于代码版本：{commit hash 或 branch}
- 预计失效条件：{什么变更会导致本条知识需要重新验证}
- 下次复查日期：{YYYY-MM-DD}
```

### 1.3 索引文件格式

每个目录下的 `_index.md` 维护该目录的知识条目列表：

```markdown
# {目录名} 知识索引

> 更新：2026-06-27 | 条目数：{N}

| ID | 标题 | 状态 | 创建日期 | 标签 |
|----|------|------|---------|------|
| kb-xxx | {标题} | stable | 2026-06-27 | #tag1 #tag2 |
```

---

## 2. 领域模型（Domain Model）

### 2.1 三级领域分类

| 领域 | 英文 | 生命周期 | 典型粒度 | 跟进频率 | 示例 |
|------|------|---------|---------|---------|------|
| 🔌 联调需求 | integration | 1-7 天 | 单个 API/接口 | 每日 | `POST /api/v1/orders` 联调 |
| 🚀 开发需求 | development | 1-4 周 | Feature/模块 | 每周 | 支付模块重构 / 用户系统 |
| 🎯 季度 O | quarterly-o | 3 个月 | OKR/战略目标 | 每两周 | Q3 技术债务削减 / 性能优化 50% |

**分类决策树**：

```
这个任务/知识涉及什么？
  ├── 是单个 API 的联调/测试/验证？
  │     → domain: integration
  │     → 生命周期：7 天后自动标记为可归档
  ├── 是一个具体的功能开发/模块重构/技术改进？
  │     → domain: development
  │     → 生命周期：功能上线后标记为可归档
  └── 是一个跨 Sprint 的战略目标/OKR？
        → domain: quarterly-o
        → 生命周期：季度末复盘后归档
        → 需要进度跟踪 + 阶段性总结
```

### 2.2 季度 O 特殊管理

季度 O（OKR 的 Objective）是企业级战略目标，需要整个季度持续跟进：

```
knowledge/domain/quarterly-o/{okr-slug}/
├── _index.md            ← 该 O 的知识索引
├── objective.md          ← O 的分解（目标 → KR → 行动计划）
├── progress.md           ← 进度跟踪（每两周更新）
├── decisions.md          ← 关键决策记录
├── retro.md              ← 季度末复盘
└── weekly/               ← 每周/每两周的跟进记录
    ├── week-01.md
    ├── week-02.md
    └── ...
```

**进度跟踪模板**（`progress.md`）：

```markdown
---
domain: quarterly-o
status: in-progress
okr_period: 2026-Q3
objective: {O 的描述}
key_results:
  - KR1: {可量化指标} — 当前：{X}% — 目标：{Y}%
  - KR2: {可量化指标} — 当前：{X}% — 目标：{Y}%
last_update: 2026-07-15
next_review: 2026-07-30
---

## 最新进度（截至 {date}）

| KR | 进度 | 状态 | 阻碍 | 下一步 |
|----|------|------|------|--------|
| KR1 | 45% | 🟡 | {阻碍描述} | {下一步} |
| KR2 | 60% | 🟢 | 无 | {下一步} |

## 历史更新
- 2026-07-01：{摘要}
- 2026-06-15：{摘要}
```

---

## 3. 来源维度（Source Dimension）

### 3.1 Inner vs Outer vs Derived

| 来源类型 | 标识 | 含义 | 存储位置 | 示例 |
|---------|------|------|---------|------|
| **Inner** | `source: inner` | 用户提供的材料 | `source/inner/` | 用户贴的代码片段、需求文档、接口文档、设计稿 |
| **Outer** | `source: outer` | Agent 搜索的外部资料 | `source/outer/` | GitHub 搜索结果、论文、博客、技术文档、Stack Overflow |
| **Derived** | `source: derived` | Agent 分析推导的结论 | 按 domain 存储 | 代码分析结论、架构推断、依赖关系图、性能评估 |

**Inner 材料的特殊管理**：
- Inner 材料是**用户信任的数据源**，Agent 不得擅自修改原始内容
- Inner 材料应完整保存原始引用（代码片段/文档链接/粘贴内容）
- Agent 对 Inner 材料的分析应另存为 derived 条目，通过 `related` 关联原 Inner 条目
- 同一 Inner 材料被多次使用时，只存一份，多次引用

### 3.2 来源标注规范

每个知识条目必须在 frontmatter 中标注来源：

```yaml
# Inner 来源
source: inner
source_files: [src/payment/handler.go:45-89, docs/api/payment.md]
source_urls: []

# Outer 来源
source: outer
source_files: []
source_urls: [https://github.com/..., https://arxiv.org/abs/...]

# Derived 来源
source: derived
source_files: [src/payment/handler.go, src/payment/service.go]
source_urls: []
based_on: [kb-20260625-001, kb-20260626-003]  # 基于哪些 Inner/Outer 条目推导
```

---

## 4. 会话维度（Conversation Dimension）

### 4.1 Prompt vs Output 分离

| 维度 | 标识 | 含义 | 存储位置 | 用途 |
|------|------|------|---------|------|
| **Prompt** | `dimension: prompt` | 用户提问 | `conversation/prompts/` | 了解用户关注什么、什么场景触发 |
| **Output** | `dimension: output` | Agent 回答 | `conversation/outputs/` | 了解 Agent 怎么回答的、结论是什么 |

**分离的价值**：
- **用户画像**：聚合所有 prompt，看出用户关注的技术领域、常见痛点、决策偏好
- **质量审计**：对比 prompt 和 output，检查 Agent 是否真正回答了用户的问题
- **模式发现**：相似 prompt 反复出现 → 说明这个领域需要系统化解决，而非每次临时回答
- **回答一致性**：同一问题在不同时间被问 → 检查 Agent 回答是否一致

### 4.2 会话归档格式

```
conversation/
├── prompts/
│   └── 2026-06-27-payment-token-expiry.md    ← 一次提问一个文件
└── outputs/
    └── 2026-06-27-payment-token-expiry.md    ← 同名文件，Agent 的回答
```

**Prompt 归档模板**：

```markdown
---
dimension: prompt
domain: development
date: 2026-06-27T14:30:00+08:00
session: 2026-06-27-session-01
tags: [payment, token, performance]
related_output: 2026-06-27-payment-token-expiry.md
---

# {日期} — {一句话概括用户的问题}

## 用户原话
{用户的原始提问，保持原样}

## 上下文
- 当前分支：{branch}
- 相关文件：{files}
- 前置对话摘要：{context}

## 问题类型
- [ ] 技术决策
- [ ] Bug 排查
- [ ] 代码理解
- [ ] 方案设计
- [ ] 工具使用
- [ ] 知识查询
```

**Output 归档模板**：

```markdown
---
dimension: output
domain: development
date: 2026-06-27T14:35:00+08:00
session: 2026-06-27-session-01
tags: [payment, token, performance]
related_prompt: 2026-06-27-payment-token-expiry.md
related_knowledge: [kb-20260627-001]
---

# {日期} — Agent 回答：{一句话概括}

## 核心结论
{TL;DR——如果只记一句话，记什么}

## 完整回答
{Agent 的完整回答——证据/推理/风险}

## 关键代码/命令
{回答中涉及的具体代码位置、命令、配置}

## 后续建议
{Agent 建议的下一步行动}
```

---

## 5. 操作流程

### 5.1 Phase 1: 知识捕获（Capture）

**触发条件**（满足任一即触发）：
1. Agent 阅读了 ≥3 个文件并形成理解
2. 用户明确说"记住这个"/"保存到知识库"/"沉淀一下"
3. 完成了一个有意义的分析（不只是"帮我看下这个函数"）
4. 外部搜索找到了有价值的参考资料
5. 做出了一个需要记录的决策（技术选型/架构变更/方案取舍）
6. 会话结束——自动触发交接记录

**捕获流程**：

```
1. 判断是否需要捕获
   ├── 单文件简单查看 → 不捕获（不值得）
   ├── 多文件分析/外部搜索 → 捕获
   └── 复杂决策/季度 O 相关 → 必须捕获

2. 确定知识分类
   ├── domain: 联调？开发？季度O？
   ├── source: Inner？Outer？Derived？
   └── dimension: Prompt？Output？Analysis？Reference？Decision？

3. 生成知识条目 ID
   格式：kb-{YYYYMMDD}-{3位序号}
   检查 _index.md 避免冲突

4. 编写知识条目
   按 §1.2 模板填写，ETR 三元组不可为空

5. 写入知识库
   写入 knowledge/{分类路径}/{id}.md
   更新对应 _index.md

6. 标注来源出处
   Inner → 保存原始材料引用
   Outer → 保存外部链接 + 访问时间
   Derived → 标注基于哪些条目推导

7. 关联已有知识
   检查是否有相关条目，通过 related 字段互链
```

**捕获决策矩阵**：

| 场景 | 是否捕获 | domain | source | dimension |
|------|---------|--------|--------|-----------|
| 阅读整个模块的代码并分析架构 | ✅ 必须 | development | derived | analysis |
| 用户提供了 API 文档让 Agent 理解 | ✅ 必须 | integration | inner | reference |
| Agent 搜索了 3+ 个外部资源做技术调研 | ✅ 必须 | development | outer | reference |
| 用户问了一个复杂问题，Agent 长篇回答 | ✅ 应该 | 按内容 | derived | output |
| 做了一个技术选型决策（A vs B） | ✅ 必须 | development | derived | decision |
| 完成了一次 API 联调 | ✅ 必须 | integration | derived | analysis |
| 季度 O 进展更新 | ✅ 必须 | quarterly-o | derived | analysis |
| 用户简单问"这个函数是干嘛的" | ❌ 不捕获 | — | — | — |
| 改了一行配置 | ❌ 不捕获 | — | — | — |
| Agent 说了个笑话 | ❌ 不捕获 | — | — | — |

### 5.2 Phase 2: 知识检索（Retrieve）

**触发时机**：
1. 新会话开始——自动检索相关知识库了解项目
2. 接到新任务——先查知识库有没有类似任务的分析
3. 用户问"之前分析过 XX 吗"——精确检索
4. Agent 发现自己要分析一个可能已被分析过的模块

**检索流程**：

```
1. 读 L1 索引
   读 MEMORY.md → 找到相关领域的知识库目录
   读 knowledge/README.md → 找到更细粒度的索引

2. 按领域过滤
   根据当前任务类型确定 domain → 读对应 _index.md

3. 按标签匹配
   搜索相关 tags → 找到候选条目 ID 列表

4. 加载候选条目
   读候选条目的 frontmatter + 核心内容（不加载全部）
   根据 relevance 排序

5. 输出检索摘要
   如果找到相关条目 → 输出摘要 + 建议直接引用的条目
   如果没找到 → 标注"该领域无已有知识，将从头分析"
```

**检索输出格式**：

```markdown
## 📚 知识库检索结果

查询：{query}
领域：{domain}
找到 {N} 条相关知识：

| # | 条目 | 相关度 | 摘要 |
|---|------|--------|------|
| 1 | [kb-xxx](path) — {标题} | ⭐⭐⭐ | {一句话摘要} |
| 2 | [kb-yyy](path) — {标题} | ⭐⭐ | {一句话摘要} |

### 可直接复用的知识
- kb-xxx 已分析过 `src/auth/login.go` 的 token 验证链——无需重新追踪
- kb-yyy 已记录 payment 模块的依赖关系——可引用于当前重构

### 知识空白
- `src/notification/` 模块无已有分析——需要从头理解

→ 基于以上 {N} 条已有知识，本次任务预计节省 ~{X} tokens / {Y} 分钟
```

### 5.3 Phase 3: 知识存储（Store）

**写入前检查**：
1. 是否与已有条目重复？→ 去重检查（标题相似度 > 80% → 更新而非新建）
2. Frontmatter 是否完整？→ id/domain/source/dimension/status/tags 六个必填字段
3. ETR 三元组是否齐全？→ Evidence/Thinking/Risk 不可为空
4. 来源是否标注？→ source_files 或 source_urls 至少一个非空
5. 是否与已有知识矛盾？→ 如矛盾，标注并说明

**目录自动创建**：写入时如目标目录不存在，自动创建目录 + `_index.md`。

**更新策略**：

| 场景 | 操作 | 说明 |
|------|------|------|
| 新知识，无重复 | `Write` 新文件 | 正常创建 |
| 与已有条目高度相似（>80%） | `Edit` 更新已有条目 | 更新 updated 时间，补充新发现 |
| 与已有条目矛盾 | `Write` 新文件 + 互链 | 两条都保留，related 中标注"contradicts" |
| 已有条目已过时（代码已变更） | `Edit` 标注 `status: archived` | 不删除，标注失效原因和时间 |
| 多条碎片化知识可合并 | `Write` 新文件 + 标记旧条目 archived | 合并为一条综合条目 |

### 5.4 Phase 4: 知识维护（Maintain）—— 定时巡检清理

**触发时机**：
- 用户说"整理知识库"/"清理知识库"/"定时巡检"/"归纳汇总"
- 知识库条目超过 50 条——Agent 主动建议整理
- 季度末——季度 O 归档
- 项目重大变更后——检查受影响的知识条目

**核心理念**：全部沉淀 → 定时巡检 → 去重合并 → 总结归纳 → 升级模式

**维护流程**：

```
整理知识库 启动
  │
  ├── Step 1：扫描 raw/ 层（conversation/raw/）
  │     → 列出所有原始转储文件
  │     → 统计：{N} 个会话 / {M} 次工具调用 / {K} 个涉及文件
  │
  ├── Step 2：清理过期 raw（>7 天）
  │     → 删除 >7 天的 raw JSON 文件
  │     → 如有关键信息 → 先提取再删除
  │     → 更新 raw/_index.md
  │
  ├── Step 3：从 raw 提取用户提问
  │     → 扫描 raw 中 Read/WebSearch 事件
  │     → 识别用户意图（通过文件路径/搜索关键词推断）
  │     → 写入 conversation/prompts/{date}-{topic}.md
  │     → 统计：提取了 {X} 条提问
  │
  ├── Step 4：从 raw 提取 Agent 回答模式
  │     → 扫描 raw 中 Write/Edit 事件
  │     → 识别产出类型（代码/文档/配置/分析）
  │     → 写入 conversation/outputs/{date}-{topic}.md
  │     → 统计：记录了 {Y} 类产出
  │
  ├── Step 5：升级碎片为模式
  │     → 扫描所有 knowledge/ 条目的 tags
  │     → 同一 tag 下 ≥3 条 → 合并为 conversation/patterns/{tag}-pattern.md
  │     → 同类型问题被问 ≥3 次 → 建议创建 FAQ 或专门的 Skill
  │     → 统计：发现了 {Z} 个可升级模式
  │
  ├── Step 6：去重合并
  │     → 扫描所有 _index.md → 标题相似度 > 80% 的条目对
  │     → 展示给用户确认 → 合并或保留
  │     → 统计：去重 {D} 对
  │
  ├── Step 7：归档过期条目
  │     → integration 类：创建 > 7 天且无更新 → 建议归档
  │     → development 类：关联功能已上线 > 2 周 → 建议归档
  │     → quarterly-o 类：季度结束后 → 写复盘 → 归档
  │     → 所有条目：updated > 90 天 → 标记为"需复查"
  │
  └── Step 8：生成维护报告
        → 汇总以上所有统计
        → 输出清理前后对比
        → 建议下一步行动
```

**维护报告模板**：

```markdown
## 📚 知识库维护报告

日期：{date}
维护前条目数：{N} → 维护后：{M}

### 去重合并
- 合并：kb-xxx + kb-yyy → kb-zzz（{原因}）
- 共合并 {X} 组，减少 {Y} 条

### 归档
- 归档：kb-aaa（{原因——已上线/已过时/已被替代}）
- 共归档 {X} 条

### 升级
- 升级为模式：{tag} 下 {N} 条碎片 → `knowledge/patterns/{slug}.md`
- 共升级 {X} 条

### 矛盾解决
- kb-xxx 与 kb-yyy 在 {topic} 上结论相反 → 已标注，待人工裁决

### 待处理
- {N} 条知识标记为"需复查"（>90 天未更新）
- {M} 条知识的 source_files 引用已失效
```

---

## 6. 与其他技能的集成

### 6.1 自动沉淀——各技能完成后的知识写入

知识库是一个**跨切面能力**——所有技能完成后都可以（也应该）将关键产出沉淀到知识库：

| 技能 | 沉淀内容 | 目标位置 | dimension |
|------|---------|---------|-----------|
| read-project | 项目架构理解、模块结构、技术栈 | `code/{module}/structure.md` | analysis |
| read-paper | 论文核心发现、方法对比 | `source/outer/{topic}/` | reference |
| trace-code | 函数调用链、数据流路径、关键分支 | `code/{module}/trace.md` | analysis |
| tech-radar | 技术趋势判断、技术成熟度评估 | `source/outer/tech-radar/` | reference |
| read-requirements | 需求理解、完成定义、追溯矩阵 | `domain/{domain}/{feature}/requirements.md` | analysis |
| code-implement | 变更记录、设计决策、替代方案 | `domain/{domain}/{feature}/implementation.md` | decision |
| code-review | 审查发现、阻断问题、改进建议 | `domain/{domain}/{feature}/review.md` | analysis |
| examine-quality | 测试覆盖矩阵、未覆盖风险 | `domain/{domain}/{feature}/quality.md` | analysis |
| talk-retro | 5-Whys 根因、Trade-offs、工程规范 | `domain/{domain}/{feature}/retro.md` | analysis |
| self-check | CTO 拷打记录、认知缺口 | `conversation/outputs/` | output |
| sum-session | 六要素总结（背景→发现→问题→解决→效果→展望） | `domain/{domain}/{feature}/summary.md` | analysis |
| tech-compare | 决策矩阵、ADR、最终方案及理由 | `decisions/DEC-{nnn}.md` | decision |
| api-test | API 规格、测试用例矩阵、错误码映射 | `domain/integration/{api}/` | analysis |

**自动化规则**：
- L0 风险技能（纯读/纯分析）：自动沉淀，无需用户确认
- L1+ 风险技能（涉及代码改动）：沉淀前展示摘要，用户确认后写入
- 沉淀内容 = 技能原始产出（不是摘要或二次加工），保留完整证据链

### 6.2 检索优先——新任务启动前先查知识库

Agent 在接到新任务时（尤其是 read-project / trace-code / code-implement / code-review），应先执行检索：

```
新任务 → 读 L1 索引 → 
  ├── 有相关条目 → 加载 → 基于已有知识开始工作 → 标注"基于 kb-xxx"
  └── 无相关条目 → 标注"首次分析" → 从头开始 → 完成后沉淀
```

### 6.3 会话交接（Handoff）

每次会话结束或 `/compact` 前，Agent 应自动执行交接记录：

```markdown
---
dimension: reference
domain: {当前任务领域}
source: derived
status: stable
created: {timestamp}
session: {session-id}
---

# 会话交接 — {date}

## 完成
- {完成事项 1}
- {完成事项 2}

## 停在
- {当前进度——下一步该做什么}

## 决定
- {本次会话做出的关键决策}

## 打开
- {未解决的问题/待跟进事项}

## 文件
- {本次会话修改/创建的文件列表}
```

交接记录存储在 `knowledge/sessions/{date}-{session-id}.md`。

---

## 7. 反模式

- ❌ **把所有对话都存入知识库**——大部分对话不值得沉淀。遵循 §5.1 捕获决策矩阵，只沉淀有复用价值的知识
- ❌ **知识条目写成流水账**——"然后我读了 auth.go，它有 200 行，然后我看了 login 函数..." 这不是知识，这是操作日志。知识应该是分析结论，不是过程描述
- ❌ **ETR 三元组为空**——"功能正常，测试通过" 没有 E (哪个测试？什么输出？)、没有 T (为什么通过？)、没有 R (还有什么风险？)。这样的条目 = 水文，直接阻断
- ❌ **L1 索引存内容**——MEMORY.md 和 knowledge/README.md 只存指针（标题+路径+一句话摘要），不存知识内容。内容一定在 L2
- ❌ **Inner 材料被 Agent 修改**——用户提供的材料是原始凭证，Agent 只能读不能改。分析结论另存为 derived 条目
- ❌ **知识条目不标时效性**——代码分析基于当前版本，半年后可能完全失效。必须标注基于哪个 commit、预计什么变更会导致失效
- ❌ **Prompt/Output 不分离**——混在一起无法区分"用户问了什么"和"Agent 答了什么"。必须分开存储，通过 related 互链
- ❌ **季度 O 条目当普通条目处理**——季度 O 需要进度跟踪 + 阶段性总结 + 季度末复盘。不能像普通开发需求一样写一次就不管
- ❌ **知识条目不更新 outdated 标记**——代码已改但知识条目还标着 stable → 误导下一个 Agent。发现过时条目应立即标记 archived + 注明原因
- ❌ **知识库变成代码仓库的镜像**——代码本身在 git 里，不需要在知识库里再存一遍。知识库存的是**对代码的理解和分析**，不是代码本身
- ❌ **不检查重复就新建**——同一个模块被分析两次产生两个条目，后来者不知道该信哪个。写入前必须先检索去重
- ❌ **MCP 可用但不用**——已配置 MCP Server 但 Agent 仍手动 grep _index.md，浪费 token 且搜索结果不准确

---

## 8. MCP 集成

### 8.1 MCP Server 概览

知识库提供了 MCP Server（`skills/knowledge-base/mcp-server/server.py`），将文件系统操作封装为 5 个结构化工具：

| MCP 工具 | 对应的手动操作 | 优势 |
|---------|-------------|------|
| `knowledge_search` | 手动 grep + 读 _index.md | 加权评分排序 + 多维度过滤 |
| `knowledge_context` | 手动提取关键词 + 多次搜索 | 自动关键词提取 + 去重合并 |
| `knowledge_store` | 手动写 Markdown + frontmatter + 更新 _index.md | 自动 ID / frontmatter / 去重 / 双向链接 |
| `knowledge_stats` | 手动数文件 + 统计 | 即时统计 + 过期检测 |
| `knowledge_maintenance` | 手动逐条对比 | 批量去重检测 + 碎片合并建议 |

### 8.2 配置方式

`.mcp.json`（项目根目录）：

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

首次使用前安装依赖：

```bash
pip install -r skills/knowledge-base/mcp-server/requirements.txt
```

### 8.3 使用优先级

Agent 在操作知识库时遵循以下优先级：

```
1. MCP Server 可用？
   ├── YES → 使用 MCP 工具（knowledge_search / knowledge_store / ...）
   │         → 更快、更准、自动索引
   └── NO  → 降级为手动文件操作
             → Agent 直接读写 knowledge/ 目录的 Markdown 文件
             → 手动维护 _index.md
```

### 8.4 MCP 工具速查

**knowledge_context** —— 最重要的工具，新任务启动时首先调用：

```
Tool: knowledge_context
Input:  { "task_description": "分析 src/auth/login.go 的 token 验证逻辑" }
Output: {
          "keywords_extracted": ["auth", "login", "token"],
          "found": 2,
          "context_summary": "- [kb-20260627-001] Token 验证链分析 (development/analysis)\n- [kb-20260626-003] 登录性能优化记录 (development/decision)\n"
        }
```

**knowledge_store** —— 沉淀知识时调用：

```
Tool: knowledge_store
Input:  {
          "domain": "development",
          "source": "derived",
          "dimension": "analysis",
          "title": "src/auth/login.go token 验证链分析",
          "content": "## 背景\n...\n## 核心内容\n...\n## ETR\n...",
          "tags": ["auth", "token", "login"],
          "source_files": ["src/auth/login.go:45-89", "src/auth/token.go:12-34"]
        }
Output: { "status": "stored", "id": "kb-20260627-002", "path": "domain/development/kb-20260627-002.md" }
```

**knowledge_stats** —— 启动时检查知识库健康状态：

```
Tool: knowledge_stats
Input:  {}
Output: {
          "total": 15,
          "by_domain": { "development": 8, "integration": 5, "quarterly-o": 2 },
          "stale_count": 3,
          "stale_entries": [...]
        }
```

**knowledge_maintenance** —— 维护时调用：

```
Tool: knowledge_maintenance
Input:  { "action": "full_report", "dry_run": true }
Output: {
          "stats": {...},
          "duplicates": [...],
          "consolidation_suggestions": [
            { "tag": "payment", "entry_count": 4, "suggestion": "标签 #payment 下有 4 条碎片..." }
          ]
        }
```

详见 `skills/knowledge-base/mcp-server/README.md`。

---

## 9. 版本历史

- v1.2 (2026-06-27)：Hook 级自动化——PostToolUse hook（每次工具调用自动捕获）+ SessionEnd hook（100% 会话结束沉淀）。四层会话存储（raw→prompts/outputs→sessions→patterns）。"全部沉淀→定时巡检清理→总结归纳汇总"策略。定时巡检 8 步维护流程。
- v1.1 (2026-06-27)：新增 MCP 集成——MCP Server（5 个工具）、自动索引与检索、去重检测、健康报告。编排中枢 §2 强化为 Pre-Step + Post-Step 十步知识管线。CLAUDE.md 新增 6 条自动触发规则。
- v1.0 (2026-06-27)：初始版本——三层渐进披露架构、三维领域模型（联调/开发/季度O）、来源维度（inner/outer/derived）、会话维度（prompt/output）、五阶段操作流程（捕获/检索/存储/维护/交接）、ETR 证据链标准、14 条反模式
