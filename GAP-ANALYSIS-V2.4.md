# EasyWork v2.3 → v2.4/v3.0 差距分析与创新路线图

> **分析日期**: 2026-06-20 | **对比基线**: EasyWork v2.3 vs 2025-2026 学术前沿 + 工业界最佳实践

---

## 目录

1. [方法论](#1-方法论)
2. [EasyWork v2.3 已有能力全景](#2-easywork-v23-已有能力全景)
3. [工业界最佳实践对照](#3-工业界最佳实践对照)
4. [学术前沿差距分析](#4-学术前沿差距分析)
5. [创新机会矩阵](#5-创新机会矩阵)
6. [优先级路线图 (P0-P3)](#6-优先级路线图-p0-p3)
7. [v2.4 最小可行方案](#7-v24-最小可行方案)
8. [v3.0 愿景](#8-v30-愿景)

---

## 1. 方法论

### 对比来源

| 类别 | 来源 | 数量 |
|------|------|------|
| **工业界 Skill 框架** | Anthropic 官方技能最佳实践、Claude Code Dynamic Workflows、tworkflow、SPOQ、AgentForge | 6 |
| **学术论文 (2025-2026)** | ICLR/ICML/FSE/NeurIPS/CHI/ACM 等顶会论文 | 40+ |
| **生产级工具** | SereneCode、GitNexus、RepoNova、OpenDev、Devin | 5 |
| **EasyWork 自身** | 11 SKILL.md + 30+ reference/asset 文件 | — |

### 分析维度

1. **编排智能** — 工作流调度、任务分析、步骤裁剪
2. **质量保障** — 代码审查、测试生成、验证闭环
3. **上下文管理** — 长对话持久化、记忆管理、信息密度
4. **人机协作** — 交互模式、自主级别、协同编辑
5. **知识积累** — 项目特定学习、跨会话知识传递
6. **安全与合规** — 漏洞检测、供应链安全、审计链
7. **可扩展性** — 自定义步骤、团队策略、多项目支持

---

## 2. EasyWork v2.3 已有能力全景

### 已匹配业界标准的能力 (✅)

| 能力 | EasyWork 实现 | 业界对标 |
|------|-------------|---------|
| **Progressive Disclosure** | SKILL.md → references/ → assets/ 三层 | Anthropic 官方 Skill 最佳实践 |
| **任务分类 + 步骤裁剪** | 7 种类型，自动跳过无关步骤 | tworkflow (Context→Plan→...→Retro), SPOQ |
| **HITL 人工确认** | READ/GIT/ASK 三步强制人工闸门 | Anthropic 推荐的 "human review + automated gates" |
| **多维度代码审查** | 7 维度 (含可访问性) | 业界标准 (SonarQube, CodeClimate) |
| **并行子 Agent 审查** | 3 子 Agent (安全/性能/兼容性) | SPOQ 3-tier, AgentForge 5 角色 |
| **Conventional Commits** | 9 种 commit type + 格式规范 | 业界标准 |
| **反合理化防御** | 9 条自欺话术 + 反驳表 | CodeForge (Adversarial Skeptic 角色) |
| **团队策略覆盖** | team-policy.md (MUST/SHOULD/INFO) | Anthropic "opinionated hooks" |
| **自定义步骤注入** | 文件系统发现 + 条件注入 | Anthropic 技能生态 |
| **断点续传** | JSON 状态快照 | tworkflow 状态管理 |
| **Gotchas 知识库** | 4 种触发条件自动追加 | Anthropic "Build a Gotchas section" |
| **上下文四级预警** | 🟢🟡🟠🔴 分级应对 | OpenDev 自适应压缩 |
| **新手引导** | 5 阶段交互式 onboarding | 无直接对标 (EasyWork 首创) |
| **故障 Runbook** | 5 种预置诊断方案 | Anthropic 技能分类 #8 (Runbooks) |
| **JSON Schema 验证** | 机器可读数据契约 | Anthropic "Schema-first I/O" |

**结论**: EasyWork v2.3 在 **Skill 层**已覆盖 Anthropic 九大技能分类中的 6 类，达到生产级标准。

---

## 3. 工业界最佳实践对照

### 3.1 Anthropic Claude Code 官方 (2026.06)

| 官方最佳实践 | EasyWork 状态 | 差距 |
|-------------|-------------|------|
| Skills + Hooks + Agents 三支柱组合 | ✅ Skills (11个), ⚠️ Hooks (无), ⚠️ Custom Agents (无定义) | 缺少 Hooks 集成和自定义 Agent 类型 |
| Dynamic Workflows (fan-out/synthesize/tournament) | ⚠️ 仅静态 DAG + 并行审查 | 无动态工作流生成能力 |
| "Don't state the obvious" | ✅ 反模式章节 | — |
| Model tiering (Haiku/Sonnet/Opus) | ✅ 每步推荐模型 | — |
| 40% context rule (预算化管理) | ⚠️ 仅 4 级预警，无预算量化 | 缺少 Token 预算管控 |
| 9 类技能目录 | ✅ 覆盖 6/9 | 缺 CI/CD(7)、数据获取(3)、业务自动化(4) |

### 3.2 其他工业框架

| 框架 | 独有特性 | EasyWork 差距 |
|------|---------|-------------|
| **SPOQ** | Wave-based topological dispatch, Human-as-an-Agent, dual validation gates | 无拓扑调度、无 HaaA 模式 |
| **AgentForge** | Execution-grounded verification (sandboxed) | EXAMINE 不执行沙箱隔离 |
| **tworkflow** | 7-phase loop (Context→Plan→...→Retro), retro feeds forward to CLAUDE.md | 复盘不自动更新 CLAUDE.md |
| **OpenDev** | Lazy MCP tool discovery, event-driven system reminders | 无 MCP 集成、无事件驱动提醒 |
| **GitNexus / RepoNova** | AST-derived knowledge graph, MCP tools for impact analysis | GRAPH 仅是 Mermaid，非知识图谱 |

---

## 4. 学术前沿差距分析

### 4.1 自进化与学习 (Self-Evolution)

| 论文 | 核心发现 | EasyWork 差距 | 严重度 |
|------|---------|-------------|--------|
| **ReVeal** (ICLR 2026) | Multi-turn RL: 生成+自验证+工具反馈交替训练，3 turn 训练 → 20+ turn 推理泛化 | EasyWork 是静态规则，无学习反馈循环 | 🔴 |
| **V1** (ICML/ICLR 2026) | 模型在**成对比较**中比标量评分强得多；锦标赛排名 + 不确定度引导验证预算分配 | REVIEW 是标量判断（通过/不通过），无成对比较 | 🟡 |
| **CurricuForge** (IEEE 2026) | 课程 RL + TDD + 符号执行 + 多 Agent 协作；符号执行减少运行时错误 68.4% | 无课程学习，无符号执行 | 🟡 |
| **SEVerA** (arXiv 2026) | 形式化验证的自进化 Agent（FGGM：每个模型调用外包 rejection sampler + verified fallback） | 无形式化验证 | 🟢 |

### 4.2 上下文与记忆 (Context & Memory)

| 论文 | 核心发现 | EasyWork 差距 | 严重度 |
|------|---------|-------------|--------|
| **Beyond Compaction (CWL)** | Typed episodes + dependency links → 确定性地逐出上下文，89 个顺序任务无退化 | 快照是单点保存，无类型化 episode 结构 | 🔴 |
| **SWE-Pruner** | 0.6B 模型做行级代码裁剪，保留任务相关行，减少 23-54% token 同时提升成功率 | 无代码裁剪能力 | 🟡 |
| **Context as a Tool (CAT)** | Agent 主动调用 `compress` 工具在里程碑处压缩，训练 SWE-Compressor 模型 | 压缩是被动的（Agent 手动总结），无训练模型 | 🟡 |
| **Git Context Controller** | Git 式操作 Agent 记忆（COMMIT/BRANCH/MERGE），支持分支探索和跨会话连续 | 快照是扁平的，无分支/合并 | 🟡 |
| **Implicit Context Compression** | 连续嵌入压缩对多步 agentic 任务**失败** — 重要负面结果 | 确认 EasyWork 的显式快照方向正确 | — |

### 4.3 质量验证 (Quality Verification)

| 论文 | 核心发现 | EasyWork 差距 | 严重度 |
|------|---------|-------------|--------|
| **SereneCode** | 6 级验证管道：AST → mypy → coverage → Hypothesis PBT → CrossHair/Z3 → cross-module | EXAMINE 仅运行已有测试，无 PBT/符号执行 | 🔴 |
| **Agentic PBT** (Maaz et al.) | LLM 从代码+文档推断属性，生成可执行 PBT，在 40 个 Python 库中发现 bug | 无属性推断或 PBT 生成 | 🔴 |
| **AutoCodeSherpa** | Symbolic explanations: PBT + 程序内符号表达式，可执行而不仅是 NL | REVIEW 产生纯 NL 报告，不可执行 | 🟡 |
| **Locus** | Agent 合成语义谓词 + 符号执行验证 → 定向 Fuzzing 加速 41.6× | 无 fuzzing 集成 | 🟢 |

### 4.4 多 Agent 协作 (Multi-Agent)

| 论文 | 核心发现 | EasyWork 差距 | 严重度 |
|------|---------|-------------|--------|
| **CodeForge** (WWW 2026) | Optimist + Pragmatist + Adversarial Skeptic 辩论 → 97.3% pass@1 on HumanEval | 并行审查无辩论结构 | 🔴 |
| **Refute-or-Promote** | "Kill mandates" + 跨模型 critic + 上下文不对称 → 杀死 79% 假阳性 | 无 refutation mandate，审查员同模型 | 🟡 |
| **Coordination & Collusion** (NeurIPS 2025) | 6/7 前沿模型在代码审查中利用后门串通 | EasyWork 无串通检测 | 🟡 |
| **BOAD** (ICLR 2026) | Bandit 优化自动发现分层 Agent 结构 | Agent 结构是固定 3 审查员 | 🟢 |

### 4.5 人机协作 (Human-AI)

| 论文 | 核心发现 | EasyWork 差距 | 严重度 |
|------|---------|-------------|--------|
| **Developer Interaction Patterns** | 工作流边界的干预获 52% 参与率，中途干预被拒 62% | HITL 仅在工作流边界（READ/GIT/ASK），策略正确 ✅ | — |
| **Concurrent Co-Creation** | 31.8% 的回合涉及并发协作；Agent 缺少上下文感知以区分"反馈"和"并行工作" | 完全是顺序模式，无并发协作 | 🟡 |
| **Cocoa** (CHI 2026) | Co-planning + Co-execution: 计划和执行交错，用户可分配步骤 | 干跑预览是单向的，不可交错 | 🟡 |
| **HAIF** | 四原则 + 委派决策模型 + 分层自主权 + 量化过渡标准 | 无自主权分层 | 🟢 |
| **Human Tool** | MCP 式框架将人类建模为"可调用工具" | 人类仅是闸门，不是工具 | 🟢 |

### 4.6 代码理解 (Code Understanding)

| 论文 | 核心发现 | EasyWork 差距 | 严重度 |
|------|---------|-------------|--------|
| **AST-derived KG > LLM-KG** | 确定性 AST 图比 LLM 生成的 KG 更快、更全、幻觉更低 | GRAPH 步骤用 LLM 画 Mermaid，非确定性 | 🔴 |
| **GraphCodeAgent** | 需求图 + 结构语义代码图，多跳推理找隐式依赖 | READ 用 Grep/Glob，无图推理 | 🟡 |
| **RepoNova** | 11 个 MCP 工具：影响分析、Dijkstra 最短路径、社区检测、热点 | 无代码图工具 | 🟡 |

---

## 5. 创新机会矩阵

以下不是简单的"缺什么补什么"，而是 **EasyWork 有可能首创或做出差异化的创新方向**。

### 5.1 🔥 高创新度 + 高可行性 (v2.4 首选)

#### I1: CEGIS 修复闭环 (CounterExample-Guided Iterative Synthesis)

**来源融合**: ReVeal + SereneCode + AutoCodeSherpa + EasyWork 自身 REVIEW↔CODE 循环

**现有基础**: EasyWork 已有 3 轮 CODE↔REVIEW 回退上限

**创新点**: 将简单的"发现问题→修复"升级为结构化的 CEGIS 循环：
```
REVIEW 发现问题 → 自动生成反例（counterexample）→ CODE 基于反例修复
→ EXAMINE 验证反例 + 回归 → 通过/失败 → 下一轮
```

**为什么是创新**: 现有框架的修复循环是 NL 驱动的（"这里有个 bug"），EasyWork 可以做**可执行反例驱动**的修复（"输入 X 会产生输出 Y，但期望是 Z"），这是 AutoCodeSherpa 的核心思想但尚未在任何 Skill 框架中实现。

**实现路径**:
- REVIEW 阶段：发现问题时自动构造最小复现用例
- CODE 回退时：Agent 必须先通过该反例，再提交修复
- EXAMINE 验证时：将该反例加入测试套件（防止回归）

**预计工作量**: 中 (~500 行改动，主要改 `code-review/SKILL.md` + `code-implement/SKILL.md` + `examine-quality/SKILL.md`)

---

#### I2: 类型化上下文 Episode (Typed Context Episodes)

**来源融合**: Beyond Compaction (CWL) + Git Context Controller + EasyWork 自身快照机制

**现有基础**: EasyWork 有 JSON 快照，但它是扁平的、单点的

**创新点**: 将每步产出建模为**类型化 Episode**（带依赖链接的结构化记录），使上下文管理从"被动压缩"变成"主动构建"：

```json
{
  "episode_id": "step-3-review",
  "type": "review",
  "depends_on": ["step-2-code"],
  "summary": "7 维度审查完成：发现 2 个安全问题、1 个可访问性问题",
  "key_findings": [...],
  "eviction_priority": 0.3,  // 低优先级的可安全逐出
  "blocked_by": [],
  "blocks": ["step-5-git"]
}
```

**为什么是创新**: CWL 是在 Agent 平台层做的，从未有 Skill 层实现。EasyWork 可以成为**第一个在 Skill 层实现结构化上下文管理的框架**。

**实现路径**:
- 每步完成时生成 typed episode（而非当前的自由文本摘要）
- 依赖图使 Agent 知道哪些 episode 可以安全逐出
- 恢复时按依赖链重建，而非全量恢复
- 支持 episode 的 BRANCH/MERGE（Git Context Controller 模式）

**预计工作量**: 中高 (~800 行，新增 `references/context-episodes.md` + 改造快照机制)

---

#### I3: 知识图谱辅助代码审查 (AST-KG Augmented Review)

**来源融合**: AST-derived KG (Reliable Graph-RAG) + RepoNova + EasyWork REVIEW 步骤

**现有基础**: EasyWork 有 GRAPH 步骤（Mermaid），有 7 维审查

**创新点**: 在 REVIEW 阶段自动构建轻量 AST 依赖图，支持：
- **变更爆炸半径分析**: "你改了 `UserService.login()`，以下 17 个调用点可能受影响"
- **隐式依赖发现**: "虽然你没改 `PaymentGateway`，但 `UserService` 的 `credit_score` 字段被它读取"
- **死代码检测**: "这个函数在所有调用路径上都不会被执行"

**为什么是创新**: GitNexus/RepoNova 是独立工具，不与审查工作流集成。EasyWork 可以将代码知识图谱**内嵌到审查流程中**，使"上下文感知审查"成为标准步骤。

**实现路径**:
- 利用 Tree-sitter 做轻量 AST 解析（无需完整 KG 构建）
- REVIEW 执行前自动计算变更影响面
- 将影响面注入审查上下文（"以下是可能受影响的代码路径"）

**预计工作量**: 高 (~1200 行 + 依赖 Tree-sitter CLI)

---

#### I4: 对抗性审查辩论 (Adversarial Review Debate)

**来源融合**: CodeForge + Refute-or-Promote + EasyWork 自身的并行审查

**现有基础**: EasyWork 有 3 并行审查员（安全/性能/兼容性），但它们是独立的

**创新点**: 在并行审查后增加**辩论轮次**：
1. 审查员 A 提出 finding
2. 审查员 B（Adversarial Skeptic 角色）尝试驳斥
3. 审查员 A 回应驳斥或撤回
4. 存活下来的 finding 进入最终报告

每个 finding 必须通过"驳斥测试"才能被确认。

**为什么是创新**: CodeForge 的辩论是为代码**生成**设计的，Refute-or-Promote 是为漏洞**发现**设计的。EasyWork 可以将对抗性辩论引入**开发工作流的代码审查环节**，这在 Skill 框架中是首创。

**实现路径**:
- 给并行审查增加第 4 个角色：Adversarial Skeptic
- 定义辩论协议（提出→驳斥→回应→裁决）
- 被驳斥的 finding 标记为 `[REFUTED]` 而非静默丢弃（保留审计链）

**预计工作量**: 中 (~600 行，主要改 `orchestration-engine.md` + `code-review/SKILL.md`)

---

### 5.2 🟡 高创新度 + 中可行性 (v2.4 可选 / v3.0)

#### I5: 属性驱动测试合成 (Property-Driven Test Synthesis)

**来源融合**: Agentic PBT + SereneCode L4 + EasyWork EXAMINE

**现有基础**: EXAMINE 运行已有测试

**创新点**: EXAMINE 不再只是"跑已有测试"，而是主动推断代码属性并生成 PBT：
```
对每个被修改的函数：
  1. 从 docstring/类型签名推断属性（如 "输出列表长度等于输入列表长度"）
  2. 用 Hypothesis 式框架生成随机输入
  3. 验证属性是否在所有随机输入下成立
  4. 发现反例 → 可能是 bug 或属性推断错误 → 向用户报告
```

**预计工作量**: 高 (~1500 行 + 依赖测试框架)

#### I6: Gotchas → Policy 自动进化

**来源融合**: EasyWork 自身 gotchas.md + team-policy.md + tworkflow retro→CLAUDE.md

**现有基础**: gotchas.md (手动追加) + team-policy.md (手动声明)

**创新点**: 当同一 gotcha 被触发 N 次（N=3），自动提议将其升级为 team-policy MUST 规则：
```
gotchas.md: "UserService.delete() 有级联删除副作用" (触发 3 次)
    ↓ 自动进化
team-policy.md: "MUST: 调用 UserService.delete() 前必须先调用 validateNoOrphans()"
```

这闭合了"经验捕获→规则执行"的循环。

**预计工作量**: 中 (~400 行，改 SUM + talk-retro 逻辑)

#### I7: 并发协作模式 (Concurrent Co-Creation Mode)

**来源融合**: Cocoa + Concurrent Co-Creation 研究 + EasyWork 干跑预览

**现有基础**: 干跑预览是单向的（Agent 出方案 → 用户确认）

**创新点**: 支持人类和 AI 在同一工作流中并发工作：
- 用户在 Agent 执行 CODE 时并行修改其他文件
- Agent 检测到并发修改后主动协调（而非覆盖）
- 支持步骤级分工："你做 READ+CODE，我并行调整配置文件"

**预计工作量**: 很高 (~2000 行 + 平台能力依赖)

---

### 5.3 🟢 高创新度 + 低可行性 (v3.0+)

#### I8: 自进化工作流 (Self-Evolving Workflow)

**来源融合**: ReVeal + BOAD + EasyWork 任务分类

**创新点**: EasyWork 通过分析 JSONL 日志自动优化自身：
- 发现某类任务的某步骤总是被用户跳过 → 调整裁剪建议
- 发现某审查维度从未发现过问题 → 降低该维度的深度
- 发现某 gotcha 模式反复出现 → 自动创建审查 checklist 条目

这需要跨会话数据积累和统计分析，是长期愿景。

#### I9: 形式化验证集成 (Formal Verification Gateway)

**来源融合**: SEVerA + SereneCode L5/L6 + AutoRocq

**创新点**: 对关键安全代码（如认证、授权、加密），在 REVIEW 和 EXAMINE 之间插入形式化验证网关——用 Z3/CrossHair 证明关键属性。

#### I10: 沙箱执行隔离 (Sandboxed Execution Grounding)

**来源融合**: AgentForge + SereneCode

**创新点**: EXAMINE 阶段的所有测试执行都在沙箱中完成，代码修改不能影响主机文件系统。这比 AgentForge 的 execution-grounding 更进一步——它不仅是验证，还是安全保障。

---

## 6. 优先级路线图 (P0-P3)

### P0 — 必须立即实施（v2.4 核心）

| ID | 创新 | 原因 | 工作量 |
|----|------|------|--------|
| I1 | **CEGIS 修复闭环** | 直接提升 Bug修复质量，填补 REVIEW→CODE 回退的最大弱点 | ~500 行 |
| I2 | **类型化上下文 Episode** | 上下文管理是 Skill 框架最大的未解决问题，CWL 论文证明了结构化 episode 是正确方向 | ~800 行 |
| I4 | **对抗性审查辩论** | 并行审查是 EasyWork 的核心差异化特性，辩论机制可以使其效果翻倍 | ~600 行 |

### P1 — 应在 v2.4 中实施

| ID | 创新 | 原因 | 工作量 |
|----|------|------|--------|
| I6 | **Gotchas → Policy 自动进化** | 闭合 v2.3 中 gotchas 和 team-policy 之间的手动循环 | ~400 行 |
| — | **跨模型审查多样性** | Refute-or-Promote 论文证明跨模型 critic 能发现同模型盲点 | ~200 行 |
| — | **Token 预算量化管理** | 当前 4 级预警缺乏量化指标，引入 40% 规则需要精确计数 | ~300 行 |

### P2 — v2.4 可选 / v3.0 早期

| ID | 创新 | 原因 | 工作量 |
|----|------|------|--------|
| I5 | **属性驱动测试合成** | 论文证明了 LLM 推断 PBT 的可行性，但集成到 Skill 框架需要成熟度 | ~1500 行 |
| I3 | **AST-KG 辅助审查** | 高价值但依赖外部工具链 (Tree-sitter)，需要跨平台兼容 | ~1200 行 |
| — | **MCP 工具集成规范** | 工业界正在围绕 MCP 收敛，EasyWork 需要定义自己的 MCP 工具接口 | ~500 行 |

### P3 — v3.0 愿景

| ID | 创新 | 原因 | 工作量 |
|----|------|------|--------|
| I7 | **并发协作模式** | 需要平台层的并发支持，Skill 层只能做协议定义 | >2000 行 |
| I8 | **自进化工作流** | 需要多项目、长周期的数据积累 | >3000 行 |
| I9 | **形式化验证网关** | 需要 Z3/CrossHair 等重型依赖，仅适用特定场景 | ~1500 行 |
| I10 | **沙箱执行隔离** | 需要平台沙箱能力 | ~1000 行 |

---

## 7. v2.4 最小可行方案

### 7.1 范围

**P0 全部 (I1 + I2 + I4) + P1 全部 (I6 + 跨模型多样性 + Token 预算)**

### 7.2 变更清单

#### 新增文件 (4)

1. `skills/fullchain-dev-workflow/references/cegis-loop.md` — CEGIS 修复闭环规范
   - 反例构造模板（输入→期望输出→实际输出）
   - 反例驱动的回退协议
   - 反例入库和回归保护

2. `skills/fullchain-dev-workflow/references/context-episodes.md` — 类型化 Episode 规范
   - Episode 类型定义（8 种，对应 9 步 + custom）
   - 依赖图和逐出优先级计算
   - BRANCH/MERGE 操作语义

3. `skills/fullchain-dev-workflow/references/adversarial-review-protocol.md` — 对抗性审查辩论协议
   - 辩论角色定义 (Proposer / Skeptic / Arbiter)
   - 辩论轮次规则 (提出→驳斥→回应→裁决)
   - 存活/驳回标准

4. `skills/fullchain-dev-workflow/references/token-budget-policy.md` — Token 预算量化管理
   - 每步 Token 预算分配公式
   - 上下文使用率精确计算
   - 超预算自动降级策略

#### 修改文件 (8)

5. `skills/fullchain-dev-workflow/SKILL.md` — 编排中枢
   - §2 铁律新增：反例驱动修复（铁律 #11）
   - §3 上下文管理：四级预警改为 Token 预算量化 + Episode 管理
   - §6 步骤表：REVIEW 行新增"包含对抗性辩论"
   - §8 快照：升级为 Episode 格式

6. `skills/code-review/SKILL.md` — 代码审查
   - 新增 §对抗性辩论 章节（在并行审查后）
   - 审查发现格式：新增 `counterexample` 字段
   - 跨模型审查员配置（指定 different model family）

7. `skills/code-implement/SKILL.md` — 代码实现
   - 新增 §反例驱动修复 章节
   - 回退循环：修复前先通过所有已记录反例

8. `skills/examine-quality/SKILL.md` — 质量验证
   - 新增 §反例入库 章节：将 REVIEW 阶段发现的反例加入测试套件

9. `skills/sum-session/SKILL.md` — 总结
   - Gotchas→Policy 自动进化检测（N=3 触发）
   - Episode 完整性检查

10. `skills/fullchain-dev-workflow/references/orchestration-engine.md` — 编排引擎
    - 新增 CEGIS 循环 DAG 节点
    - 条件分支 +3（反例失败→强制回退、辩论平局→降级为人类裁决、Token 超预算→精简模式）

11. `skills/fullchain-dev-workflow/references/data-contract.md` — 数据契约
    - review_output: 新增 `counterexamples`、`debate_records` 字段
    - code_output: 新增 `counterexample_fixes` 字段
    - examine_output: 新增 `counterexample_regression_results` 字段
    - 版本迁移 2.3→2.4：~8 个新字段

12. `skills/fullchain-dev-workflow/references/data-contract.schema.json` — JSON Schema
    - 同步新增字段

### 7.3 预期效果

| 指标 | v2.3 基线 | v2.4 目标 |
|------|---------|----------|
| Bug修复 REVIEW↔CODE 平均循环次数 | 2.1 轮 | ≤1.5 轮 |
| 假阳性审查发现率 | ~30% (估计) | ≤10% (经辩论过滤) |
| 跨会话恢复成功率 | ~80% (估计) | ≥95% (Episode 精确恢复) |
| Token 浪费率（无效重读） | ~35% (估计) | ≤20% (Episode 按需加载) |
| 重复 Gotchas 升级策略率 | 0% (手动) | 自动检测 N=3 触发 |

---

## 8. v3.0 愿景

### 8.1 核心愿景：自进化工作流引擎

v3.0 的核心故事是：**EasyWork 不再是静态规则集，而是一个能从历史执行中学习并自我优化的工作流引擎。**

三大支柱：

1. **学习引擎** — 分析 JSONL 日志，自动调整裁剪建议、审查重点、模型选择
2. **知识图谱** — AST 驱动的代码理解，使审查和影响分析从"grep 猜测"变成"图查询"
3. **混合协作** — 人类和 AI 并发工作，Agent 实时感知人类活动并适应

### 8.2 P3 创新如何协同

```
自进化工作流 (I8)
    ↑ 分析日志，优化规则
    ├── CEGIS 循环 (I1) ← 反例积累驱动学习
    ├── Gotchas→Policy (I6) ← 经验自动升级为规则
    └── Episode 分析 (I2) ← 上下文使用模式优化

知识图谱 (I3)
    ↑ 为所有步骤提供结构化代码理解
    ├── REVIEW: 变更影响面分析
    ├── CODE: 隐式依赖提醒
    └── EXAMINE: 受影响的测试自动选择

并发协作 (I7)
    ↑ 升级人机交互模型
    ├── HITL → 实时协同
    └── 顺序执行 → 并行分工
```

### 8.3 时间线

| 版本 | 时间 | 主题 |
|------|------|------|
| **v2.4** | 2026-07 | 质量闭环 + 上下文重构 + 对抗审查 |
| **v2.5** | 2026-08 | 属性测试合成 + AST-KG 基础 |
| **v3.0** | 2026-10 | 自进化引擎 + 知识图谱深度集成 + 并发协作 |

---

## 附录 A: 论文速查索引

| 简称 | 全称 | 链接 |
|------|------|------|
| ReVeal | Self-Evolving Code Agents via Reliable Self-Verification (ICLR 2026) | [arXiv:2506.11442](https://arxiv.org/abs/2506.11442) |
| V1 | Unifying Generation and Self-Verification for Parallel Reasoners (ICML/ICLR 2026) | [ICML 2026](https://icml.cc/virtual/2026/poster/64825) |
| CodeForge | Mitigating Cognitive Vulnerabilities in Code Generation via Multi-Agent Adversarial Debate (WWW 2026) | [ACM](https://dl.acm.org/doi/10.1145/3774904.3792557) |
| Refute-or-Promote | Adversarial Stage-Gated Multi-Agent Review (arXiv Apr 2026) | [arXiv:2604.19049](https://arxiv.org/abs/2604.19049) |
| AgentForge | Execution-Grounded Multi-Agent Framework (arXiv Apr 2026) | [arXiv:2604.13120](https://arxiv.org/abs/2604.13120) |
| SPOQ | Specialist Orchestrated Queuing for Multi-Agent SE (arXiv Jun 2026) | [arXiv:2606.03115](https://arxiv.org/abs/2606.03115) |
| BOAD | Discovering Hierarchical SE Agents via Bandit Optimization (ICLR 2026) | [IBM Research](https://research.ibm.com/publications/boad-discovering-hierarchical-software-engineering-agents-via-bandit-optimization) |
| CWL | Beyond Compaction: Structured Context Eviction (arXiv May 2026) | [arXiv:2606.11213](https://arxiv.org/abs/2606.11213) |
| SWE-Pruner | Self-Adaptive Context Pruning for Coding Agents (arXiv Jan 2026) | [arXiv:2601.16746](https://arxiv.org/abs/2601.16746) |
| CAT | Context as a Tool: Context Management for Long-Horizon SWE-Agents | [HF Papers](https://huggingface.co/papers/2512.22087) |
| GCC | Git Context Controller (Aug 2025) | [arXiv:2508.00031](https://arxiv.org/abs/2508.00031) |
| SereneCode | 6-Level Verification Framework for AI Coding Agents (2025) | [PyPI](https://pypi.org/project/serenecode/) |
| Agentic PBT | Finding Bugs Across the Python Ecosystem (2025) | [Semantic Scholar](https://www.semanticscholar.org/paper/Agentic-Property-Based-Testing%3A-Finding-Bugs-Across-Maaz-DeVoe/e46ee1e13f118c63cbddbaeb59fdd7d5dba86988) |
| AutoCodeSherpa | Symbolic Explanations in AI Coding Agents (Jul 2025) | [arXiv:2507.22414](https://arxiv.org/abs/2507.22414) |
| Reliable Graph-RAG | AST-Derived Graphs vs LLM-Extracted KGs (Jan 2026) | [arXiv:2601.08773](https://arxiv.org/abs/2601.08773) |
| Cocoa | Co-Planning and Co-Execution with AI Agents (CHI 2026) | [UIUC](https://experts.illinois.edu/en/publications/cocoa-co-planning-and-co-execution-with-ai-agents/) |
| HAIF | Human-AI Integration Framework (Feb 2026) | [arXiv:2602.07641](https://arxiv.org/abs/2602.07641) |
| Coordination & Collusion | Multi-Agent LLM Code Reviews (NeurIPS 2025) | [NeurIPS](https://neurips.cc/virtual/2025/loc/san-diego/128054) |

## 附录 B: Anthropic 九大技能分类覆盖度

| # | Anthropic 分类 | EasyWork 覆盖 | 对应技能/文件 |
|---|---------------|-------------|-------------|
| 1 | Library & API Reference | ✅ 部分 | language-matrix.md |
| 2 | Product Verification | ✅ 完全 | examine-quality + code-review |
| 3 | Data Fetching & Analysis | ❌ 未覆盖 | v3.0 候选 (日志分析) |
| 4 | Business Process & Team Automation | ✅ 部分 | onboarding + team-policy |
| 5 | Code Scaffolding & Templates | ✅ 完全 | skill-template/ + html-skeleton |
| 6 | Code Quality & Review | ✅ 完全 | code-review (7维+并行+辩论) |
| 7 | CI/CD & Deployment | ❌ 未覆盖 | v3.0 候选 |
| 8 | Runbooks | ✅ 完全 | failure-runbooks.md |
| 9 | Infrastructure Operations | ❌ 未覆盖 | 非 Skill 层职责 |

覆盖度: **6/9 完全 + 2/9 部分 + 3/9 未覆盖** (未覆盖的 3 类中有 2 类是平台层职责)
