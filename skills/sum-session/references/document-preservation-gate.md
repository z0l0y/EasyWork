# Document Preservation Gate（文档保真闸门）

> **铁律 #29**：写入文档之前必须检查内容保真度。文档结构合格（通过拓扑闸门）≠ 内容合格。文档更新后字数/证据密度/历史版本数不得下降。
> 对已有正式工程文档，默认使用局部更新（Normal），禁止无基准 overwrite。本轮报告可以短（round_report），但正式文档不能因为本轮报告短而变短（engineering_active）。

---

## 1. 什么是内容退化

内容退化（Content Degradation）指文档在多次迭代更新后，虽然拓扑结构合法，但**内容质量持续下降**：

| 退化形式 | 表现 | 根因 |
|---------|------|------|
| 字数缩水 | v1 有 3000 字，v3 只剩 800 字 | 每轮 overwrite 时只写了当轮摘要，丢失了前面版本的详细内容 |
| 证据密度下降 | v1 有 5 处代码摘录+测试输出，v3 只剩"测试通过" | Agent 凭记忆写报告，未保留 step_output 中的证据 |
| 历史版本丢失 | 版本索引说到了 v3，但节点内只剩 v3 的版本小节 | 未 fetch 现有文档直接 overwrite，旧版本小节被覆盖 |
| 流程节点缩减 | v1 有 READ/CODE/REVIEW/EXAMINE 四个节点，v3 只剩 CODE | Overwrite 时只写了本轮涉及的节点，其余节点被丢弃 |
| 轮次摘要冒充正式文档 | Quick Fix 的 3 句话被当成整篇文档写入 | round_report 内容 overwrite 了 engineering_active |

**核心原则**：文档是持续演进的知识库。每次更新是**追加**（add），不是**替换**（replace）。内容只增不减，版本只进不退。

---

## 2. 七项内容保真检查

### Check C1 — 内容长度退化

**检测方法**：
1. Fetch 现有文档 → 统计总字数（中文字 + 英文单词，不含 Markdown 标记符号如 `#` `|` `-` `*` `[]` `()`）
2. 执行 structured merge → 统计 merge 后文档总字数
3. 对比：若 merge 后字数 < 现有文档字数的 80% → 阻断

**违规示例**：
```
现有文档：3500 字（含 READ/CODE/REVIEW/EXAMINE 四个节点的完整内容）
Merge 后：1200 字（只有本轮的 CODE 变更摘要，其余节点内容丢失）
→ C1 阻断：merge 后字数仅为 34%，远低于 80% 阈值
```

**判定**：
| 模式 | 处理 |
|------|------|
| 任一 | **HARD GATE** — 字数不达标 80% 阈值 → 阻断写入，回退补全内容 |

**修复**：从 `all_step_outputs` 中提取完整步骤产出，补入对应流程节点。不可仅写摘要。

**阈值说明**：
- 80% 阈值考虑正常的编辑精简（如重写表述、删除冗余措辞）
- 纯新增内容（如 Bug 修复在不改动其他节点的情况下新增 v{N} 小节）不应导致字数下降
- 如果确实需要大幅缩减（如用户要求"精简文档"），需用户显式确认

---

### Check C2 — 证据密度下降

**检测方法**：
统计以下三类"证据锚点"的数量，merge 前后对比：

| 证据类型 | 检测模式 | 示例 |
|---------|---------|------|
| 代码摘录 | 含文件路径+行号的代码引用（如 `auth.service.ts:88-95`） | `**变更位置**：auth.service.ts:88` |
| 测试输出 | 含终端命令+输出的测试证据块 | `go test -v -run TestAuth` + 输出片段 |
| 数据对比 | 含数值的对比表（至少 2 列 × 2 行） | `| 指标 | 修改前 | 修改后 |` |

**判定**：
| 模式 | 处理 |
|------|------|
| 任一 | 任一类证据数下降 → **HARD GATE** — 阻断写入 |
| 例外 | 如果本轮未涉及某类证据（如纯文档任务无测试）→ 该维度不参与比较 |

