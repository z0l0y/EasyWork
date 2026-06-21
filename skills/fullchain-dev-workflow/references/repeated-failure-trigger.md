# Repeated Failure Trigger（重复失败触发器）

> **铁律 #35**：同一问题修复失败两次 → BLOCK 进一步小修补。必须输出——前两次为何未修复根因、正确的问题模型、新测试如何覆盖旧盲区、哪些假设需用户确认。Agent 不可自行解除 BLOCK。
> 此触发器在第 2 次失败时生效（非第 3 次），优先级高于铁律 #5 的回退上限（3 次）。

---

## 1. 触发条件

以下任一条件满足时触发：

### 条件 A：同函数/文件连续修复失败

```
同一文件的同一函数/逻辑块：
  Round 1: CODE→REVIEW→阻断（REVIEW发现阻断性问题） 或  EXAMINE→测试失败
  Round 2: CODE（修复）→REVIEW→再阻断 或  EXAMINE→测试仍失败
  → TRIGGER: repeated_failure_trigger
```

### 条件 B：同 Bug 跨回退轮次失败

```
同一 Bug（相同 test_name 或 相同 error message）：
  CODE↔REVIEW 回退 Round 1: 修复→REVIEW通过→EXAMINE→测试FAIL
  CODE↔REVIEW 回退 Round 2: 再修复→REVIEW通过→EXAMINE→测试仍FAIL
  → TRIGGER: repeated_failure_trigger
```

### 条件 C：两轮修复后 SELFCHECK 仍质疑同一方案

```
Round 1: CODE→REVIEW→EXAMINE→SELFCHECK→"方案层面缺陷"→回退CODE
Round 2: CODE→REVIEW→EXAMINE→SELFCHECK→"修正后方案仍有同样缺陷"
  → TRIGGER: repeated_failure_trigger
```

### 不触发的情况

```
以下情况不算"重复失败"：
  - 不同文件的独立问题 → 独立跟踪
  - 第一轮修复了 A，第二轮发现了新问题 B（B 不是 A 的衍生）→ 不算重复
  - 用户主动更换了方案 → 重置计数
```

---

## 2. BLOCK 后的强制输出

触发后，Agent **必须立即停止**代码修改操作，输出以下四要素：

### 2.1 根因分析：为什么前两次没修好根因

```markdown
### 🔍 重复失败根因分析

#### 失败记录

| 轮次 | 修复方案 | 修复内容 | 失败表现 | 失败阶段 |
|------|---------|---------|---------|---------|
| Round 1 | {方案 1 简述} | {改了哪些} | {失败表现} | REVIEW / EXAMINE |
| Round 2 | {方案 2 简述} | {改了哪些} | {失败表现} | REVIEW / EXAMINE |

#### 为什么前两次没修好根因？

1. **Round 1 失败根因**：{不是"代码写错了"，而是"为什么这个修复方向不对"}
   - 例："Round 1 修复了 UserService 中的空值判断，但实际问题在 AuthMiddleware 中将 null user 传递给了下游——应该在源头修复"

2. **Round 2 失败根因**：{同上，深度分析}
   - 例："Round 2 在 AuthMiddleware 加了 null check，但没有处理 null user 的 session 清理——导致 token 仍然有效但 user 为 null"

3. **真正的根因**：{跨轮次的系统性根因}
   - 例："根本问题不是 null check——是 user session 的生命周期管理：session 创建时 user 必然非 null，但后续 user 被删除时 session 未同步失效"
```

### 2.2 正确模型：对问题的正确理解

```markdown
### 📐 正确的问题模型

#### 之前理解的错误模型
{用 3-5 句话描述——Agent 之前对问题的理解方式}

例："之前认为：'UserService.getUser() 可能返回 null，需要在所有调用处加 null check'
     这个理解错在：______"

#### 修正后的正确模型
{用 3-5 句话描述——修正后对问题的正确理解}

例："正确理解：'user 不会凭空变 null——是 session 未随 user 删除而失效。修复方向不是防御性 null check，而是 session-user 生命周期一致性'"
```

