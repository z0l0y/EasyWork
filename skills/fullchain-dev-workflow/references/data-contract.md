# 步骤间数据传递契约

本文档定义 EasyWork 工作流中每一步产出的**最小必填字段**。
前一步产出的字段名即为后一步的引用键。Agent 在每步结束时应按此契约输出，
后续步骤引用 `{step}_output.{field}` 而非靠上下文回忆。

## 设计原则

1. **必填字段是行为约束，不是建议**——任何标 `[必填]` 的字段，前一步未产出则后一步应挂起索要
2. **字段名稳定**——改名等于破坏契约，所有子技能必须使用相同的字段名
3. **渐进式**——纯理解任务跳过的步骤不需要产出，但被跳过的步骤应显式标记为 `null`
4. **🆕 v2.7 深度感知**——字段标注 `[必填|brief]` 表示所有深度均必填，`[必填|standard]` 表示 standard/detailed 必填，`[必填|detailed]` 表示仅 detailed 必填。brief 模式不会产生 detailed-only 字段

## READ 产出契约

```
read_output:
  goal: string              # [必填|brief] 核心目标，1-3 句话，业务语言可验证
  business_background: string  # 🆕 v2.7 [必填|detailed] 需求背景（业务上下文，非纯技术描述）
  user_persona: string         # 🆕 v2.7 [必填|detailed] 用户目标（谁在什么场景下要做什么）
  scope:                    # [必填|brief] 修改范围
    files: string[]         #   [必填|brief] 涉及的文件路径列表
    modules: string[]       #   [必填|standard] 涉及的模块/服务名列表
  constraints: string[]     # [必填|standard] 技术和业务约束
  acceptance_criteria: string[]  # [必填|brief] 可验证的验收标准（brief≥1条, standard≥2条, detailed≥3条）
  non_goals: string[]       # [必填|standard] 明确排除的内容（brief可为空，standard/detailed≥1条）
  mvp_scope: string[]          # 🆕 v2.7 [必填|detailed] MVP边界（本次做/不做清单）
  clarifications: string[]  # [可选|detailed] 向用户确认的问题
```

**消费方**：CODE（用 scope + constraints 限定改动范围）、REVIEW（用 constraints 检查兼容性）、SUM（用 goal + acceptance_criteria 对照验收）、SELFCHECK（用 business_background + user_persona 拷打业务理解）

## CODE 产出契约

```
code_output:
  files_changed:            # [必填|brief] 变更文件清单
    - path: string          #   文件路径
      change_type: string   #   "add" | "modify" | "delete"
      lines_estimated: int  #   预估改动行数
      reason: string        #   改动原因（关联到 read_output.acceptance_criteria 的哪条）
  new_dependencies:         # [可选|standard] 新增的第三方依赖
    - name: string
      version: string
      why_necessary: string
  impact_assessment: string # [必填|brief] 影响面评估（直接+间接影响）
  implementation_notes: string  # [必填|standard] 实现方案概述；detailed 模式必须含核心设计说明（为什么这样设计）
  design_rationale: string      # 🆕 v2.7 [必填|detailed] 核心设计说明（架构选择理由、设计权衡）
  key_functions:                # 🆕 v2.7 [必填|detailed] 关键函数/模块职责（≥2个）
    - name: string              #   函数/模块名
      file_path: string         #   文件路径
      responsibility: string    #   职责描述
  edge_case_handling:           # 🆕 v2.7 [必填|detailed] 重要边界处理（≥1个）
    - scenario: string          #   边界场景描述
      handling: string          #   处理方式
  code_excerpts:                # 🆕 v2.7 [必填|detailed] 关键代码摘录（≥1段，每段≤30行）
    - file_path: string         #   文件路径
      lines: string             #   行号范围（如 "88-95"）
      description: string       #   这段代码做了什么
      code: string              #   代码内容（≤30行）
```

