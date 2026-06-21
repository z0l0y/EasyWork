# Gate Dependency Graph（闸门依赖图）

> 补充设计 #12：文档化 EasyWork v2.12 全部 40 条铁律之间的依赖关系和闸门执行顺序。确保闸门按正确顺序执行，检测闸门冲突。

---

## 1. 全部 40 条铁律 → 闸门映射表

| 铁律 # | 闸门/规则名称 | 执行步骤 | 闸门类型 | 前置依赖铁律 | v2.12 风险等级门槛 |
|--------|------------|---------|---------|------------|------------------|
| 1 | 不确定时挂起询问 | 全部 | 全局 | — | 全部 |
| 2 | 每步完成后打卡 | 全部 | 全局 | — | 全部 |
| 3 | 产出物不丢失 | 全部 | 全局 | — | 全部 |
| 4 | 用户可随时叫停 | 全部 | 全局 | — | 全部 |
| 5 | 回退循环上限 3 次 | CODE↔REVIEW↔EXAMINE | 全局 | — | 全部 |
| 6 | 步骤预算 15 文件 | 全部 | 全局 | — | 全部 |
| 7 | 步骤间数据传递 | 全部 | 全局 | — | 全部 |
| 8 | 产物后端可插拔 | SUM | 全局 | — | 全部 |
| 9 | 步骤产出自检 | 每步 | 全局 | #7 | 全部 |
| 10 | 变更前 checkpoint | CODE | 全局 | — | L2+ |
| 11 | Git 写操作确认 | GIT | 全局 | — | L2+ |
| 12 | 输出内容脱敏 | SUM | 全局 | — | 全部 |
| 13 | 自定义步骤预确认 | READ | 全局 | — | 全部 |
| 14 | 文件写入限于项目目录 | CODE | 全局 | — | 全部 |
| 15 | 仅被显式调用时激活 | 启动 | 全局 | — | 全部 |
| 16 | 产物后端不可自行选择 | SUM | 全局 | #8 | 全部 |
| 17 | 飞书后端 MCP 前置检查 | SUM | 全局 | #8 | 全部 |
| 18 | SelfCheck 不可跳过 | SELFCHECK | 全局 | — | 全部 |
| 19 | 报告深度不可低于任务要求 | SUM | HARD | — | 全部 |
| 20 | 流式增量写入保障 | SUM | HARD | #19 | 全部 |
| 21 | 内容丰满度自检闸门 | SUM | HARD | #19 | L1+ |
| 22 | 报告类型与深度匹配 | SUM | 全局 | #19 | L1+ |
| 23 | CODE↔REVIEW 质量门禁 | CODE/REVIEW | HARD | #5 | L1+ |
| 24 | READ 需求理解显式确认 | READ | HARD | — | 全部 |
| 25 | 文档迭代增量更新 | SUM | HARD | #28, #36, #37 | L1+ |
| 26 | 交互式应用 EXAMINE 增强 | EXAMINE | HARD | — | L3+ |
| 27 | 反水文闸门 | SUM | HARD | — | L1+ |
| 28 | 文档拓扑闸门 | SUM | HARD | #25 | L1+ |
| 29 | 文档保真闸门 | SUM | HARD | #28, #25 | L1+ |
| **30** | **完成定义闸门** | **READ** | **HARD** | #24 | **全部** |
| **31** | **需求可追溯矩阵** | **READ** | **HARD** | #30 | **L1+** |
| **32** | **环境保真闸门** | **EXAMINE** | **HARD** | #26, #39 | **L3+** |
| **33** | **参考基线闸门** | **READ** | **HARD** | — | **L2+** |
| **34** | **测试充分性闸门** | **EXAMINE** | **HARD** | #31 | **L1+** |
| **35** | **重复失败触发器** | **CODE↔REVIEW↔EXAMINE** | **HARD** | #5 | **触发时** |
| **36** | **历史版本覆盖** | **SUM** | **HARD** | #28 | **L2+** |
| **37** | **来源出处闸门** | **SUM** | **HARD** | #36 | **L1+** |
| **38** | **证据账本** | **SUM** | **HARD** | #34, #31 | **L1+** |
| **39** | **风险分类闸门** | **READ(分类)** | **HARD** | — | **全部** |
| **40** | **上下文丢失防护** | **全部** | **HARD** | — | **全部** |

---

## 2. 闸门执行顺序 DAG

