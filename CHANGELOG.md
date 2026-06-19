# 更新日志

EasyWork 的所有重要变更记录。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [2.3.0] — 2026-06-20

### 新增
- **Gotchas 知识库**（`references/gotchas.md`）：项目特定反直觉陷阱记录，Agent 踩坑后自动追加，后续执行时主动扫描预警
- **Skill 自测提示词集**（`references/self-test-prompts.md`）：10 个覆盖全部任务类型的测试场景，修改 Skill 后验证未退化
- **并行审查**：高风险任务（重构/功能开发）的 REVIEW 可启用 3 个并行子 Agent（安全/性能/兼容性），与主审查同步
- **反合理化防御**：`code-review/SKILL.md` 新增 9 条 Agent 自我欺骗话术及反驳表，每次审查前先过目
- **团队策略覆盖**（`references/team-policy.md`）：团队可在不修改核心文件前提下声明强制/建议/提示规则。支持 `comment_language` 配置
- **自定义步骤注入**：编排中枢自动发现 `.claude/skills/easywork/custom/` 下的技能，按 `insert_after` + `insert_condition` 注入流程
- **条件分支扩展**：新增 7 条条件分支（兼容性问题追加测试、覆盖率不足警告、重复根因升级策略、混合文件 ≥3 警示等）
- **逐步骤预览**：每步执行前可选微型预览（步骤名、预计操作、预计耗时/Token）
- **交互式新手引导**（`assets/onboarding.md`）：5 阶段引导脚本——需求了解→级别推荐→最小演示→首任务→学习总结
- **可访问性审查**（第 7 维度）：`code-review` 新增 a11y 维度（语义化HTML/ARIA/键盘导航/色彩对比/屏幕阅读器/焦点管理）
- **供应链安全检查**：REVIEW 检测新增依赖时自动检查许可证兼容性、已知漏洞（CVE）、维护状态
- **Conventional Commits**：`git-split-commit` 强制使用 Conventional Commits 格式（feat/fix/refactor/test/docs/style/chore/perf/ci）
- **JSON Schema 数据契约**（`data-contract.schema.json`）：机器可读的步骤产出验证 Schema，与人工自检形成双重保障
- **故障模式 Runbook**（`references/failure-runbooks.md`）：5 种重复故障的预置诊断方案（测试框架不可用/依赖冲突/工作区不干净/Agent 自我怀疑/上下文溢出）
- **日志分析脚本**（`.claude/easywork/analyze-logs.sh`）：一键分析 JSONL 日志——总览/步骤统计/瓶颈分析/趋势
- **增强技能模板**（`skill-template/SKILL.md`）：新增 Gotchas 段、反合理化防御表、测试提示词、Before/After 对比

### 变更
- 编排中枢 §2 铁律 #7 新增 `data-contract.schema.json` 引用
- 编排中枢 §4 新增团队策略加载、Gotchas 扫描、逐步骤预览子节
- 编排中枢 §6 步骡表更新：REVIEW 6维→7维、CODE 注释可配置、GIT 含 Conventional Commits
- 编排中枢 §6 新增自定义步骤注入说明
- 编排中枢 §10 新增 2 条反模式（自欺审查、不记录 Gotchas）
- `code-review/SKILL.md` 审查维度 6→7，新增反合理化防御表、供应链检查流程
- `code-implement/SKILL.md` 铁律 #1 注释语言由硬编码中文改为可配置（`comment_language`）
- `git-split-commit/SKILL.md` 新增提交消息规范（Conventional Commits）、各维度对应 commit type
- `examine-quality/SKILL.md` 版本升级至 2.3
- `orchestration-engine.md` 新增：并行审查架构、自定义步骤注入机制、条件分支扩展（7 条新分支）、自检增强（Schema 验证）
- `data-contract.md` 新增 2.2→2.3 版本迁移条目（6 个新字段）
- `acceptance-gates.md` 新增 v2.3 关卡：反合理化防御、a11y 检查、供应链检查、Conventional Commits、Gotchas 扫描、Team Policy 加载
- 所有 10 个 Skill 的 YAML frontmatter `version` 更新至 2.3

### 修复
- 并行审查、自定义步骤注入、条件分支扩展——这些是平台已有能力（Agent 工具），Skill 层之前未利用，现补齐

---

## [2.2.0] — 2026-06-19