**消费方**：REVIEW（用 files_changed 确定审查范围）、EXAMINE（确定需要运行的测试子集）、GIT（用 files_changed 做提交拆分）、SUM（用 code_excerpts + design_rationale 丰富最终报告）

## REVIEW 产出契约

```
review_output:
  verdict: string           # [必填|brief] "pass" | "pass_with_fixes" | "blocked"
  dimensions:               # [必填|brief] 七维度审查结果
    correctness:
      status: string        #   [必填|brief] "pass" | "issues_found" | "not_applicable"
      issues: string[]      #   [必填|standard] 发现的问题（含具体代码位置：文件+行号）
      checkpoints: string[] #   🆕 v2.7 [必填|detailed] 具体检查点（≥2条，非"没有发现问题"占位）
    security:
      status: string        #   [必填|brief]
      issues: string[]      #   [必填|standard] 发现的问题（含具体代码位置）
      checkpoints: string[] #   🆕 v2.7 [必填|detailed] 具体检查点（≥2条）
    compatibility:
      status: string        #   [必填|brief]
      issues: string[]      #   [必填|standard]
      checkpoints: string[] #   🆕 v2.7 [必填|detailed] 具体检查点（≥2条）
    maintainability:
      status: string        #   [必填|brief]
      issues: string[]      #   [必填|standard]
      checkpoints: string[] #   🆕 v2.7 [必填|detailed] 具体检查点（≥2条）
    performance:
      status: string        #   [必填|brief]
      issues: string[]      #   [必填|standard]
      checkpoints: string[] #   🆕 v2.7 [必填|detailed] 具体检查点（≥2条）
    observability:
      status: string        #   [必填|brief]
      issues: string[]      #   [必填|standard]
      checkpoints: string[] #   🆕 v2.7 [必填|detailed] 具体检查点（≥2条）
    accessibility:            # 🆕 v2.3 第7维度
      status: string          #   [必填|brief] "pass" | "issues_found" | "not_applicable"
      issues: string[]        #   [必填|standard] (纯后端/CLI变更标注 not_applicable)
      checkpoints: string[]   #   🆕 v2.7 [必填|detailed] 具体检查点（≥2条，或标注 not_applicable）
  blocking_issues: int      # [必填|brief] 阻断性问题数量
  blocking_issues_detail:   # 🆕 v2.7 [必填|detailed] 阻断问题详情（如有；无则**说明为什么没有**——非空泛的"代码质量好"）
    - issue: string         #   问题描述（含代码位置：文件+行号）
      fix: string           #   修复记录
  fixes_applied: string[]   # [可选|standard] 回退到 CODE 修复并重新审查后，记录修复内容
  supply_chain_check:       # 🆕 v2.3 [可选] 供应链检查结果（有新增依赖时）
    checked: bool
    findings: string[]
  parallel_reviews:         # 🆕 v2.3 [可选] 并行审查结果（仅高风险任务启用）
    security_reviewer:
      verdict: string       #   "pass" | "issues_found"
      blocking_count: int
      findings: string[]
    performance_reviewer:
      verdict: string
      blocking_count: int
      findings: string[]
    compatibility_reviewer:
      verdict: string
      blocking_count: int
      findings: string[]
  cross_check:              # [可选] 二次独立抽查结果
```

**消费方**：EXAMINE（用 dimensions 确定测试重点，如 security 有问题则加强安全测试）、SUM（引用审查结论）、ASK（用 blocking_issues 判断风险）、SELFCHECK（用 blocking_issues_detail 拷打实现过程）

## EXAMINE 产出契约

