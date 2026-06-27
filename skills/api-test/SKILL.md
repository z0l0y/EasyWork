---
name: api-test
description: >
  接口联调测试——面向联调场景的全覆盖 API 测试技能。自动生成全量测试用例
  （等价类划分+边界值+错误路径+状态转换），预计算每个用例的预期结果与
  非预期返回的含义及解决方式，生成 MySQL 5.7 兼容的数据库验证 SQL /
  Redis 验证命令 / MQ 消息检查脚本，内置安全防护避免打爆测试环境。
  参考业界最佳实践：等价类划分（IEEE 829）、边界值分析（JSTQB）、
  双校验模式（API+DB）、契约测试（OAS/JSON Schema）、
  MySQL 5.7 兼容方案（无 CTE/无窗口函数）。
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
model: sonnet
version: 1.0
capability:
  id: api-test
  display_name: 接口联调测试
  emoji: "🔌"
  category: quality
  tier: 2
  inputs:
    - { name: api_spec, type: text, required: true, description: "接口规格——URL/方法/请求体/响应体/错误码定义" }
    - { name: test_scope, type: text, required: false, description: "测试范围——all/quick/error-only/boundary/db-verify（默认 all）" }
  outputs:
    - { name: test_case_matrix, type: table, description: "全量测试用例矩阵（含预期结果）" }
    - { name: error_code_map, type: table, description: "错误码映射表——含义/原因/排查步骤/解决方案" }
    - { name: db_verify_sql, type: code, description: "MySQL 5.7 兼容的数据库验证 SQL 脚本" }
    - { name: middleware_verify, type: code, description: "Redis/MQ 等中间件验证命令脚本" }
    - { name: test_script, type: code, description: "可执行的 curl/httpie 测试脚本" }
  triggers: ["接口测试", "联调测试", "API 测试", "api test", "接口联调",
             "测试这个接口", "帮我测接口", "生成测试用例", "接口验证",
             "test this api", "帮我联调", "构造测试参数", "检查接口"]
  related_skills:
    - { skill: code-implement, relationship: inbound, desc: "code-implement 产出接口实现后可调用 api-test 做联调验证" }
    - { skill: code-review, relationship: inbound, desc: "code-review 发现接口逻辑问题后可调用 api-test 构造用例验证" }
    - { skill: article-write, relationship: outbound, desc: "测试报告超过 30 行时调用 article-write 写入 .md 文件" }
    - { skill: self-check, relationship: outbound, desc: "测试完成后用 CTO 拷打验证测试充分性" }
  suggested_when:
    - "用户需要联调某个 API 接口"
    - "用户说'帮我构造参数测这个接口'"
    - "用户想确认接口返回值是否正确"
    - "用户遇到看不懂的错误码"
    - "用户需要检查数据库/缓存/消息队列里的数据对不对"
  pipeline_placement:
    good_after: ["code-implement", "code-review", "read-requirements"]
    good_before: ["article-write", "self-check", "sum-session"]
  autonomous:
    callable_by_other: true
    requires_confirmation: false
    max_depth: 1
  risk_level: L1
---

# API Test（接口联调测试）

## 0. 定位：不只是"测一下能不能通"

普通 Agent 的接口测试 = 帮你写几个 curl + 看 200 还是 500。

**这不是联调。** 联调需要：

| Agent 能做到的 | 你必须做到的 |
|--------------|------------|
| 发几个请求看能不能通 | **穷举所有等价类和边界值，确保每个参数的正确/错误/边界/异常组合都覆盖到** |
| 返回 500 就说"报错了" | **提前算好每个请求的预期返回值，拿到非预期结果就定位到具体参数/逻辑问题** |
| 看不懂错误码就去查文档 | **把每个错误码的含义、出现原因、排查步骤、解决方案全列出来，不用用户自己查** |
| 只看 API 返回值 | **生成 MySQL 5.7 SQL / Redis 命令 / MQ 检查脚本，验证存储层数据是否正确** |
| 疯狂发请求 | **内置安全防护——限流/参数边界/不删数据/不回滚交易/不打爆测试环境** |

本技能的核心信条：**联调不靠猜。每个测试用例的预期结果在发请求之前就已经算好了。**

### 参考实现

