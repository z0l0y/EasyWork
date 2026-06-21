# Evidence Ledger（证据账本）

> **铁律 #38**：每个交付轮次生成证据账本——结论/证据类型/证据位置/可复现？。证据样本数须满足最低门槛（L0:1条/L1:2条/L2:3条/L3:4条/L4:5条）。无证据样本 = 不可声称"完成"。
> 此闸门与 v2.9 ETR（每个结论有 Evidence/Thinking/Risk）互补——ETR 是质量要求，Evidence Ledger 是汇总索引表（所有证据可扫描、可追溯）。

---

## 1. 账本结构

### 账本行格式

| # | 结论 | 证据类型 | 证据位置 | 可复现？ |
|---|------|---------|---------|---------|
| E1 | 登录 P99 延迟从 2.8s 降到 320ms | METRIC | `EXAMINE: perf_test_output` 第 3-5 行 | ✅ `ab -n 1000 -c 10 /api/login` |
| E2 | 密码为空时返回 400（非 500） | TEST_OUTPUT | `tests/login/boundary.test.ts:42-58` | ✅ `npm test -- --testPathPattern=boundary` |
| E3 | Token 刷新逻辑修复：过期 Token 刷新后旧 Token 立即失效 | CODE_DIFF | `auth.service.ts:120-145` (commit def5678) | ✅ 代码审查 + 测试验证 |
| E4 | Safari 17 上登录页无白屏 | SCREENSHOT | 手动验证：Safari 17, macOS 14, 1920×1080 | ⚠️ 需手动复现（Safari 17 非 CI 环境） |

### 证据项定义

| 字段 | 含义 | 要求 |
|------|------|------|
| **结论** | 从工作流产出的关键结论（1句话） | 必须可验证——非"功能正常" |
| **证据类型** | 支持此结论的证据类别 | 必须是六种枚举之一 |
| **证据位置** | 到哪里找这个证据 | 具体到文件路径+行号 或 URL |
| **可复现？** | 能不能用自动化方式重新生成此证据 | ✅（命令可复现）/ ⚠️（需手动/特定环境）/ ❌（一次性） |

---

## 2. 证据类型枚举

| 类型 | 含义 | 示例位置 |
|------|------|---------|
| **TEST_OUTPUT** | 测试命令+关键输出 | `EXAMINE step output: test_results` |
| **CODE_DIFF** | 代码变更摘录（含路径+行号） | `CODE step output: code_excerpts[0]` |
| **LOG_ENTRY** | 日志条目/错误信息 | `修复前错误日志：/var/log/app.log:342` |
| **SCREENSHOT** | 截图/界面描述 | `手动验证：Chrome 125, Login page, 1920×1080` |
| **METRIC** | 量化对比表/指标数据 | `EXAMINE: perf_comparison_table` |
| **CONFIRMATION** | 用户确认记录 | `ASK 步骤：用户确认"已完成，符合预期"` |

### 证据类型与步骤产出的映射

| 类型 | 来源步骤 | data-contract 字段 |
|------|---------|-------------------|
| TEST_OUTPUT | EXAMINE | `examine_output.test_results` / `test_output_snippet` |
| CODE_DIFF | CODE | `code_output.code_excerpts` / `files_changed` |
| LOG_ENTRY | READ | `read_output` 中的报错日志/监控告警 |
| SCREENSHOT | EXAMINE | `examine_output.interactive_ux_validation` |
| METRIC | EXAMINE / SUM | `examine_output.perf_comparison` / `sum_output.outcome` |
| CONFIRMATION | ASK / READ | `ask_output.user_confirmations` / `read_output.understanding_confirmation` |

---

## 3. 最低证据样本数

| 风险等级 | 最低证据数 | 必须包含的证据类型 | 说明 |
|---------|-----------|-----------------|------|
| **L0** | 1 | CODE_DIFF 或 CONFIRMATION | 纯查询任务：代码位置引用或用户确认即足够 |
| **L1** | 2 | TEST_OUTPUT（如修Bug）或 CODE_DIFF | 小修复：至少测试输出+代码变更 |
| **L2** | 3 | TEST_OUTPUT + CODE_DIFF | 正常功能：测试+代码+至少一个其他类型 |
| **L3** | 4 | TEST_OUTPUT + CODE_DIFF + METRIC | 交互式/并发：+性能指标 |
| **L4** | 5 | 全部六种类型至少各一 | 数据迁移/权限/部署：全类型证据覆盖 |