**修复**：从 `all_step_outputs` 中回补缺失的证据——代码摘录从 `code_output.code_excerpts`、测试输出从 `examine_output.test_output_snippet`、数据对比从 `examine_output` 或 `read_output.acceptance_criteria`。

---

### Check C3 — 历史版本丢失

**检测方法**：
1. 统计现有文档中所有 `### v{N}` 子节的总数（跨所有流程节点）
2. 统计 merge 后文档中所有 `### v{N}` 子节的总数
3. 若数量下降 → 版本丢失 → 阻断

**违规示例**：
```
现有文档：
  ## 1. READ
    ### v1 — 2026-06-18（初始）     ← 1
    ### v2 — 2026-06-20（补充）     ← 2
  ## 2. CODE
    ### v1 — 2026-06-18（初始）     ← 3
    ### v2 — 2026-06-20（变更）     ← 4
    ### v3 — 2026-06-21（变更）     ← 5
  共 5 个版本小节

Merge 后：
  ## 1. READ
    ### v3 — 2026-06-21（补充）     ← 只剩 1 个
  ## 2. CODE
    ### v3 — 2026-06-21（变更）     ← 只剩 1 个
  共 2 个版本小节

→ C3 阻断：丢失了 v1, v2 共 3 个版本小节
```

**判定**：
| 模式 | 处理 |
|------|------|
| Mode B | **HARD GATE** — 版本数下降即阻断。版本只增不减 |
| Mode A | 不直接比较（每 Run 自包含），但 Run 数量不得减少 |

**修复**：从 fetch 的现有文档中恢复丢失的 `### v{N}` 小节，归位到对应流程节点下。

---

### Check C4 — 流程节点缩减

**检测方法**：
1. 统计现有文档中顶层流程节点（`## \d+\. (READ|CODE|REVIEW|EXAMINE|GIT|GRAPH|SUM|TALK|SELFCHECK|ASK)`）的数量
2. 统计 merge 后文档中顶层流程节点的数量
3. 若数量下降 → 节点丢失 → 阻断

**违规示例**：
```
现有文档：
  ## 1. READ
  ## 2. CODE
  ## 3. REVIEW
  ## 4. EXAMINE
  共 4 个流程节点

Merge 后：
  ## 2. CODE
  共 1 个流程节点

→ C4 阻断：丢失了 READ, REVIEW, EXAMINE 三个节点
```

**判定**：
| 模式 | 处理 |
|------|------|
| Mode B | **HARD GATE** — 节点数下降即阻断。每个已有节点的历史内容必须保留 |
| Mode A | N/A（每个 Run 自包含，节点数因 Run 而异） |

**修复**：从 fetch 的现有文档中恢复丢失的流程节点及其全部历史版本小节。

---

### Check C5 — 无基准覆写

**检测方法**：
检查 `structured_merge_plan.existing_doc_fetched` 是否为 `true`。若为 `false` 且 `write_mode` ≠ `full_archive`（首次创建）→ 阻断。

**违规信号**：
- 未执行 Step 1（Fetch 现有文档）就直接进入写入流程
- Agent 凭"记忆中"的文档内容进行写入
- `existing_doc_fetched = false` 但文档 ID 指向已有文档

**判定**：
| 模式 | 处理 |
|------|------|
| 任一 | **HARD GATE** — 无基准即阻断。必须先读后写 |
| 例外 | 首次创建（新文档，无已有产物）— 标记为 `existing_doc_fetched: n/a (new)` |

**修复**：立即执行 Fetch——读取已有文档完整内容 → 重新执行 Topology Gate + Preservation Gate。

---

### Check C6 — round_report 冒充 engineering_active

**检测方法**：
检查待写入内容是否满足以下**全部 3 条**简易信号（同时满足即判定为 round_report）：

1. 总字数 < 500 字
2. 无代码摘录（不含文件路径+行号的代码引用）
3. 无版本小节（不含 `### v{N}` 格式的版本子标题）

