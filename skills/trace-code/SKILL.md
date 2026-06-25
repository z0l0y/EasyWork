---
name: trace-code
description: >
  函数级代码追踪与调用链深度分析。不是画架构图——而是从入口函数出发，
  递归展开完整调用树，分析每个函数在干嘛、传什么参数为什么传、
  谁调用了它它又调用了谁、有没有操作数据库改了哪张表、
  RPC/HTTP 入口在哪里、有哪些错误分支。
  核心原则：不潦草带过——每个被调函数必须展开到叶子节点；
  追溯本源——让完全没接触过这个系统的人也能看懂每一步在干嘛、为什么要这样干。
  输出固定 8 段结构：追踪概览→完整调用树→参数全链路追踪
  →数据库操作汇总→RPC/外部调用汇总→错误处理路径→关键决策点与分支逻辑→修改影响分析。
allowed-tools: Read, Bash, Grep, Glob, Write
model: sonnet
version: 1.0
capability:
  id: trace-code
  display_name: 代码追踪器
  emoji: "🔬"
  category: learning
  tier: 1
  inputs:
    - { name: entry_function, type: string, required: true, description: "入口函数名或 API 路径" }
    - { name: entry_file, type: path, required: false, description: "入口函数所在文件（如已知）" }
    - { name: trace_depth, type: enum, required: false, description: "shallow(2)/standard(4)/deep(6)/exhaustive" }
  outputs:
    - { name: trace_report, type: markdown, description: "8 段代码追踪报告（概览→调用树→参数追踪→DB汇总→RPC汇总→错误路径→决策点→影响分析）" }
  triggers: ["追踪代码", "trace", "调用链", "这个函数怎么走", "代码追踪", "追一下"]
  related_skills:
    - { skill: read-project, relationship: inbound, desc: "先理解项目架构再追踪具体调用链" }
    - { skill: test-coverage, relationship: outbound, desc: "追踪中发现覆盖盲区可建议检查测试覆盖" }
  suggested_when:
    - "用户需要理解一个函数/API 的内部实现逻辑"
    - "接到 Bug 需要定位出问题的代码路径"
    - "Code Review 时需要理清复杂函数的所有副作用"
  pipeline_placement:
    good_after: [read-project]
    good_before: [test-coverage, code-implement]
  autonomous:
    callable_by_other: true
    requires_confirmation: false
    max_depth: 2
  risk_level: L0
---

# Trace Code（代码追踪器）

## 定位

**函数级代码追踪器。不是架构概览（那是 `read-project` 的事）——而是从一个函数/接口/入口出发，像调试器一样逐层展开所有调用，让一个完全没接触过这个系统的人也能看懂每一步在干嘛、为什么要这样干。**

跟 `read-project` 的关系：

| | read-project | trace-code |
|---|-------------|-----------|
| 粒度 | 项目级（模块/架构/数据流） | 函数级（每个调用/每个参数/每个if分支） |
| 问题 | "这个项目是什么？" | "这段代码内部怎么走的？" |
| 产出 | 架构图 + 模块深潜 + 接手指南 | 完整调用树 + 参数追踪 + DB/RPC汇总 |
| 阅读方式 | 广度优先（先扫全貌） | 深度优先（从入口一路追到叶子） |
| 典型场景 | 接手新项目，不知道从哪下手 | 接到一个 Bug/需求，要改代码但不知道这段逻辑怎么串的 |

**trace-code 不画架构图，不介绍模块职责——它只做一件事：把一个函数/API 入口的完整执行逻辑递归展开，追到每一个叶子节点。**

---

## 前置判断

### 什么时候用这个 skill

| 场景 | 触发词 |
|------|--------|
| 接手一个 Bug，需要理解出问题的代码路径 | "帮我追踪这个函数 / trace 一下 XX 方法 / 这段代码怎么走的" |
| Code Review 时发现一个函数逻辑复杂，需要理清 | "这个函数内部调用链帮我理一下" |
| 要改一个功能，需要知道会影响哪些地方 | "改这个函数会影响到哪些代码路径" |
| 新人 onboarding，需要理解核心接口的完整实现 | "从 API 入口开始帮我完整追踪一遍" |
| 怀疑有隐藏的副作用（DB 写入/RPC 调用），需要全部找出来 | "帮我找出这个函数所有数据库操作和外部调用" |

