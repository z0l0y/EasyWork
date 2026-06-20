---
name: fullchain-skill-index
description: >
  EasyWork 全链路 AI 辅助开发工作流技能包索引。9 步流程按需裁剪：
  READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → TALK → ASK。
  入口技能：fullchain-dev-workflow（含任务分类器，自动判断需要哪些步骤）。
  v2.5: 可插拔产物后端（local_html/markdown/lark_doc）、飞书原生文档沉淀、
  Git链路追踪（任务→提交→Check→hash→测试→飞书）、文档写作规范、
  Git提交粒度增强（业务上下文+开发者Check+风险验证）。
  v2.4: Git安全管控、敏感信息脱敏、自定义步骤预确认、供应链外部搜索防护、
  Gotchas候选-确认制、文件系统写保护。
  v2.3: 并行审查、反合理化防御、Gotchas知识库、团队策略覆盖、自定义步骤注入、
  可访问性审查、供应链检查、Conventional Commits、交互式入门、故障Runbook。
version: 2.5
model: sonnet
---

# EasyWork 技能包索引

## 工作流：9 步 → 按需裁剪

不是所有任务都需要 9 步。`fullchain-dev-workflow` 编排中枢内置了**任务分类器**，
会根据任务类型（纯理解/纯文档/微调/Bug修复/重构/功能开发）自动建议要执行和跳过的步骤。

| 序号 | 技能 | 路径 | 一句话职责 |
|------|------|------|-----------|
| 0 | **编排中枢** | `skills/fullchain-dev-workflow/SKILL.md` | 任务分类 + 步骤裁剪 + 流程编排 |
| 1 | READ | `skills/read-requirements/SKILL.md` | 多态输入理解（文档/图片/日志/代码/口语） |
| 2 | CODE | `skills/code-implement/SKILL.md` | 克制编码（注释可配置/复用模式/反炫技） |
| 3 | REVIEW | `skills/code-review/SKILL.md` | 七维度自审查（含反合理化防御、供应链检查） |
| 4 | EXAMINE | `skills/examine-quality/SKILL.md` | 找测试→跑→补→修→重跑至全绿 |
| 5 | GIT | `skills/git-split-commit/SKILL.md` | 按维度拆分提交 + Git链路追踪（Conventional Commits + 业务上下文 + Check清单） |
| 6 | GRAPH | `skills/graph-fullchain/SKILL.md` | Mermaid/飞书 流程图/架构图/时序图（支持飞书画板） |
| 7 | SUM | `skills/sum-session/SKILL.md` | 六要素总结 + 调用产物后端写入最终报告（背景→发现→问题→解决→效果→展望） |
| 8 | TALK | `skills/talk-retro/SKILL.md` | 5-Whys 根因 + Trade-offs + 工程规范 |
| 9 | ASK | `skills/ask-change-questions/SKILL.md` | 六维度人工确认（HITL 终极闸门） |

## 目录结构

每个技能目录采用三层渐进式披露设计：

```
skills/<skill-name>/
├── SKILL.md          # 核心行为指令（自包含，Agent 只读此文件即可执行）
├── assets/           # 输出模板（标准化产出格式）
└── references/       # 深度参考（细节规则，Agent 按需查阅）
```

编排中枢额外包含：
- `assets/walkthrough-example.md` — 3 个端到端完整示例（Bug修复 + 纯理解 + 功能开发）
- `assets/html-skeleton.html` — HTML 报告骨架（Agent 直接复制填充，无需从零生成）
- `assets/onboarding.md` — 🆕 交互式新手引导（5 阶段对话脚本）
- `references/data-contract.md` — 步骤间数据传递契约（含版本迁移规则）
- `references/data-contract.schema.json` — 🆕 JSON Schema 机器可读验证
- `references/language-matrix.md` — 语言/技术栈适配速查（Node/Python/Go/Java/Rust）
- `references/maturity-levels.md` — 渐进式成熟度配置（L1/L2/L3）
- `references/orchestration-engine.md` — 编排引擎详细机制（DAG、并行审查、条件分支、自定义步骤、自检、日志）
- `references/log-analysis-guide.md` — JSONL 日志分析指南
- `references/gotchas.md` — 🆕 项目踩坑知识库（Agent 自动追加 + 执行前扫描）
- `references/self-test-prompts.md` — 🆕 Skill 自测提示词集（10 个测试场景）
- `references/team-policy.md` — 🆕 团队策略覆盖（强制/建议/提示规则 + 注释语言配置）
- `references/failure-runbooks.md` — 🆕 故障模式诊断与预置方案（5 种重复故障）
- `skill-template/`（根目录）— 🆕 增强技能创建模板（含 Gotchas/反合理化/测试提示词/Before-After）

## 使用入口

- **全链路（推荐）**：触发 `fullchain-dev-workflow`，编排中枢会先分类任务，再按裁剪后的流程执行
- **单步**：直接触发对应技能，如只需要审查代码 → `/code-review`
- **半链路**：用户指定从哪里开始，如"代码已写好，从 REVIEW 往后走"
- **🆕 新手入门**：说"带我入门"触发交互式引导（`assets/onboarding.md`）

## 维护原则

- **渐进式披露**：SKILL.md 自包含可执行指令，references/ 提供深度细节
- **U 型注意力**：核心约束放在文件顶部和底部，中间放详细规则
- **命令式语气**：用"检查 X"、"确保 Y"而非"你应该检查 X"
- **反模式显式化**：每个技能都有"禁止做"清单，比"应该做"清单更有效
- **术语一致**：全项目统一使用"阻断性问题"、"挂起"、"打卡"等术语
- **步骤自检**：每步结束强制对照 data-contract 自检必填字段
- **干跑预览**：中高风险任务先输出预览，用户确认后才执行
- **交叉审查**：REVIEW 后用不同视角做二次独立抽查
- **结构化日志**：每步追加 JSONL 日志，用于后续分析和优化
- **Gotchas 积累**：🆕 Agent 踩坑后自动追加到 gotchas.md，后续执行前扫描预警
- **反合理化防御**：🆕 每次审查前先过目 9 条自我欺骗话术及反驳
- **团队策略覆盖**：🆕 团队可在 team-policy.md 中声明规则，无需修改核心文件