**判定**：
| 条件 | 处理 |
|------|------|
| 3 条全满足 + document_scope = engineering_active | **HARD GATE** — 阻断覆写，重定向为 Quick Fix 追加版本记录 |
| 3 条全满足 + document_scope = round_report | 放行（round_report 本就允许简短） |
| 不满足（≥1 条不满足） | 放行 |

**修复**：
- 如果用户只需要快速记录 → 切换 `document_scope = "round_report"`，生成独立的简短摘要
- 如果用户需要更新正式文档 → 回退到各步骤补充完整产出，再执行 merge

---

### Check C7 — 写入模式错配

**检测方法**：

| 错配类型 | 检测信号 | 处理 |
|---------|---------|------|
| Quick Fix → Overwrite | `write_mode = "quick_fix"` 但执行了 full overwrite（非局部追加） | **HARD GATE** — 阻断，强制改为局部追加 |
| Normal → 摘要级内容 | `write_mode = "normal"` 但内容 < 800 字 且 无代码摘录 | **HARD GATE** — 阻断，要求补全内容 |
| Full Archive → 无 checklist | `write_mode = "full_archive"` 但未附带 preservation checklist | **HARD GATE** — 阻断，要求完成 checklist |

**判定**：
| 模式 | 处理 |
|------|------|
| 任一 | **HARD GATE** — 模式与行为不符即阻断 |

**修复**：根据实际意图切换 write_mode 或调整写入行为。

---

## 3. Anti-Overwrite Rules（禁止无基准覆写）

### R1 — 已有文档默认局部更新

**规则**：对已有正式工程文档（已有 `engineering_active` 产物），**默认使用 Normal 模式**（structured merge），禁止把本轮总结当成整篇文档 overwrite。

**适用条件**：`existing_doc_fetched = true` 且 `write_mode` 未显式声明 → 默认为 `normal`

**违规处理**：检测到 overwrite 行为但 write_mode 不是 `full_archive` → 阻断，要求改用 Normal

---

### R2 — Overwrite 必须附带 Preservation Checklist

**规则**：任何 `write_mode = "full_archive"` 的写入操作，必须在写入前完成 §6 的 7 项 Preservation Checklist，逐项打勾确认。

**适用条件**：`write_mode = "full_archive"`

**违规处理**：未完成 checklist → 阻断写入，回退补充 checklist

---

### R3 — Quick Fix 禁止覆写正式文档

**规则**：`write_mode = "quick_fix"` 的写入**只允许**：
1. 在版本索引表追加一行新版本记录
2. 在受影响节点下新增 `### v{N} — {date}（{变更类型}）` 小节
3. 保留其他所有内容**完全不变**

**禁止**：
- 替换/删除/修改任何已有版本小节的内容
- 删除/合并已有流程节点
- 重写版本索引（仅追加行，不重建）

**违规处理**：检测到 quick_fix 执行了超出上述范围的操作 → 阻断，回滚到写入前状态

---

### R4 — round_report 不得 overwrite engineering_active

**规则**：`document_scope = "round_report"` 的内容**不得写入** `engineering_active` 的产物路径。
- round_report → 输出到聊天回复 或 `.claude/easywork/round_reports/`
- engineering_active → 输出到正式产物后端（local_html/markdown/lark_doc）

**混用阻断**：检测到 round_report 内容试图写入 engineering_active 路径 → 阻断

**正确做法**：
- 本轮改动小但需要更新正式文档 → `write_mode = "quick_fix"` + `document_scope = "engineering_active"` → 追加版本记录
- 本轮只需要聊天汇报 → `document_scope = "round_report"` → 简短摘要输出到聊天

---

### R5 — Overwrite 仅限三种合法场景

**规则**：`write_mode = "full_archive"`（全量覆写）仅在以下三种场景合法：

| # | 场景 | 前置条件 |
|---|------|---------|
| 1 | **首次创建** | 无已有产物文档 |
| 2 | **用户明确要求重写整篇** | 用户说"重写整篇""全量重建""完整重写""重新生成整个文档" |
| 3 | **已拿当前全文做了完整 merge** | 已完成 Fetch→Parse→Pre-check(Topo+Preservation)→Distribute→Index→Mark，且 Preservation Gate 全部 C1-C7 通过 |

