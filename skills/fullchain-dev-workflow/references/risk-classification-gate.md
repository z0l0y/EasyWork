# Risk Classification Gate（风险分类闸门）

> **铁律 #39**：不同风险等级适用不同闸门集和阻断策略。任务启动时完成风险分级，全程按等级裁剪。不能所有任务用一样的流程——小改动不需要全部门禁，高风险操作必须全部门禁+额外保护。
> 风险等级在 READ 阶段由任务分类器自动判定，用户可覆盖。涉及数据迁移/权限变更/线上发布/删除操作 → 最低 L4。

---

## 1. 五级风险定义

### L0 — 纯文档/查询

**特征**：只读操作、生成文档、回答问题、代码解释、信息查询。

**示例**：
- "这个函数是做什么的？"
- "帮我写一份 README"
- "解释一下这个模块的架构"

**策略**：最小流程。Delivery Definition (brief) + Context Loss Protection。其余闸门全部跳过。

**阻断策略**：无阻断——纯理解/文档任务不涉及代码变更，无风险。

---

### L1 — 小修复

**特征**：单文件修改、单函数改动、无 API 变更、< 20 行代码、无新增依赖。

**示例**：
- "把 config.ts 第 42 行的 == 改成 ==="
- "修复这个 typo"
- "给这个函数加个空值检查"

**策略**：单元测试 + 简短记录。

| 闸门 | 状态 |
|------|------|
| Delivery Definition | ✅ 必执行（brief） |
| Traceability Matrix | ✅ 必执行（1-2 行即可） |
| Reference Baseline | ⏭ 跳过（非成熟领域无需参考） |
| Test Adequacy | ✅ 必执行（如是 Bug 修复 → 回归测试强制） |
| Environment Fidelity | ⏭ 跳过（单文件改动无环境差异） |
| Evidence Ledger | ⚠ 可选（brief:1 条证据即可） |
| Historical Version Coverage | ⏭ 跳过 |
| Source Provenance | ✅ 必执行（标注本轮来源） |

---

### L2 — 正常功能

**特征**：多文件修改、新增功能、中等重构、有 API 变更、涉及测试。

**示例**：
- "新增用户注销功能"
- "重构支付模块的错误处理"
- "给所有 API 加 rate limiting"

**策略**：单元测试 + Review + 文档 Structured Merge。

| 闸门 | 状态 |
|------|------|
| Delivery Definition | ✅ 必执行（standard） |
| Traceability Matrix | ✅ 必执行（≥3 行） |
| Reference Baseline | ⚠ 可选（如属成熟领域→建议执行） |
| Test Adequacy | ✅ 必执行（五维覆盖检查） |
| Environment Fidelity | ⚠ 可选（如不涉及交互→跳过） |
| Evidence Ledger | ✅ 必执行（≥3 条证据） |
| Historical Version Coverage | ✅ 必执行 |
| Source Provenance | ✅ 必执行 |
| Repeated Failure Trigger | 🔒 仅触发时执行 |

---

### L3 — 交互式/并发/外部 API

**特征**：CLI/TUI/GUI/Web 前端/游戏/实时系统、并发/多线程/分布式、调用外部 API/微服务。

**示例**：
- "实现 WebSocket 实时通知"
- "重构前端状态管理（Redux → Zustand）"
- "对接微信支付 API"

**策略**：单元测试 + Smoke Test + 环境矩阵 + 用户体验确认。

| 闸门 | 状态 |
|------|------|
| Delivery Definition | ✅ 必执行（detailed） |
| Traceability Matrix | ✅ 必执行（≥5 行） |
| Reference Baseline | ✅ 必执行（成熟领域强制搜索） |
| Test Adequacy | ✅ 必执行（五维全覆盖 + 并发/安全专项） |
| Environment Fidelity | ✅ **强制必执行**（至少 1 次近真实环境 smoke test） |
| Evidence Ledger | ✅ 必执行（≥4 条证据，含 METRIC 类型） |
| Historical Version Coverage | ✅ 必执行 |
| Source Provenance | ✅ 必执行 |
| Repeated Failure Trigger | 🔒 仅触发时执行 |

