# EasyWork 快速参考卡片

> 30 秒看懂怎么用。详细内容见各技能 SKILL.md 和 `walkthrough-example.md`。

## 触发方式

> **🆕 v2.4**：EasyWork 仅在用户**明确说"用 EasyWork"**后才启用。普通开发任务不自动套用。

| 你说的话 | Agent 做什么 |
|---------|-------------|
| "用 EasyWork 修一下 XX bug" / "走 EasyWork 流程实现 XX 功能" | → 全链路（分类 → 裁剪 → 执行） |
| "用 EasyWork 帮我看下这段代码" | → 纯理解（只走 READ+GRAPH+SUM） |
| "用 EasyWork review 这段代码" | → 纯审查（只走 READ+REVIEW） |
| "帮我修一下 XX bug" / "实现 XX 功能"（没说"用 EasyWork"） | → **普通模式**，不套用 EasyWork 流程 |
| **🆕 v2.12+ 单步调用**（零散需求，只需一个节点） | |
| "CTO 拷打 / 拷打我自己" | → 🥊 仅 SELFCHECK（其余全跳，跳过全部闸门） |
| "检查清单 / 就绪检查 / 核对清单 / 预检 / 交付出清" | → ✅ 仅 CHECKLIST（其余全跳，跳过全部闸门） |
| "帮我复盘 / 5-whys / 根因分析" | → 🧠 仅 TALK（其余全跳，跳过全部闸门） |
| "画架构图 / 可视化 / mermaid" | → 📊 仅 GRAPH（其余全跳，跳过全部闸门） |
| "只理解需求 / 只读代码" | → 👁️ 仅 READ（其余全跳，跳过全部闸门） |
| "只审查 / 纯 review 一下" | → 🔍 仅 REVIEW（其余全跳，跳过全部闸门） |
| "只写总结 / 帮我总结 / 汇总一下" | → 📋 仅 SUM（其余全跳，跳过全部闸门） |
| "读论文 / 看论文 / paper / 论文阅读" | → 📖 仅 READ-PAPER（其余全跳，跳过全部闸门） |
| "读项目 / 看项目 / 理解项目 / 接手项目" | → 📐 仅 READ-PROJECT（其余全跳，跳过全部闸门） |
| "追踪代码 / trace / 调用链 / 代码追踪" | → 🔬 仅 TRACE-CODE（其余全跳，跳过全部闸门） |
| "技术保鲜 / tech radar / 快速扫一下（面）/ 全面深扫（体）" | → 🛰️ 仅 TECH-RADAR（面/体模式，其余全跳，跳过全部闸门） |
| "深扫 / 聚焦 + 具体技术名（如 '深扫 MCP 协议'）" | → 🛰️ 仅 TECH-RADAR（点模式聚焦深扫，其余全跳，跳过全部闸门） |
| "测试覆盖率 / 覆盖盲区 / test coverage / 哪些没测" | → 🧪 仅 TEST-COVERAGE（其余全跳，跳过全部闸门） |
| "生成文档 / 输出文档 / 保存输出 / 导出报告 / write article" | → 📝 仅 ARTICLE-WRITE（其余全跳，跳过全部闸门） |
| "斜杠命令 / slash command / 命令管理 / 命令列表" | → 💻 仅 SLASH-CMD（其余全跳，跳过全部闸门） |
| "快问快答 / quick question / tldr / 说重点 / 别废话 / 直接说 / 快点 / 讲核心 / quick-answer" | → ⚡ 仅 QUICK-ANSWER（其余全跳，跳过全部闸门） |
| "技术选型 / 方案对比 / 技术对比 / tech compare / 选型分析 / 技术调研 / 选哪个技术 / 技术决策" | → ⚖️ 仅 TECH-COMPARE（其余全跳，跳过全部闸门） |
| "接口测试 / 联调测试 / API 测试 / api test / 接口联调 / 测试这个接口 / 帮我测接口" | → 🔌 仅 API-TEST（其余全跳，跳过全部闸门） |
| "知识库 / knowledge base / 查知识库 / 沉淀知识 / 整理知识库 / 我的知识库 / 知识管理" | → 📚 仅 KNOWLEDGE-BASE（其余全跳，跳过全部闸门） |

## 任务类型 → 步骤裁剪

