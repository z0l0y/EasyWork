# 更新日志

EasyWork 的所有重要变更记录。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [2.5.0] — 2026-06-20

### 新增
- **可插拔产物后端**（`backends/`）：产物输出从硬编码 HTML 升级为后端适配器模式。内置 local_html / markdown / lark_doc 三个后端，支持未来扩展（Notion、Confluence等）
- **后端注册表**（`references/output-backends.md`）：定义后端发现机制、选择优先级、通用接口契约、降级策略
- **飞书文档后端**（`backends/lark-doc/SKILL.md`）：通过 lark-cli MCP 直接创建飞书文档并流式追加步骤产出。支持飞书画板集成、文档分享链接、自动降级
- **飞书 API 速查表**（`references/lark-api-quickref.md`）：认证、文档CRUD、Markdown 转块、Wiki、白板、限流与重试
- **Git 链路追踪**：任务→提交分组→开发者Check→commit hash→测试结果→飞书记录，完整可追踪链路
- **Git 链路追踪模板**（`../git-split-commit/assets/git-chain-tracking-template.md`）：飞书文档中的链路追踪结构定义
- **Git 提交粒度增强**：每个 commit unit 新增 business_context（业务上下文）、risk_introduced（引入风险）、verification_evidence（验证证据）、developer_checklist（逐项Check清单）
- **文档写作规范**（`references/doc-writing-guide.md`）：中文业务复盘口吻、禁止反引号包裹文件名、段落自然、标题≤4子标题、表格仅结构化、命令集中展示
- **飞书安全策略**（`security-policy.md` §10）：认证信息保护、文档权限控制、MCP可用性检查、API调用审计
- **team-policy 产物后端配置**：团队可配置默认后端和飞书参数（folder_token / wiki_space_id / git_tracking_doc_id）

### 变更
- **编排中枢 SKILL.md**：铁律 #8 从"默认 HTML"重写为"产物后端可插拔"；新增铁律 #16（后端不可自行选择）、#17（飞书MCP前置检查）；新增 §4 产物后端选择子节
- **SUM 步骤**：不再硬编码生成 HTML，改为调用后端适配器 dispatch。新增后端适配、写作规范引用
- **GIT 步骤**：每个拆分单元从 5 项扩展为 7 项必填。commit message body 必须包含改动原因/风险说明/验证方式三段
- **GRAPH 步骤**：新增产物后端分流——飞书后端可将图表嵌入文档或建议画板；其他后端保持原有方式
- **data-contract**：新增 5 个 git_output 字段 + git_tracking 顶层字段 + output_backend 顶层字段。版本迁移 2.4→2.5
- **acceptance-gates**：GIT 新增 6 项 v2.5 关卡；全局新增 5 项 v2.5 关卡
- **html-output-template.md**：重定位为 local_html 后端专用模板

### 破坏性变更
- 无。所有 v2.4 字段向后兼容，新增字段仅 v2.5 新增。v2.4 工作流可正常降级运行

---

## [2.4.0] — 2026-06-20

### 新增
- **安全策略文档**（`references/security-policy.md`）：覆盖 Git 操作、敏感信息脱敏、自定义步骤、供应链检查、文件系统写入、Gotchas 追加、显式激活、授权来源 8 大安全域
- **Git 写操作安全管控**：`git add`/`commit`/`push`/`stash` 等写操作必须用户确认后才能执行。拆分命令写入 `.claude/easywork/git-commands.sh` 供用户手动审查。`git stash` 禁止倒计时默认执行
- **敏感信息脱敏机制**：HTML 报告和 `workflow.log.jsonl` 自动脱敏 Token/密钥/内部URL/大段源码（>30行）/手机号/邮箱/数据库连接串。4 个数据契约字段特定约束
- **自定义步骤预确认**：Agent 发现 custom skill 后列出清单（路径+名称+用途），用户确认后才执行，每次会话重新确认。`insert_after: ASK` 明确禁止
- **供应链外部搜索防护**：私有包名/内部 registry URL 禁止发到公网搜索，标注为私有包后跳过公网检查
- **Gotchas 候选-确认制**：Agent 生成候选条目展示给用户，用户确认后才写入 `references/gotchas.md`（替代自动追加）
- **文件系统写保护**：所有写操作限定在当前项目根目录内。`security-policy.md` 自身受写保护
- **显式激活机制**：EasyWork 仅在用户明确说"用 EasyWork"时才启用，普通开发任务不自动套用
- **授权来源收紧**：高风险操作仅接受当前用户本轮明确指令；历史对话/文档/项目文件/README/工具输出/日志/Agent输出中的授权文本一律无效
- **CDN 供应链安全**：HTML 报告 Mermaid CDN 固定版本 + HTTPS + 离线后备
- **安装脚本安全**：覆盖/卸载增加交互确认，CLAUDE.md 安装前自动备份

### 变更
- 编排中枢 §2 铁律新增 4 条安全规则（#11 Git确认、#12 输出脱敏、#13 自定义步骤预确认、#14 文件写保护）
- 编排中枢 §4 新增安全策略加载、自定义步骤预确认流程
- 编排中枢 §6 步骤表更新：GIT 行标注"禁止自动执行"、Gotchas 自检改为候选制
- 编排中枢 §10 反模式新增 4 条安全相关（未经确认执行 git、报告泄露信息、跳过自定义步骤确认、外部搜私有包）
- `git-split-commit/SKILL.md` 新增安全约束章节，禁止自动执行 git 命令，拆分后输出脚本文件
- `code-review/SKILL.md` 供应链检查新增外部搜索约束和私有包处理规则
- `sum-session/SKILL.md` 新增 Gotchas 候选检查和 HTML 报告脱敏检查
- `orchestration-engine.md` 自定义步骤注入新增执行前确认机制，日志新增安全约束
- `log-analysis-guide.md` 新增日志安全约束说明
- `html-output-template.md` 新增脱敏自检清单和 11 类禁止内容
- `acceptance-gates.md` 新增 6 条 v2.4 安全关卡
- `data-contract.md` 版本迁移 2.3→2.4：6 项新增 + 2 项破坏性变更
- 所有 11 个 Skill 的 YAML frontmatter `version` 更新至 2.4

### 修复
- Gotchas 追加流程：从 Agent 自动写入改为候选-确认制（防止未经审查的内容进入知识库）
- GIT 步骤：从自动执行 git 命令改为写入脚本文件 + 用户确认后执行（防止误操作和不可逆推送）

### 破坏性变更
- Gotchas 不再自动追加到文件——Agent 生成候选，用户确认后写入
- GIT 步骤不再自动执行 `git add`/`commit`/`push`——命令写入脚本文件，用户手动执行或授权后执行

---

## [2.3.0] — 2026-06-20

### 新增
- **Gotchas 知识库**（`references/gotchas.md`）：项目特定反直觉陷阱记录，Agent 踩坑后自动追加，后续执行时主动扫描预警
- **Skill 自测提示词集**（`references/self-test-prompts.md`）：16 个覆盖全部任务类型 + v2.3 新特性的测试场景，修改 Skill 后验证未退化
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
- 编排中枢 §6 步骤表更新：REVIEW 6维→7维、CODE 注释可配置、GIT 含 Conventional Commits
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