```
任务启动
    │
    ├─→ #39 Risk Classification (L0-L4) ──→ 确定适用闸门集
    ├─→ #40 Context Loss Protection (读 state file)
    │
    ▼
READ 阶段
    │
    ├─→ #30 Delivery Definition Gate ──→ #31 Traceability Matrix
    ├─→ #33 Reference Baseline Gate (L2+)
    ├─→ #24 READ 需求理解确认
    │
    ▼
CODE 阶段
    │
    ├─→ #23 CODE↔REVIEW 质量门禁 ←── #35 Repeated Failure Trigger (如触发)
    ├─→ #35 监测：同问题第2次失败 → BLOCK
    │
    ▼
EXAMINE 阶段
    │
    ├─→ #34 Test Adequacy Gate ←── #31 Traceability Matrix (测试覆盖与需求对齐)
    ├─→ #32 Environment Fidelity Gate (L3+) ←── #26 交互式应用增强
    │
    ▼
SUM 阶段 (write_final_report 前，按顺序)
    │
    ├─→ #28 Document Topology Gate
    ├─→ #36 Historical Version Coverage ←── #28 (先查拓扑再查覆盖)
    ├─→ #37 Source Provenance Gate ←── #36 (先查覆盖再查来源)
    ├─→ #29 Document Preservation Gate
    ├─→ #27 Anti-Fluff Gate
    ├─→ #38 Evidence Ledger ←── #34 (需要测试数据) ←── #31 (需要需求覆盖)
    ├─→ #30 补充：Delivery Verification Checklist
    ├─→ #21 Content Richness Self-Check
    ├─→ #19 Report Depth Check
    │
    ▼
SELFCHECK / ASK 阶段
    │
    └─→ #18 SelfCheck 不可跳过
```

---

## 3. 闸门冲突检测

### 冲突类型

| 冲突 | 涉及闸门 | 说明 |
|------|---------|------|
| L0 任务走 HARD GATE | #39 vs 全部 HARD GATE | L0 不应走 HARD GATE——风险分类应跳过 |
| Quick Fix vs Full Archive | #25 write_mode vs #29 C7 | quick_fix 不可执行 full overwrite |
| round_report vs engineering_active | #25 document_scope vs #29 C6 | round_report 不可 overwrite engineering_active |
| 第2次失败后继续 | #35 vs #5 | #35 应先于 #5 触发（第2次 vs 第3次） |
| 未 fetch 先 merge | #29 C5 vs #28 | 保真闸门的 C5 要求必须先 fetch——排在拓扑闸门之后 |
| 证据不足但声称完成 | #38 vs #21 | 内容丰满度 vs 证据账本——#21 要求内容完整，#38 要求有证据支撑 |

### 冲突解决规则

```
1. 风险等级优先：L0 任务即使触发 HARD GATE 也降级为 SOFT/SKIP
2. 阻断优先：任一 HARD GATE 阻断即可停止，不需继续后续闸门
3. 依赖优先：前置闸门通过后才执行后续闸门（如 #28→#36→#37）
4. 用户优先：用户显式确认可以覆盖任何闸门（记录覆盖原因）
```

---

## 4. 闸门执行检查算法

```
Algorithm: CHECK_GATE_ORDER

Input: risk_level (L0-L4), task_type, report_depth
Output: ordered_gate_list（按依赖排序的闸门列表）

1. 初始化 gate_list = []
2. 从 gate_dependency_graph 中取所有闸门
3. 对每个闸门：
     if 闸门.risk_level_threshold > risk_level:
        跳过（风险等级不够）
     if 闸门.task_type_excluded 包含 task_type:
        跳过（任务类型不适用）
4. 拓扑排序（尊重依赖边）
5. 验证：
     for each gate in gate_list:
         if gate.dependencies 中有未在 gate_list 中的闸门:
            报错："闸门 {gate} 依赖 {dep} 但 {dep} 不在执行列表中"
6. return gate_list
```

---

## 5. 反模式

- ❌ **跳过依赖闸门直接执行下游闸门**：不查拓扑(#28)就查覆盖(#36)——不知道有哪些节点
- ❌ **闸门执行顺序与依赖图冲突**：先查保真(#29)再查拓扑(#28)——#29 的 fetch-compare 需要拓扑信息
- ❌ **L4 任务按 L2 闸门集执行**：缺少 dry-run/备份/回滚——违反风险分类
- ❌ **HARD GATE 阻断后 Agent 自行"修复"继续**：必须先报告用户，不可静默通过