```
examine_output:
  verdict: string           # [必填|brief] "pass" | "conditional_pass" | "fail"
  test_command: string      # [必填|brief] 实际执行的测试命令（完整可复制执行）
  test_results:             # [必填|brief]
    total: int
    passed: int
    failed: int
    skipped: int
  test_coverage_matrix:     # 🆕 v2.7 [必填|detailed] 测试覆盖矩阵
    - test_case: string     #   测试用例名
      covers: string        #   覆盖了什么场景/验收标准
      result: string        #   "passed" | "failed" | "skipped"
  new_tests_added:          # [可选|standard] 补充的测试用例
    - file: string
      description: string
      covers: string        #   覆盖了什么场景
  test_output_snippet: string  # [必填|standard] 关键输出片段（作为测试凭据，非"全部通过"占位）
  uncovered_scenarios:      # 🆕 v2.7 [必填|detailed] 已知未覆盖的场景（≥1个，含原因说明）
    - scenario: string      #   未覆盖的场景
      reason: string        #   为什么未覆盖
      risk: string          #   潜在风险
```

**消费方**：SUM（引用 test_results 作为效果证据 + test_coverage_matrix 丰富报告）、ASK（用 uncovered_scenarios 向用户确认测试覆盖度）

## GIT 产出契约

```
git_output:
  total_files: int          # [必填] 本次改动文件总数
  total_units: int          # [必填] 拆分后的提交单元数
  units:                    # [必填] 各提交单元
    - index: int
      dimension: string     #   "config" | "logic" | "ui" | "test_docs"
      files: string[]       #   本单元文件清单
      summary: string       #   改动说明
      business_context: string  # 🆕 v2.5 [必填] 业务上下文（为什么改、对用户/业务的影响）
      risk_level: string    #   "low" | "medium" | "high"
      risk_detail: string   #   具体风险分析
      risk_introduced: string   # 🆕 v2.5 [必填] 引入风险详细说明（场景、影响范围、缓解措施）
      verification: string  #   验证方式（引用 review_output 和 examine_output）
      verification_evidence: string  # 🆕 v2.5 [必填] 验证证据（测试覆盖场景 + 结果）
      developer_checklist:  # 🆕 v2.5 [必填] 开发者逐项 Check 清单
        scope_correct: bool     #   改动范围符合需求
        no_side_effects: bool   #   无意外副作用
        test_coverage: bool     #   测试覆盖充分
        style_consistent: bool  #   代码风格一致
        docs_updated: bool      #   文档/注释已更新
      commit_message:       # 🆕 v2.3 [必填] Conventional Commits 格式
        type: string        #   "feat" | "fix" | "refactor" | "test" | "docs" | "style" | "chore" | "perf" | "ci"
        scope: string       #   模块/服务名（可选但建议填写）
        subject: string     #   提交主题（≤50字符/25汉字）
        body: string        #   提交正文（🆕 v2.5 必须包含：改动原因/风险说明/验证方式）
  mixed_files_warning: string[]  # [可选] 无法拆分的混合变更文件及警示
  command_script_path: string    # 🆕 v2.4 [必填] git 命令脚本路径
```

**消费方**：SUM（引用拆分方案）、SELFCHECK（引用 business_context + risk_introduced + developer_checklist 拷打方案合理性）、ASK（引用 risk_level 帮助用户判断审查优先级）、lark-doc 后端（读取 git_tracking 写入飞书追踪文档）

## GRAPH 产出契约

```
graph_output:
  diagram_type: string      # [必填] "flowchart" | "sequence" | "architecture"
  mermaid_code: string      # [必填] 完整 Mermaid 代码块
  node_mapping:             # [必填] 节点与代码对照表
    - node: string          #   图中节点名称
      entity: string        #   对应代码实体
      location: string      #   文件位置（含行号）
  text_explanation: string  # [必填] 关键流程的文字解释
```

**消费方**：SUM（引用图表作为可视化证据）

## SUM 产出契约