### 证据质量要求

每条证据必须满足：
- **可定位**：证据位置不是"见上文"——具体的文件路径+行号或 URL
- **可验证**：可复现为 ✅ 或 ⚠️ 且有说明——不能全部为 ❌
- **不重复**：不同结论用不同证据——不能 5 条结论都指向同一条测试输出

---

## 4. 与 ETR（v2.9）的关系

| 维度 | ETR（v2.9） | Evidence Ledger（v2.12） |
|------|-----------|----------------------|
| **粒度** | 每个关键结论有 E/T/R | 所有结论汇总到一个索引表 |
| **格式** | 内联在报告文本中 | 独立的 Markdown 表格 |
| **用途** | 写作质量——确保结论不凭空出现 | 可追溯性——确保所有结论有据可查 |
| **强制性** | 写作规范（SOFT GATE） | HARD GATE——证据数不达标不可写入 |

**互补关系**：
- ETR 确保"写报告的时候每条结论都附带了证据"（写作质量）
- Evidence Ledger 确保"报告写完后所有证据汇总成一个可扫描的索引"（可追溯性）
- Ledger 不替代 ETR——两者共存，互相验证

---

## 5. 账本输出格式

```markdown
## 📒 证据账本（Evidence Ledger）

### 账本索引

| # | 结论 | 证据类型 | 证据位置 | 可复现？ |
|---|------|---------|---------|---------|
| E1 | 登录 P99 从 2.8s 降到 320ms | METRIC | `EXAMINE: perf_comparison_table` 第 3 行 | ✅ `ab -n 1000 -c 10` |
| E2 | 空密码返回 400 非 500 | TEST_OUTPUT | `tests/login/boundary.test.ts:42` | ✅ `npm test -- boundary` |
| E3 | Token 刷新后旧 Token 立即失效 | CODE_DIFF | `auth.service.ts:120-145` (def5678) | ✅ Code Review + 测试 |
| E4 | Safari 17 登录页无白屏 | SCREENSHOT | 手动验证：Safari 17/macOS 14 | ⚠️ 需手动复现 |

### 证据统计

| 指标 | 值 |
|------|-----|
| 风险等级 | L2 — 正常功能 |
| 最低要求 | 3 条 |
| 实际提交 | 4 条 |
| 必须包含类型 | TEST_OUTPUT ✅, CODE_DIFF ✅ |
| 证据类型分布 | METRIC:1, TEST_OUTPUT:1, CODE_DIFF:1, SCREENSHOT:1 |

### 证据充分性判定

✅ 证据充分（4/3 ≥ 最低要求）。所有结论有据可查。
```

---

## 6. Gate Judgment Rules

| 深度 | 闸门类型 | 命中处理 |
|------|---------|---------|
| **detailed** | **HARD GATE** | 证据样本数 < 最低门槛 → 阻断写入 → 补充证据 |
| **standard** | **SOFT GATE** | 警告但允许（标注"证据不足"） |
| **brief** | **SKIP** | 跳过（L0/L1） |

### 证据数不达标的处理

```
证据数 < 最低门槛：
  → 从 step_outputs 中搜索可用的证据源
  → 优先补充：TEST_OUTPUT > CODE_DIFF > METRIC > 其他
  → 如果确实无法补充（如纯理解任务无测试）→ 标注原因 + 用户确认豁免
```

---

## 7. 反模式

- ❌ **所有证据位置写"见上文"**：不可定位——必须有具体路径+行号
- ❌ **用同一个测试输出充当 5 条不同结论的证据**：1 条测试只能支持 1 条结论——需要不同的证据
- ❌ **证据全标"可复现"但没有任何命令**：`✅ 可复现` 但没有写复现命令——不可验证
- ❌ **用"代码已提交"充当证据**：commit hash 不是证据类型——需要 CODE_DIFF 摘录具体内容
- ❌ **证据数刚好等于最低门槛但全是同一种类型**：L2 要求 TEST_OUTPUT + CODE_DIFF——不能 3 条全是 METRIC
