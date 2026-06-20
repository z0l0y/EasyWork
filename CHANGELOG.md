# 更新日志

EasyWork 的所有重要变更记录。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [2.9.0] — 2026-06-20

### 新增
- **反水文闸门（Anti-Fluff Gate）**：6类水文信号检测（空泛结论/无证据通过/无位置描述/无取舍/无风险/SelfCheck放水）。detailed→HARD GATE（命中即阻断写入），standard→SOFT GATE（警告+用户确认），brief→跳过但标注免责声明（铁律#27）
- **MCR→MCR+ 质量升级**：每个步骤的 MCR 从"数量要求"升级为"质量要求"。新增反例表（禁止项）和合格例。READ MCR+（需求来源/用户真实目标/影响量化/可验证验收/不做事项含原因）、CODE MCR+（变更位置+原因/关键逻辑3-6句/替代方案≥1/代码摘录含位置）、REVIEW MCR+（每维度≥2条检查点绑定位置/"通过"必须说明为什么能通过/发现问题写全位置+触发+影响+修复+回归）、EXAMINE MCR+（测试命令+目的/失败前后对比/覆盖矩阵标注新增/输出凭据）、SELFCHECK MCR+（≥8问/≥2反事实/≥2替代方案质询/≥1为什么之前没发现/≥1防复发/≥1认知缺口）
- **ETR 标准**：每个关键结论必须满足 Evidence / Thinking / Risk 三元组。任何没有证据、没有推理、没有风险边界的结论视为不合格
- **同行审查就绪六问自检**：最终报告写入前自问——另一个工程师能否复现问题/定位代码/知道为什么/知道测试覆盖/知道未覆盖/判断合并。任一答案为否→报告不允许写入
- **写后 Fetch 验证**：写入文档后必须 fetch 回读，验证内容未截断/代码块正确/表格完整/字符无乱码/所有步骤可见。详细修复循环最多 3 轮
- **文档质量评分**：100 分制（需求与背景15/根因方案推理20/代码位置摘录15/测试证据20/风险取舍15/SelfCheck拷打质量15）。<80分→detailed engineering_record 禁止写入。扣分规则明确（空泛结论-5/关键证据缺失-10/无未覆盖风险-15/无替代方案-10/SelfCheck<8问-15）
- **禁止凭记忆写报告**：SUM 不得凭上下文自由发挥，必须基于 step_output 拼装报告。某步骤不满足 MCR+ → 回退补充
- **3 个新参考文件**：`skills/sum-session/references/anti-fluff-gate.md`（6类水文信号+检测逻辑+反例）、`peer-review-standard.md`（6问+判定标准）、`quality-scoring.md`（6维度评分+扣分规则+闸门阈值）

### 变更
- **编排中枢 SKILL.md**：铁律新增 #27（反水文闸门）；§6 MCR 表升级为 MCR+ 表（每行增加反例+合格例）；新增 ETR 标准说明；§6 SUM 行更新（"禁止凭记忆写报告"）；§8 状态快照新增 5 个字段；§10 反模式新增 8 条；version→2.9
- **data-contract.md**：新增 anti_fluff_gate_result/peer_review_ready/quality_score/fetch_verify_result/etr_compliant 顶层字段；READ 新增 requirement_source/user_real_goal/impact_if_not_done；CODE 新增 alternatives_rejected；SELFCHECK 新增 mcr_plus_checks/counterfactuals/alternative_challenges；版本迁移表新增 2.8→2.9
- **acceptance-gates.md**：每步骤新增 MCR+ 质量关卡（READ+5/CODE+4/REVIEW+3/EXAMINE+4/SELFCHECK+8）；新增 SUM Anti-Fluff Gate/ETR/Peer Review/Quality Scoring/Write-then-Fetch/Anti-Memory 6 个专区；全局新增 8 条 v2.9 关卡
- **sum-session/SKILL.md**：新增 6 个 v2.9 专区（ETR标准/Anti-Memory Rule/Anti-Fluff Gate/Peer Review Readiness/Quality Scoring/Write-then-Fetch）；产物后端适配流程从 6 步扩展为 11 步；反模式新增 7 条；version→2.9
- **5 个步骤技能 MCR+ 升级**：read-requirements（需求来源/用户真实目标/影响量化+反例表）、code-implement（变更位置/原因/关键逻辑/替代方案+反例表）、code-review（检查点绑定位置/"通过"依据/问题全写+反例表）、examine-quality（测试命令+目的/前后对比/覆盖矩阵+反例表）、self-check（≥8问/≥2反事实/≥2替代方案/防复发/反例+硬性指标表）
- **doc-writing-guide.md**：新增 §9"ETR 标准与反水文写作"（ETR三段式/水文信号自查表/写作范例对比）
- 铁律总数 26→27；maturity-levels.md 铁律数更新