```
sum_output:
  background: string        # [必填|brief] 为什么要做这件事（brief:1-2句，standard/detailed:完整业务上下文）
  discovery: string         # [必填|standard] 发现/排查过程（到代码行级根因；brief模式可为空）
  problem: string           # [必填|brief] 问题的技术本质
  solution: string          # [必填|brief] 怎么修的 + 为什么这样修（brief:1-2句，detailed:含取舍分析）
  outcome:                  # [必填|brief] 最终效果
    test_results_ref: string    # 引用 examine_output.test_results
    acceptance_check: string[]  # 逐条对照 read_output.acceptance_criteria
    metrics:                    # 量化对比（detailed 必填；standard 推荐；brief 可选）
      - name: string
        before: string
        after: string
  future: string[]          # [必填|standard] 遗留问题 + 后续建议（brief可为空）
  skipped_steps: string[]   # [必填|brief] 被跳过的步骤及原因
  mcr_gate_result:          # 🆕 v2.7 [必填|detailed] MCR自检闸门结果
    passed: bool            #   是否通过
    step_results:           #   逐步骤检查结果
      - step: string        #     步骤名
        passed: bool        #     是否通过
        missing: string[]   #     缺失的MCR条目
        action: string      #     "passed" | "supplemented" | "waived_user"
    overall_verdict: string #   "pass" | "pass_with_waivers" | "fail"
```

**消费方**：TALK（用 problem + solution 作为 5-Whys 的起点）、SELFCHECK（用全部六要素作为拷打的输入材料）、ASK（用 future 中的风险点提问）

## TALK 产出契约

```
talk_output:
  five_whys:                # [必填] 5-Whys 追溯
    - level: int
      question: string
      answer: string
  root_cause: string        # [必填] 最终系统性根因
  root_cause_type: string   # [必填] "process" | "tooling" | "knowledge" | "design"
  trade_offs:               # [必填] 取舍分析
    - item: string
      benefit: string
      cost: string
      intentional: bool     #   主动选择 or 被迫妥协
      followup: string
  engineering_rules: string[]  # [必填] 提炼的工程规范（具体可执行）
```

**消费方**：SELFCHECK（用 root_cause + trade_offs 拷打实现过程和方案合理性）、ASK（用 root_cause + trade_offs 生成确认问题中的风险维度）

## SELFCHECK 产出契约

```
selfcheck_output:
  mode: string                    # [必填] "full" | "standard" | "quick" | "light"
  business_understanding:         # [必填] 阶段1：业务背景拷打
    real_problem: string          #   真正要解决的业务问题（业务语言，不讲代码）
    business_value: string        #   业务价值（可量化则量化）
    user_impact: string           #   对用户/业务方的影响
    data_evidence: string         #   数据支撑（有则填具体数字，无则说明为什么没有）
  problem_discovery:              # [必填] 阶段2：问题发现拷打（轻量模式可为空）
    discovery_method: string      #   怎么发现的（用户反馈/监控/自查/上级要求）
    evidence_type: string         #   证据类型
    evidence_detail: string       #   具体证据
    impact_scope: string          #   影响面评估
  solution_rationale:             # [必填] 阶段3：解决方案拷打
    chain_position: string        #   在整条链路中的位置
    why_here_not_there: string    #   为什么在这里改不在那里改
    alternatives_considered: string[]  # 考虑过的其他方案（至少2个）
    why_not_alternatives: string  #   为什么不用其他方案（具体技术理由）
    risk_before: string           #   事前风险评估
    risk_during: string           #   事中监控方案
    risk_after: string            #   事后验证方案
    downstream_impact: string     #   下游影响分析
  implementation_reflection:      # [必填] 阶段4：实现过程拷打（轻量/快速模式可为空）
    difficulties: string[]        #   遇到的难点
    how_solved: string            #   怎么解决的
    unexpected: string            #   一开始没想到的
    why_not_before: string        #   之前为什么没这样改（历史原因分析）
    future_optimizations: string[]  # 后续可优化的地方
    solution_type: string         #   "临时方案" | "长期方案" | "临时→长期有计划"
  readiness_assessment:           # [必填] 汇报就绪检查（轻量模式可为空）
    three_sentence_summary: string  # 3句话说清楚（让不懂技术的人能听懂）
    leader_questions: string[]    #   领导可能会问的问题（至少5个）
    colleague_concerns: string[]  #   同事review可能质疑的点（至少3个）
    incident_plan: string         #   上线出问题的排查思路
    ready_to_report: bool         #   是否准备好向领导汇报
    gaps_identified:              #   🆕 v2.7 [必填|detailed] 认知缺口（≥1个，或**说明为什么没有**）
      - gap: string               #     认知缺口描述
        remediation: string       #     后续补救动作（谁/什么时候/怎么做）
        severity: string          #     "critical" | "major" | "minor"
  cto_qa_transcript:              # 🆕 v2.7 [必填|detailed] 完整CTO问答记录（不可用摘要表替代）
    - phase: string               #     阶段名（business_understanding/problem_discovery/solution_rationale/implementation_reflection/readiness）
      questions:                  #     该阶段的所有问答
        - question: string        #        CTO的问题
          answer: string          #        开发者的回答
          followup: string        #        追问（如有）
          followup_answer: string #        追问回答（如有）
```