**额外检查**（继承 v2.8 铁律 #26）：
- 交互式 UX 验证：首屏稳定性 / 输入反馈 / 退出路径 / 渲染频率
- 环境一致性：主要运行环境中行为一致

---

### L4 — 数据迁移/权限/线上发布/删除操作

**特征**：数据库 schema 变更、数据迁移（含回滚）、权限模型变更、线上发布/部署、删除操作（文件/数据/资源）、涉及 PII/敏感数据。

**示例**：
- "user 表拆分：将 profile 字段迁移到独立的 user_profiles 表"
- "修改 RBAC 权限模型"
- "删除废弃的 /api/v1 端点"

**策略**：**全部闸门** + Dry-Run + 备份 + Rollback + 用户显式确认。

| 闸门 | 状态 |
|------|------|
| 全部 L0-L3 闸门 | ✅ 全部必执行（detailed） |
| Dry-Run（预演） | ✅ **强制必执行**——在非生产环境完整预演 |
| Backup（备份） | ✅ **强制必执行**——提供可执行备份方案 |
| Rollback（回滚） | ✅ **强制必执行**——提供可执行回滚方案 |
| 用户显式确认 | ✅ **强制必执行**——逐项确认后放行 |

**额外检查**：
- 数据完整性验证：迁移前后数据条数/checksum 对比
- 回滚时间估算：回滚操作预计耗时
- 影响面评估：直接影响/间接影响/级联影响

---

## 2. 风险等级自动判定算法

### Step 1 — 关键词扫描

```
输入：task_description + 影响范围 + 用户原始消息
输出：初始风险等级

扫描规则（优先级从高到低）：

L4 关键词（任一命中 → 最低 L4）：
  - 数据相关：migration, migrate, schema, 迁移, 建表, 改表, 删表, DDL, 数据库变更
  - 权限相关：permission, role, RBAC, ACL, 权限, 角色, 授权
  - 发布相关：deploy, release, publish, 上线, 发布, 部署
  - 删除相关：delete, drop, remove, 删除, 移除, 废弃, deprecate（含实际删除）
  - 敏感数据：PII, GDPR, 加密, 脱敏, 隐私

L3 关键词（任一命中 → 最低 L3）：
  - 交互式：CLI, TUI, GUI, Web, frontend, UI, 前端, 界面, 页面, 游戏, game
  - 并发：concurrent, async, race, 并发, 异步, 竞态, WebSocket, SSE, realtime
  - 外部 API：API, SDK, webhook, 回调, 第三方, 外部服务, 支付, 短信, 邮件

L2 关键词（任一命中 → 最低 L2）：
  - 多文件：多个文件, 跨模块, 重构, refactor, 新增功能, feature, 实现
  - 默认：无法明确判断 → 默认 L2

L1 关键词（任一命中 → 最低 L1）：
  - 单文件：typo, config, 配置, 修, fix, 改, 一行, 单文件, 小改动

L0 关键词（任一命中 → 最低 L0）：
  - 纯查询：解释, 说明, 文档, 什么是, 怎么样, 为什么, how, what, why, explain
```

### Step 2 — 文件数修正

```
影响文件数：
  >10 个文件 → 当前等级 +1（上限 L4）
  3-10 个文件 → 不变
  1-2 个文件 → 不变
  0 个文件（纯查询）→ L0
```

### Step 3 — 升级触发

```
以下条件触发自动升级（不可降级）：
  - 涉及数据库 schema 变更 → 最低 L4
  - 涉及用户权限/认证/授权变更 → 最低 L4
  - 涉及生产环境发布 → 最低 L4
  - 涉及 PII/敏感数据处理 → 最低 L4
  - task_type = "Bug修复" 且涉及安全漏洞 → 最低 L3
```

### Step 4 — 用户确认

```
Agent 输出：
  【风险等级判定】
  初始判定：L{N}（{等级名称}）
  判定依据：{命中关键词/文件数/升级触发}
  适用闸门：{列出必执行的闸门}
  如你认为等级不准确，可以说"这是 L{M} 操作"来覆盖。

用户可回复：
  - 确认（默认接受）
  - "这是 L{M}"（覆盖）
  - "升级到 L{M}"（手动升级）
```