**违规处理**：不符合以上任一场景的 overwrite → 阻断，强制降级为 Normal（structured merge）

---

### R6 — Overwrite 后必须 fetch-compare

**规则**：任何 `write_mode = "full_archive"` 写入完成后，**必须立即 fetch 回读**，执行内容保真对比：

1. 字数对比：写入后字数 ≥ 写入前字数 × 80%
2. 证据密度对比：写入后证据数 ≥ 写入前证据数
3. 版本数对比：写入后版本小节数 ≥ 写入前版本小节数
4. 节点数对比：写入后流程节点数 ≥ 写入前流程节点数（Mode B）

**发现退化** → 立即报告用户 → 回滚到写入前版本 → 分析退化原因 → 重新 merge

---

## 4. Write Mode Classification（写入模式三级分类）

### 模式总览

| 模式 | 名称 | 适用场景 | 写入行为 | 可否 Overwrite |
|------|------|---------|---------|---------------|
| **quick_fix** | 快速记录 | 微调（typo/config/样式）、<5 行改动、无新增逻辑、report_depth=brief | 仅追加：版本索引 +1 行 + 受影响节点下 `### v{N}` 小节 | **NEVER** |
| **normal** | 正常更新 | 标准功能开发/Bug 修复/重构（**DEFAULT**） | Full structured merge：Fetch→Parse→Pre-check(Topo+Preservation)→Distribute→Index→Mark→Verify | 仅限完整 merge 后 |
| **full_archive** | 全量重建 | 首次创建 / 用户明确要求重写 / 已有全文完整 merge | 全量写入，附带 preservation checklist + post-write fetch-compare | 仅限三合法场景 |

### 模式选择决策树

```
新任务 → 是否有已有产物文档？
  ├── 否 → 新文档 → normal（首次创建初始化结构，实质是 full_archive 的合法场景 #1）
  └── 是 → Fetch 已有文档 → 判断任务规模 →
        ├── 微调任务（task_type=微调 或 report_depth=brief）→ quick_fix
        │     └── 仅追加版本记录，不覆写已有内容
        ├── 标准任务 → normal（DEFAULT）
        │     └── 执行完整 structured merge
        └── 用户明确说"重写整篇""全量重建""完整重写" →
              └── 已 fetch 当前全文 + 完成 merge → full_archive
              └── 未 fetch → 先执行 fetch + merge，再决定

用户显式指示：
  - "快速记录一下""小改动，记录一下" → quick_fix
  - 未说明 → normal（DEFAULT）
  - "重写整篇""全量重建""完整重写" → full_archive（需验证前置条件）
```

### Quick Fix 详细行为规范

**允许的操作**：
1. 在 `## 0. 版本索引` 表格追加一行新版本记录
2. 在受影响的流程节点下新增 `### v{N} — {date}（{变更类型}）` 小节
3. 更新版本索引中"当前版本"字段
4. 如涉及修改已有结论，在旧版本小节前追加 `[已过时 — v{N} 起]` 标记

**禁止的操作**：
- 删除/修改任何已有版本小节内的一段文字
- 删除/合并任何已有流程节点（`## 1-10`）
- 重建/重写版本索引表（只能追加行）
- 修改文档标题或元信息
- 删除任何 `[已过时]` 标记

---

## 5. Document Scope（文档作用域）

### 两种作用域

| 作用域 | 标识 | 用途 | 可短？ | 可覆写正式文档？ | 典型存储位置 |
|--------|------|------|--------|-----------------|-------------|
| **round_report** | `round_report` | 当前轮摘要——聊天回复、快速沟通、敏捷站会汇报 | YES（1-2 页，六要素概要） | **NEVER** | 聊天输出 / `.claude/easywork/round_reports/` |
| **engineering_active** | `engineering_active` | 长期工程档案——Code Review 参考、团队交接、合规审计 | NO（保留全部历史版本） | 仅限 full_archive 三合法场景 | 正式产物后端（local_html / markdown / lark_doc） |

### 混用阻断规则

