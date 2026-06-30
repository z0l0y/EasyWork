# CLAUDE.md

> L1 薄路由 · 始终加载 · 项目规范与架构概览

## 项目概述

EasyWork 是一个 Claude Code 技能生态系统，提供 27 个专业技能 + 流水线编排 + 网状自治分析。覆盖从需求理解、代码实现、审查、测试、复盘到 CTO 拷打的完整研发生命周期。

---

## 🚪 从哪里开始？

**你不需要记住 27 个技能名或 28 条命令。** 只需用自然语言描述你想做什么，Agent 自动匹配最合适的技能：

| 你想... | 直接说 |
|---------|--------|
| 🔍 理解代码/项目 | "帮我理解这个项目" / "追踪这个函数" / "XX 是什么" |
| ✏️ 修复/开发 | "帮我修复 XX bug" / "实现 XX 功能" / "帮我测试接口" |
| 🧠 审查/选型/复盘 | "帮我 review" / "对比 A 和 B" / "复盘 XX 问题" |
| 🎨 编排流程 | "用 EasyWork" 走完整流程 |
| 🖼 可视化编排 | `/easywork:canvas` 打开画布 |

> 📖 5 分钟入门 → [GETTING_STARTED.md](GETTING_STARTED.md)
> 📖 全部命令速查 → [QUICKREF.md](QUICKREF.md)

---

## 构建与运行

- 本项目为 Claude Code Skills 集合，无编译/构建步骤
- Skill 文件位于 `skills/` 目录，每个技能一个 `SKILL.md`
- 斜杠命令位于 `.claude/commands/easywork/`（28 条命令）
- 编排中枢：`skills/fullchain-dev-workflow/SKILL.md`
- 快速参考：`QUICKREF.md`
- MCP Server：`skills/knowledge-base/mcp-server/`（知识库自动索引）
- 知识存储：SQLite + FTS5（`knowledge/conversation.db`，Stop hook 每轮实时写入）
- Hook 管线：SessionStart → PostToolUse → Stop → PreCompact → SessionEnd

## Hook 知识捕获管线

| Hook | 触发时机 | 写入目标 | 延迟 |
|------|---------|---------|------|
| **SessionStart** | 会话启动 | 注入知识索引到上下文 | 0 |
| **PostToolUse** | 每次工具调用 | buffer/{session_id}.jsonl（元数据） | 实时 |
| **Stop** | 每轮 Agent 回复结束 | SQLite turns 表（Q&A 全文，FTS5 索引） | 实时 |
| **PreCompact** | 上下文压缩前 | flush → raw/daily/handoff | 压缩时 |
| **SessionEnd** | 会话退出 | flush → raw/daily/handoff + MCP store | 退出时 |

## 架构概览

```
EasyWork/
├── CLAUDE.md                 ← 本文件（L1 路由，始终加载）
├── MEMORY.md                 ← 知识库索引（指针列表）
├── QUICKREF.md               ← 30 秒快速参考
├── skills/                   ← 27 个技能定义（核心流程）
│   ├── fullchain-dev-workflow/  ← 编排中枢（点线网三级）
│   ├── scenario-runner/         ← 场景执行引擎（🆕 v3.1）
│   ├── scenario-builder/        ← 场景构建器（🆕 v3.1）
│   ├── knowledge-base/          ← 知识库管理（跨切面能力 + MCP Server）
│   └── ...
├── tools/                    ← 工具层（非核心，手动调用）
│   └── scenario-canvas/      ← 🆕 可视化拖拽场景编辑器（浏览器打开）
├── scenarios/                ← 🆕 场景定义存储（YAML）
│   ├── library/              ← 7 个预置场景模板
│   └── user/                 ← 用户自定义场景
├── .claude/commands/easywork/ ← 28 条斜杠命令入口
└── knowledge/                 ← 知识库内容层（L2）
```

## 编码规范

- **Skill 文件**：YAML frontmatter + Markdown，中文为主要文档语言
- **Emoji** 作为技能唯一视觉标识符（不可重复使用）
- **铁律系统**：40 条全局铁律（编排中枢 §2-3），风险 L0-L4 五级分类
- **ETR 证据标准**：所有关键结论必须含 Evidence/Thinking/Risk 三元组
- **命令文件**：`disable-model-invocation: false`，让模型能看到并执行路由指令（加载 SKILL.md + 传递 $ARGUMENTS）

## 技能调用方式

> **⚠️ CRITICAL：EasyWork 技能 ≠ `Skill` 工具。`Skill` 工具只认 Claude Code 内置技能（update-config、claude-api 等），
> 调用 EasyWork 技能会报 `Unknown skill`。正确做法：直接 `Read` 对应的 `skills/<name>/SKILL.md`，按其中规则执行。**

1. **自然语言**：说触发词（如"技术选型"、"帮我测接口"）→ Agent 自动 Read 对应 SKILL.md
2. **斜杠命令**：`/easywork:<name>`（如 `/easywork:radar`）→ 命令文件路由 → Agent Read 对应 SKILL.md
3. **编排中枢**：说"用 EasyWork" 走完整 10 步流程
4. **场景画板**（🆕 v3.1）：`/easywork:canvas` 打开可视化拖拽编辑器 → `/easywork:scenario run <id>` 执行
5. **禁止行为**：❌ 不要对 EasyWork 技能调用 `Skill` 工具（会报 `Unknown skill`）

---

## 📚 知识库（可配置，可选）

> 知识库默认开启。关闭方式：`.easywork/config.json` 中设置 `"enabled": false`。
> 领域（domains）、话题分类（topic_rules）均可在 config.json 中自定义，不再硬编码。
> 详细规则见 `skills/knowledge-base/SKILL.md`。

- 会话启动 → 自动检索 MEMORY.md + knowledge/ 索引
- 新任务启动 → 知识优先（先查已有分析，避免重复阅读）
- 阅读/搜索完成后 → 判断是否值得沉淀
- 会话结束 → 自动交接记录

## 反模式速查

- ❌ 新会话直接开始分析代码，不先查知识库
- ❌ 分析完一个模块不沉淀，下次又重读
- ❌ 知识条目不标 commit hash，代码变了条目还标着 stable
- ❌ L1 索引存内容——MEMORY.md 只存指针
- ❌ MCP 可用时还手动 grep _index.md