| 类型 | 步骤 |
|------|------|
| 🔍 纯理解 | READ → GRAPH → SUM → SELFCHECK(轻量) |
| 🔎 纯审查 | READ → REVIEW → SELFCHECK(轻量) |
| 📝 纯文档 | READ → CODE → REVIEW → GIT → SUM → SELFCHECK(标准) → ASK |
| ⚡ 微调 | READ → CODE → REVIEW → GIT → SELFCHECK(快速) → ASK |
| 🐛 Bug修复 | READ → CODE → REVIEW → EXAMINE → GIT → SUM → TALK → SELFCHECK(完整) → ASK |
| 🔧 重构 | READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → TALK → SELFCHECK(完整) → ASK |
| 🚀 功能开发 | READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → SELFCHECK(完整) → ASK（9步，跳过TALK） |
| 🥊 单步拷打 | SELFCHECK（完整）——仅此一步，无闸门，无状态文件 |
| 🧠 单步复盘 | TALK——仅此一步，无闸门，无状态文件 |
| 📊 单步画图 | GRAPH——仅此一步，无闸门，无状态文件 |
| 👁️ 单步理解 | READ——仅此一步，无闸门，无状态文件 |
| 🔍 单步审查 | REVIEW——仅此一步，无闸门，无状态文件 |
| 📋 单步总结 | SUM——仅此一步，无闸门，无状态文件 |
| 📖 单步读论文 | READ-PAPER——仅此一步，无闸门，无状态文件 |
| 📐 单步读项目 | READ-PROJECT——仅此一步，无闸门，无状态文件 |
| 🔬 单步代码追踪 | TRACE-CODE——仅此一步，无闸门，无状态文件 |
| 🛰️ 单步技术雷达 | TECH-RADAR——仅此一步（点/面/体三级粒度），无闸门，无状态文件 |
| 🧪 单步覆盖率分析 | TEST-COVERAGE——仅此一步，无闸门，无状态文件 |
| ✅ 单步清单审计 | CHECKLIST——仅此一步（Pre-flight/Audit 双模式），无闸门，无状态文件 |
| 📝 单步文档编写 | ARTICLE-WRITE——仅此一步（6 种文档类型模板），无闸门，无状态文件 |
| 💻 单步命令管理 | SLASH-CMD——仅此一步（20 条斜杠命令管理维护），无闸门，无状态文件 |
| ⚡ 单步快问快答 | QUICK-ANSWER——仅此一步（答案先行/要点为辅/展开按需），无闸门，无状态文件 |
| ⚖️ 单步技术选型对比 | TECH-COMPARE——仅此一步（六阶段战略决策框架），无闸门，无状态文件 |
| 🔌 单步接口联调测试 | API-TEST——仅此一步（五阶段全覆盖+MySQL5.7兼容SQL+Redis/MQ验证），无闸门，无状态文件 |
| 📚 单步知识库 | KNOWLEDGE-BASE——仅此一步（捕获/检索/存储/维护/交接五阶段），无闸门，无状态文件 |

## 每步产出

| 步骤 | 产出物 |
|------|--------|
| READ | 五要素需求说明（目标/范围/约束/验收/不做） |
| CODE | 变更记录（文件清单 + 改动原因 + 影响面；注释语言可配置） |
| REVIEW | 审查报告（七维度扫描 + 反合理化防御 + 供应链检查） |
| EXAMINE | 质量报告（测试命令 + 结果 + 新增测试） |
| GIT | 拆分方案（按维度拆为多提交单元 + Conventional Commits） |
| GRAPH | Mermaid 图表 + 节点对照表 |
| SUM | 六要素总结（背景→发现→问题→解决→效果→展望） |
| TALK | 5-Whys 追溯 + Trade-offs + 工程规范 |
| SELFCHECK | 🆕 CTO拷打记录（四阶段盘问）+ 认知缺口 + 汇报就绪评估 |
| ASK | 六维度确认清单（需用户逐项确认） |

## 上下文满了怎么办

| 级别 | 操作 |
|------|------|
| 🟢 60%以下 | 正常执行 |
| 🟡 60-80% | 精简输出，每步后问"继续？" |
| 🟠 80-95% | 保存状态快照 → `/clear` → 粘贴快照恢复 |
| 🔴 95%以上 | 强制暂停，保存快照，等 `/clear` |