**消费方**：ASK（用 gaps_identified + readiness_assessment 判断是否需要追加确认问题）、SUM（引用拷打结果作为质量证明）

## ASK 产出契约

```
ask_output:
  questions:                # [必填] 六维度确认问题
    - dimension: string     #   "scope" | "behavior" | "data" | "security" | "test" | "deploy"
      question: string
      why_asked: string     #   为什么问这个
      if_no_action: string  #   如果答案为否，下一步做什么
  confirmed_dimensions: int # [必填] 已确认的维度数
  pending_dimensions: string[]  # [可选] 未确认的维度
  user_skip_note: string    # [可选] 用户跳过 ASK 时的记录
```

---

## 使用方式

Agent 在每步结束时输出对应契约的字段值。后续步骤引用时使用标准键名。

示例——SUM 阶段引用前序产出：
```
根据 read_output.acceptance_criteria[0]（登录接口 P99 < 300ms），
examine_output 显示 test_results.passed=12，
确认 code_output.files_changed 中 auth.service.ts 的修改达成了验收标准。
```

## 🆕 v2.5 顶层字段

```
# 以下字段为 v2.5 新增，存在于顶层 data-contract 中，非某步骤产出

git_tracking:                # [可选，GIT 步骤执行时必填] Git 链路追踪数据
  task_description: string   #   任务简述（业务语言）
  task_date: string          #   YYYY-MM-DD
  task_type: string          #   Bug修复/功能开发/重构/微调/纯文档
  risk_level: string         #   low/medium/high
  units: [...]               #   与 git_output.units 结构相同（含 developer_checklist）
  examine_result:            #   测试结果摘要
    test_command: string
    test_total: int
    test_passed: int
    test_failed: int
    test_skipped: int
    verdict: string          #   pass/conditional_pass/fail

output_backend:              # [必填] 当前产物后端信息
  format: string             #   "html" | "markdown" | "lark_doc"
  name: string               #   后端名称（local_html / markdown / lark_doc）
  share_link: string         #   产物分享链接（飞书文档 URL 或本地文件路径）
```

**消费方**：lark-doc 后端（读取 git_tracking 写入飞书追踪文档）、SUM（记录 output_backend 用于最终报告）

## 🆕 v2.7 顶层字段

```
report_depth:                # [必填] 报告深度
  level: string              #   "brief" | "standard" | "detailed"
  source: string             #   来源："task_type_default" | "user_override" | "team_policy" | "auto_escalated"
  escalated: bool            #   是否发生过自动升级
  escalation_reason: string  #   升级原因（如未升级则为 null）

report_type:                 # [必填] 报告类型
  type: string               #   "executive_summary" | "engineering_record"
  source: string             #   来源："task_type_default" | "user_override" | "team_policy"
  downgrade_warning: bool    #   是否显示了降级警告（如适用）

streaming_status:            # [必填] 流式写入状态
  backend_supports: bool     #   后端是否支持流式追加
  steps_streamed: string[]   #   已流式追加的步骤列表
  full_detail_restored: bool #   最终报告是否恢复了完整步骤详情（不支持流式时必须为 true）
```