### 什么时候不用

- 你只需要找一个函数/类的定义 → 用 Grep/Glob
- 你需要的是项目整体架构理解 → 用 `read-project`
- 函数逻辑非常简单（<10 行，无外部调用）→ 直接 Read，不需要 trace
- 你需要的是性能 profiling → 这不是 trace-code 的职责

### 追踪深度控制

| 深度 | 适用场景 | 行为 |
|------|---------|------|
| **浅层**（shallow，深度 2） | 快速了解调用结构 | 展开 2 层子调用，第 3 层起只列函数名 |
| **标准**（standard，深度 4，默认） | 正常理解代码逻辑 | 展开 4 层，够覆盖大部分业务代码 |
| **深度**（deep，深度 6） | 复杂逻辑/怀疑有隐藏调用 | 展开 6 层，进入框架/库的内部实现 |
| **穷尽**（exhaustive，不限深度） | 安全审计/全面理解 | 追到叶子节点（纯计算/IO 操作/第三方库调用停止） |

用户可指定深度："简单追一下"（浅层）/ "追深一点"（深层）/ "全部追到底"（穷尽）。

**叶子节点判定标准**（遇到以下情况停止展开）：
- 纯计算/数据转换（无外部调用）
- 第三方库函数（标注 `[第三方: {库名}]`）
- 标准库函数（标注 `[stdlib]`）
- 语言内置操作（`len()`/`append`/`map[]`）
- 已达最大深度（标注 `[深度限制]`）
- 已在该调用链中出现过（标注 `[递归, 见上文]`）

---

## 执行流程

### 阶段 1：定位入口

```
用户指定入口 →
  如果是函数名：Grep 找到定义位置
  如果是 API 路径：从路由注册 → handler → 业务逻辑
  如果是文件+行号：直接定位
→ 确认入口函数签名、所在文件、所属模块
→ 如果用户未指定，Agent 主动问："从哪个函数/API 开始追踪？"
```

**常见入口类型**：
| 类型 | 示例 | 定位方法 |
|------|------|---------|
| HTTP handler | `POST /api/order/create` | 路由注册 → handler 函数 |
| gRPC handler | `CreateOrder(ctx, req)` | proto 定义 → 实现函数 |
| CLI 命令 | `app create order --id=123` | 命令注册 → 执行函数 |
| 事件处理器 | `onUserRegistered` | 事件注册 → 回调函数 |
| 定时任务 | cron job | 调度注册 → job 执行函数 |
| 指定函数 | `func ProcessOrder(...)` | 直接 Grep 找到定义 |

### 阶段 2：BFS/DFS 递归展开

从入口函数开始，对每个函数执行：

```
1. Read 函数源码
2. 提取：
   a) 完整签名（参数名+类型+默认值）
   b) 返回值（类型+含义）
   c) 函数体内的所有调用：
      - 本包函数调用 → 递归追踪
      - 外部包函数调用 → 标注 [外部包] + 去 go.mod/package.json 找版本
      - 第三方库调用 → 标注 [第三方: {库名}]
      - 标准库调用 → 标注 [stdlib]
      - 方法调用（obj.Method()）→ 找到类型定义，追到实际实现
      - 接口调用（interface.Method()）→ 找到注入的具体实现
   d) 所有数据库操作（ORM调用/SQL字符串/查询构建器）
   e) 所有 RPC/HTTP/消息队列调用
   f) 所有 if/switch 分支条件
   g) 所有 error/panic/throw 及处理逻辑
3. 对每个本包子函数调用 → 进入递归（深度+1）
4. 如果函数在当前调用链上已出现 → 标注 [递归, 见上文 {位置}]
```