- **核心原则**：只加载当前步骤的 SKILL.md，不一次性加载全部
- **恢复方式**：每步完成自动输出 JSON 快照，清上下文后粘贴即可从中断处继续

## 五条救命规则

1. **不确定就挂起**：任何技术决策没有 100% 把握 → 停止 → 描述问题 → 给出选项 → 等用户指示
2. **回退不超 3 次**：CODE↔REVIEW 来回到第 4 轮 → 挂起，可能有更深层问题
3. **可插拔产物后端**：用户指定/team-policy 配置/默认 local_html → 生成产物到对应后端（HTML文件/md文件/飞书文档）
4. **每步自检必填字段**：每步结束对照 data-contract 检查产出，缺失立即补全
5. **踩坑追加 Gotchas（候选制）**：耗时 >10min 的 bug / 反直觉陷阱 / 用户指出的边界 → 生成候选 → 用户确认后写入

## 🆕 v2.13 点线网三级编排（技能智能组合）

| 层级 | 触发方式 | 示例 |
|------|---------|------|
| 🎯 **点** Point | 单技能触发词 | "读论文" / "追踪代码" / "技术保鲜" |
| 🔗 **线** Line | "先...再..." / 流水线触发词 | "扫技术动态并深读" / "全面理解这个项目" |
| 🌐 **网** Net | "全面分析 / 帮我搞清楚 / 深度排查" | "帮我搞清楚这个项目的支付模块能不能扛住双11" |

| 内置流水线 | 触发词 | 技能序列 |
|----------|--------|---------|
| 🔭 扫描→深读 | "扫技术动态并深读" | 🛰️ tech-radar(面/体) → 📖 read-paper |
| 🏗️ 理解→追踪 | "理解项目并追踪" | 📐 read-project → 🔬 trace-code |
| 🧪 覆盖→补测 | "分析覆盖率并补测试" | 🧪 test-coverage → 👁️ read-requirements → ✏️ code-implement |
| 🏗️🔬 全理解 | "全面理解这个项目" | 📐 read-project → 🔬 trace-code → 🧪 test-coverage |

> 点线网完整设计见 `skills/fullchain-dev-workflow/references/skill-graph-orchestration.md`

## 🆕 v2.13 新特性（点线网三级编排 + 5 个学习型技能）

| 特性 | 怎么用 |
|------|--------|
| 风险分类 L0-L4（铁律#39） | 任务启动自动判定，不同等级适用不同闸门集。L0最小流程，L4全闸门+dry-run+备份+回滚 |
| 完成定义闸门（铁律#30） | READ输出六维完成定义（机器可验证+人工验证+高风险操作+不可交付条件+证据要求）。SUM自动生成交付验证清单逐项回溯 |
| 需求可追溯矩阵（铁律#31） | READ输出五列表（用户需求→验收标准→自动化测试→手动验证→状态），uncovered行L2+阻断 |
| 参考基线闸门（铁律#33） | 成熟领域+WebSearch搜索外部实现→≥3种模型→对比表（≥6维度），L2+强制执行 |
| 测试充分性闸门（铁律#34） | 五维覆盖检查（Happy Path/边界/错误/并发/安全）。Bug修复强制回归测试（老FAIL新PASS） |
| 环境保真闸门（铁律#32） | L3+交互式应用强制近真实环境冒烟测试，产出环境矩阵（OS/浏览器/设备/网络） |
| 重复失败触发器（铁律#35） | 同问题第2次修复失败→BLOCK→强制输出四要素（根因分析/正确模型/新测试覆盖/需确认假设） |
| 历史版本覆盖（铁律#36） | 版本索引每个版本必须在节点内有独立`### v{N}`小节，产出覆盖矩阵表 |
| 来源出处闸门（铁律#37） | 每版本标注来源类型，摘要恢复须声明"非逐字原始记录" |
| 证据账本（铁律#38） | 每轮（结论+证据类型+证据位置+可复现？），证据数≥L(N)门槛 |
| 上下文丢失防护（铁律#40） | `.claude/easywork/state-v{N}.json` 每步写入，跨/clear存活，启动时自动读取 |
| 闸门依赖图 | 40条铁律的依赖关系和执行顺序DAG可视化 |