### 破坏性变更
- **MCR→MCR+ 升级**：v2.8 中 MCR 仅检查"有没有"，v2.9 中 MCR+ 同时检查"好不好"。已有的 MCR 检查全部保留，额外叠加 MCR+ 质量维度。不能满足 MCR+ 的 detailed 报告将被阻断写入
- **Anti-Fluff Gate 可能大量阻断**：v2.8 中没有水文检测，Agent 常产出"测试通过""功能正常""后续优化"等空话。v2.9 中 detailed 模式这些将被 HARD GATE 阻断——Agent 需要大幅提高产出质量才能通过
- **SelfCheck 要求大幅提高**：从"有问答就行"升级为 ≥8问/≥2反事实/≥2替代方案/≥1防复发/≥1认知缺口/零模糊词放水。现有的简短 SelfCheck 将不通过 MCR+

---

## [2.8.0] — 2026-06-20

### 新增
- **CODE↔REVIEW 质量门禁循环**：REVIEW 发现阻断问题 → 必须回退 CODE 修复后重新 REVIEW，不可带着已知问题进入 EXAMINE（铁律#23）。循环上限 3 轮，3 轮后挂起用户
- **多路径回退机制**：CODE↔REVIEW（最多3轮）、EXAMINE→CODE（测试失败根因为代码逻辑，最多3轮）、SELFCHECK→CODE（方案层面缺陷，最多2轮）、ASK→CODE（用户质疑核心实现，最多1轮）
- **READ 需求理解显式确认**：READ 完成后 Agent 必须用自己的话重述需求理解（含业务目标、技术方案假设、不确定点），在进入 CODE 前获得用户确认（铁律#24）。未指定实现方法时必须列出≥1个澄清问题
- **文档迭代增量更新**：需求变更时在原有排版下追加"更新记录"子节，标注版本号和日期，过时信息标注 `[已过时 — vX.X 起]` 而非直接删除（铁律#25）
- **交互式应用 EXAMINE 增强**：CLI/TUI/GUI/Web前端/游戏/交互式IO任务必须在 EXAMINE 额外验证真实使用体验——首屏稳定性、输入反馈、退出路径、stdin边界、ANSI兼容性、渲染频率（铁律#26）。纯后端/库/脚本标注 N/A
- **七维度交叉分析**：REVIEW 新增 5 组跨维度关联检查（安全性×性能、正确性×兼容性、可维护性×可观测性、安全性×可访问性、性能×兼容性），捕捉单维度审查遗漏的交叉风险
- **回退历史追踪**：状态快照新增 `rollback_history` 字段，记录每次回退的 from_step/to_step/round/reason/issues_found/fixes_applied

### 变更
- **编排中枢 SKILL.md**：铁律 #5 扩展为 4 条具体回退路径；新增铁律 #23-#26；§6 MCR 表新增"交互式应用 EXAMINE 补充 MCR"（9 个验证维度）；§6 步骤表 READ/CODE/REVIEW/EXAMINE/SUM 行更新；§7 进度卡新增回退记录行；§8 状态快照新增 rollback_history/read_confirmation/is_interactive_ui_task/doc_iteration 字段；version→2.8
- **data-contract.md**：新增 read_output.understanding_confirmation（必填）；review_output 新增 rollback_round/rollback_history（detailed必填）；examine_output 新增 interactive_ux_validation（detailed必填，含 10 个字段）；sum_output 新增 doc_iteration（detailed必填）；版本迁移表新增 2.7→2.8 条目
- **acceptance-gates.md**：READ 新增 3 条理解确认关卡；REVIEW 新增 3 条回退循环关卡；EXAMINE 新增 10 条交互式应用验证关卡；SUM 新增 3 条文档迭代关卡；全局新增 6 条 v2.8 关卡
- **code-review/SKILL.md**：审查结果改为三档判定表（pass/pass_with_fixes/blocked）；新增回退循环机制图；新增 5 组七维度交叉分析；回退历史记录格式定义
- **examine-quality/SKILL.md**：新增"交互式应用真实体验验证"专区（触发判断/验证清单 6 项/CLI+TUI额外 4 项/ANSI兼容性说明模板/自动刷新验证模板）
- **read-requirements/SKILL.md**：新增第 3 步"输出需求理解确认"（确认模板/确认规则/澄清问题质量要求）
- **sum-session/SKILL.md**：新增"文档迭代增量更新"专区（触发判断/5条增量规则/更新记录格式/过时信息标注格式/禁止事项）
- **doc-writing-guide.md**：新增 §8"文档迭代与版本管理"（核心原则/更新记录格式/过时信息处理/自检清单 6 项）
- **orchestration-engine.md**：DAG 新增 4 条回退虚线边；条件分支表新增 4 条回退触发规则
- **maturity-levels.md**：铁律数更新（22→26）
- 全部 9 个子技能 SKILL.md version 2.7→2.8；3 个后端适配器 version 1.1→1.2；html-skeleton footer v2.7→v2.8

