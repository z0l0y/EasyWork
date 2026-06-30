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
| "我不懂 / 零基础 / 举例子 / 通俗解释 / 大白话 / 说人话 / ELI5 / 画个图 / 什么是什么意思 / 完全不懂 / 新手 / 需要先懂什么" | → 🧠 仅 LEARN-FROM-ZERO（其余全跳，跳过全部闸门） |
| "需求拆解 / 拆分需求 / 任务拆分 / 帮我拆解 / 分解需求 / decompose / task breakdown / 需求太大 / 拆成小任务 / 分步做 / WBS / 第一步做什么" | → 🧩 仅 REQUIREMENT-DECOMPOSE（其余全跳，跳过全部闸门） |
| "场景画板 / scenario / 执行场景 / 场景列表 / 场景编排" | → 🎨 仅 SCENARIO-RUNNER（其余全跳，跳过全部闸门） |
| "打开画布 / canvas / 可视化编排 / 拖拽编排" | → 🖼 仅 SCENARIO-CANVAS（打开浏览器可视化编辑器） |

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
| 💻 单步命令管理 | SLASH-CMD——仅此一步（28 条斜杠命令管理维护），无闸门，无状态文件 |
| ⚡ 单步快问快答 | QUICK-ANSWER——仅此一步（答案先行/要点为辅/展开按需），无闸门，无状态文件 |
| ⚖️ 单步技术选型对比 | TECH-COMPARE——仅此一步（六阶段战略决策框架），无闸门，无状态文件 |
| 🔌 单步接口联调测试 | API-TEST——仅此一步（五阶段全覆盖+MySQL5.7兼容SQL+Redis/MQ验证），无闸门，无状态文件 |
| 📚 单步知识库 | KNOWLEDGE-BASE——仅此一步（捕获/检索/存储/维护/交接五阶段），无闸门，无状态文件 |
| 🧠 单步从零学习 | LEARN-FROM-ZERO——仅此一步（四级解释阶梯+知识树+图解+类比+误区），无闸门，无状态文件 |
| 🧩 单步需求拆解 | REQUIREMENT-DECOMPOSE——仅此一步（六阶段拆解流水线+5种拆解方法+原子任务检验+完成检查清单），无闸门，无状态文件 |

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

> 💡 v2.3-v3.1 的版本特性历史已移至 [DEVLOG.md](DEVLOG.md)。此处只保留日常速查内容。

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