| 项目 | 类型 | 我们借鉴了什么 |
|------|------|--------------|
| [iulspop/aidd-skills integration-tests](https://github.com/iulspop/aidd-skills) | Claude Code Skill | 集成测试五问法（被测单元/预期行为/前置条件/预期结果/如何定位 bug） |
| [Kamil Buksakowski "Letting Claude Code Test Your Backend"](https://dev.to/kamilbuksakowski/letting-claude-code-test-your-backend-verifying-business-logic-via-api-and-sql-1635) | 实践文章 | API + SQL 双重验证模式、并行多场景测试 |
| [CSDN "接口自动化测试｜MySQL 断言"](https://devpress.csdn.net/xclaw/6a053a840a2f6a37c5a9ff36.html) | 实践文章 | 接口+数据库双校验架构、db_schema.json 自动生成、DB_ASSERT 开关 |
| [掘金 "Claude Code Skill 接口自动化测试设计实践"](https://juejin.cn/post/7623748440833474570) | 实践文章 | 15 条硬约束规则、四层模板架构、10+ 踩坑经验 |
| [meirm/api-testing Skill](https://skillsmp.com/skills/meirm-askgpt-examples-skills-api-testing-skill-md) | Claude Code Skill | API 测试的端点覆盖、请求/响应验证、错误案例 |
| [PICT Test Designer](https://mcpmarket.com/zh/tools/skills/pict-test-designer-1) | Claude Code Skill | 组合测试（正交/配对）减少用例爆炸 |
| IEEE 829 / JSTQB | 测试标准 | 等价类划分、边界值分析、错误推测法 |

---

## 1. 核心理念：五阶段接口联调流水线

```
阶段 1: 接口规格解析（API Spec Parsing）
  → 从接口定义中提取参数约束、返回值规格、错误码定义
阶段 2: 测试用例生成（Test Case Generation）
  → 等价类划分 + 边界值分析 + 错误路径 + 状态转换 + 组合测试
阶段 3: 预期结果计算（Expected Result Computation）
  → 每个用例的预期 HTTP 状态码 + 响应体结构 + 数据库状态 + 中间件状态
阶段 4: 错误码映射（Error Code Mapping）
  → 每个错误码的含义/触发条件/排查步骤/解决方案
阶段 5: 验证脚本生成（Verification Script Generation）
  → curl/httpie 测试脚本 + MySQL 5.7 SQL + Redis 命令 + MQ 检查
```

---

## 2. 阶段 1：接口规格解析

### 2.1 从任何格式中提取接口规格

无论用户提供什么形式的接口定义，必须提取以下结构化信息：

```markdown
## 接口规格卡

| 字段 | 值 |
|------|-----|
| **HTTP 方法** | GET / POST / PUT / DELETE / PATCH |
| **URL 路径** | /api/v1/resource/{id} |
| **Content-Type** | application/json / multipart/form-data / ... |
| **Auth** | Bearer Token / Basic Auth / API Key / None |

### 请求参数
| 参数名 | 位置 | 类型 | 必填 | 约束 | 默认值 | 业务含义 |
|--------|------|------|------|------|--------|---------|
| {name} | path/query/header/body | string/int/bool/array/object | ✅/❌ | {min/max/pattern/enum} | {default} | {含义} |

### 成功响应
| HTTP 状态码 | 响应体结构 | 响应体字段说明 |
|------------|-----------|-------------|
| 200 | { ... } | {字段含义} |
| 201 | { ... } | {字段含义} |

### 错误响应（已知的）
| HTTP 状态码 | 错误码 | 响应体 | 含义 |
|------------|--------|--------|------|
| 400 | INVALID_PARAM | { ... } | {含义} |
| 401 | UNAUTHORIZED | { ... } | {含义} |
| 404 | NOT_FOUND | { ... } | {含义} |
| ... | ... | ... | ... |
```

### 2.2 从多种来源解析

| 来源格式 | 解析策略 |
|---------|---------|
| **OpenAPI/Swagger JSON/YAML** | 直接解析 `paths`→`parameters`/`requestBody`/`responses` |
| **Proto/gRPC 定义** | 解析 message 字段、service 方法签名 |
| **代码注解** | 从 Spring `@RestController`/FastAPI `@app.post`/Gin `router.POST` 提取 |
| **口头描述** | 从用户描述中推断参数类型和约束，不确定处标注 `[待确认]` |
| **抓包/Curl** | 从 curl 命令中提取 URL/方法/headers/body |

### 2.3 规格完整性检查

以下信息缺失时必须询问用户：

| 缺失信息 | 默认行为 | 何时必须问 |
|---------|---------|----------|
| Auth 方式 | 假设无认证 | 如果接口在生产环境需要认证 |
| 参数格式约束（email/手机号等） | 假设无约束 | 如果参数名暗示有格式要求 |
| 错误码定义 | 只测标准 HTTP 错误码 | 如果已知业务错误码 |
| 数据库表结构 | 从 SQL/ORM 文件推断 | 如果需要生成 DB 验证 SQL |

---

## 3. 阶段 2：测试用例生成

### 3.1 五大测试维度（缺一不可）

对每个参数独立应用以下五类测试，然后做组合。

### 3.2 等价类划分（Equivalence Partitioning）

```markdown
## 等价类划分

### 参数：{param_name}（类型：{type}，约束：{constraints}）

| 类 | 分类 | 代表值 | 预期结果 |
|----|------|--------|---------|
| V1 | 有效——典型值 | {典型值} | 200/201 |
| V2 | 有效——最小值 | {min} | 200/201 |
| V3 | 有效——最大值 | {max} | 200/201 |
| I1 | 无效——类型错误 | {错误类型值} | 400 |
| I2 | 无效——低于最小值 | {min-1} | 400 |
| I3 | 无效——高于最大值 | {max+1} | 400 |
| I4 | 无效——空值 | null / "" / 缺失 | 400 |
| I5 | 无效——特殊字符 | {SQL注入/脚本注入/Unicode} | 400 |
| I6 | 无效——超长字符串 | {max_length * 10} | 400 |
```

### 3.3 边界值分析（Boundary Value Analysis）

```markdown
## 边界值分析

### 参数：{param_name}，范围：[{min}, {max}]，长度限制：{len_min}-{len_max}

| 边界值 | 预期 |
|--------|------|
| {min-1} | 400（低于最小值） |
| **{min}** | **200（刚好等于最小值——必须测）** |
| {min+1} | 200（最小值+1） |
| {max-1} | 200（最大值-1） |
| **{max}** | **200（刚好等于最大值——必须测）** |
| {max+1} | 400（超过最大值） |
| 空字符串（""） | 400（字符串类型必测） |
| 仅空格（"   "） | 视业务规则：400 或 200（trim 后等效于空） |
| null / undefined / 缺失 | 400（必填参数必测） |
| 0（数值类型） | 视业务规则：可能有效也可能无效 |
| 负数（数值类型，若范围全为正） | 400 |
```

### 3.4 错误路径覆盖（Error Path Coverage）

```markdown
## 错误路径覆盖

### 认证相关（如果接口需要认证）
| 操作 | 用例 | 预期 |
|------|------|------|
| 缺少 Token | 不带 Authorization header | 401 |
| 错误 Token | Authorization: Bearer invalid-token | 401 |
| 过期 Token | {过期 Token} | 401 |
| 无权限 | 用普通用户 Token 访问管理员接口 | 403 |
| 跨租户访问 | 用租户 A 的 Token 访问租户 B 的资源 | 403/404 |

### 资源相关
| 操作 | 用例 | 预期 |
|------|------|------|
| 不存在的 ID | GET /resource/999999 | 404 |
| 已删除的 ID | GET /resource/{已软删除的id} | 404/410 |
| 别人的资源 | GET /resource/{其他用户的资源id} | 403/404 |

### 业务规则相关
| 操作 | 用例 | 预期 |
|------|------|------|
| 重复创建 | POST 相同唯一键的数据 | 409 Conflict |
| 违反关联约束 | POST 引用不存在的外键 | 400/422 |
| 状态不允许 | {在状态 A 下执行只能在状态 B 下才能做的操作} | 409/422 |
```

### 3.5 状态转换覆盖（State Transition Coverage）

```markdown
## 状态转换测试

假设资源有以下状态流转：待处理 → 处理中 → 已完成 / 已取消

| 从 | 操作 | 到 | 预期 |
|----|------|----|------|
| 待处理 | 开始处理 | 处理中 | 200 |
| 待处理 | 取消 | 已取消 | 200 |
| 待处理 | 标记完成 | — | 400（不能跳跃状态） |
| 处理中 | 标记完成 | 已完成 | 200 |
| 处理中 | 取消 | 已取消 | 200（视业务规则） |
| 已完成 | 取消 | — | 400（已完成不可取消） |
| 已取消 | 开始处理 | — | 400（已取消不可恢复） |
```

### 3.6 组合测试策略

当参数之间有关联时，不盲目做全组合（N 个参数 × M 个取值 = 爆炸）：

| 策略 | 适用场景 | 用例数 |
|------|---------|--------|
| **全组合** | 参数 ≤ 3 个且取值 ≤ 5 种 | N₁ × N₂ × N₃ |
| **成对组合（Pairwise）** | 参数 4-10 个 | ~N log N（参考 PICT 算法） |
| **关键路径组合** | 参数 > 10 个 | 只覆盖业务关键路径 |

**组合测试的重点**：不要把失效的参数组合在一起——一个无效参数足以触发错误，不用叠加多个无效参数。

### 3.7 安全防护规则（硬约束）

在生成测试用例时，以下规则绝对不可违反：

| # | 规则 | 说明 |
|---|------|------|
| 1 | **限流** | 单接口测试不超过 30 个请求，总请求间隔 ≥ 200ms。超过 30 个用例→分批次执行 |
| 2 | **不删生产数据** | DELETE 测试仅对测试环境且用户确认后执行。对生产环境只做 GET 不做写操作 |
| 3 | **参数边界** | 字符串长度不超过 10KB、数值不超过 Java Long MAX_VALUE、数组不超过 100 个元素 |
| 4 | **不回滚事务** | 涉及交易的接口，测试金额用最小值（如 0.01），不用真实金额 |
| 5 | **不触发副作用** | 短信/邮件/推送/扣款/扣库存/Webhook——在测试用例中明确标注，等待用户确认后才执行 |
| 6 | **数据库不爆** | SQL 查询带 LIMIT 100，不执行全表扫描的查询。大数据量表加索引条件 |
| 7 | **账号安全** | 不测试他人账号的密码、不使用真实手机号/邮箱（用 test@example.com）、不泄露 Token |

---

## 4. 阶段 3：预期结果计算

### 4.1 每个测试用例的预期结果卡片

```markdown
## 测试用例 #{N}

| 属性 | 值 |
|------|-----|
| **用例名称** | {描述性名称} |
| **测试维度** | 等价类-有效 / 等价类-无效 / 边界值 / 错误路径 / 状态转换 |
| **优先级** | P0（核心） / P1（重要） / P2（边界） / P3（罕见） |
| **前置条件** | {数据库需存在的数据、需要的认证 Token、资源状态} |

### 请求
```bash
curl -X {METHOD} "{BASE_URL}/api/v1/resource/{id}" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 预期响应
- **HTTP 状态码**: {200/400/401/...}
- **响应体**:
```json
{
  "code": "{expected_code}",
  "message": "{expected_message}",
  "data": { ... }
}
```
- **响应头**: Content-Type: application/json

### 如果不是预期的，说明什么？
| 实际状态码 | 可能原因 | 排查步骤 | 解决方案 |
|-----------|---------|---------|---------|
| 200（预期400） | 参数校验未生效 | 1. 检查校验注解 2. 检查是否走了默认值 | 添加参数校验逻辑 |
| 500（预期200） | 空指针/DB连接失败 | 1. 查看服务日志 2. 检查 DB 是否可达 | 修复代码 bug/检查基础设施 |
| ... | ... | ... | ... |
```

### 4.2 预期结果与检查点的四层验证

```
第一层：HTTP 响应        → 状态码、响应头、响应体结构
第二层：业务逻辑         → 响应体字段值的正确性（金额/状态/时间等）
第三层：数据库状态       → 数据是否写入、字段值是否正确、关联表是否更新
第四层：中间件状态       → 缓存是否更新、消息是否投递、事件是否发布
```

### 4.3 复杂业务规则的预期计算

对涉及计算/转换/校验的接口，必须展示预期的推导过程：

```markdown
### 业务预期推导

**输入**：{参数列表及值}
**业务规则**：{规则描述}
**推导过程**：
  1. {步骤 1}
  2. {步骤 2}
  3. {步骤 3}
**预期输出**：{字段: 预期值}

**如果输出不一致**：
  - 字段 {X} 偏大 → 可能原因：{...}
  - 字段 {X} 偏小 → 可能原因：{...}
  - 字段 {X} 为空 → 可能原因：{...}
```

---

## 5. 阶段 4：错误码映射

### 5.1 完整错误码地图

```markdown
## 错误码映射表

| HTTP 状态码 | 错误码 | 含义 | 触发条件 | 谁返回的 | 排查步骤 | 解决方案 | 是否可重试 |
|------------|--------|------|---------|---------|---------|---------|----------|
| 400 | INVALID_PARAM | 请求参数不合法 | 参数校验失败 | 应用层 | 检查哪个参数值不符合约束 | 修正参数后重试 | ✅ |
| 400 | PARAM_TYPE_MISMATCH | 参数类型错误 | 应传 int 却传了 string | 框架层（Spring/FastAPI） | 检查请求体 JSON 类型 | 修正类型后重试 | ✅ |
| 401 | UNAUTHORIZED | 未认证 | Token 缺失/无效/过期 | 网关/中间件 | 1. 检查 Header 2. 检查 Token 是否过期 | 刷新 Token 后重试 | ✅ |
| 403 | FORBIDDEN | 无权限 | 角色/权限不满足 | 应用层 | 检查用户角色和接口所需权限 | 联系管理员授权 / 使用正确角色 Token | ❌（需改权限） |
| 404 | NOT_FOUND | 资源不存在 | 资源 ID 不存在或已被软删除 | 应用层 | 1. 确认 ID 正确 2. 查 DB 确认资源状态 | 使用正确的 ID | ❌（需确认 ID） |
| 409 | CONFLICT | 资源冲突 | 唯一键冲突/版本冲突/状态冲突 | 应用层 | 1. 检查唯一字段 2. 检查资源当前状态 | 先查询再操作 / 使用乐观锁重试 | ✅（修正后） |
| 422 | UNPROCESSABLE_ENTITY | 参数语义错误 | 参数格式正确但业务语义不通 | 应用层 | 检查字段间的业务关联约束 | 按业务规则修正 | ✅ |
| 429 | TOO_MANY_REQUESTS | 请求过于频繁 | 触发了限流 | 网关/中间件 | 检查请求频率 | 降低请求频率后重试 | ✅（等待后） |
| 500 | INTERNAL_ERROR | 服务器内部错误 | 代码异常/NPE/DB 连接超时 | 框架/应用 | 1. 查看服务日志 2. 检查 DB 连接 | 修复代码/重启服务 | ✅（修复后） |
| 502 | BAD_GATEWAY | 上游服务异常 | 网关后面的服务挂了 | 网关 | 检查上游服务健康状态 | 重启上游服务 | ✅（修复后） |
| 503 | SERVICE_UNAVAILABLE | 服务不可用 | 服务宕机/熔断/限流 | 网关/熔断器 | 检查服务健康检查状态 | 恢复服务/等待熔断恢复 | ✅（等待后） |
```

### 5.2 业务错误码映射

```markdown
## 业务错误码（应用自定义）

| 错误码 | 消息 | 含义 | 在哪个条件下触发 | 前序状态 | 排查 SQL | 解决方案 |
|--------|------|------|---------------|---------|---------|---------|
| ORDER_STATUS_INVALID | "当前订单状态不允许此操作" | 订单状态不是待支付 | 在已支付/已取消的订单上调用支付 | 查 order 表 status 字段 | `SELECT id, status FROM orders WHERE id={id};` | 检查订单状态流转规则 |
| INSUFFICIENT_BALANCE | "余额不足" | 账户余额<订单金额 | 支付时余额不够 | 查 account 表 balance 字段 | `SELECT user_id, balance FROM accounts WHERE user_id={uid};` | 充值或用其他支付方式 |
| ... | ... | ... | ... | ... | ... | ... |
```

---

## 6. 阶段 5：验证脚本生成

### 6.1 可执行测试脚本

生成可直接复制粘贴执行的测试脚本。默认使用 curl（零依赖），同时提供 httpie 版本。

```bash
#!/bin/bash
# ============================================================
# API Test Script: {接口名称}
# 生成时间: {timestamp}
# 用例总数: {N} | P0: {n0} | P1: {n1} | P2: {n2} | P3: {n3}
# ============================================================

BASE_URL="${BASE_URL:-http://localhost:8080}"
TOKEN="${TOKEN:-your-token-here}"

# 颜色输出
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
PASS="${GREEN}PASS${NC}"; FAIL="${RED}FAIL${NC}"; SKIP="${YELLOW}SKIP${NC}"

pass=0; fail=0; skip=0

assert_status() {
  local expected=$1 actual=$2 case_name=$3
  if [ "$actual" -eq "$expected" ]; then
    echo -e "$PASS  $case_name (expected $expected, got $actual)"
    ((pass++))
  else
    echo -e "$FAIL $case_name (expected $expected, got $actual)"
    ((fail++))
  fi
}

# ---- P0: 核心功能 ----

# TC001: 正常创建
echo "TC001: 正常创建资源"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/resource" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"test","value":100}')
HTTP_CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
assert_status 201 "$HTTP_CODE" "TC001: 正常创建"
echo "  Response: $BODY"

# TC002: 参数缺失
echo "TC002: 缺少必填字段 name"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/resource" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value":100}')
HTTP_CODE=$(echo "$RESP" | tail -1)
assert_status 400 "$HTTP_CODE" "TC002: 缺少必填字段"

# ... 更多用例 ...

echo "============================================"
echo "Results: $pass passed, $fail failed, $skip skipped"
echo "============================================"
```

### 6.2 MySQL 5.7 数据库验证 SQL

**关键约束**：
- ❌ 不使用 CTE（WITH 子句）—— MySQL 5.7 不支持
- ❌ 不使用窗口函数（ROW_NUMBER/RANK/LAG/SUM OVER）—— MySQL 5.7 不支持
- ❌ 不使用 JSON_TABLE / JSON_ARRAYAGG —— MySQL 5.7 部分不支持
- ✅ 使用子查询替代 CTE
- ✅ 使用用户变量（`@var`）模拟窗口函数（需要时）
- ✅ 所有查询加 LIMIT 100
- ✅ 使用标准 JOIN 语法（INNER/LEFT/RIGHT），不用 LATERAL
- ✅ VARCHAR 字段用 utf8mb4，索引前缀长度不超过 767 字节

```sql
-- ============================================================
-- DB Verification SQL: {接口名称}
-- 目标数据库: MySQL 5.7.x
-- 生成时间: {timestamp}
-- ============================================================

-- [TC001] 正常创建——验证数据正确写入
-- 验证：order 表新增 1 条记录，字段值正确
SELECT
    id,
    order_no,
    user_id,
    amount,
    status,
    created_at,
    updated_at
FROM orders
WHERE order_no = '{expected_order_no}'
  AND user_id = {expected_user_id}
LIMIT 1;
-- 预期：
--   id 不为 NULL（自增主键）
--   status = 'PENDING'
--   amount = 100.00
--   created_at 接近当前时间（±5秒内）
--   如果 status != 'PENDING' → 检查状态机逻辑
--   如果 amount != 100.00 → 检查金额计算逻辑（精度？折扣？）

-- [TC002] 正常创建——验证关联表更新
-- 验证：order_item 表写入关联记录
SELECT
    oi.id,
    oi.order_id,
    oi.product_id,
    oi.quantity,
    oi.unit_price
FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.id
WHERE o.order_no = '{expected_order_no}'
LIMIT 100;
-- 预期：
--   order_item 至少有 1 条记录
--   order_id 等于上面查到的 orders.id
--   如果为空 → 订单创建了但订单项没写入（事务回滚？）

-- [TC003] 更新操作——验证状态变更
-- 验证：status 从 PENDING 变为 PAID
-- （MySQL 5.7 兼容写法：不用 CTE，直接用子查询）
SELECT
    id,
    status,
    updated_at
FROM orders
WHERE id = {created_order_id}
  AND status = 'PAID'
LIMIT 1;
-- 预期：
--   能查到记录（status 已变更为 PAID）
--   如果查不到 → 状态更新失败，检查 update 语句的 WHERE 条件

-- [TC004] 删除操作——验证软删除
-- 验证：deleted 标记从 0 变为 1
SELECT
    id,
    is_deleted,
    deleted_at
FROM orders
WHERE id = {created_order_id}
  AND is_deleted = 1
LIMIT 1;
-- 预期：
--   is_deleted = 1
--   deleted_at 不为 NULL
--   如果 is_deleted 仍为 0 → 软删除逻辑未生效

-- [TC005] 唯一键冲突后——验证数据未重复写入
-- 验证：唯一键冲突后，数据库中仍然只有 1 条记录
SELECT COUNT(1) AS cnt
FROM orders
WHERE order_no = '{duplicate_order_no}';
-- 预期：cnt = 1
--   如果 cnt > 1 → 唯一键约束未生效或事务隔离级别有问题

-- [TC006] 复杂业务验证——订单金额 = 订单项金额之和（MySQL 5.7 子查询替代 CTE）
SELECT
    o.order_no,
    o.amount AS order_amount,
    IFNULL(item_sum.total, 0) AS items_total,
    ABS(o.amount - IFNULL(item_sum.total, 0)) AS diff
FROM orders o
LEFT JOIN (
    SELECT order_id, SUM(quantity * unit_price) AS total
    FROM order_items
    GROUP BY order_id
) item_sum ON o.id = item_sum.order_id
WHERE o.order_no = '{expected_order_no}'
HAVING diff > 0.01
LIMIT 1;
-- 预期：查不到记录（diff = 0，订单金额 = 订单项汇总金额）
--   如果能查到 → 订单金额与订单项不匹配：
--     1. 检查 amount 是在哪里计算的（代码？触发器？）
--     2. 检查是否有折扣/优惠券没有体现在 order_items 中

-- [TC007] 分页查询——验证数据量和排序
-- （MySQL 5.7 兼容：不用 ROW_NUMBER()，用 LIMIT OFFSET）
SELECT id, order_no, created_at
FROM orders
WHERE user_id = {test_user_id}
ORDER BY created_at DESC
LIMIT 10 OFFSET 0;
-- 预期：返回 ≤ 10 条记录，按创建时间倒序
--   如果第一条不是最新创建的 → ORDER BY 字段不对

-- [TC008] 关联数据完整性——无孤儿记录
SELECT oi.id AS orphan_item_id, oi.order_id
FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.id
WHERE o.id IS NULL
LIMIT 100;
-- 预期：查到 0 条
--   如果能查到 → order_items 中有孤儿记录（order 被删了但 items 没删）
```

### 6.3 Redis 缓存验证命令

```bash
# ============================================================
# Redis Verification: {接口名称}
# 目标 Redis 版本: 5.x / 6.x / 7.x（兼容）
# ============================================================

# [TC-R01] 验证缓存写入
# 查询缓存 key（根据业务规则拼接 key 格式）
redis-cli GET "cache:user:{user_id}:profile"
# 预期：返回 JSON 字符串，字段与接口返回一致
# 如果返回 (nil) → 缓存写入失败或 TTL 已过期

# [TC-R02] 验证缓存更新
# 更新用户信息后，缓存应同步更新或失效
redis-cli GET "cache:user:{user_id}:profile"
# 预期：返回更新后的数据，或 (nil)（如果策略是删除缓存而非更新）

# [TC-R03] 验证缓存 TTL
redis-cli TTL "cache:user:{user_id}:profile"
# 预期：剩余 TTL 在合理范围内（如 300-3600 秒）
# 如果 TTL = -1（永不过期）→ 检查缓存配置
# 如果 TTL = -2（key 不存在）→ 缓存从未写入

# [TC-R04] 验证缓存失效
# 删除用户后，缓存应同步删除
redis-cli EXISTS "cache:user:{user_id}:profile"
# 预期：返回 0（key 不存在）
# 如果返回 1 → 缓存未失效（脏数据）

# [TC-R05] 验证分布式锁（如适用）
redis-cli GET "lock:order:{order_id}"
# 预期：操作完成后锁已释放（返回 nil）
# 如果还持有锁 → 死锁或解锁逻辑未执行

# [TC-R06] 验证限流计数器
redis-cli GET "ratelimit:api:/resource:{user_id}:{timestamp}"
# 预期：计数器 ≤ 限流阈值
# 如果不存在 → 限流未生效（请求可能没经过限流中间件）
```

### 6.4 消息队列（MQ）验证命令

```bash
# ============================================================
# MQ Verification: {接口名称}
# 支持: RabbitMQ / Kafka / RocketMQ
# ============================================================

# RabbitMQ: 验证消息投递
rabbitmqctl list_queues name messages | grep "{queue_name}"
# 预期：messages ≥ 1（消息已投递到队列）
#   如果 messages = 0 → 消息未投递（生产者配置问题？交换机绑定？）

# Kafka: 验证消息写入
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic {topic_name} \
  --from-beginning --max-messages 1 --timeout-ms 5000
# 预期：能消费到刚发送的消息
#   如果超时无消息 → 生产者发送失败或 topic 名称不匹配

# 验证消息内容
# 消费消息后检查其 body 是否包含预期的字段：
#   {检查 JSON 字段列表}
```

---

## 7. 输出格式

### 7.1 三种深度模式

| 模式 | 触发词 | 产出 |
|------|--------|------|
| **quick** | "快速测一下 / quick test" | 只生成 P0 用例（核心功能 + 主要错误路径），≤15 条用例，简化错误码映射 |
| **standard**（默认） | 无特殊指定 | 五维度全覆盖，所有等价类 + 边界值 + 错误路径 + 关键状态转换，含 DB 验证 SQL |
| **detailed** | "全面测试 / 深度测试 / 完整联调" | standard + 组合测试 + 性能预检（说明并发风险点）+ Redis/MQ 验证 + 完整错误码地图 |

### 7.2 报告结构

完整报告使用 `assets/test-report-template.md`，输出为 Markdown 文件。结构：

1. 接口规格卡
2. 测试用例矩阵（表格，含预期结果）
3. 非预期结果排查指南（按状态码分类）
4. 错误码映射表
5. 数据库验证 SQL（MySQL 5.7）
6. 中间件验证命令（Redis / MQ）
7. 可执行测试脚本（curl）
8. 测试环境准备清单

---

## 8. 安全防护 & 测试环境保护

### 8.1 请求前检查清单

在生成任何测试脚本之前，必须自检：

```markdown
## 安全自检

- [ ] 测试 BASE_URL 指向测试环境（非生产环境）？
- [ ] 测试 Token 是测试账号（非真实用户）？
- [ ] 写操作（POST/PUT/DELETE）的目标是测试数据？
- [ ] 测试金额 ≤ 0.01 元（非真实金额）？
- [ ] 测试数据不涉及真实手机号/邮箱/身份证？
- [ ] SQL 查询都带了 LIMIT 100？
- [ ] 没有 DROP/TRUNCATE/ALTER 语句？
- [ ] 没有全表扫描风险（WHERE 条件有索引）？
- [ ] 没有调用发送短信/邮件/推送的接口？
```

### 8.2 环境区分

| 环境 | GET 请求 | POST/PUT/DELETE | DB 验证 SQL |
|------|---------|----------------|-------------|
| **生产** | ✅ 可执行（只读） | ❌ 禁止，只生成脚本供审查 | ❌ 只生成 SELECT，禁止写操作 |
| **预发/Staging** | ✅ 可执行 | ⚠️ 生成后需用户逐条确认 | ✅ 只读查询可执行 |
| **测试** | ✅ 可执行 | ✅ 可执行（标注需确认的操作） | ✅ 可执行 |
| **本地** | ✅ 可执行 | ✅ 全自动执行 | ✅ 全量可执行 |

### 8.3 反模式总表

#### 测试用例生成
- ❌ 只测 happy path——至少覆盖无效等价类 + 边界值 + 认证错误
- ❌ 把所有无效参数放在一个请求里测——无效参数之间可能互相掩盖
- ❌ 没有优先级标注——P0/P1/P2/P3 让执行者知道哪些必须先测
- ❌ 忽略了状态转换——CRUD 之外还有状态机
- ❌ 组合爆炸不收敛——N > 10 个参数时不做全组合

#### 预期结果
- ❌ 只写了"200"或"报错"——必须具体到响应体字段值
- ❌ 不计算业务预期——API 返回 200 但数据算错了查不出来
- ❌ 不写"如果非预期说明什么"——联调的核心价值就是快速定位问题

#### 错误码
- ❌ 错误码只有状态码没有业务错误码——很多业务问题藏在 200+body.error_code 里
- ❌ 错误码含义写"系统错误"——等于没写
- ❌ 没有排查步骤和解决方案——用户还是要自己去查

#### 数据库验证
- ❌ SQL 用了 CTE（WITH）/窗口函数——MySQL 5.7 不支持
- ❌ 查询不带 LIMIT——大表可能打爆 DB
- ❌ 只验证主表不验证关联表——关联数据最容易出问题
- ❌ UPDATE/DELETE SQL 不带 WHERE——灾难性操作

#### 安全
- ❌ 不区分环境——在生产的 curl 里写 POST 请求还自动执行
- ❌ 测试金额用真实数字——触发真实扣款
- ❌ 不检查副作用——触发了短信/邮件/推送/Webhook

---

## 9. 与其他技能的关系

| 场景 | 建议组合 |
|------|---------|
| 新接口开发完成→联调 | ✏️ code-implement → 🔌 api-test → 🥊 self-check |
| Review 发现可疑逻辑→验证 | 🔍 code-review → 🔌 api-test |
| 理解接口需求→生成测试 | 👁️ read-requirements → 🔌 api-test |
| 测试完成→写报告 | 🔌 api-test → 📝 article-write |
| 排查线上问题→构造复现用例 | 📐 read-project → 🧪 api-test(quick) |

---

## 10. 参考实现

| 项目 | 类型 | 借鉴了什么 |
|------|------|----------|
| [iulspop/aidd-skills integration-tests](https://github.com/iulspop/aidd-skills) | Claude Code Skill | 五问法测试结构、前置条件/预期结果/ui-verify 三件套 |
| [meirm/api-testing](https://skillsmp.com/skills/meirm-askgpt-examples-skills-api-testing-skill-md) | Claude Code Skill | 端点覆盖、请求/响应断言、错误案例生成 |
| [测试用例自动生成论文（Sevilla 大学）](http://personal.us.es/amarlop/wp-content/uploads/2023/02/Automated-Test-Case-Generation-for-RESTful-Web-APIs-Towards-a-Testing-as-a-Service-Model.pdf) | 学术论文 | OAS 解析→等价类→边界值→组合测试的自动化流水线 |
| [PICT Test Designer](https://mcpmarket.com/zh/tools/skills/pict-test-designer-1) | Claude Code Skill | Pairwise 组合测试减少用例爆炸 |
| [Kamil Buksakowski "Claude Code Test Backend"](https://dev.to/kamilbuksakowski/letting-claude-code-test-your-backend-verifying-business-logic-via-api-and-sql-1635) | 实践文章 | API+SQL 双重验证、决策树用例组织 |
| [CSDN "接口自动化测试｜MySQL 断言"](https://devpress.csdn.net/xclaw/6a053a840a2f6a37c5a9ff36.html) | 实践文章 | 接口+DB 双校验架构 |
| [掘金 "Claude Code Skill 接口自动化测试"](https://juejin.cn/post/7623748440833474570) | 实践文章 | 四层模板架构、15 条硬约束、10+ 踩坑经验 |
| [MySQL 5.7 窗口函数模拟指南](https://towardsdev.com/emulating-window-functions-in-mysql-5-7-a-comprehensive-guide-85b171da7ba6) | 技术文章 | 用户变量/自连接/存储过程替代方案 |