**关键规则**：
- **接口/抽象的方法调用必须找到具体实现**。如果项目用了 DI/接口，Agent 必须追踪注入点，找到运行时会用到的那个实现类。找不到则标注 `[接口调用，实现未确定——可能的实现：A、B、C]`
- **分支必须走全**。if-else 的两条路径都要分析，标注条件。
- **defer/finally 块不能漏**。这些块中的 DB 提交/回滚/清理操作往往是关键。

### 阶段 3：参数数据流追踪

从入口参数开始，追踪每个关键参数在调用链上的传递和转换：

```
参数: userID (入口)
  ├── Handler: userID = req.Params("id")           // 从 URL 提取，string
  ├── Handler→Service: ProcessOrder(userID)         // 原样传递
  │   ├── Service: userID → strconv.Atoi(userID)   // 转换为 int
  │   ├── Service→Repository: FindUser(uid)        // 改名+传类型后传递
  │   │   └── Repository: uid → DB query WHERE id=? // 拼接 SQL
  │   └── Service→PaymentGateway: 未传 userID       // ⚠️ 注意：该参数未传递到支付网关
  └── 最终使用：{users 表的 id 字段 WHERE 条件}
```

### 阶段 4：汇总与输出

将追踪结果按 §5 输出格式模板组织为 8 段报告。

---

## 输出格式模板

```
# 《{入口名称}》代码追踪报告

> 入口：{函数签名 / API 路径} → {文件:行号}
> 追踪深度：{N} 层 | 展开函数：{M} 个 | 叶子节点：{K} 个
> 分析时间：{YYYY-MM-DD HH:MM}

## 0. 追踪概览

| 项目 | 内容 |
|------|------|
| 入口函数 | `{完整签名}` @ `{文件:行号}` |
| 追踪深度 | {shallow(2)/standard(4)/deep(6)/exhaustive(∞)} |
| 展开函数总数 | {M} 个（本包 {m1} + 外部包 {m2} + 标准库 {m3}） |
| 涉及文件 | {N} 个 |
| 数据库操作 | {读 X 次 + 写 Y 次}，涉及 {表1, 表2, ...}，数据库 {db1, db2} |
| RPC/HTTP 调用 | {P} 次，目标 {svc1, svc2, ...} |
| 错误分支 | {E} 条可能的错误返回路径 |
| 关键决策点 | {D} 个分支条件（影响执行路径的 if/switch） |

### 调用树总览（缩略版，每层只显示函数名，不展开详情）

```
{入口函数}                                                 ← 入口
├── {子函数1}                                               ← Layer 1
│   ├── {孙函数1.1}                                         ← Layer 2
│   │   ├── {曾孙函数1.1.1}                                 ← Layer 3
│   │   └── {曾孙函数1.1.2}                                 ← Layer 3 → [stdlib]
│   ├── {孙函数1.2}                                         ← Layer 2
│   │   └── 🗄️ DB: UPDATE {table}                          ← DB操作
│   └── {孙函数1.3}                                         ← Layer 2 → [第三方: gin]
├── {子函数2}                                               ← Layer 1
│   ├── {孙函数2.1}                                         ← Layer 2
│   │   └── 🌐 RPC: {service.Method}                       ← RPC调用
│   └── {孙函数2.2}                                         ← Layer 2
│       ├── ❌ error: {错误类型}                             ← 错误分支
│       └── {曾孙函数2.2.1}                                 ← Layer 3
└── {子函数3}                                               ← Layer 1 → [递归, 见子函数1]