## 🆕 v2.11 新特性（文档保真闸门 + 禁止无基准覆写 + 写入模式三级分类）

| 特性 | 怎么用 |
|------|--------|
| **文档保真闸门** | 7项检查（字数退化/证据密度下降/版本丢失/节点缩减/无基准覆写/round_report冒充/full overwrite错配）→detailed命中即阻断+修复（铁律#29） |
| **禁止无基准覆写** | 6条规则：已有文档默认局部更新/Overwrite必须带checklist/Quick Fix禁止覆写/round_report不得覆盖engineering_active/Overwrite仅三场景/Overwrite后fetch-compare |
| **写入模式三级分类** | quick_fix（仅追加，绝不覆写）/normal（DEFAULT, structured merge）/full_archive（三合法场景+checklist） |
| **文档作用域** | round_report（轮次摘要，可短，聊天用）/engineering_active（工程档案，保留全部历史）。两种作用域物理隔离 |

## 🆕 v2.10 新特性（文档拓扑闸门 + 双模文档结构 + 结构化合并）

| 特性 | 怎么用 |
|------|--------|
| **文档拓扑闸门** | 7项检查（重复节点/模式混用/索引缺失/内容未入节点/孤儿更新记录块/历史混淆/索引不一致）→detailed命中即阻断+自动修复（铁律#28） |
| **双模文档结构** | Mode A（审计日志，用户显式选择）：每 Run 完整 READ→CODE→... 链路。Mode B（持续维护，**默认**）：每流程节点一个顶层，节点内按版本分层 |
| **结构化合并** | 替代尾部追加更新记录。Fetch→Parse→Pre-check→Distribute→Index→Mark 六步，内容入对应流程节点 |
| **版本索引** | Mode B 顶部 `## 0. 版本索引` 表格——版本/日期/摘要/影响节点。节点内 `### v{N} — date（变更类型）` |

## 🆕 v2.9 新特性（反水文闸门 + MCR+ 质量升级 + ETR 证据链）

| 特性 | 怎么用 |
|------|--------|
| **反水文闸门** | 6类水文信号检测（空泛结论/无证据通过/无位置/无取舍/无风险/SelfCheck放水）→detailed命中即阻断（铁律#27） |
| **MCR→MCR+** | 每步增加质量维度和反例表——不再只问"有没有"，还要问"好不好"。禁止"正确性：通过"等水话 |
| **ETR 标准** | 每个关键结论必须有 Evidence（证据）+ Thinking（推理）+ Risk（风险），三者缺一视为不合格 |
| **同行审查就绪** | 写入前六问自检：能否复现/定位/理解原因/知道覆盖/知道未覆盖/判断合并？任一否→阻断 |
| **写后 Fetch 验证** | 写入后回读验证——防截断/代码块错误/表格破损/中文乱码。最多3轮修复循环 |
| **质量评分** | 100分制（需求15/推理20/代码15/测试20/风险15/拷打15）。detailed<80分→禁止写入 |
| **禁止凭记忆写报告** | SUM 必须基于 step_output 拼装，不得凭上下文自由发挥 |

## 🆕 v2.8 新特性（质量门禁 + 需求确认 + 交互式应用增强）

| 特性 | 怎么用 |
|------|--------|
| **CODE↔REVIEW 质量门禁** | REVIEW 发现阻断问题→必须回退 CODE 修复→重新 REVIEW 通过才放行。不可带着问题进 EXAMINE（铁律#23）。最多3轮 |
| **多路径回退** | REVIEW→CODE(3轮)/EXAMINE→CODE(3轮)/SELFCHECK→CODE(2轮)/ASK→CODE(1轮)，各有独立上限和触发条件 |
| **READ 需求理解确认** | READ 完成后必须用自己的话重述需求理解+列出澄清问题+获用户确认后才进入 CODE（铁律#24） |
| **文档迭代增量更新** | v2.8→v2.10→v2.11：从文档级追加→节点内版本合并+写入模式三级分类。Mode B 默认 structured merge。Quick Fix 仅追加版本记录。（铁律#25） |
| **交互式应用 EXAMINE 增强** | CLI/TUI/GUI/Web/游戏额外验证首屏稳定性/输入反馈/退出路径/stdin边界/ANSI兼容性/渲染频率（铁律#26） |
| **七维度交叉分析** | REVIEW 新增 5 组跨维度关联检查（安全×性能、正确性×兼容性、可维护性×可观测性等） |
| **回退历史追踪** | 状态快照新增 rollback_history 字段，记录每次回退的路径/轮次/原因/修复 |

