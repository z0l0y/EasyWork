# Reference Baseline Gate（参考基线闸门）

> **铁律 #33**：对成熟领域（认证/支付/上传/缓存等），CODE 之前必须在 GitHub/Web 搜索已有实现模型，列出常见实现模型，产出对比表（我们的方案 vs 参考实现）。禁止闭门造车。
> 此闸门在 L2+ 任务且领域为"成熟"时强制执行。L0/L1 和非成熟领域跳过，但需标注理由。

---

## 1. 适用判断

### 什么领域是"成熟"的

成熟领域 = 有广泛使用的开源项目、官方 SDK、或大量技术文章覆盖的领域。包括但不限于：

| 领域 | 成熟信号 |
|------|---------|
| 认证系统 | OAuth 2.0, JWT, SAML, Passport.js, Auth0 |
| 支付集成 | Stripe, PayPal, 微信支付, 支付宝 |
| 文件上传 | Multer, Uppy, tus.io, AWS S3 SDK |
| 缓存策略 | Redis, Memcached, LRU, Cache-Aside, Write-Through |
| 消息队列 | RabbitMQ, Kafka, SQS, Bull |
| 邮件发送 | Nodemailer, SendGrid, SES |
| 日志系统 | Winston, Pino, ELK, OpenTelemetry |
| 数据库 ORM | Prisma, TypeORM, Sequelize, Drizzle |
| 表单验证 | Zod, Joi, Yup, React Hook Form |
| 状态管理 | Redux, Zustand, MobX, Pinia |
| API 设计 | RESTful 规范, GraphQL, tRPC, gRPC |
| 定时任务 | Cron, Bull Queue, node-cron, Agenda |

### 什么领域不需要参考基线

| 领域类型 | 理由 | 处理 |
|---------|------|------|
| 公司内部业务逻辑 | 外部无参考实现 | 标注"非成熟领域：公司内部业务逻辑，无可参考外部实现" |
| 全新协议/算法 | 学术前沿，无广泛使用案例 | 标注"非成熟领域：{具体说明}"，建议搜索学术论文 |
| 胶水代码 | 只是连接两个已有系统 | 标注"非成熟领域：胶水代码，直接使用官方 SDK 文档" |
| L0/L1 任务 | 改动太小，无需外部参考 | 标注"跳过：风险等级 L{N}，不适用参考基线闸门" |

---

## 2. 参考基线收集流程

### Step 1 — 搜索

**搜索目标**（选 2-3 个）：

```
GitHub 搜索：
  - {语言} + {领域关键词} + "best practice" / "example" / "boilerplate"
  - sort:stars → 取前 5 个结果中活跃的项目（最近 6 个月有提交）
  
Web 搜索：
  - "{领域} 最佳实践" / "{领域} 实现方案对比"
  - 官方文档（如 stripe.com/docs, auth0.com/docs）
  - 技术博客（如 medium.com, dev.to, 掘金, 知乎专栏）
  
如需要，使用 WebSearch 工具：
  - "how to implement {领域} in {语言}"
  - "{领域} architecture patterns"
```

### Step 2 — 提取实现模型

从搜索结果中提取 **3-5 种常见实现模型**。每种模型：

| 字段 | 内容 |
|------|------|
| **模型名称** | 给这种实现方式起一个简短的名字 |
| **核心设计** | 3-5 句话描述关键设计决策 |
| **代表性项目** | GitHub URL 或 npm 包名（含 stars/下载量） |
| **适用场景** | 什么条件下这个模型是最佳选择 |
| **局限性** | 什么条件下这个模型不适用 |

### Step 3 — 对比表

用自己的方案与参考模型做对比：

```markdown
| 维度 | 我们的方案 | 参考模型 A ({名称}) | 参考模型 B ({名称}) |
|------|-----------|-------------------|-------------------|
| 核心思路 | ... | ... | ... |
| 复杂度 | 低/中/高 | 低/中/高 | 低/中/高 |
| 依赖 | ... | ... | ... |
| 性能 | ... | ... | ... |
| 安全性 | ... | ... | ... |
| 可维护性 | ... | ... | ... |
| 社区支持 | ... | {stars/contributors} | {stars/contributors} |
```

### Step 4 — 选择理由

```markdown
**我们选择 {方案 X / 模型 A} 的理由**：
1. {技术理由 1}
2. {技术理由 2}
3. {与项目现有技术栈的契合度}

**不选择 {模型 B} 的理由**：
1. {具体技术理由——不是"太复杂"，而是"引入 Kafka 需要运维团队支持，当前团队无此能力"}
```

---