图例：🗄️=数据库操作 | 🌐=RPC/HTTP调用 | ❌=错误返回路径 | 📎=中间件/拦截器
```

## 1. 完整调用树（深度展开）

> 每一层完整展开，不跳步，不潦草带过。每个函数回答三个问题：干嘛的、传了什么、为什么传。

### Layer 0 — 入口

#### `{函数名}({完整参数列表})` → `{返回值类型}`  @ `{文件:行号}`

**职责**：{用一句话说清楚这个函数在整个业务流程中承担什么角色}

**参数详解**：

| 参数 | 类型 | 来源 | 用途 | 为什么需要 |
|------|------|------|------|-----------|
| `{param1}` | `{type}` | {从哪来——URL参数/请求体/上游传入/配置/常量} | {在这个函数或下游中怎么用} | {为什么这个参数不能省略/替换——业务含义} |
| `{param2}` | `{type}` | {来源} | {用途} | {为什么需要} |

**参数来源分类**：
- `[外部输入]`：来自 HTTP 请求、gRPC 请求、CLI 参数、消息队列消息
- `[配置]`：来自配置文件/环境变量
- `[上游传入]`：由调用方传入，在调用方处分析
- `[常量]`：硬编码常量值
- `[上下文]`：来自 context，用于超时控制/追踪/权限传递

**返回值详解**：

| 返回值 | 类型 | 含义 | 调用方怎么用 |
|--------|------|------|------------|
| `{ret1}` | `{type}` | {这个返回值代表什么} | {调用方用它做什么决策/操作} |
| `error` | `error` | {什么情况返回什么错误} | {调用方如何处理这个错误} |

**关键逻辑**（伪代码）：

```
{函数名}({参数列表}):
  1. {步骤1——如"从 context 中提取 userID"}
  2. {步骤2——如"校验订单状态是否为 pending"}
     → if 不是 pending: return error("order not pending")
  3. {步骤3——如"调用 paymentGateway.Charge()"→见 Layer 1}
  4. {步骤4——如"更新订单状态为 paid"→🗄️ DB WRITE}
  5. {步骤5——如"defer 中发送通知"→🌐 MQ publish}
```

**子调用清单**：

| # | 调用 | 所在行 | 类型 | 是否追踪展开 |
|---|------|--------|------|------------|
| 1 | `{子函数1}(args)` | :{line} | 本包函数 | ✅ → Layer 1 |
| 2 | `{子函数2}(args)` | :{line} | 外部包 | → Layer 1（标注包来源） |
| 3 | `db.Exec(...)` | :{line} | 🗄️ DB WRITE | → §3（不展开，在DB汇总分析） |
| 4 | `http.Get(...)` | :{line} | 🌐 HTTP | → §4（不展开，在RPC汇总分析） |
| 5 | `strconv.Atoi(...)` | :{line} | stdlib | ❌ 叶子节点 |

---

### Layer 1 — {子函数1名}

#### `{子函数1完整签名}`  @ `{文件:行号}`

**谁调用了它**：`{父函数名}` @ `{文件:行号}`

**为什么需要这个函数**：{它在父函数逻辑中的角色——父函数需要它完成什么子任务}

**职责**：{一句话}

**参数详解**：

| 参数 | 类型 | 来源（从父函数传入的是什么） | 用途 | 为什么需要 |
|------|------|--------------------------|------|-----------|
| `{p1}` | `{type}` | 父函数的 `{param_name}` 直接传入 / 父函数的 `{param_name}` 经过 `{转换}` 后传入 | {用途} | {为什么} |

**返回值详解**：{同上格式}

**关键逻辑**（伪代码）：

```
{子函数1}({参数}):
  1. ...
  2. ...