## 🆕 v2.7 新特性（报告深度分层 + MCR 闸门）

| 特性 | 怎么用 |
|------|--------|
| **报告深度分层** | brief/standard/detailed 三级——任务类型自动决定默认值。功能开发/重构/Bug修复→detailed，微调→brief |
| **最小内容要求(MCR)** | detailed 模式每步骤有硬性最低产出（READ 5项/CODE 5项/REVIEW 3项/EXAMINE 4项/GIT 5项/SELFCHECK 3项），不满足则阻断写入 |
| **内容丰满度自检闸门** | write_final_report 前强制执行 MCR 自检。detailed→HARD GATE(不通过阻断)，standard→SOFT GATE(警告记录) |
| **报告类型** | executive_summary(领导层摘要,brief) vs engineering_record(工程记录,standard/detailed)。功能开发/重构自动选后者 |
| **深度自动升级** | 发现安全问题/测试根因复杂/改动超预估2倍/用户补充重要信息 → standard 自动升级为 detailed |
| **流式增量写入保障** | 每步骤完成后立即追加到文档；非流式后端在最终报告中恢复完整详情。禁止"浓缩版"替代逐步骤产出 |
| **代码摘录位置标注** | 所有代码引用必须包含文件路径和行号（格式：auth.service.ts:88-95），确保可追溯 |
| **同行审查就绪** | detailed 报告应满足"另一个工程师不读源码也能理解完整上下文"的标准 |

## 🆕 v2.6 新特性（CTO 拷打层）

| 特性 | 怎么用 |
|------|--------|
| **SelfCheck CTO 拷打** | 新增第 10 步，Agent 切换 CTO 角色进行四阶段深度盘问（业务背景→问题发现→解决方案→实现过程） |
| **汇报就绪检查** | 完整模式下强制检查：3句话说清楚、领导5问、同事3质疑、排查思路 |
| **全任务类型强制自检** | 所有任务类型必须执行 SELFCHECK（模式不同：完整/标准/快速/轻量），CTO 质检是底线 |
| **拷打语气规范** | 直接、具体、不留情面——AI 不拷打你，同事和领导就要拷打你 |
| **认知缺口记录** | 开发者答不上来的问题记录到 gaps_identified，有后续跟进计划才放行 |

## 🆕 v2.5 新特性（飞书原生沉淀 + 可插拔后端）

| 特性 | 怎么用 |
|------|--------|
| **可插拔产物后端** | 支持 local_html / markdown / lark_doc 三种后端，用户指定或 team-policy 配置 |
| **飞书文档沉淀** | 配置 `lark-cli` MCP 后，产物直接写入飞书文档，发送链接即可分享 |
| **Git 链路追踪** | GIT 步骤产出链路数据 → 写入飞书追踪文档（任务→提交→Check→hash→测试） |
| **Git 提交粒度增强** | 每个 commit unit 含业务上下文 + 引入风险 + 验证证据 + Check 清单 |
| **文档写作规范** | 中文复盘口吻、禁反引号、禁套话、段落自然、标题≤4子标题、表格仅结构化 |
| **后端适配层** | 飞书逻辑封装在 `lark-doc` 适配器中，新增后端不改核心 |

## 🆕 v2.4 新特性（安全加固）

| 特性 | 怎么用 |
|------|--------|
| **Git 安全管控** | git write 操作必须用户确认，命令写入脚本文件手动审查 |
| **敏感信息脱敏** | HTML 报告/日志自动脱敏 Token/密钥/内部URL/源码/手机/邮箱 |
| **自定义步骤预确认** | 列出 custom skill 清单，用户确认后才执行 |
| **供应链搜索防护** | 私有包名不发送到公网，标注为私有包 |
| **Gotchas 候选制** | Agent 生成候选 → 用户确认 → 才写入文件（不再自动追加） |
| **文件写保护** | 写操作限定项目根目录内，禁止系统/上级目录 |