### 破坏性变更
- **REVIEW 质量门禁**：v2.7 中 REVIEW 发现问题后行为是"建议回退"，v2.8 升级为"硬门禁"——verdict=blocked 时禁止进入 EXAMINE。已有工作流如习惯带着 warning 前进，需适应新的严格门禁
- **READ 确认成为必选项**：v2.7 中 READ 完成后直接进入 CODE，v2.8 要求必须获得用户对需求理解的确认。可能增加一轮对话交互，但大幅降低理解偏差风险

---

## [2.7.0] — 2026-06-20

### 新增
- **报告深度分层**：brief / standard / detailed 三级深度。任务类型自动决定默认值（功能开发/重构/Bug修复→detailed，纯理解/审查/文档→standard，微调→brief），用户可覆盖，团队可在 team-policy 配置
- **最小内容要求（MCR）**：detailed 模式下每个步骤定义硬性最低产出要求。READ 5项（需求背景/用户目标/MVP边界/验收标准≥2/不做事项≥1）、CODE 5项（文件变更表/核心设计说明/关键函数职责≥2/边界处理≥1/代码摘录≤30行含路径行号）、REVIEW 3项（每维度≥2条检查点/阻断问题详情/issue含代码位置）、EXAMINE 4项（测试命令/覆盖矩阵/输出凭据/未覆盖风险）、GIT 5项（拆分方案/business_context/risk_introduced/verification_evidence/developer_checklist）、SELFCHECK 3项（完整CTO问答/认知缺口/补救动作）
- **内容丰满度自检闸门（MCR Gate）**：write_final_report 前强制执行。detailed→HARD GATE（不通过=拒绝写入→回退补充→重新自检，最多2轮），standard→SOFT GATE（警告记录），brief→跳过
- **报告类型**：executive_summary（领导层摘要，强制 brief）vs engineering_record（工程记录，standard/detailed）。功能开发/重构选前者时 Agent 必须强烈警告
- **深度自动升级**：4 个触发条件——安全问题/测试失败根因复杂/实际改动超预估2倍/用户补充重要信息 → standard 自动升级为 detailed
- **流式增量写入保障**：每步骤完成后立即追加到产物文档。非流式后端在最终报告中恢复完整结构化产出。明确禁止"浓缩版"反模式
- **代码摘录位置标注**：所有代码引用必须包含文件路径和行号（格式：`auth.service.ts:88-95`），确保可追溯到源码
- **同行审查就绪标准**：detailed 报告应让另一个工程师不读源码也能理解完整上下文
- **report_type 降级保护**：功能开发/重构选择 executive_summary 时 Agent 必须强烈警告并建议切换
- **team-policy 扩展**：新增 `report_depth` 和 `report_type` 配置段，支持团队级别默认值、白名单和强制规则