```

**子调用清单**：
{同上格式}

---

### Layer 1 — {子函数2名}
{同上格式，递归展开}

---

### Layer 2 — {孙函数名}
{同上格式}

---

{继续递归展开，直到所有分支到达叶子节点}

{对于每个函数，重复以下结构：}
{#### `函数签名` @ `文件:行号`}
{**谁调用了它** / **为什么需要这个函数** / **职责** / **参数详解** / **返回值详解** / **关键逻辑伪代码** / **子调用清单**}

## 2. 参数全链路追踪

> 追踪关键参数从入口到最终使用的完整路径——包括类型转换、重命名、拆分、合并。

### 参数 `{param_name}`（{类型}）

| 阶段 | 函数 | 变量名 | 类型 | 操作 | 行号 |
|------|------|--------|------|------|------|
| 🔵 来源 | — | — | — | {从 HTTP body 解析 / 从 URL path 提取 / ...} | — |
| 入口 | `{入口函数}` | `{var1}` | `string` | 接收原始值，未处理 | :{line} |
| 校验 | `{入口函数}` | `{var1}` | `string` | 校验非空 + 格式 | :{line} |
| 转换 | `{子函数A}` | `{var2}` | `int64` | `strconv.ParseInt(var1)` | :{line} |
| 传递 | `{孙函数B}` | `uid` | `int64` | 作为参数传入，改名 | :{line} |
| 🔴 使用 | `{Repository}` | `uid` | `int64` | `WHERE user_id = uid` | :{line} |

**数据流图**：

```
{param_name} (外部输入, string)
  │
  ├─[入口函数:line] 接收: var1 = req.Body["xxx"]   // string
  │   ├─ 校验: if var1 == "" → return 400
  │   └─ 传递: call 子函数A(var1)
  │
  ├─[子函数A:line] 接收: param = var1              // string
  │   └─ 转换: uid = strconv.Atoi(param)           // string → int
  │       ├─ 成功: call 孙函数B(uid)
  │       └─ 失败: return error("invalid id")      // ❌ 错误分支
  │
  └─[孙函数B:line] 接收: userID = uid              // int
      └─ 使用: db.Query("SELECT * FROM users WHERE id=?", userID)
                                                  // 🗄️ 读 users 表
```

### 参数 `{另一个关键参数}`
{同上格式}

{对 2-5 个最关键的参数进行全链路追踪}

## 3. 数据库操作汇总

### 操作清单

| # | 深度 | 函数 | 文件:行号 | 操作 | 数据库 | 表 | SQL 概要 | 影响 |
|---|------|------|---------|------|--------|-----|---------|------|
| 1 | L0 | `入口函数` | svc.go:42 | 🔍READ | `main_db` | `orders` | `SELECT * FROM orders WHERE id=?` | 获取订单详情 |
| 2 | L1 | `子函数A` | repo.go:88 | ✏️UPDATE | `main_db` | `orders` | `UPDATE orders SET status=? WHERE id=?` | 修改订单状态 |
| 3 | L2 | `孙函数B` | repo.go:120 | ✏️INSERT | `main_db` | `order_logs` | `INSERT INTO order_logs (...) VALUES (...)` | 写入操作日志 |
| 4 | L1 | `子函数C` | cache.go:30 | 🔍READ | `cache_db` | — | `GET order:{id}` (Redis) | 查缓存 |

**图例**：🔍读 | ✏️写 | 🗑️删除 | 🔒事务开始 | ✅事务提交 | ⏪事务回滚

### 数据库分布

| 数据库 | 涉及表 | 操作次数 |
|--------|--------|---------|
| `main_db` (PostgreSQL) | `orders`, `order_logs`, `users` | 读 2 / 写 3 |
| `cache_db` (Redis) | — | 读 1 |

### 事务分析

| 事务范围 | 开始位置 | 结束位置 | 涉及操作 | 回滚条件 |
|---------|---------|---------|---------|---------|
| 入口函数:42-88 | :43 `tx.Begin()` | :87 `tx.Commit()` / :76 `tx.Rollback()` | #1, #2, #3 | 任一步骤返回 error 则回滚 |

> ⚠️ 如果发现没有被事务包裹的关联写操作，标注为潜在风险。

## 4. RPC / HTTP / 外部调用汇总

| # | 深度 | 调用方函数 | 文件:行号 | 目标 | 协议 | 超时 | 重试 | 关键参数 |
|---|------|----------|---------|------|------|------|------|---------|
| 1 | L1 | `子函数A` | svc.go:55 | `payment-service/PaymentService.Charge` | gRPC | 3s | 无 | `orderID, amount, token` |
| 2 | L2 | `孙函数C` | svc.go:78 | `https://api.notify.example.com/send` | HTTP POST | 5s | 3次 | `userID, message` |
| 3 | L1 | `子函数D` | mq.go:20 | `rabbitmq://order.exchange` | AMQP | — | persistent | `orderID, event=created` |

**每个外部调用的上下文**：