### 新增
- **步骤产出强制自检**：每步结束时自动对照 `data-contract.md` 检查所有 `[必填]` 字段是否已产出，缺失则自动补全
- **干跑预览模式**：中高风险任务先输出每步预期操作和产出，用户确认后才开始实际执行
- **结构化 JSONL 日志**：每步完成追加一行到 `.claude/easywork/workflow.log.jsonl`，支持事后分析
- **二次独立抽查**（交叉审查）：REVIEW 后切换审查视角对最自信的 2 个维度做快速验证
- **步骤间依赖 DAG**：可视化步骤依赖关系，标注可并行执行的步骤（GRAPH ∥ SUM）
- **条件分支**：REVIEW 发现安全问题 → EXAMINE 自动追加安全测试；TALK 触及黑盒 → 自动降级
- **模型分层推荐**：每步标注推荐模型 tier（快速/标准/深度），优化成本与质量
- **渐进式成熟度配置**（L1/L2/L3）：L1=4 个核心技能、L2=7 个（+测试+提交+总结）、L3=完整 10 个

### 变更
- 编排中枢 §2 新增铁律 #9（步骤产出自检不可跳过）
- 编排中枢 §6 重写：新增强制自检机制、步骤依赖 DAG、条件分支规则、模型分层、JSONL 日志
- `code-review/SKILL.md` 新增二次独立抽查流程
- README FAQ 新增渐进式成熟度说明
- QUICKREF 新增 v2.2 新特性速查表

---

## [2.1.0] — 2026-06-19

### 新增
- 一键安装脚本（`install.bat` for Windows, `install.sh` for Unix）
- HTML 骨架文件（`html-skeleton.html`）— Agent 可直接复制填空而非从头生成
- 故障排查与自救指南（`TROUBLESHOOTING.md`）
- 语言/技术栈适配速查（`references/language-matrix.md`）
- 功能开发端到端示例（walkthrough 新增示例 3）
- ASK 快速模式 — 轻量任务只需确认安全+回滚 2 个维度
- README 新增 Mermaid 工作流图、详细分平台安装指南、各平台功能对比表
- `LICENSE`（MIT）、`CHANGELOG.md`、`CONTRIBUTING.md`
- 技能模板（`skill-template/`）— 用户可据此创建自定义技能

### 修复
- 编排中枢 `SKILL.md` 中编号错误：两个 §4 已修正为 §4 和 §5，后续编号顺延
- 上下文管理 §3 中对状态快照的交叉引用更新为正确的节号

### 变更
- README 安装指南从 3 句简写扩展为分平台详细指南（含功能降级说明）
- `data-contract.md` 新增版本兼容性声明（§版本迁移）
- 编排中枢增引 `language-matrix.md` 和 `html-skeleton.html` 作为按需查阅资源

---

## [2.0.0] — 2026-06-18

### 新增
- **任务分类器**（任务分类器 + 步骤跳过机制）：7 种任务类型（纯理解/纯审查/纯文档/微调/Bug修复/重构/功能开发），自动建议裁剪方案
- **默认 HTML 输出**：用户未指定格式时自动生成自包含 HTML 报告（`html-output-template.md`）
- **断点续传**：JSON 状态快照机制，支持跨对话恢复
- **上下文管理策略**：四级预警（🟢→🟡→🟠→🔴）+ 单技能加载模式 + 精简模式
- **意图路由表**：根据用户关键词自动判断任务类型
- **回退循环限制**：CODE↔REVIEW 最多 3 轮
- **步骤间数据契约**（`data-contract.md`）：定义每步最小必填字段
- **端到端示例**（`walkthrough-example.md`）：Bug修复 + 纯理解 2 个完整场景
- **快速参考卡片**（`QUICKREF.md`）

### 变更
- 编排中枢从简单顺序调用重写为完整的任务分类 + 流程编排引擎
- 所有子技能 SKILL.md 重写（清理前版本中损坏的内容）
- 反模式章节全面强化（"禁止做"指令比"应该做"更有效）

### 移除
- v1.0 中"所有任务强制走 9 步"的硬性规则

---

## [1.0.0] — 2026-06-17

### 新增
- 初始版本：9 步全链路工作流（READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → TALK → ASK）
- 6 维度代码审查（正确性/安全性/兼容性/可维护性/性能/可观测性）
- 测试驱动质量验证（找→跑→补→修→重跑至全绿）
- 4 维度提交拆分（配置/核心逻辑/UI/测试）
- Mermaid 可视化图表（流程图/时序图/架构图）
- 5-Whys 根因分析 + Trade-offs 取舍
- 6 维度人工确认（HITL 最终闸门）
- 全局异常处理 SOP + Checklist 打卡机制
- Chinese 注释约束 + 反模式显式化