## 🆕 v2.3 新特性

| 特性 | 怎么用 |
|------|--------|
| **Gotchas 知识库** | Agent 踩坑后自动追加；执行前扫描已知陷阱 |
| **并行审查** | 高风险任务自动启用 3 个子 Agent 审查安全/性能/兼容 |
| **反合理化防御** | 审查前先过目 9 条 Agent 自我欺骗话术 |
| **团队策略覆盖** | 编辑 `references/team-policy.md` 声明团队规则 |
| **自定义步骤** | 在 `.claude/skills/easywork/custom/` 下放置技能 |
| **逐步骤预览** | 关键步骤执行前先输出微型预览 |
| **交互式新手引导** | 说"带我入门"开始 5 阶段引导 |
| **可访问性审查** | 前端代码自动检查 a11y（第 7 维度） |
| **供应链检查** | 新增依赖自动检查 CVE + 许可证 + 维护状态 |
| **Conventional Commits** | 提交消息自动生成 feat/fix/refactor 等格式 |
| **JSON Schema 数据契约** | `data-contract.schema.json` 提供机器可读验证 |
| **条件分支扩展** | 17 条条件分支覆盖步骤间+上下文自适应场景 |
| **Skill 自测提示词** | 16 个测试场景覆盖全部任务类型 + v2.3 新特性 |
| **增强技能模板** | `skill-template/` 含 Gotchas/反合理化/测试提示词 |
| **JSONL 日志分析** | `bash .claude/easywork/analyze-logs.sh` 一键分析 |
| **故障 Runbook** | 常见故障有预置诊断和修复方案 |

## 项目文件导航

| 想看什么 | 去这里 |
|---------|--------|
| 新手入门，端到端示例 | `skills/fullchain-dev-workflow/assets/walkthrough-example.md` |
| 完整输出模板 | `skills/fullchain-dev-workflow/assets/output-template.md` |
| HTML 输出格式规范 | `skills/fullchain-dev-workflow/assets/html-output-template.md` |
| HTML 骨架（可直接复制） | `skills/fullchain-dev-workflow/assets/html-skeleton.html` |
| 步骤间数据契约 | `skills/fullchain-dev-workflow/references/data-contract.md` |
| 每步验收标准 | `skills/fullchain-dev-workflow/references/acceptance-gates.md` |
| 语言/框架适配速查 | `skills/fullchain-dev-workflow/references/language-matrix.md` |
| 渐进式成熟度 L1/L2/L3 | `skills/fullchain-dev-workflow/references/maturity-levels.md` |
| 编排引擎机制（DAG/并行审查/自定义步骤） | `skills/fullchain-dev-workflow/references/orchestration-engine.md` |
| 🆕 v2.13 技能图谱（点线网三级编排） | `skills/fullchain-dev-workflow/references/skill-graph-orchestration.md` |
| 🆕 v2.13 流水线编排器（7条内置流水线+动态DAG） | `skills/fullchain-dev-workflow/references/pipeline-composer.md` |
| 🆕 v2.13 元编排器（网模式意图解析+自治扩散） | `skills/fullchain-dev-workflow/references/meta-orchestrator.md` |
| JSONL 日志分析 | `skills/fullchain-dev-workflow/references/log-analysis-guide.md` |
| JSON Schema 数据契约 | `skills/fullchain-dev-workflow/references/data-contract.schema.json` |
| Gotchas 知识库 | `skills/fullchain-dev-workflow/references/gotchas.md` |
| 团队策略覆盖 | `skills/fullchain-dev-workflow/references/team-policy.md` |
| 故障 Runbook | `skills/fullchain-dev-workflow/references/failure-runbooks.md` |
| Skill 自测提示词 | `skills/fullchain-dev-workflow/references/self-test-prompts.md` |
| 交互式新手引导 | `skills/fullchain-dev-workflow/assets/onboarding.md` |
| 日志分析脚本 | `.claude/easywork/analyze-logs.sh` |
| 安装脚本 | `install.bat` (Win) / `install.sh` (Unix) |
| 故障排查 | `TROUBLESHOOTING.md` |
| 版本历史 | `CHANGELOG.md` |
| 创建自定义技能 | `skill-template/` |