### `{外部调用1}`
- **为什么调**：{业务原因——如"支付必须在订单状态变更前完成"}
- **调用时机**：{在哪个操作之后/之前}
- **失败影响**：{如果这个调用失败了，业务流程会怎样——如"返回 500，订单保持 pending，但 payment 已扣款（双写问题⚠️）"}
- **幂等性**：{是否有幂等保证——如"payment-service 基于 orderID 去重"}

## 5. 错误处理路径

### 错误路径总览

```
入口函数
├─ ✅ 正常路径: 参数校验通过 → 查订单 → 支付 → 更新状态 → 发通知 → 返回 200
├─ ❌ 路径1 (L0): 参数校验失败 → return 400 "invalid order_id"
├─ ❌ 路径2 (L1): 订单不存在 → return 404 "order not found"
├─ ❌ 路径3 (L2): 订单状态不是 pending → return 409 "order already processed"
├─ ❌ 路径4 (L2): 支付网关超时 → return 502 "payment timeout"
│   └── ⚠️ 注意：此时订单保持 pending，但支付状态未知（需人工对账）
├─ ❌ 路径5 (L3): DB 更新失败 → return 500 → ⏪ 事务回滚
└─ ❌ 路径6 (L2): 通知发送失败 → ⚠️ 仅 log.Warn，不影响返回（非关键路径）
```

### 逐条错误路径分析

| # | 触发条件 | 触发位置 | 返回内容 | HTTP状态码 | 数据一致性 | 调用方应如何处理 |
|---|---------|---------|---------|-----------|-----------|---------------|
| 1 | order_id 为空或格式非法 | `入口函数:40` | `{"error": "invalid order_id"}` | 400 | ✅ 无副作用 | 提示用户检查输入 |
| 2 | 订单不存在 | `子函数A:65` | `{"error": "order not found"}` | 404 | ✅ 无副作用 | 确认 order_id 是否正确 |
| 3 | 订单状态!=pending | `入口函数:50` | `{"error": "order already processed"}` | 409 | ✅ 无副作用 | 幂等重试/提示用户 |
| 4 | 支付网关超时 | `子函数A:72` | `{"error": "payment timeout"}` | 502 | ⚠️ **双写风险** | 查询支付网关确认状态后重试 |
| 5 | DB 写入失败 | `孙函数B:125` | `{"error": "internal error"}` | 500 | ✅ 事务回滚 | 重试（指数退避） |
| 6 | 通知发送失败 | `子函数C:90` | （不影响返回） | — | ⚠️ 通知丢失 | 后续补偿（MQ 死信队列） |

> **数据一致性评级**：✅ 安全 | ⚠️ 有风险（标注风险类型） | ❌ 已知问题

## 6. 关键决策点与分支逻辑

### 决策点分析

对每个影响执行路径的 if/switch 条件：

#### 决策点 1：`if order.Status != "pending"` — @ `入口函数:50`

**为什么有这个判断**：防止重复支付/重复发货。只有 pending 状态的订单才能进入支付流程。

**条件分析**：
```
order.Status == "pending"   → ✅ 继续支付流程（正常路径）
order.Status == "paid"      → ❌ 返回 409 "already processed"
order.Status == "cancelled" → ❌ 返回 409 "order was cancelled"
order.Status == "expired"   → ❌ 返回 409 "order expired"
其他未知状态                  → ❌ 返回 500 "unknown order status"
```

**如果这个判断被绕过会怎样**：用户可能对同一订单重复付款。支付网关可能有去重（基于 orderID），但不保证。

#### 决策点 2：`switch paymentMethod` — @ `子函数A:80`

**为什么有分支**：不同支付渠道的处理流程不同。

| 分支值 | 走向 | 核心差异 |
|--------|------|---------|
| `"card"` | → `chargeCard()` @ :82 | 同步返回结果，无回调 |
| `"alipay"` | → `createAlipayOrder()` @ :85 | 返回跳转 URL，异步回调确认 |
| `"wechat"` | → `createWxOrder()` @ :88 | 返回 prepay_id，客户端调起支付 |
| `default` | → return error @ :91 | 不支持的支付方式 |

