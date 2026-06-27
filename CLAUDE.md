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
- MCP Server：`skills/knowledge-base/mcp-server/`（知识库自动索引）

## 架构概览

```
EasyWork/
├── CLAUDE.md                 ← 本文件（L1 路由，始终加载）
├── MEMORY.md                 ← 知识库索引（指针列表）
├── QUICKREF.md               ← 30 秒快速参考
├── skills/                   ← 19 个技能定义
│   ├── fullchain-dev-workflow/  ← 编排中枢
│   ├── knowledge-base/          ← 知识库管理（跨切面能力 + MCP Server）
│   └── ...
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

---

## 📚 知识库自动触发规则（CRITICAL）

> **目标**：避免每次新会话重读代码/重搜资料，跨上下文复用知识。
> **机制**：L1 索引始终在上下文中（MEMORY.md），L2 内容按需加载（knowledge/）。

### 规则 1：会话启动 → 自动检索

**每个新会话开始**（或 `/clear` 后），在回答用户第一个问题之前：

```
1. 读 MEMORY.md（已在上下文中，无需再读）
2. 如果用户的问题涉及具体模块/API/功能：
   → 搜索 knowledge/ 目录下的 _index.md 文件
   → 检查是否有相关条目
   → 如有，加载相关条目的 frontmatter + 核心内容（不加载全部）
   → 在回答开头标注："📚 知识库找到 {N} 条相关知识，已加载"
3. 如果用户的问题无法匹配已有知识：
   → 标注："📚 该领域无已有知识，将从零分析"
```

**具体执行**：
- 搜索路径：`knowledge/domain/{domain}/_index.md`、`knowledge/code/{module}/`、`knowledge/decisions/_index.md`
- 匹配方式：标签匹配 + 标题关键词匹配
- 加载上限：最多加载 3 条知识条目的核心内容（避免爆上下文）

### 规则 2：阅读分析 → 自动捕获

**当 Agent 执行以下操作时**，必须在完成后判断是否需要沉淀知识：

| 触发条件 | 判断标准 | 动作 |
|---------|---------|------|
| 阅读 ≥3 个源码文件并形成理解 | 理解涉及跨文件调用链/架构模式/非显而易见的设计 | 沉淀到 `knowledge/code/{module}/`，dimension=analysis |
| 用户提供了文档/代码/需求材料 | 材料 ≥50 行或包含关键信息（API 规格/业务规则/数据模型） | 保存到 `knowledge/source/inner/`，source=inner |
| 搜索了 ≥3 个外部资源（GitHub/论文/博客） | 搜索结果形成了有价值的判断 | 沉淀到 `knowledge/source/outer/`，source=outer |
| 做出了技术决策（A vs B） | 决策涉及 ≥2 个方案的取舍 | 沉淀到 `knowledge/decisions/DEC-{nnn}.md`，dimension=decision |
| 用户说"记住这个"/"保存"/"沉淀" | 无条件 | 立即执行完整知识沉淀流程 |

**执行方式**：
- 判断符合条件后，Agent 在对话中简洁标注："📚 已自动沉淀到 knowledge/{path}"
- 不打断主流程——沉淀是后台动作，不影响当前对话
- 如果是 L1+ 风险级别的改动，先展示摘要等用户确认

### 规则 3：新任务启动 → 知识优先

**当接到任何开发/分析类任务时**（在开始 READ 或 CODE 之前）：

```
1. 快速扫描 knowledge/ 目录的 _index.md
2. 检查：这个模块/API/功能是否被分析过？
3. 检查：是否做过类似的决策？
4. 检查：用户之前是否问过类似的问题？
5. 输出："📚 知识库状态：{N} 条相关 / {M} 条可复用 / 预计节省 ~{X} tokens"
```

**如果找到相关条目的代码分析**（如 `knowledge/code/auth/`），直接引用已有分析而非重新读代码——除非：
- 知识条目标注了 `status: archived`（已过时）
- 代码版本已变更（条目中的 commit hash 与当前不同）
- 用户明确要求"重新分析"

### 规则 4：会话结束 → 自动交接

**以下情况触发会话交接记录**：
- 用户说"/clear"或"/compact"之前
- 完成了一个完整的 EasyWork 流水线（走完 SUM 或 SELFCHECK）
- 对话时长超过 30 分钟且涉及 ≥3 个文件的代码改动
- 用户明确说"写交接"/"保存进度"

**交接记录写入**：`knowledge/sessions/{YYYY-MM-DD}-{session-id}.md`
**模板**：见 `skills/knowledge-base/assets/handoff-template.md`

### 规则 5：知识维护周期

| 周期 | 动作 |
|------|------|
| **每次沉淀后** | 更新对应 `_index.md` 的条目表 |
| **每天首次会话** | 扫描 `knowledge/` 统计，如有 >7 天未更新的 integration 条目 → 提醒归档 |
| **每周** | 检查 `knowledge/code/` 下的条目是否有代码变更（对比 commit hash） |
| **每季度末** | 季度 O 强制复盘 → 归档 |

### 规则 6：MCP Server 优先

如果 `knowledge-base` MCP Server 可用（见 `skills/knowledge-base/mcp-server/`）：
- **检索**：优先使用 MCP 工具 `knowledge_search` / `knowledge_context`（比手动搜索 _index.md 更准确）
- **写入**：使用 MCP 工具 `knowledge_store`（自动维护 frontmatter + 更新索引 + 去重检测）
- **统计**：使用 MCP 工具 `knowledge_stats`
- **维护**：使用 MCP 工具 `knowledge_maintenance`

如果 MCP Server 不可用（首次启动 / Python 环境问题），降级为手动文件操作——Agent 直接读写 knowledge/ 目录下的 Markdown 文件。

---

## 反模式速查

- ❌ 新会话直接开始分析代码，不先查知识库
- ❌ 分析完一个模块不沉淀，下次又重读
- ❌ 知识条目不标 commit hash，代码变了条目还标着 stable
- ❌ L1 索引存内容——MEMORY.md 只存指针
- ❌ MCP 可用时还手动 grep _index.md