| 违规行为 | 检测方法 | 处理 |
|---------|---------|------|
| round_report → engineering_active 路径 | `document_scope = "round_report"` 但调用了 `write_final_report` → 正式后端 | 阻断 → 改为聊天输出或存储到 round_reports 目录 |
| engineering_active 因 Quick Fix 缩短 | 文档字数/证据/版本数下降 | C1-C4 阻断 |
| 用户说"记录一下"未指明作用域 | 无法判断 | Agent **必须追问**：记录为 round_report（聊天摘要）还是更新 engineering_active（正式文档） |

### round_report 格式要求

round_report 允许简短，但必须包含：
1. 本轮做了什么（1-2 句）
2. 改了什么文件/关键代码位置（至少 1 处含路径+行号）
3. 结果如何（测试通过/验收确认）
4. 标注 `⚠️ 本报告为轮次摘要（round_report），非正式工程文档。详细内容见 engineering_active。`

---

## 6. Preservation Checklist（覆写前置检查清单）

以下 7 项必须在 `write_mode = "full_archive"` 写入前逐项确认：

```
【Preservation Checklist】— write_mode=full_archive

- [ ] 1. 已 Fetch 当前完整文档（非凭记忆）
- [ ] 2. 已完成 Structured Merge（Fetch→Parse→Pre-check→Distribute→Index→Mark）
- [ ] 3. Topology Gate 已通过（7 项检查均 PASS 或已修复）
- [ ] 4. Preservation Gate C1-C7 已执行且全部通过
- [ ] 5. 待写入内容字数 ≥ 现有文档字数 × 80%（C1）
- [ ] 6. 待写入内容证据数 ≥ 现有文档证据数（C2）
- [ ] 7. 待写入内容版本数 ≥ 现有文档版本数（C3）

以上任一项为否 → 禁止 overwrite → 降级为 normal（structured merge）
```

---

## 7. Fetch-Compare Methodology（取回对比方法）

### 字数统计规则

```
字数 = 中文字符数 + 英文单词数

中文字符：Unicode 范围 一-鿿 㐀-䶿
英文单词：连续 [A-Za-z0-9]+ 序列

不计数：
  - Markdown 标记符号：# ## ### | - * [] () ` ``` ~~
  - 空白行
  - 表格分隔行（如 |------|------|）
  - 代码块围栏（```）
  - HTML 标签（如有）
  - URL（仅计链接文本，不计 URL 本身）

可计数：
  - 代码块内的注释和字符串文字
  - 表格内的文字内容
  - 版本索引表内的文字
```

### 证据密度统计规则

```
证据锚点类型及检测模式：
  1. 代码摘录：匹配 "文件路径:行号" 模式
     - 如 "auth.service.ts:88-95"、"styles/layout.css:45"
     - 或 "**变更位置**：`...`"
  2. 测试输出：匹配测试命令 + 输出片段
     - 如 "go test -v"、"npm test"、"pytest" + 后续输出行
     - 或 "**测试命令**" / "**关键输出**" 段落
  3. 数据对比：匹配对比表
     - 含 "指标" + "修改前" + "修改后" 表头的表格
     - 或 "| 指标 | ... | ... | 变化 |" 格式的对比表
```

### 版本计数规则

```
统计模式：扫描所有 "### v\d+" 标题（跨所有流程节点 ## 1-10）
  每个 ### v{N} 子标题计为 1 个版本记录
  Mode A：改统计 "## Run" 标题数
```

### 节点计数规则

```
统计模式：扫描所有 "## \d+\. (READ|CODE|REVIEW|EXAMINE|GIT|GRAPH|SUM|TALK|SELFCHECK|ASK)" 标题
  不统计 "## 0. 版本索引"（非流程节点）
  不统计 "## Run"（Mode A 用 Run 数）