**扩展时注意**：新增支付方式需要实现 `PaymentMethod` 接口（定义在 `payment.go:15`），并在本 switch 中添加分支。

#### 决策点 3：{描述}
{同上格式}

## 7. 修改影响分析

### 如果要改这个入口的逻辑

| 改动意图 | 需要改的函数 | 文件:行号 | 影响范围 | 风险等级 |
|---------|------------|---------|---------|---------|
| 修改订单状态流转 | `入口函数:50` (switch 分支) + `子函数A:65` (状态校验) | svc.go | 仅状态机逻辑 | 🟡 中——需确保状态迁移合法 |
| 新增支付方式 | `子函数A:80` (switch) + 新增 `payment_xxx.go` | svc.go + payment/ | 支付层扩展 | 🟢 低——接口化设计，插拔式 |
| 修改扣款逻辑 | `chargeCard()` @ payment/card.go:30 | payment/card.go | 支付核心 | 🔴 高——涉及资金安全 |
| 添加操作审计 | 入口函数 `defer` 块 @ :87 | svc.go | 仅日志 | 🟢 低——纯增量 |
| 修改超时时间 | `子函数A:72` (context timeout) | svc.go | 调用链超时 | 🟡 中——影响用户体验和重试策略 |
| 加缓存 | `子函数A:60` 前插入缓存检查 + `子函数A:90` 后写入缓存 | svc.go | 查询路径 | 🟡 中——涉及缓存一致性 |

### 改动检查清单

在修改代码前，确认以下事项：
- [ ] 找到所有调用被改函数的调用方 → `{列出文件}`
- [ ] 确认修改不会破坏现有测试 → 测试文件位于 `{路径}`
- [ ] 确认 DB schema 是否需要同步变更 → `{migrations 目录}`
- [ ] 确认 RPC/API 接口是否需要版本升级 → `{proto/api定义位置}`
- [ ] 如果有新错误类型，确认调用方能正确处理 → `{调用方文件}`

---

## 输出后 Agent 行为

追踪完成后，Agent 主动提供后续交互选项：

```
【代码追踪完成】

从 {入口函数} 出发，追踪了 {M} 个函数（深度 {N} 层）。
发现 {D} 个数据库操作、{R} 个外部调用、{E} 条错误路径。

现在你可以：
A) 让我展开某个被跳过的分支（"追一下 {函数名} 的内部"）
B) 让我按某个参数反向追踪（"{参数名} 是从哪里传过来的？"）
C) 让我跨文件分析某个改动的影响面（"如果改了 {函数}，哪些地方会受影响？"）
D) 让我检查某个具体问题（"这个 defer 里的 rollback 在所有错误路径下都会执行吗？"）
E) 让我对比两个函数的实现差异（"对比 {函数A} 和 {函数B}"）
F) 导出追踪报告（"保存到 XX.md"）
G) 基于这个追踪结果，直接开始写代码（"好，现在帮我在 {位置} 加一个 {功能}"）

→ 你想怎么做？
```

---

## 反模式

- ❌ 只追 Happy Path，不展开错误分支——trace-code 的核心价值之一就是暴露隐藏的错误处理
- ❌ 遇到接口调用不找具体实现——标注 `[接口，实现未确定]` 但必须列出可能的实现类
- ❌ defer/finally 块的内容被忽略——这些块的 DB 提交/回滚/资源释放往往是关键
- ❌ 参数只说类型不说为什么——`userID string` 不是分析，要说"userID 是用户的唯一标识，从 JWT token 中提取，用于 DB 查询和权限校验"
- ❌ 外部调用只说"调了 XX 服务"——要说明为什么调、什么时候调、失败了会怎样
- ❌ 数据库操作只说"写了 orders 表"——要说明写的具体字段、在哪个数据库、是否在事务中
- ❌ 错误处理只说"返回 error"——要说明什么条件触发、调用方怎么处理、对数据一致性有什么影响
- ❌ 很深的调用链中途放弃——如果因为上下文限制无法完整追踪，明确标注 `[追踪中断于第 N 层——原因：上下文窗口不足/第三方库闭源]`
- ❌ 猜测函数的实现而非读取源码——必须 Read 实际代码，不能凭函数名推断行为
- ❌ 追踪报告变成"调用关系图"——每个函数必须解释"为什么要这样设计"，不仅"谁调谁"
- ❌ 对 ORM 的隐式操作视而不见——`user.Orders.Load()` 可能触发了 DB 查询，必须标注
- ❌ Middleware/Interceptor/AOP 的隐性逻辑被忽略——这些在请求进入 handler 之前就已经执行了，可能修改了 context/参数/权限
- ❌ 修改影响分析写成"改了 A 会影响 B"——要精确到文件:行号 + 风险等级 + 检查清单
- ❌ 追踪完不提供后续交互选项——用户可能想继续深入某个分支

