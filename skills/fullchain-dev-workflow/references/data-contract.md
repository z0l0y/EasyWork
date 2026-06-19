# 步骤间数据传递契约

本文档定义 EasyWork 工作流中每一步产出的**最小必填字段**。
前一步产出的字段名即为后一步的引用键。Agent 在每步结束时应按此契约输出，
后续步骤引用 `{step}_output.{field}` 而非靠上下文回忆。

## 设计原则

1. **必填字段是行为约束，不是建议**——任何标 `[必填]` 的字段，前一步未产出则后一步应挂起索要
2. **字段名稳定**——改名等于破坏契约，所有子技能必须使用相同的字段名
3. **渐进式**——纯理解任务跳过的步骤不需要产出，但被跳过的步骤应显式标记为 `null`

## READ 产出契约

```
read_output:
  goal: string              # [必填] 核心目标，1-3 句话，可验证
  scope:                    # [必填] 修改范围
    files: string[]         #   涉及的文件路径列表
    modules: string[]       #   涉及的模块/服务名列表
  constraints: string[]     # [必填] 技术和业务约束
  acceptance_criteria: string[]  # [必填] 可验证的验收标准（至少 1 条）
  non_goals: string[]       # [必填] 明确排除的内容
  clarifications: string[]  # [可选] 向用户确认的问题
```

**消费方**：CODE（用 scope + constraints 限定改动范围）、REVIEW（用 constraints 检查兼容性）、SUM（用 goal + acceptance_criteria 对照验收）

## CODE 产出契约

```
code_output:
  files_changed:            # [必填] 变更文件清单
    - path: string          #   文件路径
      change_type: string   #   "add" | "modify" | "delete"
      lines_estimated: int  #   预估改动行数
      reason: string        #   改动原因（关联到 read_output.acceptance_criteria 的哪条）
  new_dependencies:         # [可选] 新增的第三方依赖
    - name: string
      version: string
      why_necessary: string
  impact_assessment: string # [必填] 影响面评估（直接+间接影响）
  implementation_notes: string  # [必填] 实现方案概述
```

**消费方**：REVIEW（用 files_changed 确定审查范围）、EXAMINE（确定需要运行的测试子集）、GIT（用 files_changed 做提交拆分）

## REVIEW 产出契约

```
review_output:
  verdict: string           # [必填] "pass" | "pass_with_fixes" | "blocked"
  dimensions:               # [必填] 七维度审查结果
    correctness:
      status: string        #   "pass" | "issues_found" | "not_applicable"
      issues: string[]      #   发现的问题（如有）
    security:
      status: string
      issues: string[]
    compatibility:
      status: string
      issues: string[]
    maintainability:
      status: string
      issues: string[]
    performance:
      status: string
      issues: string[]
    observability:
      status: string
      issues: string[]
    accessibility:            # 🆕 v2.3 第7维度
      status: string          #   "pass" | "issues_found" | "not_applicable"
      issues: string[]        #   (纯后端/CLI变更标注 not_applicable)
  blocking_issues: int      # [必填] 阻断性问题数量
  fixes_applied: string[]   # [可选] 回退到 CODE 修复并重新审查后，记录修复内容
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

**消费方**：EXAMINE（用 dimensions 确定测试重点，如 security 有问题则加强安全测试）、SUM（引用审查结论）、ASK（用 blocking_issues 判断风险）

## EXAMINE 产出契约

```
examine_output:
  verdict: string           # [必填] "pass" | "conditional_pass" | "fail"
  test_command: string      # [必填] 实际执行的测试命令
  test_results:
    total: int
    passed: int
    failed: int
    skipped: int
  new_tests_added:          # [可选] 补充的测试用例
    - file: string
      description: string
      covers: string        #   覆盖了什么场景
  test_output_snippet: string  # [必填] 关键输出片段（作为凭据）
  uncovered_scenarios: string[]  # [可选] 已知未覆盖的场景及原因
```

**消费方**：SUM（引用 test_results 作为效果证据）、ASK（用 uncovered_scenarios 向用户确认测试覆盖度）

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
      risk_level: string    #   "low" | "medium" | "high"
      risk_detail: string   #   具体风险分析
      verification: string  #   验证方式（引用 review_output 和 examine_output）
      commit_message:       # 🆕 v2.3 [必填] Conventional Commits 格式
        type: string        #   "feat" | "fix" | "refactor" | "test" | "docs" | "style" | "chore" | "perf" | "ci"
        scope: string       #   模块/服务名（可选但建议填写）
        subject: string     #   提交主题（≤50字符/25汉字）
        body: string        #   提交正文
  mixed_files_warning: string[]  # [可选] 无法拆分的混合变更文件及警示
```

**消费方**：SUM（引用拆分方案）、ASK（引用 risk_level 帮助用户判断审查优先级）

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
  background: string        # [必填] 为什么要做这件事
  discovery: string         # [必填] 发现/排查过程（到代码行级根因）
  problem: string           # [必填] 问题的技术本质
  solution: string          # [必填] 怎么修的 + 为什么这样修
  outcome:                  # [必填] 最终效果
    test_results_ref: string    # 引用 examine_output.test_results
    acceptance_check: string[]  # 逐条对照 read_output.acceptance_criteria
    metrics:                    # 量化对比（如有）
      - name: string
        before: string
        after: string
  future: string[]          # [必填] 遗留问题 + 后续建议
  skipped_steps: string[]   # [必填] 被跳过的步骤及原因
```

**消费方**：TALK（用 problem + solution 作为 5-Whys 的起点）、ASK（用 future 中的风险点提问）

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

**消费方**：ASK（用 root_cause + trade_offs 生成确认问题中的风险维度）

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

如果不确定前序某字段是否存在，应该回查而非猜测。

---

## 版本迁移

### 当前版本：2.4

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
