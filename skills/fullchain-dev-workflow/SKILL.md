---
name: fullchain-dev-workflow
description: >
  全链路开发流程编排中枢。根据任务类型智能调整执行步骤（10步→按需裁剪）。
  内置任务分类器、步骤跳过机制、回退循环限制、全局异常SOP和Checklist打卡系统。
  🆕 v2.16: 点线网三级技能编排——点(单技能精准调用/19个技能点)、
  线(7条内置流水线+动态流水线/DAG编排)、网(Meta-Orchestrator+技能自治扩散+深度/预算/审批三重控制)。
  详见 references/skill-graph-orchestration.md。
  v2.12: 11条新铁律(#30-#40)、风险五级分类(L0-L4按级裁剪闸门)、上下文状态文件防丢失(铁律#40)、
  完成定义闸门+需求可追溯矩阵+环境保真闸门+参考基线闸门+测试充分性闸门(回归测试强制)、
  重复失败触发器(2次即BLOCK)+历史版本覆盖矩阵+来源出处闸门+证据账本(最低样本数)、闸门依赖图(DAG)。
  v2.11: 文档保真闸门(7项检查→HARD GATE,铁律#29)、禁止无基准覆写(6条Anti-Overwrite规则)、
  写入模式三级分类(Quick Fix/Normal/Full Archive)、文档作用域(round_report/engineering_active)。
  v2.10: 文档拓扑闸门(7项检查→HARD GATE,铁律#28)、双模文档结构(Mode A审计日志/Mode B持续维护默认)、
  结构化合并(Fetch→Check→Distribute→Index→Mark→Verify,取代尾部追加更新记录)。
  v2.9: 反水文闸门(6类水文信号检测→HARD GATE)、MCR→MCR+质量升级(每步增加反例+质量维度)、
  ETR证据链标准(Evidence/Thinking/Risk三元组)、同行审查就绪六问自检、
  写后Fetch验证(防截断/格式损毁)、文档质量评分(100分制/<80分阻断)、
  禁止凭记忆写报告(必须基于step_output拼装)。
  v2.8: CODE↔REVIEW质量门禁循环(回退不通过不可前进)、READ需求理解显式确认、
  文档迭代增量更新(原位追加+版本标注+过时信息清理)、交互式应用EXAMINE增强(
  CLI/TUI/GUI/Web前端/游戏真实体验验证)、REVIEW七维度交叉分析优化。
  v2.7: 报告深度分层(brief/standard/detailed)、MCR最小内容要求+自检闸门、
  流式增量写入保障、报告类型(executive_summary/engineering_record)、
  深度自动升级、代码摘录位置标注、同行审查就绪标准。
  v2.6: SelfCheck CTO拷打层（业务背景/问题发现/解决方案/实现过程四阶段拷打+
  汇报就绪检查）、10步工作流、全任务类型强制自检。
  v2.5: 可插拔产物后端（local_html/markdown/lark_doc）、飞书原生文档沉淀、
  Git链路追踪（任务→提交→Check→hash→测试→飞书）、文档写作规范、
  Git提交粒度增强（业务上下文+逐项Check+风险验证）。
  v2.4: Git安全管控、敏感信息脱敏、自定义步骤确认、供应链外部搜索防护、
  Gotchas候选-确认机制、文件系统写保护。
  v2.3: 并行审查、反合理化防御、团队策略覆盖、自定义步骤注入、逐步骤预览、
  Gotchas知识库、交互式新手引导、可访问性审查、供应链检查、Conventional Commits。
allowed-tools: Read, Write, Bash, Search, Grep, Glob
model: sonnet
version: 2.17
capability:
  id: fullchain-dev-workflow
  display_name: 全链路编排中枢
  emoji: "🔧"
  category: orchestration
  tier: 3
  inputs:
    - { name: user_intent, type: text, required: true, description: "用户意图描述（自然语言）" }
  outputs:
    - { name: orchestrated_execution, type: multi_skill_pipeline, description: "按需裁剪的 10 步执行流程或点线网编排结果" }
  triggers: ["用 EasyWork", "走 EasyWork 流程", "EasyWork"]
  related_skills:
    - { skill: all, relationship: orchestrator, desc: "编排中枢可调度所有 19 个技能点、7 条内置流水线、网模式自治扩散" }
  suggested_when:
    - "用户需要完整的开发流程管理"
    - "任务复杂度超过单个技能能处理的范围"
  pipeline_placement:
    good_after: []
    good_before: [all]
  autonomous:
    callable_by_other: false
    requires_confirmation: false
    max_depth: 0
  risk_level: L0
---

# Fullchain Dev Workflow（核心编排中枢）

## 1. 核心理念：不是每个任务都需要 10 步

完整流程是 READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → TALK → SELFCHECK → ASK。
**强制所有任务走完 10 步是愚蠢的**——改一个文案不需要画架构图，看一段代码不需要写测试。实际上，只有重构任务才走全部 10 步，其余类型均按需裁剪。但 **SELFCHECK（CTO 拷打）不可跳过**——任何任务类型都必须执行，仅模式不同（完整/标准/快速/轻量）。

本模块的核心智能在于**任务分类前置**：先判断"这到底是个什么类型的任务"，然后裁剪步骤。

### 🆕 v2.13 点线网三级编排

EasyWork 不只是 10 步开发流程。12 个独立技能节点可以按三种模式组合执行。详见 `references/skill-graph-orchestration.md`。

| 模式 | 触发 | 行为 | 适用场景 |
|------|------|------|---------|
| 🎯 **点** | 触发词精准命中 | 单技能直调，零开销 | "读论文" / "追踪代码" |
| 🔗 **线** | "先...再..." / 流水线触发词 | 技能 DAG 串联，前驱输出→后继输入 | "扫技术动态并深读" |
| 🌐 **网** | "全面分析 / 帮我搞清楚" | Meta-Orchestrator 分析意图 → 技能自治扩散 | 复杂问题需多技能协作 |

**网模式扩散控制**：最大深度 3 层 / 预算上限 100K token / 涉及代码改动必须用户审批 / 循环检测 / 30 分钟超时自动收敛。
用户始终保有最终决定权——可以接受建议的裁剪方案，也可以手动指定。

> **新手引导**：如果你是第一次使用，Agent 会运行交互式入门（`assets/onboarding.md`）。想先看示例？读 `assets/walkthrough-example.md` 中的三个端到端示例。

## 2. 全局管线

### 📚 §2.1 知识库自动管线（Pre-Step + Post-Step）

每个执行步骤都包含**前置知识检索**和**后置知识沉淀**两个自动化动作。这是跨切面能力——不走 EasyWork 的单步调用也会触发。

#### 前置检索（Pre-Step）——每步开始前

```
Step N 开始前：
  1. 检查当前任务领域（integration/development/quarterly-o）
  2. 搜索 knowledge/domain/{domain}/ 下的 _index.md
  3. 搜索 knowledge/code/{module}/ 下的已有分析
  4. 匹配标签 → 加载相关条目（最多 3 条）
  5. 输出："📚 知识库：找到 {N} 条相关 / {M} 条可复用"
  6. 有可复用知识 → 标注"基于 kb-xxx"，避免重复分析
  7. 无相关条目 → 标注"首次分析，完成后将写入知识库"
```

#### 后置沉淀（Post-Step）——每步完成后

| 步骤 | 触发条件 | 沉淀内容 | 目标位置 | ETR 要求 | 自动/确认 |
|------|---------|---------|---------|---------|----------|
| **READ** | 阅读 ≥3 个文件 **或** 用户提供了新材料 | 需求理解 + 完成定义 + 材料归档(inner) | `knowledge/domain/{domain}/{feature}/requirements.md` + `knowledge/source/inner/` | E:需求来源 T:理解推理 R:不确定点 | L0 自动 |
| **CODE** | 涉及 ≥2 个文件 **或** 有设计决策 | 变更记录 + 设计决策(为什么这样改) + 替代方案 | `knowledge/domain/{domain}/{feature}/implementation.md` + `knowledge/decisions/DEC-{nnn}.md` | E:代码位置 T:选择理由 R:影响面 | 展示摘要→确认 |
| **REVIEW** | 发现阻断问题 **或** 重要模式 **或** 安全发现 | 审查发现(位置+触发+影响+修复) + 改进模式 | `knowledge/domain/{domain}/{feature}/review.md` | E:发现位置 T:为什么是问题 R:未覆盖风险 | L0 自动 |
| **EXAMINE** | 测试结果有失败 **或** 覆盖率变化 >5% **或** 交互式验证完成 | 测试覆盖矩阵 + 未覆盖风险 + 环境矩阵 | `knowledge/domain/{domain}/{feature}/quality.md` | E:测试输出 T:覆盖评估 R:未测场景 | L0 自动 |
| **GIT** | 拆分 ≥3 个提交单元 **或** 涉及 DB/权限变更 | 拆分方案 + business_context + risk | `knowledge/domain/{domain}/{feature}/git-plan.md` | E:拆分逻辑 T:风险依据 R:回滚方案 | 展示摘要→确认 |
| **GRAPH** | 生成了架构图 **或** 发现了跨模块依赖 | Mermaid 源码 + 节点对照表 + 依赖矩阵 | `knowledge/code/{module}/architecture.md` | E:图表 T:架构分析 R:演进风险 | L0 自动 |
| **SUM** | **总是** | 六要素总结(背景→发现→问题→解决→效果→展望) **完整 ETR** | `knowledge/domain/{domain}/{feature}/summary.md` | E:每要素证据 T:完整推理链 R:未覆盖+副作用 | L0 自动 |
| **TALK** | **总是** | 5-Whys 根因链 + Trade-offs + 工程规范抽取 | `knowledge/domain/{domain}/{feature}/retro.md` | E:每次追问证据 T:根因链 R:复发可能性 | L0 自动 |
| **SELFCHECK** | 发现 ≥1 个认知缺口 **或** CTO 追问暴露盲区 | 认知缺口 + 补救计划 + 汇报就绪评估 | `knowledge/domain/{domain}/{feature}/selfcheck.md` | E:CTO追问记录 T:认知缺口分析 R:补救风险 | L0 自动 |
| **会话结束** | **总是**（/clear /compact /exit 前） | 会话交接：完成/停在/决定/打开/文件 | `knowledge/sessions/{date}-{session-id}.md` | E:完成证据 T:下次从哪开始 R:打开事项风险 | L0 自动 |

#### 沉淀执行流程

```
Post-Step 沉淀：
  1. 步骤完成 → 产出 step_output
  2. 检查沉淀触发条件（上表第 2 列）
  3. 满足条件 → 生成知识条目
     ├── L0 风险（纯分析）→ 自动写入，对话标注 "📚 → knowledge/{path}"
     └── L1+ 风险（涉及代码改动）→ 展示 3 行摘要 → 等用户确认 → 写入
  4. 更新对应 _index.md（新增条目行）
  5. 如有 related 条目 → 双向链接（更新旧条目的 related 字段）
  6. 去重检查：标题相似度 >80% → 更新旧条目而非新建
```

#### 知识库健康检查（每次流程启动时）

```
EasyWork 流程启动 → 任务分类完成 →
  ├── 扫描 knowledge/ 统计 → 
  │   总条目: {N} / 活跃: {A} / 归档: {B}
  ├── 时效性告警：
  │   - {X} 条 integration 条目 >7 天未更新（建议归档）
  │   - {Y} 条 code 条目 commit hash 与当前分支不匹配（建议复查）
  │   - {Z} 条条目 >90 天未更新（建议复查）
  └── 输出："📚 知识库健康：{A}/{N} 活跃 | {X} 条待归档 | {Y} 条可能过时"
```

### 🔧 §2.2 MCP Server 优先策略

如果 `knowledge-base` MCP Server 已配置并可用：
- **检索** → `knowledge_search` / `knowledge_context`（语义搜索，比 grep 准）
- **写入** → `knowledge_store`（自动 frontmatter + 去重 + 双向链接）
- **统计** → `knowledge_stats`（条目数/时效性/领域分布）
- **维护** → `knowledge_maintenance`（去重/归档/升级）

MCP 不可用时降级为手动文件操作（Agent 直接读/写 knowledge/ 目录的 Markdown 文件）。

详见 `skills/knowledge-base/SKILL.md` §MCP 集成。

## 3. 全局铁律（不随步骤跳过而失效）

1. **不确定时立刻挂起询问**：任何步骤中遇到无法 100% 确定的决策，停止并询问用户，禁止抛硬币
2. **每步完成后打卡**：即使某步骤被跳过，也要在进度卡中标记 `[skip]`（而非留空）
3. **产出物不丢失**：跳过的步骤不产生对应产出物，但最终总结中注明哪些步骤被跳过及原因
4. **用户可随时叫停或调整**：用户说"跳过这个"、"直接做"、"不用了" → 立即响应
5. **回退循环上限 3 次**：任何"发现问题→回退→修复→重新检查"的循环，**最多 3 轮**。超过 3 轮 → 挂起向用户报告，可能涉及更深层的设计或需求问题。具体回退路径：
	   - **CODE↔REVIEW 回退**：REVIEW 发现阻断性问题 → 回退 CODE 修复 → 修复后重新 REVIEW（最多3轮）。详见铁律#23
	   - **EXAMINE↔CODE 回退**：EXAMINE 发现测试失败且根因为代码逻辑错误 → 回退 CODE 修复 → 修复后重新 EXAMINE（最多3轮）
	   - **SELFCHECK→CODE 回退**：SELFCHECK 发现方案层面缺陷（非表述不清）→ 回退 CODE 调整设计 → 调整后重新走 REVIEW→EXAMINE→SELFCHECK（最多2轮，因为涉及面更广）
	   - **ASK→CODE 回退**：用户在 ASK 阶段质疑核心实现 → 回退 CODE 调整 → 重新走完整验证链（最多1轮，用户明确要求时触发）
6. **步骤预算**：每步最多搜索/读取 15 个文件，超过时挂起向用户确认是否继续
7. **步骤间数据传递**：每步结束按 `references/data-contract.md` 中定义的字段输出，后续步骤引用前序字段而非靠上下文回忆。可选引用 `references/data-contract.schema.json` 做机器验证
8. **产物后端可插拔**：工作流产物输出由可插拔后端决定（local_html / markdown / lark_doc / 未来扩展）。Agent 根据优先级选择后端：用户显式指定 > team-policy 配置 > 默认 local_html。后端选择与操作规范见 `references/output-backends.md`。写入前先确保 `.claude/easywork/` 目录存在（不存在则 `mkdir -p`）
9. **步骤产出自检**：每步结束时，Agent 必须对照 `references/data-contract.md` 自检是否产出了所有 `[必填]` 字段。任一必填字段缺失或为空占位符（"无"/"N/A"）→ 补全后再进入下一步。此检查不可跳过
10. **变更前 checkpoint**：在执行任何会修改文件的步骤前（CODE、以及 CODE↔REVIEW 回退修复），若项目为 git 仓库，先确保工作区干净。需 stash 时，**必须等待用户明确回复同意**，禁止倒计时默认执行（详见 `references/security-policy.md` §1.5）。如果 REVIEW 回退达 3 轮上限 → 请求用户确认后 `git stash pop` 恢复修改前状态
11. **Git 写操作必须用户确认**：`git add`/`commit`/`push`/`stash`/`reset`/`rebase`/`tag`/`branch -D`/PR创建/部署等操作，**绝对禁止**在用户明确说"可以执行"之前自动执行。GIT 步骤产出拆分方案后，将具体命令写入 `.claude/easywork/git-commands.sh`（或 `.bat`）供用户审查后手动执行。详见 `references/security-policy.md` §1
12. **输出内容脱敏**：HTML 报告和 `workflow.log.jsonl` 不得包含 API Key/Token/密码/内部URL/完整日志/大段源码（>30行）/手机号/邮箱/数据库连接串。Agent 在保存报告前必须执行脱敏自检。详见 `references/security-policy.md` §2
13. **自定义步骤必须预确认**：Agent 在任务分类后，列出所有发现的 custom skill（路径+名称+用途），等待用户确认后才执行。每次会话重新确认，不可沿用上次。详见 `references/security-policy.md` §3
14. **文件写入限于项目目录**：所有 Write/Edit/Bash 写操作不得超出当前项目根目录。不得写入系统目录、上级目录、或 `/tmp` 中的敏感项目数据。详见 `references/security-policy.md` §5
15. **仅在被显式调用时激活**：EasyWork 不是默认工作模式。Agent 仅在用户明确说"用 EasyWork"、"走 EasyWork 流程"、"EasyWork 模式"或类似显式调用时才启用完整 10 步流程。普通开发任务（用户说"修一下这个 bug"、"加个功能"、"帮我 review"）不自动套用 EasyWork 流程，除非用户明确要求。详见 `references/security-policy.md` §8
16. **产物后端不可自行选择**：Agent 不得自行决定使用哪个产物后端。后端选择优先级为：用户本轮显式指定 > team-policy 配置 > 默认 local_html。Agent 在未得到用户指示时使用默认后端，发现用户指定了但不可用的后端时必须报告并提供降级方案。详见 `references/output-backends.md` §2
17. **飞书后端 MCP 前置检查**：当选择 lark_doc 后端时，Agent 必须先检查 `lark-cli` MCP 服务是否可用。否则告知用户并降级到 local_html，同时在 SUM 产出中记录。详见 `references/security-policy.md` §10
18. **SelfCheck CTO 拷打不可跳过**：任何任务类型都必须执行 SelfCheck 步骤。CTO 质检是底线——AI 不拷打你，同事和领导就要拷打你。任务分类后按类型选择拷打模式（完整/标准/快速/轻量），但不可整体跳过。详见 `../self-check/SKILL.md`
19. **报告深度不可低于任务要求（🆕 v2.7）**：report_depth 由任务类型决定默认值（功能开发/重构/Bug修复→detailed，纯理解/审查/文档→standard，微调→brief）。Agent 可在发现重要发现时升级（standard→detailed，见§4深度升级触发条件），但**不可自行降级**（detailed→standard）除非用户显式要求。brief 模式仅适用于微调和用户显式指定的低风险任务
20. **流式增量写入保障（🆕 v2.7）**：每个步骤完成后必须立即追加到产物文档。支持流式追加的后端(lark-doc)：每步完成即调用 write_step_output。不支持流式追加的后端(local-html/markdown)：每步产出在内存中保留**完整结构化数据**（不可精简为摘要），write_final_report 时一次性恢复所有步骤完整详情。**禁止**最后一次性写"浓缩版"替代逐步骤详情，禁止以"上下文不足"为由截断步骤产出
21. **内容丰满度自检闸门 — HARD GATE（🆕 v2.7）**：在 write_final_report 之前，必须逐步骤对照 MCR 表（见§6）检查产出是否满足最小内容要求。detailed 模式：任一必填项缺失 → **拒绝写入** → 输出缺失清单 → 回退补充 → 重新自检（最多2轮，2轮后仍不通过→挂起报告用户）。standard 模式：缺失项记录警告但允许写入。brief 模式：跳过此闸门。此闸门不可跳过，不因后端而异
22. **报告类型与深度匹配（🆕 v2.7）**：executive_summary（领导层摘要）仅适用于 brief 深度，engineering_record（工程记录）适用于 standard/detailed 深度。如果用户对功能开发/重构/Bug修复选择 executive_summary，Agent 必须给出**强烈警告**并建议切换回 engineering_record。executive_summary 默认仅推荐用于微调任务
23. **CODE↔REVIEW 质量门禁循环（🆕 v2.8）**：REVIEW 发现阻断性问题时，必须回退 CODE 修复后重新 REVIEW——不可带着已知阻断问题继续前进。此循环最多 3 轮，每轮修复后必须重新过七维度审查（不可只查"修了什么"）。3 轮后仍未清零 → 挂起用户，输出已发现的所有问题和修复历程，可能涉及更深层的设计或需求问题。REVIEW 通过（verdict=pass 或 pass_with_fixes 且无阻断问题）是进入 EXAMINE 的**硬前置条件**
24. **READ 需求理解必须显式确认（🆕 v2.8）**：READ 阶段完成后，Agent 必须产出"需求理解确认"——用自己的话重述对需求的理解（含业务目标、技术方案假设、不确定点），并在进入 CODE 前等待用户确认。如果用户未指定实现方法，Agent 必须列出≥1个澄清问题，不可自行假设实现方案。需求理解有偏差在这一步修正成本最低，进入 CODE 后再改代价倍增
25. **文档迭代增量更新（🆕 v2.8，升级至 v2.10，补充 v2.11）**：当对已有产物文档进行需求变更时，不可新建文档。v2.8 方式：在文档末尾"更新记录"子节追加（仅 Mode A 审计日志下保留）。v2.10 方式（Mode B 持续维护，默认）：在对应流程节点内追加 `### v{N}` 版本小节，通过结构化合并（Fetch→Parse→Pre-check→Distribute→Index→Mark）实现。v2.11 补充：write_mode 决定更新粒度——Quick Fix 仅追加版本记录、Normal 执行完整 structured merge、Full Archive 仅在三合法场景使用。旧内容标注 `[已过时 — v{N} 起]` 而非删除。核心意图不变：确保文档可追溯完整演进历史
26. **交互式应用 EXAMINE 增强（🆕 v2.8）**：当任务涉及 CLI/TUI/GUI/Web 前端/游戏/交互式输入输出时，EXAMINE 步骤必须在 standard/detailed 模式下额外覆盖真实使用体验验证。详见 §6 交互式应用 EXAMINE 补充 MCR 表。对于纯后端/纯库/纯脚本任务，此条不适用
27. **反水文闸门 — HARD GATE（🆕 v2.9）**：在 write_final_report 之前，必须逐段扫描报告是否存在水文信号（见 `skills/sum-session/references/anti-fluff-gate.md`）。六类水文信号——空泛结论（"功能正常""提升用户体验"）、无证据通过（"测试通过"无命令+输出）、无位置描述（提代码无文件+函数+行号）、无取舍（只说采用了方案不说为什么不用别的）、无风险（无未覆盖风险/副作用说明）、SelfCheck放水（<8问/无反事实/无认知缺口/含模糊词未追问）。detailed 模式：任一命中→**拒绝写入**→回退补充→重新检测。standard 模式：命中警告+用户确认。brief 模式：跳过但标注免责声明。此闸门不可跳过，不因后端而异
28. **文档拓扑闸门 — HARD GATE（🆕 v2.10）**：在 write_final_report 之前，必须检查文档拓扑结构是否合法（见 `skills/sum-session/references/document-topology-gate.md`）。七项检查——重复顶层流程节点、模式混用、版本索引缺失、本轮内容未入节点、孤儿更新记录块、历史与当前混淆、索引与实际不一致。detailed 模式：任一命中→**拒绝写入**→自动structured merge repair→重新检测（最多2轮）。standard 模式：命中警告+用户确认（默认修复）。brief 模式：跳过但标注"拓扑未经检查"。Mode B（持续维护，默认）下严格约束，Mode A（审计日志，用户显式选择）下放宽。此闸门不可跳过，不因后端而异
29. **文档保真闸门 — HARD GATE（🆕 v2.11）**：在 Document Topology Gate 通过后、Write 之前，必须检查内容保真度（见 `skills/sum-session/references/document-preservation-gate.md`）。七项检查——内容长度退化（merge后字数<现有80%→阻断）、证据密度下降（代码摘录/测试输出/数据对比数下降→阻断）、历史版本丢失（### v{N}数量下降→阻断）、流程节点缩减（节点数下降→阻断）、无基准覆写（未fetch→阻断）、round_report冒充engineering_active（<500字+无代码摘录+无版本小节→阻断）、写入模式错配（quick_fix却full overwrite→阻断）。detailed→HARD GATE（任一命中阻断+修复），standard→SOFT GATE（警告+用户确认），brief→跳过但标注免责。Quick Fix禁止覆写正式文档，overwrite必须带preservation checklist。round_report不得overwrite engineering_active。已有文档默认Normal（局部更新），非Full Archive。此闸门不可跳过，不因后端而异
30. **完成定义闸门 — HARD GATE（🆕 v2.12）**：READ 阶段必须输出结构化的"完成定义"（见 `skills/read-requirements/references/delivery-definition-gate.md`）。六维清单——任务类型、机器可验证完成标准、仅人工可验证标准、高风险操作需显式确认、不可交付条件、证据要求。不定义"做到什么程度算完成"就不可进入 CODE。SUM 阶段交付验证清单从完成定义自动生成，逐项回溯勾选。detailed→HARD GATE（为空或只有"功能正常"→阻断），standard→SOFT GATE，brief→跳过但标注免责
31. **需求可追溯矩阵 — HARD GATE（🆕 v2.12）**：READ 阶段必须生成需求可追溯矩阵（见 `skills/read-requirements/references/traceability-matrix.md`）。五列——用户需求→验收标准→自动化测试→手动验证→状态。禁止测试不覆盖真实用户痛点。有任何行"未覆盖"且风险≥L2→阻断。矩阵<3行→回退补充。detailed→HARD GATE，standard→SOFT GATE
32. **环境保真闸门 — HARD GATE（🆕 v2.12）**：交互式应用（CLI/TUI/GUI/Web/Game）L3+必须在 EXAMINE 阶段至少执行一次近真实环境冒烟测试（见 `skills/examine-quality/references/environment-fidelity-gate.md`）。产出环境矩阵（OS/浏览器/设备/网络条件）。纯后端/库/脚本标注 N/A。L3+未执行冒烟→阻断。此闸门不可跳过
33. **参考基线闸门 — HARD GATE（🆕 v2.12）**：对成熟领域（认证/支付/上传/缓存等），CODE 之前必须在 GitHub/Web 搜索已有实现模型（见 `skills/fullchain-dev-workflow/references/reference-baseline-gate.md`）。列出≥3种常见实现模型，产出对比表（我们的方案 vs 参考实现）。禁止闭门造车。成熟领域未搜索→阻断。非成熟领域→跳过标注。L2+适用
34. **测试充分性闸门 — HARD GATE（🆕 v2.12）**：EXAMINE 从"跑测试"升级为"判断测试是否覆盖风险"（见 `skills/examine-quality/references/test-adequacy-gate.md`）。五维覆盖——Happy Path/边界/错误路径/并发/安全。Bug修复必须新增至少一个在老代码上FAIL、在新代码上PASS的回归测试。无回归测试=不可声称修复完成。L2+三维未覆盖→阻断或声明豁免。此闸门不可跳过
35. **重复失败触发器 — HARD GATE（🆕 v2.12）**：同一问题修复失败两次→BLOCK 进一步小修补（见 `skills/fullchain-dev-workflow/references/repeated-failure-trigger.md`）。必须输出——前两次为何未修复根因、正确的问题模型、新测试如何覆盖旧盲区、哪些假设需用户确认。Agent不可自行解除BLOCK。此触发在第2次失败（非第3次）生效，优先级高于铁律#5回退上限
36. **历史版本覆盖 — HARD GATE（🆕 v2.12）**：版本索引条目必须在对应影响节点下有独立版本小节（见 `skills/sum-session/references/historical-version-coverage.md`）。不可仅有版本索引+节点内一行摘要。产出覆盖矩阵表——版本/受影响节点/已覆盖节点/缺失节点/恢复状态。有缺失→阻断写入，先修复覆盖。此闸门不可跳过
37. **来源出处闸门 — HARD GATE（🆕 v2.12）**：每个版本内容必须标注来源类型（见 `skills/sum-session/references/source-provenance-gate.md`）。完整记录/摘要恢复/重构推断/外部引用。如为摘要恢复→必须声明"该版本为摘要恢复，非逐字原始记录"。禁止文档伪装完整却实际残缺。任何版本小节无来源标注→阻断。此闸门不可跳过
38. **证据账本 — HARD GATE（🆕 v2.12）**：每个交付轮次生成证据账本（见 `skills/sum-session/references/evidence-ledger.md`）。每行——结论/证据类型(TEST_OUTPUT/CODE_DIFF等)/证据位置/可复现？。证据样本数须满足最低门槛（L0:1条/L1:2条/L2:3条/L3:4条/L4:5条）。无证据样本=不可声称"完成"。低于门槛→阻断。此闸门不可跳过
39. **风险分类闸门 — HARD GATE（🆕 v2.12）**：任务启动时按 L0-L4 五级分类（见 `skills/fullchain-dev-workflow/references/risk-classification-gate.md`）。L0 纯文档/查询→最小流程，L1 小修复→单测+简短记录，L2 正常功能→单测+review+structured merge，L3 交互/并发/外部API→+smoke+环境矩阵+UX确认，L4 数据迁移/权限/部署/删除→+dry-run+备份+回滚+用户显式确认。不同风险等级适用不同闸门集和策略。等级不匹配→拒绝继续。此闸门不可跳过
40. **上下文丢失防护 — HARD GATE（🆕 v2.12）**：每轮产出机器可读状态文件 `.claude/easywork/state-v{N}.json`（见 `skills/fullchain-dev-workflow/references/context-loss-protection.md`）。字段——task/current_version/doc_url/baseline_revision/latest_revision/known_artifacts/open_risks等7分组。每次EasyWork会话启动时读取此状态文件。不可仅依赖聊天上下文恢复。`/clear`后必须先读state file再继续。无state文件→标注"新任务"。此闸门不可跳过

## 3. 上下文管理（防止爆上下文）

EasyWork 全链路 10 步涉及大量 skill 指令和产出物，在长对话中必然面临上下文窗口压力。
以下是四级应对策略，Agent 应根据当前上下文余量自动采取行动。

### 策略分级

| 级别 | 触发条件 | 策略 | 操作 |
|------|---------|------|------|
| 🟢 正常 | 上下文使用 < 60% | 正常执行，每步输出完整内容 | 无需特殊处理 |
| 🟡 预警 | 上下文使用 60-80% | 精简输出，上步产出仅保留结构化摘要 | 每步结束后输出一句话摘要，问用户"继续？" |
| 🟠 警戒 | 上下文使用 80-95% | 状态快照 + 状态文件 + 建议分步 | 保存状态快照，写入 `.claude/easywork/state-v{N}.json`（见铁律#40），建议 `/clear` 后从当前步骤继续 |
| 🔴 危急 | 上下文使用 > 95% | 强制保存状态+状态文件，停止执行 | 立刻保存状态快照+写入状态文件，停止新操作，等用户 `/clear` |

### 默认策略：单技能加载模式

**Agent 不要一次性加载所有 10 个 skill**。每步执行时只加载当前技能：

```
步骤执行流程：
  1. 读取当前步骤的 SKILL.md（如 skills/code-implement/SKILL.md）
  2. 执行该步骤，产出结构化结果
  3. 产出完成 → 在对话中保留简短摘要（3-5 行），详细内容写入 HTML/文件
  4. 进入下一步骤 → 读取下一个 SKILL.md
```

**编排中枢本身**保持在上下文中（它很轻量），但 9 个子技能的 SKILL.md **按需加载，用完即弃**。

### 策略一：分步执行 + 状态快照（推荐）

每个步骤完成后，Agent 主动评估上下文余量。如果预计下几步会超出窗口：

```
【上下文预警】
当前上下文已使用约 {X}%。建议处理方式：
  A) 我保存当前状态快照，你执行 /clear，然后粘贴快照我从中断处继续
  B) 我继续执行，但后续输出会精简（只保留关键结论，省略详细过程）
  C) 直接跳到最终步骤（跳过中间不必要步骤）
→ 请选择。
```

### 策略二：子 Agent 隔离执行

对于特别重的步骤（如 EXAMINE 需要运行大量测试、GRAPH 需要搜索大量文件），
Agent 可以将该步骤委托给子 Agent 执行。子 Agent 在独立上下文中工作，只返回最终结果。
**这只在平台支持子 Agent 且上下文确实紧张时使用**。

> 对于高风险任务的 REVIEW 步骤，可使用**并行审查**——3 个子 Agent 分别审查安全/性能/兼容性，
> 与主审查同步进行。详见 `references/orchestration-engine.md` §并行审查。

### 策略三：精简模式

当上下文紧张时，每步产出精简为以下最小格式：

```
[步骤 N/10 {步骤名}] ✅
{一句话结论}
{关键数字/发现（1-3 条）}
→ 详细内容已写入 {HTML文件路径 或 md文件路径}
```

完整产出物写入 HTML/文件，对话中只保留可供下一步使用的关键信息。

### 状态快照保存

详见 §8 的 JSON 格式。Agent 在每步结束后默认更新快照。用户说"继续"时，Agent 从快照恢复。

### 上下文感知检查

Agent 在**每步开始前**应简要评估："这一步需要读取多少文件？预计消耗多少上下文？"如预计会超出，提前使用上述策略。

## 4. 任务分类器（启动时首先执行）

Agent 加载本 Skill 后，**不要立刻开始流程**。先收集信息，输出分类结果让用户确认。

### 意图路由（用户说什么 → 判断为什么）

在正式分类之前，先根据用户的关键词做快速路由：

| 用户说了什么（关键词） | 快速判断 |
|----------------------|---------|
| "review / 审查 / 检查代码 / 帮我看下有没有问题" | → 🔎 纯审查（2步：READ+REVIEW） |
| "理解 / 分析 / 这段代码在干嘛 / 梳理 / 解释" | → 🔍 纯理解（3步：READ+GRAPH+SUM） |
| "修 / fix / 改一下 / 解决 / bug / 报错 / 500" | → 🐛 Bug修复（9步，跳过 GRAPH） |
| "加一个 / 新增 / 实现 / 功能 / feature" | → 🚀 功能开发（9步，跳过 TALK） |
| "重构 / 整理 / 优化结构" | → 🔧 重构（10步全走） |
| "改一下文案 / 改配置 / 改个颜色 / 改个参数" | → ⚡ 微调（5步：READ+CODE+REVIEW+GIT+SELFCHECK+ASK） |
| "写文档 / 改注释 / 更新 README / CHANGELOG" | → 📝 纯文档（7步，跳过 EXAMINE+GRAPH+TALK） |
| "CTO 拷打 / 拷打我自己 / 帮我拷打 / 拷打一下" | → 🥊 单步拷打（仅 SELFCHECK，其余全跳） |
| "检查清单 / 就绪检查 / 核对清单 / 清单审计 / 预检 / 交付出清 / 开发前检查 / 交付检查 / checklist / preflight / pre-flight" | → ✅ 单步清单审计（仅 CHECKLIST，其余全跳） |
| "帮我复盘 / 5-whys / 根因分析 / 为什么反复出问题" | → 🧠 单步复盘（仅 TALK，其余全跳） |
| "画架构图 / 画个图 / 可视化 / mermaid / 架构图" | → 📊 单步画图（仅 GRAPH，其余全跳） |
| "只理解需求 / 只读代码 / 只看一下 / 帮我看懂" | → 👁️ 单步理解（仅 READ，其余全跳） |
| "只审查 / 纯 review / 就 review 一下" | → 🔍 单步审查（仅 REVIEW，其余全跳） |
| "只写总结 / 帮我总结 / 写个报告 / 汇总一下" | → 📋 单步总结（仅 SUM，其余全跳） |
| "读论文 / 看论文 / paper / arxiv / 论文阅读 / 帮我读这篇" | → 📖 单步读论文（仅 READ-PAPER，其余全跳） |
| "读项目 / 看项目 / 理解项目 / 项目代码 / 接手项目 / read project" | → 📐 单步读项目（仅 READ-PROJECT，其余全跳） |
| "追踪代码 / trace / 调用链 / 这个函数怎么走 / 代码追踪 / 追一下" | → 🔬 单步代码追踪（仅 TRACE-CODE，其余全跳） |
| "技术保鲜 / 扫一下技术动态 / tech radar / 前沿扫描 / 技术雷达 / 快速扫一下 / 有什么新东西 / 全面深扫 / 深度扫描" | → 🛰️ 单步技术雷达（仅 TECH-RADAR，面/体模式，其余全跳） |
| "深扫 / 聚焦 / 这个技术怎么样 + 具体技术名" | → 🛰️ 单步技术雷达（仅 TECH-RADAR，点模式聚焦深扫，其余全跳） |
| "测试覆盖率 / 覆盖盲区 / test coverage / 哪些没测 / 测试有没有用" | → 🧪 单步覆盖率分析（仅 TEST-COVERAGE，其余全跳） |
| "生成文档 / 输出文档 / 保存输出 / 导出报告 / write article / write doc / save output / generate doc / article-write" | → 📝 单步文档编写（仅 ARTICLE-WRITE，其余全跳） |
| "斜杠命令 / slash command / 命令管理 / 命令列表 / slash-cmd / command list" | → 💻 单步命令管理（仅 SLASH-CMD，其余全跳） |
| "快问快答 / quick question / tldr / 说重点 / 别废话 / 直接说 / 快点回答 / 别啰嗦 / 讲核心 / quick-answer" | → ⚡ 单步快问快答（仅 QUICK-ANSWER，其余全跳） |
| "技术选型 / 方案对比 / 技术对比 / tech compare / 选型分析 / 技术调研 / 方案选型 / 技术评估 / compare solutions / 对比方案 / 选哪个技术 / 技术决策 / tech decision" | → ⚖️ 单步技术选型对比（仅 TECH-COMPARE，其余全跳） |
| "接口测试 / 联调测试 / API 测试 / api test / 接口联调 / 测试这个接口 / 帮我测接口 / 生成测试用例 / 接口验证 / test this api / 帮我联调 / 构造测试参数 / 检查接口" | → 🔌 单步接口联调测试（仅 API-TEST，其余全跳） |
| "知识库 / knowledge base / 查知识库 / 沉淀知识 / 整理知识库 / 我的知识库 / 知识管理 / 写入知识库 / 检索知识 / kb" | → 📚 单步知识库管理（仅 KNOWLEDGE-BASE，其余全跳） |

### 🆕 v2.13 流水线触发（🔗 线模式）
| 用户说了什么 | 流水线 | 技能序列 |
|------------|--------|---------|
| "扫技术动态并深读 / scan and deep read" | 🔭 扫描→深读 | 🛰️ tech-radar(面/体) → 📖 read-paper |
| "理解项目并追踪 / understand and trace" | 🏗️ 理解→追踪 | 📐 read-project → 🔬 trace-code |
| "分析覆盖率并补测试 / coverage and fix" | 🧪 覆盖→补测 | 🧪 test-coverage → 👁️ read-requirements → ✏️ code-implement |
| "全面理解这个项目 / full understand" | 🏗️🔬 全理解 | 📐 read-project → 🔬 trace-code → 🧪 test-coverage |
| "先...再...然后..."（自然语言流水线） | 🔗 动态流水线 | Meta-Orchestrator 解析用户意图 → 构建 DAG |

### 🆕 v2.13 网络触发（🌐 网模式）
| 用户说了什么 | 行为 |
|------------|------|
| "全面分析 / 深度排查 / 帮我搞清楚 / 完整评估" | Meta-Orchestrator 分析意图 → 初始技能图 → 执行中技能自扩散 |
| 复杂意图（涉及 3+ 技能才能回答的问题） | Meta-Orchestrator 建议切换网模式 |

### 分类维度

**维度一：改动性质**
- 🔍 **纯理解**：只是看代码、理解逻辑、分析架构，不产生任何代码改动
- 🔎 **纯审查**：只对已有代码做审查/评估，不修改代码
- 📝 **纯文档**：写/改 README、注释、CHANGELOG，不涉及逻辑代码
- ⚡ **微调**：改配置、文案、样式微调、一行 bug 修复，影响范围极小
- 🐛 **Bug 修复**：修复明确的 bug，改动集中在 1-5 个文件
- 🔧 **重构**：结构调整、代码整理，不改外部行为
- 🚀 **功能开发**：新增功能、新增接口、新增模块
- 🎯 **单步调用（🆕 v2.12+）**：零散需求，只需一个 skill 节点参与。不产生代码改动，跳过全部闸门，风险固定 L0。如：CTO 拷打、画架构图、根因复盘、纯读代码、论文阅读、项目理解、代码追踪、技术保鲜、覆盖率分析

**维度二：影响范围**
- 🟢 **低风险**：改动局限在单个文件/模块，不影响公共 API
- 🟡 **中风险**：改动涉及多个文件，或修改了被其他模块引用的公共接口
- 🔴 **高风险**：改动涉及核心模块、数据库 schema、API 签名、权限逻辑

**🆕 v2.12 维度三：风险等级 L0-L4（铁律#39）**
Agent 必须在任务分类时执行风险分级（详见 `references/risk-classification-gate.md`）：
- **L0 纯文档/查询**：只读/生成文档/回答问题 → 最小流程
- **L1 小修复**：单文件、单函数、无 API 变更、< 20 行 → 单测+简短记录
- **L2 正常功能（默认）**：多文件、有测试、非交互 → 单测+review+structured merge
- **L3 交互/并发/外部 API**：CLI/TUI/GUI/Web/Game/实时/API 调用 → +smoke+环境矩阵+UX确认
- **L4 数据迁移/权限/部署/删除**：不可逆操作、影响数据完整性 → +dry-run+备份+回滚+用户确认

分级依据：关键词扫描→文件数修正→升级触发。涉及DB schema/权限/部署/删除 → 最低 L4。
用户可覆盖："这是 L{M}"。

### 分类输出模板

```
## 任务分类

| 维度 | 判断 |
|------|------|
| 改动性质 | {类型} |
| 影响范围 | {风险等级} |
| 🆕 v2.12 风险等级 | L{N} — {等级名称} |
| 预估文件数 | {N} 个 |
| 🆕 v2.12 适用闸门 | {列出必执行闸门} |
| 🆕 v2.12 跳过闸门 | {列出跳过闸门} |

## 裁剪方案

[ ] 1. READ  — {执行/跳过} — {理由}
[ ] 2. CODE  — {执行/跳过} — {理由}
...
请确认或调整。
```

### 裁剪参考表

| 任务类型 | READ | CODE | REVIEW | EXAMINE | GIT | GRAPH | SUM | TALK | SELFCHECK | ASK | report_depth(默认) | report_type(默认) |
|---------|------|------|--------|---------|-----|-------|-----|------|-----------|-----|-------------------|-------------------|
| 🔍 纯理解 | ✅ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ✅ | ✅ | ⏭️ | ✅(轻量) | ⏭️ | standard | engineering_record |
| 🔎 纯审查 | ✅ | ⏭️ | ✅ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ✅(轻量) | ⏭️ | standard | engineering_record |
| 📝 纯文档 | ✅ | ✅ | ✅ | ⏭️ | ✅ | ⏭️ | ✅ | ⏭️ | ✅(标准) | ✅ | standard | engineering_record |
| ⚡ 微调 | ✅ | ✅ | ✅ | ⏭️ | ✅ | ⏭️ | ⏭️ | ⏭️ | ✅(快速) | ✅ | brief | executive_summary |
| 🐛 Bug修复 | ✅ | ✅ | ✅ | ✅ | ✅ | ⏭️ | ✅ | ✅ | ✅(完整) | ✅ | detailed | engineering_record |
| 🔧 重构 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅(完整) | ✅ | detailed | engineering_record |
| 🚀 功能开发 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⏭️ | ✅(完整) | ✅ | detailed | engineering_record |
| 🥊 单步拷打 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ✅(完整) | ⏭️ | brief | — |
| 🧠 单步复盘 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ✅ | ⏭️ | ⏭️ | brief | — |
| 📊 单步画图 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ✅ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 👁️ 单步理解 | ✅ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 🔍 单步审查 | ⏭️ | ⏭️ | ✅ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 📋 单步总结 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ✅ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 📖 单步读论文 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 📐 单步读项目 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 🔬 单步代码追踪 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 🛰️ 单步技术雷达 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 🧪 单步覆盖率分析 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| ✅ 单步清单审计 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 📝 单步文档编写 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 💻 单步命令管理 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| ⚡ 单步快问快答 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| ⚖️ 单步技术选型对比 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 🔌 单步接口联调测试 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |
| 📚 单步知识库 | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | brief | — |

> 上表是默认建议，不是死规则。具体问题具体分析。团队可在 `references/team-policy.md` 中声明额外约束。
> 自定义步骤（`.claude/skills/easywork/custom/`）在裁剪方案中以 `[+]` 前缀展示。
>
> **🆕 v2.12+ 单步调用规则**（🥊🧠📊👁️🔍📋📖📐🔬🛰️🧪✅📝💻⚡⚖️🔌📚）：
> - **只加载目标 skill 的 SKILL.md**，不加载编排中枢其余步骤和子技能
> - **跳过全部闸门**（铁律 #1-#40 均不适用），风险固定 L0
> - **不写状态快照、不写 state file、不写 workflow.log.jsonl**
> - **不需要 report_depth / report_type**，直接产出一个 skill 的原始产出
> - **不经过任务分类确认**——触发词命中即直接执行（零开销）
> - 用户可用"用 EasyWork + {原触发词}"显式走完整分类流程

### 报告深度选择逻辑（🆕 v2.7）

**默认映射规则**：
- 任务类型决定默认 report_depth 和 report_type（见上表）
- "用 EasyWork 做项目" 等模糊指令 → 默认 standard/detailed，**绝不** brief
- "用 EasyWork 帮我看看这段代码" → standard

**用户覆盖**：
- 用户可在任务分类确认时覆盖深度和类型："用 brief 模式""只要简要总结""详细报告"
- 用户覆盖 engineering_record → executive_summary 时：
  - 如任务为微调/小bug → 允许
  - 如任务为功能开发/重构/Bug修复 → **强烈警告**并建议切换回 engineering_record
  - 如用户坚持 → 记录警告但尊重用户选择

**深度升级（自动触发）**：
以下情况发生时，Agent 必须自动将 report_depth 从 standard 升级为 detailed，
在进度卡中标注 `[⬆ 深度升级]` 并说明具体原因：

| 触发条件 | 说明 |
|---------|------|
| 安全发现 | REVIEW 发现阻断性安全问题（review_output.blocking_issues > 0 且涉及 security 维度） |
| 测试根因复杂 | EXAMINE 发现测试失败且定位到复杂根因（>2 层调用链） |
| 改动超预估 | CODE 阶段实际改动文件数超过预估 2 倍 |
| 需求补充 | 用户中途补充了重要需求信息 |

升级后在进度卡中展示：
```
⚠️ 深度升级：standard → detailed（原因：REVIEW 发现 1 个阻断性安全问题，需详细记录安全审查过程和修复方案）
```

**深度降级保护**：
- Agent **不得自行降级**。detailed→standard 或 standard→brief 必须用户显式要求
- 用户显式降级 → 记录警告但允许：
  "⚠️ brief 模式将省略排查路径、量化对比、代码摘录等内容，后续追溯可能信息不足。已按要求降级。"

**报告类型一致性**：
- executive_summary 强制 report_depth=brief（如用户选 executive_summary 但 depth=detailed → 提示"executive_summary 仅支持 brief 深度"并自动调整）
- engineering_record 可选 standard 或 detailed，不强制某一深度

**分类输出模板新增**（在 §4 分类输出模板末尾追加）：
```
## 报告配置

| 配置项 | 值 | 依据 |
|--------|-----|------|
| report_depth | {brief/standard/detailed} | 任务类型默认 / 用户覆盖 / team-policy |
| report_type | {executive_summary/engineering_record} | 任务类型默认 / 用户覆盖 / team-policy |
```

### 团队策略加载

Agent 在任务分类后、执行前，检查 `references/team-policy.md` 是否存在且包含团队规则。
如果存在，将规则注入到对应步骤的约束条件中。例如：
- `comment_language: english` → CODE 步骤使用英文注释
- 强制规则（MUST）→ 阻断级别，违反则挂起
- 建议规则（SHOULD）→ 警告级别，在 SUM 中注明

### 安全策略加载（🆕 v2.4）

Agent 在任务分类后、执行前，**必须**加载 `references/security-policy.md`。
安全策略覆盖以下方面，所有步骤强制执行：

| 安全域 | 核心规则 | 违反后果 |
|--------|---------|---------|
| Git 操作 | 写操作必须用户确认，拆分命令写入文件供手动执行 | 阻断——不得自动执行 |
| 敏感信息 | HTML/日志脱敏：Token/密钥/内部URL/大段源码/手机/邮箱 | 保存前必须自检 |
| 自定义步骤 | 列出清单→等待用户确认→每次会话重新确认 | 未确认=跳过 |
| 供应链检查 | 禁止将内部包名/私有 registry 发到外网搜索 | 阻断——标注为私有包 |
| 文件写入 | 限定项目根目录内，禁止系统/上级/敏感临时目录 | 阻断——不得写入 |
| Gotchas | 生成候选→用户确认→才写入文件（非自动追加） | 候选保留在 SUM 产出中 |

### 产物后端选择（🆕 v2.5）

Agent 在安全策略加载完成后，**必须**确定当前会话的产物后端。

1. 读取 `references/output-backends.md` 了解可用后端
2. 扫描 `backends/*/SKILL.md` 发现已安装的后端适配器
3. 按优先级选择后端：
   - 用户本轮显式指定（"输出到飞书""生成 markdown"）→ 直接使用
   - `team-policy.md` 中 `output_backend.preferred` 配置 → 如可用则使用
   - 默认：`local_html`（所有环境均可用）
4. 检查后端依赖是否满足（MCP 可用性、网络连接等）
5. 将选定的后端记录到 data-contract 的 `output_backend` 字段

**降级规则**：用户指定了不可用的后端时，Agent 必须告知原因并降级到 local_html，不可静默切换。
见 `references/output-backends.md` §6。

| 后端 | output_format | 依赖 | 适用场景 |
|------|-------------|------|---------|
| local_html | html | 无 | 默认后端，所有环境可用 |
| markdown | markdown | 无 | 纯文本记录、PR 描述、Git 归档 |
| lark_doc | lark_doc | MCP: lark-cli | 飞书用户，团队协作与分享 |


Agent 发现 `.claude/skills/easywork/custom/` 下有自定义技能时：
1. 列出所有发现的技能：路径、名称（from YAML frontmatter）、用途（from description）
2. 以清单形式展示，等待用户确认
3. 用户确认后才注入并执行
4. 未被确认的 → 进度卡标注 `[+][skip] {名称} — 用户未确认`
5. **每次会话重新确认**，不可沿用历史确认记录

### 项目 Gotchas 扫描

Agent 在 READ 阶段应浏览 `references/gotchas.md` 中的项目陷阱记录。
如果当前任务涉及已记录的陷阱模块，在干跑预览中主动标注：
"⚠️ 根据 gotchas.md，{模块} 曾有 {陷阱描述}，执行时会特别注意。"

> **🆕 v2.4**：Gotchas 追加改为候选制。Agent 在 SUM 步骤检查触发条件，生成候选条目展示给用户，
> 用户确认后才写入 `references/gotchas.md`。详见 `references/security-policy.md` §6。

### 干跑预览模式（推荐用于中高风险任务）

任务分类完成后、实际执行前，Agent **必须先输出"干跑预览"**再等待用户确认。这让用户在每一步执行前就知道"Agent 会做什么"。

**必须输出干跑预览的场景**：
- 🔴 高风险任务（≥7 步）
- 🟡 中风险任务（≥5 步）
- 用户明确说"先让我看看你会怎么做"

**可以跳过干跑的场景**：
- 🟢 低风险任务（≤3 步）
- 用户说"直接做"、"不用预览"
- 当前是第 N 次执行同类任务且用户已熟悉流程

**干跑预览模板**：

```
## 🔍 执行预览（用户确认后才开始实际执行）

| 步骤 | 状态 | 预计操作 | 涉及文件/模块 | 预计产出 |
|------|------|---------|-------------|---------|
| 1. READ | 执行 | 阅读 {N} 个文件，提取需求 | {文件列表} | 五要素需求说明 |
| 2. CODE | 执行 | 修改 {N} 个文件，约 {M} 行 | {文件列表} | 变更记录 + 代码改动 |
| 3. REVIEW | 执行 | 七维度审查 {N} 个变更文件 | 同 CODE | 审查报告 |
| 4. EXAMINE | 跳过 | {跳过理由} | — | — |
| ... | ... | ... | ... | ... |

⚠️ 风险提示：
- {风险点1及缓解措施}
- {风险点2及缓解措施}
- {如有 gotchas 命中：⚠️ gotchas 记录：{陷阱简述}}

→ 回复"执行"开始，或回复"调整 {步骤名} {修改意见}"来修改方案。
```

**用户确认后**，Agent 才开始实际读取文件、修改代码。在用户说"执行"之前，Agent **只做搜索和分类，不做任何修改**。

### 逐步骤预览（🆕 v2.3）

干跑预览是工作流级别的。**逐步骤预览**是步骤级别的——在每步实际执行前，Agent 输出一个微型预览：

```
▶ 即将执行 步骤 3/9：REVIEW（代码审查）

  基于 CODE 阶段产出的 {N} 个变更文件，执行七维度自审查。
  其中安全性和正确性审查维度将使用深度模式（Opus）。
  预计耗时：{M} 秒 | 预计 Token：{T}

  → 执行中……
```

**适用场景**：
- 该步骤将消耗大量 Token（如 EXAMINE 运行全量测试）
- 上下文 🟡 预警（让用户决定是否继续）

**可跳过**：🟢 低风险任务、纯理解/纯审查等 ≤3 步任务。

## 5. 全局异常处理 SOP

**触发条件**：找不到需要的信息、输入材料矛盾、改动会导致不可控的连锁影响、无法验证正确性、对决策没有 100% 把握。

**SOP 动作**：
```
【异常挂起 — {步骤名称}】
问题：{一句话说清卡在哪}
已尝试：{列出现有尝试}
选项：A) {方案A+利弊}  B) {方案B+利弊}  C) {其他}
建议：{推荐方案及理由}
→ 请选择或给出新指示。
```

**绝对禁止**：自行猜答案、假装没问题跳过、用模糊话术掩盖不确定性。

> **常见故障模式**：`references/failure-runbooks.md` 为 5 种重复故障（测试环境不可用、依赖冲突、工作区不干净、Agent 自我怀疑循环、上下文溢出）提供了预置诊断步骤和解决方案。Agent 遇到这些模式时优先查 Runbook 而非重新发明应对。

## 6. 十步流程（执行细节见各子技能 SKILL.md）

| 步骤 | 加载技能 | 一句话职责 | 产出物 | 跳过条件 | 推荐模型 |
|------|---------|-----------|--------|---------|---------|
| 1. READ | read-requirements | 多态输入→结构化需求 + **需求理解确认**（铁律#24）+ **🆕 v2.12 完成定义闸门(铁律#30)+需求可追溯矩阵(铁律#31)+参考基线闸门(铁律#33)** | 五要素需求说明 + 六维完成定义 + 五列追溯矩阵 + 参考基线对比表 | 用户指令极其精确，无歧义 | Haiku / 快速 |
| 2. CODE | code-implement | 克制编码（注释可配置/复用/反炫技）+ **回退入口**（REVIEW/EXAMINE/SELFCHECK可回退到此） | 变更记录 | 纯理解/纯审查 | Sonnet / 标准 |
| 3. REVIEW | code-review | 七维度静态自审查 + 反合理化防御 + **质量门禁**（不通过不可进入EXAMINE，铁律#23） | 审查报告 | 纯配置/纯文案/纯样式变更 | Opus / 深度 |
| 4. EXAMINE | examine-quality | 找测试→跑→补→修→重跑至全绿 + **交互式应用真实体验验证**（铁律#26）+ **🆕 v2.12 测试充分性闸门(铁律#34)+环境保真闸门(铁律#32)** | 质量报告+测试凭据+五维覆盖评估+回归测试+环境矩阵+冒烟测试 | 纯理解/纯文档，或项目无测试框架 | Sonnet / 标准 |
| 5. GIT | git-split-commit | 按维度拆分提交 + Conventional Commits + Git链路追踪数据（禁止自动执行） | 拆分方案 + git命令脚本 + 链路追踪数据 | 改动≤2文件且同维度 | Haiku / 快速 |
| 6. GRAPH | graph-fullchain | Mermaid可视化（lark_doc后端: 飞书画板集成） | Mermaid代码+对照表 | 改动仅1文件且逻辑简单 | Haiku / 快速 |
| 7. SUM | sum-session | 按 report_depth 输出六要素 + MCR+质量闸门 + Anti-Fluff Gate水文检测 + 同行审查就绪六问 + 质量评分 + **文档拓扑闸门(7项检查,铁律#28)** + **文档保真闸门(7项检查,铁律#29)** + **🆕 v2.12 历史版本覆盖(铁律#36)+来源出处闸门(铁律#37)+证据账本(铁律#38)+交付验证清单(铁律#30补充)** + 写后Fetch验证 + **禁止凭记忆写报告**（必须基于step_output拼装）+ **v2.10双模文档结构(审计日志/持续维护)+结构化合并** + **v2.11写入模式三级分类(Quick Fix/Normal/Full Archive)+文档作用域(round_report/engineering_active)+禁止无基准覆写** | 总结文档 + 后端产物 + 版本覆盖矩阵 + 来源标注 + 证据账本 + 交付验证清单 | 极微改动且用户不需要记录（brief模式） | Sonnet / 标准 |
| 8. TALK | talk-retro | 5-Whys+Trade-offs+规范 | 复盘报告 | 功能开发/纯理解/微调 | Opus / 深度 |
| 9. SELFCHECK | self-check | 🆕 CTO拷打层：四阶段深度盘问+汇报就绪检查（不可跳过） | 拷打记录+认知缺口 | 永不跳过——仅模式不同（完整/标准/快速/轻量） | Opus / 深度 |
| 10. ASK | ask-change-questions | 六维度人工确认 | 确认单 | 纯理解/纯审查（无上线产物） | Sonnet / 标准 |

> **模型分层说明**：`快速`=低成本模型即可胜任（分类、格式转换、模板填充）；`标准`=通用模型（代码生成、文档撰写）；`深度`=需最强推理能力（多维度交叉审查、系统性根因追溯）。Agent 在调用时优先使用匹配的模型 tier 以优化成本和质量。平台不支持多模型时全部使用当前模型，此列仅作建议。
>
> **注释语言配置**：CODE 步骤的注释语言默认为中文。团队可在 `references/team-policy.md` 中设置 `comment_language: english` 切换为英文，或 `auto` 自动跟随项目。

**每步执行时**：Agent 加载对应子技能的 SKILL.md，按其 Checklist 和 SOP 执行。每步结束按 `references/data-contract.md` 输出结构化数据，供后续步骤引用。

**依赖 DAG 与并行**：步骤间依赖为 `READ→CODE→REVIEW→EXAMINE→GIT→(GRAPH∥SUM)→TALK→SELFCHECK→ASK`。GRAPH 和 SUM 都可并行（都只依赖 GIT，无相互依赖），其余步骤严格串行。SELFCHECK 依赖 SUM（和 TALK，如执行）的产出，是 ASK 的前置——开发者必须通过 CTO 拷打才能进入人工确认。条件分支（如安全审查发现问题 → 自动追加安全测试）和完整 DAG 图见 `references/orchestration-engine.md`。高风险任务的 REVIEW 可启用并行审查（3 个子 Agent 分别审查安全/性能/兼容性）。

**每步产出强制自检**：每步结束时，Agent 必须对照 `references/data-contract.md` 检查所有 `[必填]` 字段是否已产出。`null`/`""`/`[]`/`"无"`/`"N/A"` 均视为未产出，必须补全后再进入下一步。跳过步骤也需自检并显式标注 `[skip]`。详细自检清单和必填字段速查表见 `references/orchestration-engine.md`。

**结构化日志**：每步完成向 `.claude/easywork/workflow.log.jsonl` 追加一行 JSON（字段：session/step/status/skipped/tokens_est/duration_s/ts）。分析指南见 `references/log-analysis-guide.md`，自动化分析脚本见 `.claude/easywork/analyze-logs.sh`。

**Gotchas 追加自检**：Agent 在 SUM 步骤自检时，检查是否满足 4 种追加触发条件。若满足，生成 Gotchas 候选条目展示给用户，**用户确认后才写入** `references/gotchas.md`。未确认的候选保留在 SUM 产出中。详见 `references/security-policy.md` §6。

**产物后端调度（🆕 v2.5）**：SUM 步骤结束时，Agent 调用当前激活的后端适配器（`backends/{backend}/SKILL.md`）的 `write_final_report` 操作，将全部 10 步产出写入产物容器。后端选择在任务分类后确定（见 §4 产物后端选择），SUM 只负责调度不负责选择。详见 `references/output-backends.md`。

**Git 链路追踪（🆕 v2.5）**：GIT 步骤产出额外的 `git_tracking` 数据（含 business_context / developer_checklist / risk_introduced / verification_evidence）。当后端为 lark_doc 时，此数据写入飞书 Git 链路追踪文档，形成 任务→提交分组→Check→hash→测试 的完整链路。详见 `../git-split-commit/assets/git-chain-tracking-template.md`。

**SelfCheck CTO 拷打（🆕 v2.6）**：SELFCHECK 步骤（第 9 步）在任何任务类型中都不可跳过。Agent 切换为 CTO 角色，对开发者进行四阶段深度盘问（业务背景→问题发现→解决方案→实现过程）+ 汇报就绪检查。拷打模式由任务类型决定（完整/标准/快速/轻量），但不允许整体跳过。产出 `selfcheck_output` 含认知缺口和汇报就绪评估。详见 `../self-check/SKILL.md`。

**SUM 深度感知（🆕 v2.7）**：SUM 步骤根据 report_depth 决定产出粒度：
- brief：仅六要素概要（每要素1-2句），跳过详细排查路径和量化对比。最终报告约 1-2 页
- standard：六要素完整版（=当前 v2.6 行为），含排查路径、量化对比、取舍分析。最终报告约 3-5 页
- detailed：六要素完整版 + 逐步骤 MCR 自检 + 流式增量保障 + 代码摘录含路径行号。最终报告约 6-10 页

**内容丰满度自检闸门（🆕 v2.7）**：SUM 在调用 write_final_report 之前，必须逐步骤对照 MCR 表（见下方）检查。detailed→HARD GATE（不通过=拒绝写入→回退补充→重新自检，最多2轮），standard→SOFT GATE（警告但允许通过），brief→跳过。详见 `sum-session/SKILL.md`。

**流式增量写入保障（🆕 v2.7）**：见铁律 #20。详细策略见 `sum-session/SKILL.md` §流式增量写入保障。

### 最小内容要求（MCR）— detailed 模式强制执行（🆕 v2.7）

以下表格定义 detailed 模式下每个步骤的**最小必产出内容**。
MCR 是最小值不是最大值——步骤可以产出更多。
standard 模式下 MCR 作为建议参考（SOFT GATE：警告但不阻断）。
brief 模式下 MCR 不适用。

| 步骤 | MCR-1 | MCR-2 | MCR-3 | MCR-4 | MCR-5 |
|------|-------|-------|-------|-------|-------|
| **READ** | 需求背景(业务上下文，非纯技术描述) | 用户目标(谁在什么场景下要做什么) | MVP边界(本次做/不做清单) | 验收标准(≥2条，可测试) | 不做事项(≥1条，非"不涉及其他模块"占位) |
| **CODE** | 文件变更表(路径+变更类型+行数+原因) | 核心设计说明(为什么这样设计) | 关键函数职责(≥2个函数/模块的职责描述) | 重要边界处理(≥1个边界场景及处理方式) | ≥1段关键代码摘录(≤30行，含文件路径+行号) |
| **REVIEW** | 七维度检查表(每维度≥2条具体检查点，非"没有发现问题") | 阻断问题+修复记录(如有；无则**说明为什么没有**——非空泛的"代码质量好") | 每个发现的 issue 含具体代码位置(文件+行号) | — | — |
| **EXAMINE** | 测试命令(完整可复制执行) | 测试覆盖矩阵(测试用例→覆盖场景→结果) | 关键输出摘录(作为测试凭据，非"全部通过") | 未覆盖风险(≥1个已知未覆盖场景及原因) | — |
| **GIT** | 拆分方案(维度+文件+说明) | 每单元含 business_context(非泛泛的"修复bug") | 每单元含 risk_introduced(具体场景+影响+缓解) | 每单元含 verification_evidence | 每单元含 developer_checklist(5项齐全) |
| **SELFCHECK** | 完整CTO问答(不可用摘要表替代——每阶段有具体问答内容) | 认知缺口(≥1个 gaps_identified 或**说明为什么没有**——非空占位) | 每个 gap 有对应后续补救动作(谁/什么时候/怎么做) | — | — |

**🆕 v2.8 交互式应用 EXAMINE 补充 MCR**：
当任务涉及 CLI / TUI / GUI / Web 前端 / 游戏 / 交互式输入输出时，EXAMINE 在 detailed 模式下**额外**必须覆盖以下内容。standard 模式下作为强烈建议（SOFT GATE），brief 模式跳过。

| 验证维度 | 具体要求 | 不合格表现 |
|---------|---------|-----------|
| **首屏稳定性** | 启动后首屏渲染完整，无闪烁、无白屏、无未加载占位符。至少验证 3 次冷启动 | 首屏闪烁、空白 >1s、资源加载失败不提示 |
| **无输入时行为** | 无用户输入时界面安静/符合预期——无异常日志刷屏、无 CPU 空转、无意外网络请求 | 空闲时 CPU >10%、日志无意义刷屏、静默网络轮询 |
| **输入反馈** | 每次用户操作后 200ms 内有可见反馈（按钮态/加载态/结果展示）。无"点了没反应"的 dead zone | 点击无响应、长时间无反馈(>5s无进度提示)、操作无结果提示 |
| **退出路径** | 所有交互路径有可靠退出方式（Esc/关闭按钮/Ctrl+C/`:q`/返回键）。无"卡在某个界面出不来"的死循环 | 退出后进程残留、强制退出数据丢失、退出方式不直观 |
| **输出/渲染频率** | 如有自动刷新，频率合理(≤10Hz)，不会造成刷屏或日志爆炸。输出量可控(如分页/限流) | 刷新>30Hz导致肉眼不可读、日志无节制增长(>100行/s) |
| **环境一致性** | 在主要运行环境(Windows/Mac/Linux/主流浏览器)中行为一致。如不一致→记录已知差异 | Windows 正常 Mac 崩溃、Chrome 正常 Firefox 布局错乱 |
| **CLI/TUI stdin 边界** | 测试 stdin 关闭、空输入(直接回车)、非法输入(特殊字符/超长/emoji/二进制)、退出指令(Ctrl+C/Ctrl+D/`:q`/exit) | 空输入崩溃、Ctrl+C 无法退出、特殊字符导致乱码或 crash |
| **ANSI 控制字符** | 如使用 ANSI 清屏/着色/光标控制，必须在报告中说明 IDE 控制台兼容性风险（VS Code/WebStorm/终端差异） | 未说明兼容风险、WebStorm 控制台乱码、重定向输出含控制字符 |
| **自动刷新验证** | 如有自动刷新/实时更新/TUI 重绘，验证刷新频率不会造成刷屏、日志爆炸、或 CPU 持续高负载 | 刷新频率未控制、全量重绘导致性能问题 |

> 以上补充 MCR 的触发条件：任务分类时 Agent 判断改动涉及上述交互式应用类型。纯后端 API/库/脚本/配置变更 → 标注 `[交互式应用 EXAMINE 补充: N/A]`。

**代码摘录格式要求（🆕 v2.7）**：
所有代码摘录必须标注文件路径和行号，格式：
`// auth.service.ts:88-95 — token 过期判断`
禁止只贴代码不标位置。确保另一个工程师能根据报告定位到源码（"同行审查就绪"标准）。

### 最小内容质量要求（MCR+）— detailed 模式强制执行（🆕 v2.9）

> MCR（v2.7）定义"至少有什么"——数量要求。MCR+（v2.9）定义"质量有多好"——内容深度要求。
> MCR+ 不替换 MCR——MCR 是入场条件（检查有无），MCR+ 是质量标准（检查好坏）。
> 每个步骤的表包含：MCR+ 要求（质量维度）、反例（禁止的"水文"写法）、合格例（满足标准的最小示例）。

**ETR 标准（Evidence / Thinking / Risk）— 贯穿所有步骤**：
任何关键结论必须满足三元组，缺一不可：
- **E — Evidence（证据）**：有什么证据支撑这个结论？（测试输出/日志/代码位置/命令输出/截图/数据对比）
- **T — Thinking（推理）**：为什么这样判断？（推理链条，非跳跃式结论。不是"结果是什么"而是"为什么是这个结果"）
- **R — Risk（风险）**：还有什么风险或限制？（边界/未覆盖/副作用/假设前提/已知何时会失效）
任何没有 E/T/R 三者齐全的结论，视为不合格。此标准贯穿以下所有步骤的 MCR+。

#### READ MCR+（需求理解质量）

| # | MCR+ 要求 | ❌ 反例（禁止） | ✅ 合格例 |
|---|----------|--------------|---------|
| 1 | **需求来源**：明确谁/什么触发了这个需求（用户反馈/报错日志/线上指标/测试失败/产品文档/上级要求） | "用户希望修复问题" — 无来源 | "6月15日线上 APM 告警：login API P99 >2s，客服收到约 200 条登录慢的投诉" |
| 2 | **用户真实目标**：用户想完成什么业务目标（非"代码要改什么"） | "需要修改 auth.go 的 Login 函数" — 混淆了目标与实现 | "用户在登录时等待不超过 500ms，高峰期也能正常登录" |
| 3 | **当前问题影响**：不解决会导致什么实际后果（量化，非"影响用户体验"） | "影响用户体验" — 万能空话 | "日均 3000 次登录中约 40% 超 3s，预估每周流失约 200 个因等待放弃的用户" |
| 4 | **验收标准可验证**：≥2条，必须能用命令/测试/截图/人工步骤验证 | "确保功能正常" — 不可验证 | "1) `curl -X POST /api/auth/login -d '{"user":"test","pass":"x"}'` 返回 200 且耗时<500ms。2) 运行 `go test -run TestLogin ./auth/...` 全部通过" |
| 5 | **不做事项+原因**：≥1条，每项说明为什么不做（非占位符） | "不涉及其他模块" — 占位式不做事项 | "不做密码哈希算法替换（从 bcrypt 换 argon2）：虽然理论上更安全，但需要所有用户重置密码，当前风险等级不匹配这个代价" |
| — | **整体禁止** | 只复述用户原话、没有自己的理解和结构化 | — |

#### CODE MCR+（代码实现质量）

| # | MCR+ 要求 | ❌ 反例（禁止） | ✅ 合格例 |
|---|----------|--------------|---------|
| 1 | **变更位置**：每个变更的完整路径+函数名+行号范围 | "修改了 main.go" — 无函数+行号 | "auth/auth.go:192-198 — Login() 函数" |
| 2 | **变更原因**：为什么必须在这里改，为什么不是在别处改 | "按需求修改" — 没有独立判断 | "token 过期判断在整条认证链路中有 3 处——网关/auth/客户端。选择改 auth 层而非网关层：auth 是 token 验证的单一数据源，网关改需要同步 3 个微服务" |
| 3 | **关键逻辑**：用 3-6 句话解释核心实现逻辑（让另一个工程师不用读源码就懂） | "修改了 token 验证逻辑，增加了重试" — 没说怎么改的 | "原来 Scanner 读到 EOF 时直接 close(ch)。改为：读到 EOF 时发送 io.EOF 到 channel，由 mainLoop() 统一关闭——避免 IDE 非交互模式下读到 closed channel 后退出。mainLoop 在收到 io.EOF 后等待 200ms 确保其他 goroutine 完成写入后再 close" |
| 4 | **替代方案**：≥1个未被采用的方案+不被采用的具体技术理由 | "采用方案 A 因为最简单" — "简单"不是技术理由 | "未采用方案 B（加缓存层缓存 token）：虽然可降低首次验证耗时，但引入缓存一致性风险（token 黑名单失效延迟），且运维复杂度增加。未采用方案 C（换 SHA-256）：OWASP 明确推荐 bcrypt/argon2 用于密码存储" |
| 5 | **代码摘录**：≥1段，≤30行，含路径+行号标注 | 只贴代码不标位置 / 贴整个文件 | "auth/auth.go:88-95 — token 过期判断 `if time.Now().After(expiresAt) { ... }`" |

#### REVIEW MCR+（审查质量）

| # | MCR+ 要求 | ❌ 反例（禁止） | ✅ 合格例 |
|---|----------|--------------|---------|
| 1 | **检查点绑定位置**：每维度≥2条具体检查点，每条绑定代码位置或行为路径 | "正确性：通过，逻辑正常" — 无位置、无推理 | "正确性 — auth.go:192-198：确认 Scanner.EOF 时不再直接 close(ch)，改为发送 io.EOF → mainLoop 统一关闭。验证了对 io.EOF/context.Canceled/os.Signal 三种退出路径的响应" |
| 2 | **"通过"必须有依据**：写明"看了哪里""怎么判断的"（非"未发现问题"） | "安全性：通过，未发现安全漏洞" — 没有说看了什么 | "安全性 — auth.go:88：确认 bcrypt.CompareHashAndPassword 使用了恒定时间比较（无 timing attack 风险）。auth.go:210：确认错误信息不泄露用户存在性（"用户名或密码错误"而非"密码错误"）。数据库查询使用参数化（`db.Query("SELECT ... WHERE user=?", user)`）— 无 SQL 注入风险" |
| 3 | **发现问题必须写全**：位置+触发条件+影响+修复方式+回归验证 | "发现一处空指针风险，已修复" — 无位置、无触发条件 | "auth.go:45 — json.Unmarshal 返回值 err 未检查 → 传入非法 JSON 时 user 为 nil → auth.go:52 user.Name 空指针 panic。触发：`curl -d '{bad json}' /api/login`。修复：增加 err 检查+400 响应。回归：`TestLoginBadJSON` — 输入 `{bad json}` → 期望 400 → PASS" |

#### EXAMINE MCR+（测试质量）

| # | MCR+ 要求 | ❌ 反例（禁止） | ✅ 合格例 |
|---|----------|--------------|---------|
| 1 | **测试命令+目的**：完整可复制命令+这个命令为什么能覆盖本次改动 | "go test 通过" — 无命令、无目的 | "`go test -v -run 'TestAuth|TestToken' ./auth/...` — 因为本次改动在 auth 包的 token 验证路径，只跑 auth 相关测试而非全量（全量 2000+ 测试耗时 12min）" |
| 2 | **失败前/修复后对比**：如修 Bug，必须展示修复前的失败表现和修复后的通过表现 | "问题已修复，测试通过" — 没有对比 | "修复前：`TestScannerEOF` → FAIL — `panic: send on closed channel`。修复后：`TestScannerEOF` → PASS — 程序 200ms 内退出，退出码 0" |
| 3 | **测试覆盖矩阵**：测试用例→覆盖场景→结果，标注哪些是本次新增 | 只有通过数没有矩阵 | "TestLoginHappy — 正常登录 — passed / TestLoginExpired — token 过期重试（🆕新增）— passed / TestLoginWeakNet — 弱网降级（🆕新增）— passed / TestLoginBadJSON — 非法 JSON（🆕新增）— passed" |
| 4 | **未覆盖风险**：≥1个已知未覆盖场景+原因+风险+缓解 | "后续持续优化" — 万能结尾 | "未覆盖：1) 极弱网（<100KB/s）token 刷新重试 3 次可能不够——未模拟此环境。缓解：重试失败降级为匿名访问，用户可手动登录。2) 并发 token 刷新竞态——已知理论风险但 QPS<100 时概率极低，监控已配置" |

#### SELFCHECK MCR+（拷打质量）

| # | MCR+ 要求 | ❌ 反例（禁止） | ✅ 合格例 |
|---|----------|--------------|---------|
| 1 | **≥8 个 CTO 追问**（含跟进追问），不可用摘要表替代 | 4 个泛泛的问题 + 摘要表 | "CTO: 为什么在这里改？→ 答：因为... → CTO追问：网关层也有 token 逻辑，为什么不在那里改？→ 答：因为... → CTO再追问：如果将来网关层也需要这个修复，你的方案能扩展吗？→ 答：..." |
| 2 | **≥2 个反事实问题**："如果不用这个方案会怎么样？""如果问题再次发生怎么发现？" | 无反事实问题 — CTO 没压力测试方案边界 | "CTO: 如果不用 bcrypt factor=10 而是换 argon2，会怎样？→ 答：... CTO: 如果线上 token 刷新仍然慢（虽然我们预期不慢），你怎么第一时间知道？→ 答：APM 告警+P99 监控..." |
| 3 | **≥2 个替代方案质询**：为什么不用 X？为什么不用 Y？— 要求具体技术理由 | 无替代方案质询 — CTO 接受了"这个方案最好" | "CTO: 为什么不用 SHA-256 加盐？→ 答：OWASP 明确不推荐通用哈希做密码存储... CTO: 为什么不在网关层加缓存？→ 答：缓存一致性风险+运维复杂度..." |
| 4 | **≥1 个为什么之前没发现的追问** + **≥1 个如何防止复发的追问** | "之前没想到""后续注意" — 没有系统化反思 | "CTO: 这个 cost factor=14 的问题为什么之前没暴露？→ 答：之前用户量<1000 时无感知，6月用户量破万后 P99 才突破告警阈。CTO: 如何防止下次再有类似的性能退化？→ 答：在 CI 中加入性能基准测试，P99>500ms 时阻断合并" |
| 5 | **≥1 个认知缺口+补救动作**（谁/什么时候/怎么做） | gaps_identified 为空且未说明原因 | "认知缺口：弱网（<100KB/s）环境下的 token 刷新行为未实测。补救：小王在 v1.2 Sprint 中用 Charles Proxy 限速模拟，验证重试+降级逻辑" |
| — | **整体禁止** | "因为这样更合理""改动小所以没问题""测试通过所以没问题""后续可以优化" — 都是水文 | — |

### ETR 标准 — 贯穿所有步骤（🆕 v2.9）

> 以下标准不是某个步骤的 MCR+，而是**所有步骤产出都必须满足的质量底线**。

任何关键结论必须包含 E/T/R 三元组，缺一不可：

- **E — Evidence（证据）**：有什么证据？（测试输出片段/命令输出/日志/代码位置行号/数据对比表/截图描述）
- **T — Thinking（推理）**：为什么这样判断？（推理链条——不是"结果是什么"而是"为什么是这个结果"。从现象→排查→排除→定位→论证的逻辑链）
- **R — Risk（风险）**：还有什么风险或限制？（未覆盖场景/副作用/假设前提/已知何时会失效/依赖条件）

**不合格示例**（只有结论，无 E/T/R）：
> "测试通过，功能正常。"

**合格示例**（ETR 齐全）：
> **[E]** 运行 `go test -v -run TestAuth ./auth/...` — 12 passed / 0 failed / 0 skipped。关键输出：`TestLoginExpired: PASS (0.32s) — token 过期后重试 3 次，第 2 次成功刷新`，`TestScannerEOF: PASS (0.15s) — 收到 EOF 后 200ms 内退出，退出码 0`。
> **[T]** 这 12 个测试覆盖了正常登录、token 过期重试、EOF 退出、弱网降级、非法输入 5 类场景——是本次改动涉及的全部代码路径。新增的 TestLoginExpired 和 TestScannerEOF 专门验证本次修复的两个核心问题（token 刷新死循环 + EOF 后 panic）。
> **[R]** 未覆盖：极弱网（<100KB/s）下重试 3 次是否足够——未模拟此环境。缓解：重试失败降级为匿名访问（非 401 踢出），用户可手动登录。并发 token 刷新竞态——已知理论风险但 QPS<100 时概率极低，监控已配置。

**Agent 自检**：在每步产出后，逐条扫描步骤中的关键结论，确认每个结论都有 E/T/R。任何一个缺少 → 回退补充。

**Skill 自测**：修改任何 EasyWork 文件后，用 `references/self-test-prompts.md` 中的测试场景验证工作流是否正确。覆盖全部 7 种任务类型 + 上下文管理 + 异常处理 + 回退循环 + 干跑预览 + v2.3 新特性（可访问性/供应链/并行审查/Conventional Commits/Gotchas 追加/自定义步骤）。

**自定义步骤注入**：团队可在 `.claude/skills/easywork/custom/` 目录下放置自定义技能（如安全扫描、i18n 检查）。编排中枢在任务分类后自动发现并注入到流程中。详见 `references/orchestration-engine.md` §自定义步骤注入。

## 7. 进度卡模板

Agent 在分类确认后，输出裁剪后的进度卡：

```
EasyWork 工作流启动 — 任务：{类型} — 风险：{等级} — 深度：{brief/standard/detailed} — 报告类型：{executive_summary/engineering_record}

[ ] 1. READ     — 理解需求 → 产出需求理解确认
[ ] 2. CODE     — 代码实现
[ ] 3. REVIEW   — 七维度审查 + 质量门禁（不通过→回退CODE）
[skip] 4. EXAMINE — {跳过理由}
[+] 🔒 SECURITY_SCAN — SAST 安全扫描（团队自定义）
...
[ ] 9. SELFCHECK — CTO拷打（{模式}模式）
[ ] 10. ASK     — 人工确认

⚠️ 深度升级：{如触发升级，标注原深度→新深度及原因}
🔄 回退记录：{如发生回退，标注 回退路径 + 轮次 + 原因}
```

每完成一步更新状态。`[skip]` 步骤自动视为已完成。`[+]` 前缀表示团队自定义步骤。

## 8. 多轮对话断点续传

当用户说"先做到 XX 步，明天继续"时，Agent 必须在停止前输出状态快照：

```json
{
  "easywork_version": "2.12",
  "task_type": "Bug修复",
  "risk_level": "medium",
  "report_depth": "detailed",
  "report_type": "engineering_record",
  "document_scope": "engineering_active",
  "write_mode": "normal",
  "depth_escalated": false,
  "depth_escalation_reason": null,
  "mcr_gate_passed": false,
  "risk_classification": { "level": "L2", "level_name": "正常功能", "source": "auto_detected", "applicable_gates": ["delivery_definition", "traceability_matrix", "test_adequacy", "evidence_ledger", "historical_version_coverage", "source_provenance"] },
  "state_file_path": ".claude/easywork/state-v2.12.json",
  "delivery_definition_hash": null,
  "repeated_failure_count": 0,
  "evidence_ledger_summary": { "total_evidence": 0, "minimum_required": 3, "remaining_needed": 3 },
  "current_step": 3,
  "completed_steps": ["READ", "CODE"],
  "skipped_steps": [],
  "rollback_history": [
    { "from_step": "REVIEW", "to_step": "CODE", "round": 1, "reason": "发现阻断性安全问题", "issues_found": ["..."], "fixes_applied": ["..."] }
  ],
  "read_confirmation": { "confirmed_by_user": true, "clarifications_asked": 2, "understanding_summary": "..." },
  "is_interactive_ui_task": false,
  "doc_iteration": { "is_update": false, "previous_doc_path": null, "version_increment": null },
  "anti_fluff_passed": false,
  "peer_review_ready": false,
  "quality_score": { "total": 0, "dimensions": {}, "passed": false },
  "topology_gate_result": { "mode": "continuous_maintenance", "checks": [], "overall_pass": false, "repairs_applied": [] },
  "preservation_gate_result": { "passed": false, "existing_fetched": false, "content_fidelity": {}, "checks": [], "overall_pass": false },
  "content_fidelity_snapshot": { "before_write": {}, "after_write": {}, "degraded": false },
  "document_mode": "continuous_maintenance",
  "structured_merge_plan": { "existing_nodes": [], "new_content_distribution": {}, "version_label": "v1", "stale_markers": [] },
  "fetch_verified": false,
  "etr_compliant": false,
  "anti_memory_rule": "SUM必须基于step_output拼装，不得凭上下文自由发挥",
  "step_outputs": {
    "read_output": { "goal": "...", "scope": {...}, "constraints": [...], "acceptance_criteria": [...], "non_goals": [...] },
    "code_output": { "files_changed": [...], "impact_assessment": "...", "implementation_notes": "..." },
    "sum_output": { "background": "...", "discovery": "...", "problem": "...", "solution": "...", "outcome": {...}, "future": [...] },
    "talk_output": { "five_whys": [...], "root_cause": "...", "trade_offs": [...], "engineering_rules": [...] },
    "selfcheck_output": { "mode": "full", "business_understanding": {...}, "problem_discovery": {...}, "solution_rationale": {...}, "implementation_reflection": {...}, "readiness_assessment": {...} }
  },
  "custom_steps_completed": [],
  "timestamp": "2026-06-20T15:30:00+08:00"
}
```

下次对话开始时，用户将此 JSON 粘贴给 Agent，Agent 直接恢复到 `current_step` 的下一步（即步骤 3 REVIEW），跳过已完成的步骤。

> **注意**：此为聊天内快照（轻量、即时）。完整的磁盘持久化由 🆕 v2.12 状态文件（铁律#40）提供——`.claude/easywork/state-v{N}.json` 自动写入，跨 `/clear` 存活。

## 9. 术语约定

全项目统一使用以下中文术语（首次出现时可括号标注英文）：

| 中文术语 | 英文（首次出现时标注） | 说明 |
|---------|---------------------|------|
| 异常处理流程 | SOP | 非正常情况的标准处理步骤 |
| 人工确认 | HITL | 需要人类决策的环节 |
| 检查清单 | Checklist | 逐项确认的打卡列表 |
| 取舍分析 | Trade-off | 方案利弊和代价评估 |
| 编排中枢 | Orchestrator | 流程调度和步骤裁剪 |
| 阻断性问题 | Blocker | 必须修复才能继续的问题 |
| 挂起 | Suspend | 暂停执行等待用户指示 |
| 裁剪 | Trim/Skip | 跳过不需要的步骤 |
| 陷阱知识 | Gotchas | 项目特定的反直觉踩坑记录 |
| 团队策略覆盖 | Team Policy Overlay | 团队在不修改核心文件前提下追加的规则 |

## 10. 反模式

- ❌ 所有任务无脑走 10 步——简单任务变得冗长，用户会放弃使用
- ❌ 看到代码改动就跳过测试——Bug 修复没有测试等于埋新雷
- ❌ 用户说"不用做了"还坚持——用户指令优先级永远最高
- ❌ 跳过步骤不留 `[skip]` 标记——后续无法追溯
- ❌ 分类结果不展示给用户确认直接开始——用户不了解裁剪逻辑
- ❌ REVIEW→CODE 回退循环超过 3 次还继续——说明需求或设计有更深层问题，应挂起
- ❌ 自我审查时说"改动太小不可能有问题"——见 code-review 的反合理化防御表
- ❌ 踩过的坑不追加到 gotchas.md——同样的错误会在下一个 session 重演
- ❌ 未经用户确认就执行 git commit/push——用户可能正在等CI结果或想先审查
- ❌ HTML报告中直接粘贴完整源码——包含Token/密钥/内部URL/手机号等敏感信息
- ❌ 自定义步骤不列出清单直接执行——用户不知道会多出什么操作
- ❌ 供应链检查把私有包名发到Google搜——泄露内部技术栈给外部搜索引擎
- ❌ 写文件写到项目目录外——`/tmp/report.html` 或 `~/config.json` 都是越界
- ❌ 用户指定了飞书但 Agent 静默降级到 HTML——不告知用户就切换后端
- ❌ Agent 自行决定产物后端——用户没说"输出到飞书"就不该用飞书后端
- ❌ GIT 拆分只说"修改了某文件"不说业务原因——后人不知道这些改动在业务上达成什么
- ❌ 报告用反引号包裹每个文件名——像自动生成的 API 文档，不像人工复盘
- ❌ 跳过 SelfCheck CTO 拷打——AI 不拷打你，同事和领导就要拷打你。任何任务类型都必须执行
- ❌ SelfCheck 放水——接受"大概""应该""差不多"回答，不追问具体细节。这不是拷打，是演戏
- ❌ SelfCheck 用模板化问题——每次拷打都问一模一样的问题，不针对本次具体改动
- ❌ 最后一次性写"浓缩版"替代逐步骤详情（🆕 v2.7）——每个步骤的完整产出必须保留在最终报告中。非流式后端必须在 write_final_report 中恢复所有步骤完整结构化产出，不可用"详见上文"一笔带过
- ❌ detailed 模式产出 summary-only 报告（🆕 v2.7）——detailed 必须包含 MCR 表要求的全部内容（代码摘录含路径行号、完整CTO问答、每维度≥2条检查点等），不可降级为只有总结
- ❌ 功能开发/重构使用 executive_summary 未经警告（🆕 v2.7）——除非用户坚持且已收到强烈警告，否则默认使用 engineering_record
- ❌ 代码摘录不标文件路径和行号（🆕 v2.7）——"某处代码"等于没写。另一个工程师应该能根据报告定位到源码
- ❌ 发现安全问题但不升级深度（🆕 v2.7）——安全发现是硬触发条件，必须 standard→detailed 升级
- ❌ 跳过 MCR 自检闸门直接写入（🆕 v2.7）——无论后端，detailed 模式写入前必须逐步骤检查产出完整性。门禁不通过=拒绝写入
- ❌ 流式后端写入成功后最终报告省略步骤详情（🆕 v2.7）——流式追加和最终报告各司其职。最终报告必须可独立阅读，不可假设"流式已写过"
- ❌ REVIEW 发现问题后直接进入 EXAMINE 而不回退 CODE（🆕 v2.8）——带着已知阻断问题继续前进等于埋雷。REVIEW 不通过 → 必须回退 CODE 修复 → 重新 REVIEW 通过才能放行
- ❌ READ 不确认理解就直接开始编码（🆕 v2.8）——用户说"加个功能"就假设实现方式开始写，不问、不确认、不澄清。理解偏差被放大 9 倍后的代价远超一次确认对话
- ❌ 需求变更时新建文档或新增顶层标题（🆕 v2.8，升级至 v2.10）——破坏了文档的连续性和可追溯性。Mode A（审计日志）：必须在原有排版下追加更新记录，标注版本号。Mode B（持续维护，默认）：必须在对应流程节点内追加 `### v{N}` 版本小节，不得尾部堆叠更新记录块
- ❌ 文档迭代时不检查过时信息（🆕 v2.8）——只追加新内容不标注旧内容已过时，后来者不知道哪段是有效的
- ❌ CLI/TUI 工具不测试 stdin 关闭和空输入（🆕 v2.8）——只测 Happy Path（正常输入→正常输出），不管 Ctrl+C 能不能退出、空输入会不会崩溃
- ❌ 交互式应用 EXAMINE 只跑单元测试不验证真实体验（🆕 v2.8）——首屏是否闪烁、按钮点了有没有反应、退出路径是否可靠——这些单元测试覆盖不了，必须手动验证或自动化 E2E
- ❌ ANSI 控制字符不说明兼容性风险（🆕 v2.8）——清屏/着色/光标控制在 IDE 控制台（VS Code/WebStorm）和标准终端行为不同，不说明就是给用户埋坑
- ❌ 报告全是标题+一句话结论，没有证据/推理/风险（🆕 v2.9）——"正确性：通过""测试：通过""后续优化"——这是流程打卡表，不是工程记录。每个关键结论必须有 ETR 三元组
- ❌ SUM 凭记忆写报告（🆕 v2.9）——最后凭上下文自由发挥生成六要素，各步骤详细产出被丢弃。必须基于 step_output 拼装报告，某步骤不满足 MCR+ 则回退补充
- ❌ 水文检测闸门被跳过（🆕 v2.9）——detailed 模式此为 HARD GATE。空泛结论/无证据通过/无位置描述/无取舍/无风险——命中任一即阻断写入
- ❌ SelfCheck 走过场放水（🆕 v2.9）——<8 问、无反事实、无替代方案质询、接受"因为这样更合理""改动小所以没问题"——这不是 CTO 拷打，是演戏
- ❌ 代码摘录不写"为什么在这里改而不是别处"（🆕 v2.9）——只写改了哪里不写选择理由，读者不知道为什么代码长这样
- ❌ 写后不 fetch 验证（🆕 v2.9）——Agent 以为写了很多，但文档转换后内容被截断/代码块格式错误/特殊字符乱码。detailed 模式必须 fetch 回读
- ❌ 质量评分放水（🆕 v2.9）——detailed engineering_record <80 分仍写入——闸门存在是为了保证质量底线，不是装饰
- ❌ Mode B 下追加 `## 📝 更新记录` 块（🆕 v2.10）——文档变流水账。应拆入对应流程节点下 `### v{N}`
- ❌ Mode B 下出现重复顶层流程节点（🆕 v2.10）——如两个 `## 1. READ`。拓扑闸门会阻断，必须合并
- ❌ 不 fetch 现有文档直接覆盖写入（🆕 v2.10）——破坏已有结构和版本历史。必须先 fetch→解析拓扑→structured merge
- ❌ 新版本内容全堆在"更新记录"里，节点内无新版本子节（🆕 v2.10）——典型流水账，后人需读全部更新记录才能知道当前有效内容
- ❌ 跳过 Document Topology Gate（🆕 v2.10）——detailed 模式此为 HARD GATE（铁律#28）。7 项拓扑检查必须通过
- ❌ 未 fetch 现有文档直接 overwrite（🆕 v2.11）——无基准覆写，丢失全部历史内容。必须先读后写（铁律#29 C5）
- ❌ Quick Fix 时 overwrite 整篇文档（🆕 v2.11）——小修小补只能追加版本记录，禁止覆写已有内容（铁律#29 R3）
- ❌ round_report 覆盖 engineering_active（🆕 v2.11）——两种作用域物理隔离。当轮摘要不得替换正式工程文档（铁律#29 R4）
- ❌ 已有文档使用 overwrite 而非 structured merge（🆕 v2.11）——默认 Normal（局部更新），非 Full Archive（铁律#29 R1）
- ❌ 跳过 Document Preservation Gate（🆕 v2.11）——detailed 模式此为 HARD GATE（铁律#29）。7 项内容保真检查必须通过