---

## 特殊场景处理

### 场景 1：接口/抽象方法调用

```
文件: svc.go:55
调用: paymentGateway.Charge(ctx, req)
      ↑ paymentGateway 是 PaymentGateway 接口

追踪步骤:
1. 找接口定义 → payment/gateway.go:10 `type PaymentGateway interface { Charge(...) }`
2. 找注入点 → 通常在依赖注入/wire/init 函数中
3. 找到具体实现 → wire.go:25 `paymentGateway = &stripe.StripeGateway{}`
4. 追踪具体实现 → payment/stripe/gateway.go:30 `func (g *StripeGateway) Charge(...)`
5. 如果有多个实现 → 分析运行时会用到哪个（通常由配置/环境变量决定）
```

### 场景 2：ORM 隐式查询

```
⚠️ 注意：ORM 的某些操作会隐式触发数据库查询

Go GORM 示例:
  db.Where("status = ?", "pending").Find(&orders)     ← 显式查询
  user.Orders                                          ← ⚠️ 隐式查询！GORM Preload/Load

Python SQLAlchemy 示例:
  session.query(Order).filter_by(status="pending").all() ← 显式
  user.orders                                             ← ⚠️ 隐式查询！lazy loading

Agent 必须标注这些隐式操作。
```

### 场景 3：Goroutine / 异步调用

```
文件: svc.go:88
代码: go sendNotification(userID, message)

追踪:
- 这是一个异步调用（goroutine），不阻塞主流程
- 错误处理独立于主流程 → sendNotification 内部的 error 不会影响入口函数的返回值
- ⚠️ 注意：如果 goroutine 内部有 DB 写入，它使用独立的 context（可能已经超时）
```

### 场景 4：Middleware / Interceptor 隐性逻辑

```
请求 → [AuthMiddleware] → [RateLimitMiddleware] → [LoggingMiddleware] → Handler
         ↑ 可能在 context 中注入 userID        ↑ 可能直接返回 429，不到达 Handler

Agent 必须从路由注册代码中找到中间件链，分析每个中间件对 context/参数/响应的影响。
```

### 场景 5：代码生成 / 宏展开

如果项目使用了代码生成（protobuf、gRPC stub、ORM 生成代码等）：
- proto → gRPC stub：标注 `[生成代码] 定义来自 {proto文件}`
- 生成代码不需要逐行分析逻辑（生成框架的模板逻辑），但必须标注生成的接口和类型

---

## 与 read-project 的协作

```
用户场景 1：完全不熟悉一个项目
  步骤1: read-project → 了解项目整体架构、模块划分、数据流
  步骤2: trace-code → 针对你要改的模块/接口，深入理解内部逻辑

用户场景 2：接到一个 Bug，已经熟悉项目
  直接: trace-code → 从出问题的 API handler 开始追踪，定位 Bug 根因

用户场景 3：要做 Code Review
  直接: trace-code → 追踪 PR 中改动的函数，理解所有副作用
```

---

## 版本历史

- v1.0 (2026-06-25)：初始版本。固定 8 段输出结构，4 阶段执行流程（定位入口→递归展开→参数追踪→汇总输出）。支持 4 级追踪深度控制。强制展开错误路径。参数全链路数据流追踪。接口实现自动查找。ORM隐式操作检测。Middleware链分析。修改影响分析+风险等级。