**消费方**：SUM（读取 report_depth 决定产出粒度）、SELFCHECK（根据 report_depth 调整拷打深度）、后端适配器（根据 report_depth + report_type 调整写入格式）

如果不确定前序某字段是否存在，应该回查而非猜测。

---

## 版本迁移

### 当前版本：2.7

`easywork_version` 字段用于标记状态快照的版本。不同版本间字段变更遵循以下规则。

### 版本间差异

| 版本 | 变更类型 | 具体变更 |
|------|---------|---------|
| 1.0 → 2.0 | 新增 | `read_output.clarifications`（可选澄清问题） |
| 1.0 → 2.0 | 新增 | `code_output.new_dependencies`（可选新增依赖） |
| 1.0 → 2.0 | 新增 | `review_output.fixes_applied`（可选修复记录） |
| 1.0 → 2.0 | 新增 | `examine_output.new_tests_added`（可选补充测试） |
| 1.0 → 2.0 | 新增 | `graph_output`（整个步骤为 v2.0 新增） |
| 2.0 → 2.1 | 新增 | `ask_output.quick_mode`（可选快速模式标记） |
| 2.0 → 2.1 | 无破坏 | 所有字段向后兼容，无删除/重命名 |
| 2.1 → 2.2 | 新增 | `review_output.cross_check`（可选二次独立抽查结果） |
| 2.1 → 2.2 | 新增 | `step_selfcheck`（每步自检记录，含必填字段完整性） |
| 2.1 → 2.2 | 无破坏 | 所有字段向后兼容，无删除/重命名 |
| 2.2 → 2.3 | 新增 | `review_output.dimensions.accessibility`（第 7 审查维度：可访问性） |
| 2.2 → 2.3 | 新增 | `review_output.supply_chain_check`（可选供应链安全检查结果） |
| 2.2 → 2.3 | 新增 | `review_output.parallel_reviews`（可选并行审查结果） |
| 2.2 → 2.3 | 新增 | `git_output.units[].commit_message`（Conventional Commits 格式提交消息） |
| 2.2 → 2.3 | 新增 | `comment_language`（CODE 步骤注释语言配置：chinese/english/auto） |
| 2.2 → 2.3 | 新增 | `custom_steps_completed`（自定义步骤完成记录） |
| 2.2 → 2.3 | 无破坏 | 所有字段向后兼容，仅新增可选/扩展字段 |
| 2.3 → 2.4 | 新增 | `review_output.supply_chain_check.private_packages`（私有包标注） |
| 2.3 → 2.4 | 新增 | `git_output.command_script_path`（git 命令脚本路径） |
| 2.3 → 2.4 | 新增 | `gotchas_candidates`（Gotchas 候选条目，待用户确认） |
| 2.3 → 2.4 | 新增 | `custom_steps_confirmation`（自定义步骤用户确认记录） |
| 2.3 → 2.4 | 新增 | `html_report_sanitization_check`（HTML 报告脱敏自检记录） |
| 2.3 → 2.4 | 变更 | Gotchas 追加流程：自动追加 → 候选-确认制（破坏性变更） |
| 2.3 → 2.4 | 变更 | GIT 步骤：自动执行 → 写入脚本文件+用户确认后执行（破坏性变更） |
| 2.3 → 2.4 | 无破坏 | 其余所有字段向后兼容 |
| 2.4 → 2.5 | 新增 | `git_output.units[].business_context`（业务上下文） |
| 2.4 → 2.5 | 新增 | `git_output.units[].risk_introduced`（引入风险详细说明） |
| 2.4 → 2.5 | 新增 | `git_output.units[].verification_evidence`（验证证据） |
| 2.4 → 2.5 | 新增 | `git_output.units[].developer_checklist`（开发者逐项 Check 清单） |
| 2.4 → 2.5 | 新增 | `git_tracking`（Git 链路追踪数据，新顶层字段） |
| 2.4 → 2.5 | 新增 | `output_backend`（产物后端信息，新顶层字段） |
| 2.4 → 2.5 | 变更 | `git_output.units[].commit_message.body` 必须包含：改动原因/风险说明/验证方式 |
| 2.4 → 2.5 | 无破坏 | 其余所有字段向后兼容，新增字段均为 v2.5 新增 |
| 2.5 → 2.6 | 新增 | `selfcheck_output`（SelfCheck CTO拷打产出，含5阶段字段，新顶层字段） |
| 2.5 → 2.6 | 新增 | 工作流步骤从 9 步扩展为 10 步（新增 SELFCHECK 在 TALK 之后、ASK 之前） |
| 2.5 → 2.6 | 新增 | 铁律 #18：SelfCheck CTO 拷打不可跳过 |
| 2.5 → 2.6 | 无破坏 | 所有字段向后兼容，新增字段均为 v2.6 新增 |
| 2.6 → 2.7 | 新增 | `report_depth` / `report_type` / `streaming_status` 顶层字段 |
| 2.6 → 2.7 | 新增 | 所有步骤契约字段增加深度感知标注（`[必填|brief]` / `[必填|standard]` / `[必填|detailed]`） |
| 2.6 → 2.7 | 新增 | `read_output.business_background` / `read_output.user_persona` / `read_output.mvp_scope`（detailed必填） |
| 2.6 → 2.7 | 新增 | `code_output.design_rationale` / `code_output.key_functions` / `code_output.edge_case_handling` / `code_output.code_excerpts`（detailed必填） |
| 2.6 → 2.7 | 新增 | `review_output.dimensions[*].checkpoints`（每维度≥2条检查点，detailed必填） |
| 2.6 → 2.7 | 新增 | `review_output.blocking_issues_detail`（detailed必填——含代码位置+修复记录，或说明为什么没有） |
| 2.6 → 2.7 | 新增 | `examine_output.test_coverage_matrix`（detailed必填） |
| 2.6 → 2.7 | 新增 | `examine_output.uncovered_scenarios` 扩展为结构化对象（含scenario/reason/risk） |
| 2.6 → 2.7 | 新增 | `sum_output.outcome.metrics` 标注 detailed 必填 |
| 2.6 → 2.7 | 新增 | `sum_output.mcr_gate_result`（MCR自检闸门结果，detailed必填） |
| 2.6 → 2.7 | 新增 | 铁律 #19-#22（深度/流式/MCR闸门/类型匹配） |
| 2.6 → 2.7 | 无破坏 | 所有字段向后兼容。brief 模式等效 v2.6 行为。新增字段仅 v2.7 新增，旧版本快照中缺失字段视为 null/[] |

### 快照迁移规则

当 Agent 读取旧版本的状态快照时：

1. **版本匹配**：`easywork_version` 与当前版本一致 → 直接使用
2. **旧版本快照**：缺少的字段视为 `null`/`[]`（可选字段），必填字段不可为空
3. **未知高版本快照**（快照版本 > Agent 版本）：挂起向用户报告"快照版本过新，请更新 EasyWork"

### 破坏性变更策略

- **字段删除**：不删除字段，标记为 `[已废弃]`，至少保留 1 个大版本
- **字段重命名**：新增新字段名，旧字段名标记为 `[已废弃]`，同时填充两个字段直到旧字段被移除
- **字段类型变更**：新增一个不同名的新字段，旧字段标记为 `[已废弃]`
- **变更记录**：任何破坏性变更必须在顶层 `CHANGELOG.md` 中记录