### 2.3 新测试覆盖：如何防止旧盲区

```markdown
### 🧪 新测试覆盖旧盲区

#### 前两轮的测试盲区
| 盲区 | 为什么前两轮的测试没覆盖 |
|------|----------------------|
| {盲区 1} | {原因} |
| {盲区 2} | {原因} |

#### 新测试计划
| # | 新测试 | 覆盖的盲区 | 如何确保不再遗漏 |
|---|--------|----------|----------------|
| 1 | {test_name} | {盲区} | {具体方法} |
```

### 2.4 需用户确认的假设

```markdown
### ❓ 需要用户确认的假设

以下假设如果不成立，当前修复方案可能仍然不对：

1. **假设 {N}**：{假设内容}
   - 为什么这个假设需要确认：{理由}
   - 如果假设不成立 → 替代方案：{备选}

2. **假设 {N+1}**：{假设内容}
   - ...

→ 请确认以上假设，或提供修正信息。确认后我将按正确模型重新实施。
```

---

## 3. 解除 BLOCK 条件

| 条件 | 操作 |
|------|------|
| 用户确认了所有假设 | ✅ 解除 BLOCK → 按正确模型重新实施 |
| 用户提供了修正信息 | ✅ 解除 BLOCK → 基于修正重新设计 |
| 用户选择完全不同的方案 | ✅ 解除 BLOCK → 重置 failure_count=0 → 新方案 |
| 用户说"继续修，我负责" | ✅ 解除 BLOCK → 记录 `user_override: true` → 继续 |
| Agent 自行判断"已经分析清楚了" | ❌ **不允许**——必须用户显式确认 |

---

## 4. 与铁律 #5 回退循环的关系

| 铁律 | 触发时机 | 行为 |
|------|---------|------|
| #35（重复失败） | 第 2 次失败 | **BLOCK** + 强制输出四要素 + 等待用户确认 |
| #5（回退上限） | 第 3 次回退 | **挂起** + 报告用户 + 建议重新评估 |

**执行顺序**：#35 先触发（第 2 次）→ BLOCK → 用户确认后才能走第 3 轮。如果第 3 轮仍失败，#5 触发 → 挂起用户。

**交互规则**：
- 如果 #35 触发后用户确认了假设并提供了正确方向，则重置 failure_count 为 0
- 如果用户选择了全新方案，则视为新任务，failure_count 重建

---

## 5. 失败追踪日志

状态文件中记录：

```json
{
  "risk_tracking": {
    "repeated_failure_count": 2,
    "repeated_failure_details": [
      {
        "round": 1,
        "target": "auth.service.ts:88 login()",
        "fix_approach": "添加空值检查",
        "failure_stage": "EXAMINE",
        "failure_symptom": "login_timeout_spec.js 仍然 FAIL——Token 超时逻辑未修复"
      },
      {
        "round": 2,
        "target": "auth.service.ts:120 refreshToken()",
        "fix_approach": "修复 Token 刷新逻辑",
        "failure_stage": "EXAMINE",
        "failure_symptom": "login_timeout_spec.js FAIL——修复了刷新但 Session 未清理"
      }
    ],
    "block_triggered": true,
    "root_cause_analysis": "...",
    "user_confirmed_at": null
  }
}
```

---

## 6. 反模式

- ❌ **第 3 次尝试只改了一行代码就声称修复**：未输出四要素就继续→违反铁律 #35
- ❌ **不分析前两次为什么失败就开始第 3 次**：换一个地方加 null check→仍不是根因
- ❌ **BLOCK 后 Agent 自己"想了想"就解除**：必须用户显式确认——"我觉得这次肯定对"不算
- ❌ **把不同的失败算成"重复"**：Round 1 修了 A 但发现 B 也坏了→B 是新问题，不算重复
- ❌ **用户确认后继续用老方案**：用户说"继续"但 Agent 不按正确模型改→继续打补丁