```

---

## 8. Content Fidelity Snapshot Format（内容保真快照）

在 merge 前后各保存一份快照，用于 Preservation Gate 判定和事后审计：

```
content_fidelity_snapshot:
  before_write:
    word_count: 3500
    evidence:
      code_excerpts: 5
      test_outputs: 3
      data_tables: 2
      total: 10
    version_count: 5       # ### v{N} 小节总数
    node_count: 4          # 流程节点数（Mode B）
    mode: "continuous_maintenance"
  after_write:
    word_count: 4200
    evidence:
      code_excerpts: 5
      test_outputs: 3
      data_tables: 2
      total: 10
    version_count: 6       # 新增了 v4
    node_count: 4
  degraded: false
  comparison:
    word_count_ratio: 1.20     # 4200/3500 — 增长 20%
    evidence_ok: true
    version_ok: true
    node_ok: true
```

---

## 9. Gate 判定规则

| 深度 | 闸门类型 | 命中处理 |
|------|---------|---------|
| **detailed** | **HARD GATE** | 任一 C1-C7 命中 → 拒绝写入 → 执行修复动作 → 重新检测（最多 2 轮）。2 轮后仍不通过 → 挂起报告用户，列出退化指标和修复尝试 |
| **standard** | **SOFT GATE** | 展示退化指标 → 用户确认是否继续（默认修复） |
| **brief** | 跳过 | 标注 "⚠️ 简要摘要 — 内容保真未经检查，不适合工程追溯" |

### 与 Topology Gate 的关系

```
写入前执行顺序：
  1. Document Topology Gate（铁律 #28）— 检查结构
     → 通过（或自动修复后通过）
  2. Document Preservation Gate（铁律 #29）— 检查内容
     → 通过（或修复后通过）
  3. Write（执行写入）
  4. Write-then-Fetch Verification（v2.9）— 检查写入完整性

两道闸门互补：Topology Gate 确保"骨架对"，Preservation Gate 确保"血肉没少"。
```

### 检测报告格式

```
【Document Preservation Gate】— document_mode={Mode B} write_mode={normal}

Content Fidelity Comparison:
  Before: 3500 字 / 10 证据 / 5 版本 / 4 节点
  After:  4200 字 / 10 证据 / 6 版本 / 4 节点

| # | 检查项 | 状态 | 详情 |
|---|--------|------|------|
| C1 | 内容长度退化 | ✅ | 4200/3500 = 120% — 未退化 |
| C2 | 证据密度下降 | ✅ | 10/10 — 未下降 |
| C3 | 历史版本丢失 | ✅ | 6/5 — 新增 v4 |
| C4 | 流程节点缩减 | ✅ | 4/4 — 未缩减 |
| C5 | 无基准覆写 | ✅ | 已 fetch 现有文档 |
| C6 | round_report冒充 | ✅ | 含代码摘录+版本小节，非摘要 |
| C7 | 写入模式错配 | ✅ | normal + structured merge — 匹配 |

总体判定：pass ✅
```

---

## 10. 反模式

- ❌ 未 fetch 现有文档直接 overwrite——无基准覆写，丢失全部历史内容（C5）
- ❌ Quick Fix 时把整篇文档替换为 3 句话摘要——round_report 冒充 engineering_active（C6+R3）
- ❌ 本轮只改了 1 个文件 5 行代码，却重写了整个工程文档——write_mode 错配，应用 quick_fix（C7）
- ❌ Merge 后 READ/REVIEW/EXAMINE 节点消失——流程节点缩减，丢失历史（C4）
- ❌ 新版本小节替代了旧版本小节而非追加——历史版本丢失（C3）
- ❌ 用聊天回复的简短总结覆盖正式文档——round_report overwrite engineering_active（R4）
- ❌ Overwrite 前不做 preservation checklist——违反 R2
- ❌ 已有文档使用 overwrite 而非 structured merge——违反 R1，应默认 Normal
- ❌ 用户说"记录一下"不追问是 round_report 还是 engineering_active——作用域不明确
- ❌ Overwrite 后不 fetch-compare——无法发现内容退化（R6）
- ❌ 以"本轮改动小"为由删减文档其他部分——Quick Fix 只能追加，不能缩减
- ❌ 跳过 Preservation Gate 直接写入——detailed 模式下此为 HARD GATE（铁律 #29）