### 变更
- **编排中枢 SKILL.md**：铁律新增 #19-#22（深度不可降级/流式增量保障/MCR闸门/类型匹配）；§4 裁剪参考表新增 report_depth 和 report_type 两列；新增"报告深度选择逻辑"子节（含深度升级4触发条件+降级保护）；§6 步骤表 SUM 行更新为深度感知；新增 MCR 表（6步骤×3-5项）+ 代码摘录格式要求；§7 进度卡新增深度/类型信息；§8 状态快照新增 5 个字段；§10 反模式新增 7 条
- **data-contract.md**：新增 report_depth / report_type / streaming_status 顶层字段；所有步骤契约字段增加深度感知标注（`[必填|brief]` / `[必填|standard]` / `[必填|detailed]`）；sum_output 新增 mcr_gate_result；新增 READ/CODE/REVIEW/EXAMINE 契约字段以满足 MCR（business_background/user_persona/mvp_scope/design_rationale/key_functions/edge_case_handling/code_excerpts/dimensions.*.checkpoints/blocking_issues_detail/test_coverage_matrix/cto_qa_transcript）；版本迁移表新增 2.6→2.7 条目
- **acceptance-gates.md**：每步骤新增 MCR 验收关卡（READ+5条/CODE+5条/REVIEW+3条/EXAMINE+4条/SELFCHECK+3条）；新增"SUM — 内容丰满度自检闸门"专区（6条，区分 HARD/SOFT GATE）；全局新增 v2.7 关卡（8条）
- **sum-session/SKILL.md**：前置判断改为深度感知（brief/standard/detailed 行为差异）；新增"MCR Gate"专区（执行流程+判定逻辑+输出格式）；新增"流式增量写入保障"专区（按后端 streaming 能力分策略）；产物后端适配流程更新（新增 MCR 前置+4个新传入参数）；反模式新增 4 条
- **doc-writing-guide.md**：新增 §7"报告深度与类型指南"（深度层级表/报告类型说明/同行审查就绪标准）；§6 自检清单新增 4 条 v2.7 项
- **team-policy.md**：新增 `report_depth`（default/allow_brief_for/force_detailed_for）和 `report_type`（default/block_executive_summary_for）配置 YAML 段
- **output-backends.md**：write_final_report 接口新增 4 个参数（report_depth/report_type/mcr_gate_result/streaming_status）；write_step_output 新增流式保障说明；后端能力表新增 full_detail_restore
- **lark-doc 后端（v1.0→v1.1）**：write_step_output 新增流式增量保障；write_final_report 新增 MCR 闸门验证 + 深度感知逻辑 + 文档尾注含深度/类型信息；反模式新增 3 条
- **local-html 后端（v1.0→v1.1）**：write_step_output 重写为完整暂存模式（禁止精简）；write_final_report 新增深度感知+MCR验证+增量恢复+报告类型提示条；capabilities 新增 full_detail_restore；反模式新增 3 条
- **markdown 后端（v1.0→v1.1）**：同 local-html 模式变更；文档头新增深度/类型/流式状态元数据
- **self-check/SKILL.md**：§11 产出格式新增 detailed 模式要求（完整CTO问答记录/认知缺口含补救动作/severity标注）；反模式新增 3 条
- 所有技能文件 YAML frontmatter version 更新至 2.7
- 后端适配器 version 更新至 1.1
- install.sh / install.bat 版本号 2.6→2.7
- 其余参考文档版本号同步更新（TROUBLESHOOTING/onboarding/security-policy/orchestration-engine/html-skeleton）

### 破坏性变更
- 无。所有 v2.6 字段向后兼容。brief 模式等效 v2.6 行为，standard/detailed 为增强模式。新增字段仅 v2.7 新增
- **行为变更**：detailed 模式下 SUM 不可写入未通过 MCR 的报告（v2.6 无此闸门）。此为增强约束，不影响现有 standard/brief 流程

---

## [2.6.0] — 2026-06-20

### 新增
- **SelfCheck CTO 拷打层**（`skills/self-check/SKILL.md`）：EasyWork 的心智模型核心。Agent 切换为 CTO 角色，用拷打语气对开发者进行四个阶段深度盘问——业务背景拷打（为什么做）、问题发现拷打（怎么发现的）、解决方案拷打（为什么这样修）、实现过程拷打（怎么做到的）
- **汇报就绪检查**：完整模式下强制要求开发者 3句话说清楚、准备领导可能问的 5 个问题、同事可能质疑的 3 个点、上线排查思路
- **四种拷打模式**：完整（功能开发/重构/Bug修复）、标准（纯文档）、快速（微调）、轻量（纯理解/纯审查），按任务类型自动匹配
- **认知缺口记录**（`gaps_identified`）：开发者答不上来的问题系统化记录，有后续计划才放行
- **拷打语气规范**：直接、具体、不留情面——"AI 不拷打你，同事和领导就要拷打你"

### 变更
- **工作流 9步→10步**：新增 SELFCHECK 为第 9 步（ASK 延至第 10 步），依赖 DAG 更新为 `SUM→TALK→SELFCHECK→ASK`
- **编排中枢 SKILL.md**：铁律新增 #18（SelfCheck 不可跳过）；§4 裁剪参考表新增 SELFCHECK 列（所有任务类型均执行）；§6 步骤表新增 SELFCHECK 行；§8 状态快照新增 selfcheck_output
- **data-contract.md**：新增 `selfcheck_output`（5阶段字段）；版本迁移 2.5→2.6；消费者引用链更新（SELFCHECK 消费 SUM/TALK/GIT 产出，ASK 消费 SELFCHECK 产出）
- **acceptance-gates.md**：新增 SELFCHECK 验收关卡（8条）+ 全局 v2.6 关卡（4条）
- **sum-session/SKILL.md**：六要素末尾新增 SELFCHECK 拷打预警提示
- 所有技能文件 YAML frontmatter `version` 更新至 2.6
- `html-skeleton.html` footer 版本更新至 2.6

### 破坏性变更
- 无。所有 v2.5 字段向后兼容。工作流从 9 步扩展为 10 步，SELFCHECK 在所有任务类型中强制执行（模式不同但不可跳过）

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
