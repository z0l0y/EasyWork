# Git 链路追踪文档模板

> **🆕 v2.5**：当产物后端为 lark-doc 时，GIT 步骤产出额外的 Git 链路追踪数据，
> 写入飞书 Git 链路追踪文档，形成 任务→提交分组→用户Check→commit hash→测试结果→飞书记录 的完整链路。
>
> 本模板定义链路追踪文档的结构和各字段要求。

---

## 1. 母文档结构

Git 链路追踪母文档是一个飞书文档，标题固定为"**Git 链路追踪**"。每个 EasyWork 任务在母文档中追加一个新条目。

文档总览（按时间倒序）：
```
Git 链路追踪
├── 2026-06-20 — Bug修复：修复登录超时
│   ├── 提交分组概览（表格）
│   ├── 分组1详情
│   ├── 分组2详情
│   └── 测试结果
├── 2026-06-19 — 功能开发：新增用户导出
│   └── ...
```

---

## 2. 单次任务条目结构

### 任务标题

```
## {任务描述} — {日期}
```

- 任务描述：业务语言简述（"修复登录超时"而非"fix auth timeout"）
- 日期：YYYY-MM-DD

### 提交分组概览

一个表格，列说明：

| 列 | 说明 | 来源 |
|----|------|------|
| # | 分组序号 | `git_output.units[].index` |
| 维度 | config/logic/ui/test_docs | `git_output.units[].dimension` |
| 文件数 | 该分组涉及的改动文件数 | `git_output.units[].files.length` |
| 风险 | low/medium/high | `git_output.units[].risk_level` |
| Check | 开发者 Check 状态（初始为空，用户 commit 前填写） | 初始值：☐ 待Check |
| Commit Hash | 提交后的 hash（初始为空） | 初始值：`(待提交)` |
| 测试 | 测试结果引用 | 来自 EXAMINE 步骤 |

### 分组详情

每个 commit unit 一个子节：

```markdown
### {index}. {dimension} — {summary}

**改动文件**：
{文件清单，每文件一行}

**改动说明**（业务上下文）：
{business_context}
结合项目实际业务说明：
- 为什么要改这些文件
- 这些改动在业务上达成了什么效果
- 对用户/系统行为有什么影响

**引入风险**：
{risk_introduced}
具体说明：
- 什么场景下可能触发问题
- 影响范围是什么
- 缓解措施或回滚策略

**验证证据**：
{verification_evidence}
来自 EXAMINE 步骤的测试结果：
- 测试数量、通过/失败情况
- 覆盖的场景

**建议 Commit Message**：
  {type}({scope}): {subject}
  
  {body}

**开发者 Check**：
- [ ] 改动范围符合需求——只改了该改的，没有蔓延到无关模块
- [ ] 无意外副作用——检查了所有调用方和依赖方
- [ ] 测试覆盖充分——正常路径和异常路径都有测试
- [ ] 代码风格一致——与项目现有模式保持一致
- [ ] 文档/注释已更新——如有新增公共 API
```

### 测试结果

```markdown
### 测试结果

- 测试命令：{test_command}
- 总数：{total} | 通过：{passed} | 失败：{failed} | 跳过：{skipped}
- 测试结论：{EXAMINE verdict}

{如有新增测试，列出}
```

---

## 3. Git Tracking 数据字段定义

对应 data-contract 中的 `git_tracking` 字段：

```
git_tracking:
  task_description: string     # 任务描述（业务语言）
  task_date: string           # YYYY-MM-DD
  task_type: string           # Bug修复/功能开发/重构/微调/纯文档
  risk_level: string          # low/medium/high
  units: [{
    index: int
    dimension: string         # config/logic/ui/test_docs
    files: string[]           # 改动文件路径
    summary: string           # 改动简述
    business_context: string  # 业务上下文说明（🆕 v2.5 新增）
    risk_level: string
    risk_introduced: string   # 引入风险详细说明（🆕 v2.5 新增）
    verification_evidence: string  # 验证证据（🆕 v2.5 新增）
    commit_message:
      type: string            # feat/fix/refactor/test/docs/style/chore/perf/ci
      scope: string
      subject: string
      body: string            # 包含 改动原因/风险说明/验证方式（🆕 v2.5 增强）
    developer_checklist: [    # 逐项 Check 清单（🆕 v2.5 新增）
      scope_correct: bool
      no_side_effects: bool
      test_coverage: bool
      style_consistent: bool
      docs_updated: bool
    ]
    commit_hash: string       # 提交后回填（初始为 null）
  }]
  examine_result:
    test_command: string
    test_total: int
    test_passed: int
    test_failed: int
    test_skipped: int
    verdict: string           # pass/conditional_pass/fail
```

---

## 4. 数据流

```
READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → TALK → ASK
                                     │
                                     ├─ git_output (主产出)
                                     └─ git_tracking (链路追踪数据)
                                            │
                                            ▼
                                     lark-doc 后端
                                            │
                                     ┌──────┴──────┐
                                     │ 存在 Git     │ 不存在
                                     │ 追踪文档      │
                                     ▼              ▼
                                    追加条目到     在主文档中保留
                                    母文档         链路数据
```

---

## 5. 用户操作流程

1. Agent 完成 GIT 步骤，生成拆分方案 + 链路追踪数据
2. Agent 将数据写入飞书文档：
   - 主文档：GIT 拆分概要
   - Git 追踪文档：带 Check 清单的详细条目
3. 用户审查拆分方案，逐项 Check
4. 用户执行 `git-commands.sh` 完成提交
5. 用户（或后续 Agent 会话）回填 commit hash 到 Git 追踪文档
6. 飞书文档链接可发送给 Code Reviewer、QA、项目经理进行协作

---

## 6. 与本地 Git 操作的关系

- EasyWork **不自动执行** git add/commit/push（安全策略 §1）
- 本模板记录的是**意图和结果**，不是执行日志
- commit hash 回填是可选的——取决于团队是否在意链路完整性
- 即使不回填 hash，Check 清单 + 测试结果 + 改动说明已经形成有效的 Code Review 入口