## 3. 对比表输出格式

Agent 在 READ 阶段末尾输出（在需求可追溯矩阵之后）：

```markdown
## 📚 参考基线（Reference Baseline）

### 领域成熟度判定
- 领域：认证系统（用户登录+JWT Token管理）
- 判定：成熟领域 ✅
- 搜索范围：GitHub (Node.js + JWT auth), Web (JWT best practices 2026)

### 发现的实现模型

| # | 模型名称 | 核心设计 | 代表性项目 | 适用场景 | 局限性 |
|---|---------|---------|-----------|---------|--------|
| 1 | JWT + Refresh Token | Access Token (15min) + Refresh Token (7d) 双 token 机制 | [node-jsonwebtoken](https://github.com/auth0/node-jsonwebtoken) (17k★) | 无状态 API，微服务 | Token 无法主动失效（需黑名单） |
| 2 | Session + Redis | 服务端 Session，Redis 存储，Cookie 传输 session_id | [express-session](https://github.com/expressjs/session) (6k★) | 单体应用，需要主动登出 | 服务端有状态，水平扩展需 Redis |
| 3 | OAuth 2.0 + PKCE | 第三方登录 + Authorization Code + PKCE 防攻击 | [openid-client](https://github.com/panva/node-openid-client) (1.5k★) | 需要第三方登录（Google/GitHub） | 实现复杂，调试困难 |
| 4 | Magic Link | 邮箱收链接，点击即登录，无需密码 | [next-auth](https://github.com/nextauthjs/next-auth) (25k★) | 降低登录摩擦，无密码趋势 | 依赖邮件投递可靠性 |

### 对比分析

| 维度 | 我们的方案 (JWT+Refresh) | 模型 1 (JWT+Refresh) | 模型 4 (Magic Link) |
|------|------------------------|---------------------|-------------------|
| 核心思路 | bcrypt 验证 → 签发 JWT access+refresh token | 与我们的方案一致 | 免密码，邮箱链接登录 |
| 复杂度 | 中 | 中 | 低（对用户）/ 中（对开发者） |
| 依赖 | jsonwebtoken, bcryptjs | jsonwebtoken | nodemailer, 邮件服务 |
| 安全性 | Access Token 15min 过期 | 相同 | 链接一次性使用+5min 过期 |
| 社区支持 | — | 成熟（17k stars） | 成熟（next-auth 25k stars） |

### 选择理由

**我们选择 JWT + Refresh Token（模型 1）**：
1. 项目已是无状态 API 架构，JWT 天然匹配——不需要引入 Redis 做 Session 存储
2. bcrypt + JWT 是行业内最广泛验证的方案，安全边界清晰
3. 不需要第三方登录（无 OAuth 2.0 需求），Magic Link 需要额外邮件基础设施

**不选择 Magic Link（模型 4）**：
1. 需要引入邮件发送服务——当前项目无邮件基础设施
2. 用户群体期望传统密码登录方式（内部管理系统）
```

---

## 4. Gate Judgment Rules

| 深度 | 闸门类型 | 命中处理 |
|------|---------|---------|
| **detailed** | **HARD GATE** | 成熟领域 + L2+ 但未搜索参考实现 → **拒绝进入 CODE** → 回退搜索 |
| **standard** | **SOFT GATE** | 警告但允许继续（标注"未搜索参考基线"） |
| **brief** | **SKIP** | 跳过但标注"参考基线未经检查" |

### 质量检查

```
即使搜索了，以下情况也视为未通过：
  - 对比表为空或只有 1 个模型 → 搜索不充分
  - 所有模型都来自同一来源 → 搜索范围太窄
  - 选择理由全是"更简单""更好"等无技术内容的判断 → 分析不充分
  - 没有标注代表性项目的 stars/活跃度 → 无法评估模型可信度
```

---

## 5. 反模式

- ❌ **搜索结果全是自己公司内部代码**：没有真正搜索外部——用 WebSearch 而非搜项目内代码
- ❌ **对比表"我们的方案"全部最优**：每个维度都是自己最好——说明对比不客观，缺少诚实评估
- ❌ **跳过搜索说"这个很简单不需要参考"**：即使简单的文件上传也有 Multer vs Busboy vs 原生 stream 的设计取舍
- ❌ **只搜中文/只搜英文**：应覆盖中英文技术社区
- ❌ **参考了但没读**：列了 3 个 GitHub 项目但没看源码——对比表中的"核心设计"列是猜的
- ❌ **非成熟领域硬找参考**：公司内部结算逻辑——GitHub 上不会有。标注"非成熟领域"即可