---

## 3. 每级闸门映射总表

| 闸门（铁律 #） | L0 | L1 | L2 | L3 | L4 |
|---------------|----|----|----|----|----|
| Delivery Definition (#30) | brief | brief | standard | detailed | detailed |
| Traceability Matrix (#31) | ⏭ | 1-2行 | ≥3行 | ≥5行 | ≥5行 |
| Reference Baseline (#33) | ⏭ | ⏭ | ⚠ | ✅ | ✅ |
| Environment Fidelity (#32) | ⏭ | ⏭ | ⚠ | ✅ | ✅ |
| Test Adequacy (#34) | ⏭ | ✅* | ✅ | ✅ | ✅ |
| Repeated Failure (#35) | ⏭ | 🔒 | 🔒 | 🔒 | 🔒 |
| Historical Version Coverage (#36) | ⏭ | ⏭ | ✅ | ✅ | ✅ |
| Source Provenance (#37) | ⏭ | ✅ | ✅ | ✅ | ✅ |
| Evidence Ledger (#38) | ⏭ | 1条 | 3条 | 4条 | 5条 |
| Dry-Run | ⏭ | ⏭ | ⏭ | ⏭ | ✅ |
| Backup | ⏭ | ⏭ | ⏭ | ⏭ | ✅ |
| Rollback | ⏭ | ⏭ | ⏭ | ⏭ | ✅ |

> 图例：✅ 必执行 | ⚠ 建议执行（可选）| ⏭ 跳过 | 🔒 仅触发时执行 | * Bug修复时强制回归测试

---

## 4. Gate Judgment Rules

| 深度 | 闸门类型 | 命中处理 |
|------|---------|---------|
| **detailed** | **HARD GATE** | 风险等级与任务类型不匹配 → 拒绝继续 → 要求用户确认或重新分类 |
| **standard** | **SOFT GATE** | 警告但允许继续（用户已知风险等级） |
| **brief** | **SOFT GATE** | 仅标注风险等级，不阻断 |

### 等级不匹配的判定

```
L0 任务（纯查询）被分类器判定为 L3 → 要求用户确认
L4 任务（数据迁移）被用户手动降到 L1 → 必须警告并确认：
  "你将该操作从 L4 降为 L1。L4 要求的 dry-run/备份/回滚将被跳过。
   确认继续？(输入 yes 确认)"
```

---

## 5. 风险等级输出格式

Agent 在 READ 阶段末尾输出：

```markdown
## 风险等级判定

| 字段 | 值 |
|------|-----|
| **风险等级** | L2 — 正常功能 |
| **判定来源** | auto_detected |
| **触发关键词** | 新增功能, 多文件 (4 files) |
| **升级触发** | 无 |
| **适用闸门** | Delivery Definition, Traceability Matrix, Test Adequacy, Evidence Ledger (3条), Historical Version Coverage, Source Provenance |
| **跳过闸门** | Reference Baseline, Environment Fidelity |

如等级不准确，请回复"这是 L{N}"来覆盖。
```

---

## 6. 反模式

- ❌ **L4 操作当 L1 处理**：数据迁移不带备份方案，权限变更不走用户确认——最危险的反模式
- ❌ **用户说"小改动"就自动降级**：小于 5 行代码也可能是 L4（如删除权限检查、关闭 HTTPS 强制跳转）。Agent 必须检查改动影响，不可盲从用户描述
- ❌ **不告知用户每级闸门差异**：用户不知道 L3 比 L1 多了什么检查。Agent 必须在风险等级输出中列出适用的闸门
- ❌ **L0/L1 任务也走全部门禁**：改一个 typo 要求环境矩阵——效率浪费，Agent 应严格按闸门映射表裁剪
- ❌ **风险等级只在 READ 判定一次**：如在后续步骤发现新风险（CODE 中发现改动影响面远超预期），应重新评估风险等级
- ❌ **L4 操作不提供 dry-run 方案**：只说"建议先在 staging 测试"不算 dry-run——需要具体步骤和验证方法
- ❌ **L4 操作的回滚方案不可执行**："有问题就 revert commit"不是回滚方案——数据迁移的回滚需要具体的数据恢复步骤
