---
name: fullchain-skill-index
description: >
  EasyWork 全链路 AI 辅助开发工作流技能包索引。9 步流程按需裁剪：
  READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → TALK → ASK。
  入口技能：fullchain-dev-workflow（含任务分类器，自动判断需要哪些步骤）。
---

# EasyWork 技能包索引

## 工作流：9 步 → 按需裁剪

不是所有任务都需要 9 步。`fullchain-dev-workflow` 编排中枢内置了**任务分类器**，
会根据任务类型（纯理解/纯文档/微调/Bug修复/重构/功能开发）自动建议要执行和跳过的步骤。

| 序号 | 技能 | 路径 | 一句话职责 |
|------|------|------|-----------|
| 0 | **编排中枢** | `skills/fullchain-dev-workflow/SKILL.md` | 任务分类 + 步骤裁剪 + 流程编排 |
| 1 | READ | `skills/read-requirements/SKILL.md` | 多态输入理解（文档/图片/日志/代码/口语） |
| 2 | CODE | `skills/code-implement/SKILL.md` | 克制编码（中文注释/复用模式/反炫技） |
| 3 | REVIEW | `skills/code-review/SKILL.md` | 六维度自审查（正确/安全/兼容/可维护/性能/可观测） |
| 4 | EXAMINE | `skills/examine-quality/SKILL.md` | 找测试→跑→补→修→重跑至全绿 |
| 5 | GIT | `skills/git-split-commit/SKILL.md` | 按维度拆分提交（配置/逻辑/UI/测试） |
| 6 | GRAPH | `skills/graph-fullchain/SKILL.md` | Mermaid/飞书 流程图/架构图/时序图 |
| 7 | SUM | `skills/sum-session/SKILL.md` | 六要素总结（背景→发现→问题→解决→效果→展望） |
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
- `references/data-contract.md` — 步骤间数据传递契约（含版本迁移规则）
- `references/language-matrix.md` — 语言/技术栈适配速查（Node/Python/Go/Java/Rust）

## 使用入口

- **全链路（推荐）**：触发 `fullchain-dev-workflow`，编排中枢会先分类任务，再按裁剪后的流程执行
- **单步**：直接触发对应技能，如只需要审查代码 → `/code-review`
- **半链路**：用户指定从哪里开始，如"代码已写好，从 REVIEW 往后走"

## 维护原则

- **渐进式披露**：SKILL.md 自包含可执行指令，references/ 提供深度细节
- **U 型注意力**：核心约束放在文件顶部和底部，中间放详细规则
- **命令式语气**：用"检查 X"、"确保 Y"而非"你应该检查 X"
- **反模式显式化**：每个技能都有"禁止做"清单，比"应该做"清单更有效
- **术语一致**：全项目统一使用"阻断性问题"、"挂起"、"打卡"等术语
