---
name: git-split-commit
description: >
  提交拆分。EXAMINE 之后执行。将大坨改动按维度（配置/核心逻辑/UI/测试）
  拆成可逐个审查的小提交单元。每个单元附带文件清单、改动说明、业务上下文、
  风险分析、验证证据、开发者Check清单。这是 HITL 的关键环节——让人类能轻松审查，
  而不是面对 40 个文件的 diff 直接点 Approve。
  v2.5: 业务上下文说明、逐项开发者Check清单、风险引入与验证证据、
  Git链路追踪数据输出。
  ⚠️ 安全策略：禁止自动执行 git 命令，拆分方案和命令写入文件供用户手动执行。
allowed-tools: Bash, Read, Grep
model: haiku
version: 2.9
---

# Git Split Commit（提交拆分）

## ⛔ 安全约束（优先于所有其他规则）

**Agent 绝对禁止自动执行以下 git 命令**，必须在用户明确说"可以执行"之后方可操作：

```
禁止自动执行：git add / git commit / git push / git stash / git stash pop
              git reset / git rebase / git merge / git tag / git branch -D
              gh pr create / gh mr create / 任何部署命令
```

**正确做法**：
1. 输出拆分方案（文本/表格）供用户审查
2. 将具体 git 命令写入 `.claude/easywork/git-commands.sh`（Unix）或 `.bat`（Windows）
3. 告知用户脚本路径，由用户决定是否执行
4. 仅在用户明确授权后，Agent 才可逐条执行命令

> 详细规则见 `../fullchain-dev-workflow/references/security-policy.md` §1。

## 前置判断

**必须执行**：改动文件 ≥ 3 个且跨多个维度。

**可以跳过**：改动 ≤ 2 个文件且属同一维度（拆无可拆）、纯理解任务。

## 为什么这是 HITL 的核心

一个人面对 40 个文件的 diff，滚动 5 秒后大脑就会过载，然后倾向于直接点 Approve。
前面 REVIEW + EXAMINE 的所有努力，会在这 5 秒内化为乌有。

把大坨改动拆成 4-6 个"一口能吃下"的小单元，每个单元 2-8 个文件，附带清晰的风险标注——
人类审查者可以轻松地逐个看过去，在高风险单元多花时间，在低风险单元快速扫过。

## 提交消息规范（🆕 v2.3）

所有提交消息必须遵循 **Conventional Commits** 规范：

```
<type>(<scope>): <subject>

<body>
```

### 类型（type）

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): add OAuth2 login support` |
| `fix` | Bug 修复 | `fix(api): handle null response in payment callback` |
| `refactor` | 重构（不改外部行为） | `refactor(order): extract policy classes from OrderService` |
| `test` | 测试补充 | `test(payment): add edge case tests for refund flow` |
| `docs` | 文档 | `docs(api): update login endpoint documentation` |
| `style` | 样式/格式（不影响逻辑） | `style(button): fix hover color in dark mode` |
| `chore` | 构建/配置/依赖 | `chore(deps): upgrade jest to v29` |
| `perf` | 性能优化 | `perf(query): add index on users.email column` |
| `ci` | CI/CD 变更 | `ci: add test coverage threshold to pipeline` |

### 范围（scope）

`scope` 是可选的，但**强烈建议**标注。使用模块/服务/组件名：
- `auth`, `payment`, `order`, `user`
- `api`, `db`, `config`, `ui`

### 格式规则

1. **subject 不超过 50 字符**（英文）/ **25 个汉字**（中文）
2. **subject 用祈使语气**：`add` 而非 `added`；`fix` 而非 `fixed`
3. **body 每行不超过 72 字符**
4. **body 必须包含三段（🆕 v2.5）**：
   - **改动原因**：业务层面的为什么（不是技术层面的怎么做的）
   - **风险说明**：引入什么风险、影响范围、缓解措施
   - **验证方式**：哪些测试覆盖、结果如何
5. 如果关联 Issue/PR，在 body 末尾引用：`Closes #123` / `Refs #456`

### 提交示例（v2.5 增强）

```
feat(favorite): add bookmark article API endpoint

改动原因（业务）：
用户反馈在文章列表中看到感兴趣的内容后无法标记，需要复制链接到
笔记软件保存。新增收藏功能让用户在站内即可保存和回顾感兴趣的文章。

风险说明：
- 新增 user_favorites 表，写入操作在 POST /api/articles/:id/favorite
  端点——如果并发收藏同一篇文章，唯一索引防止重复插入
- 删除操作是软删除——不影响已有数据，风险低
- Auth 中间件已覆盖，未登录用户返回 401

验证方式：
- favorite.test.ts 覆盖：正常收藏、重复收藏（幂等）、取消收藏、
  未登录访问、收藏不存在的文章
- 全部 8 个测试通过
- REVIEW 安全性维度通过

Closes #234
```

### 不推荐的提交消息

```
❌ "fix bug"                                    — 什么 bug？哪里？
❌ "updated stuff"                              — 什么的 stuff？
❌ "WIP"                                        — WIP 之后是什么？
❌ "修复了一个问题"                                — 什么问题？
❌ "feat: add favorite, fix login bug, refactor"  — 拆开！一个提交一件事
```

## 四个拆分维度

拿到本次所有改动文件后，按以下维度归类：

| 维度 | 包含内容 | 审查优先级 | 对应 commit type | 人类应花的时间 |
|------|---------|-----------|-----------------|--------------|
| **配置/构建** | package.json、config、Dockerfile、CI、.env | ⭐ 低 | `chore`/`ci` | 快速扫一眼 |
| **核心逻辑** | Service/Domain/API/状态管理/中间件/数据库操作 | ⭐⭐⭐ 高 | `feat`/`fix`/`refactor`/`perf` | 仔细看每一行 |
| **UI/样式** | 页面模板、CSS/SCSS、布局调整 | ⭐⭐ 中 | `feat`/`fix`/`style` | 看关键交互 |
| **测试/文档** | 测试文件、README、CHANGELOG、注释 | ⭐ 低 | `test`/`docs` | 确认覆盖合理 |

## 每个拆分单元必须包含

每个拆分单元现在包含 **7 项必填内容**（v2.5 从 5 项扩展）：

1. **文件清单**：列出本单元的所有文件及一句话改动说明
2. **改动说明**：2-5 句话概括做了什么、为什么
3. **业务上下文说明（🆕 v2.5）**：结合项目实际业务说明这些改动在业务上达成了什么目的——不是泛泛的"修复了某 bug"，而是"这个改动解决了用户在什么场景下遇到的什么问题，对什么业务流程有什么影响"
4. **引入风险（🆕 v2.5）**：具体说明最大风险点——什么场景下可能触发问题、影响范围是什么、缓解措施或回滚策略
5. **验证证据（🆕 v2.5）**：引述 REVIEW 和 EXAMINE 的结果证明这个单元是可靠的——不只是"测试通过了"，而是"哪些测试覆盖了哪些场景，结果如何"
6. **开发者 Check 清单（🆕 v2.5）**：每项改动附上逐项 Check，用户在 commit 前逐项确认
7. **提交消息**：按 Conventional Commits 格式给出建议的 commit message，body **必须**包含改动原因（业务）、风险说明、验证方式

### 业务上下文说明规范（🆕 v2.5）

业务上下文不是技术描述。它回答的问题是："一个不了解这段代码的产品经理读完这段话，能理解这次改动对用户/业务产生了什么影响吗？"

❌ 错误（纯技术描述）：
> 修改了 auth.service.ts 的 login 方法，添加了 token 刷新逻辑。

✅ 正确（业务上下文）：
> 用户登录后约 15 分钟就会被踢出。原因是 session 刷新使用本地时间判断过期——当用户设备时间比服务器慢几分钟时，session 在服务器已过期但客户端以为还在有效期，下次请求直接被 401。受影响用户：日均约 300 人（设备时间偏差 >2 分钟的用户占比约 10%）。本次改动让 token 刷新基于服务器时间，用户只要在持续操作就不会被意外踢出。

### 开发者 Check 清单（🆕 v2.5）

每个拆分单元附带以下 Check 项：

```
### 开发者 Check

- [ ] 改动范围符合需求——只改了该改的，没有蔓延到无关模块
- [ ] 无意外副作用——检查了所有调用方和依赖方，确认行为不变
- [ ] 测试覆盖充分——正常路径和异常路径都有测试验证
- [ ] 代码风格一致——与项目现有模式保持一致，没有引入新的设计模式
- [ ] 文档/注释已更新——如有新增公共 API 或配置项
```

用户可以逐项勾选，在 commit 前确认。Agent 也可以在后续会话中回填 Check 状态。

## 混合文件处理

如果某个文件同时涉及配置+逻辑+UI（物理上无法拆分）：

- **不要强行拆**——拆了会导致单个提交无法编译
- **标记为【⚠️ 混合变更】**：在文件清单中用醒目标记
- **在说明中分小节**：注明不同维度改动在文件的哪些行
- **commit type 用主要变更的类型**：如果核心逻辑占 70% → 用 `fix`/`feat`

## 拆分后向用户确认

输出拆分方案，等待用户确认：

```
【GIT 拆分方案】
共 {N} 个文件，拆为 {M} 个提交单元：

1. chore(config): 升级依赖版本（{x}个文件）— 风险：低
   提交消息：chore(deps): upgrade jest to v29 and typescript to v5
2. fix(payment): 修复支付回调空指针（{y}个文件）— 风险：高 ⚠️ 重点审查
   提交消息：fix(payment): handle null response body in alipay callback
3. test(payment): 补充支付回调测试（{z}个文件）— 风险：低
   提交消息：test(payment): add null response and timeout tests for callback

请确认拆分方案，或告诉我需要调整的部分。

⛔ 确认后，我将把 git 命令写入 .claude/easywork/git-commands.sh，
   你可以审查后手动执行，或授权我逐条执行。
```

> **拆分策略与操作命令**：拆分原则、常见场景拆分示例、实际 git 操作命令、HITL 交互指南，见 `references/split-strategies.md`。

> **安全策略**：禁止 Agent 在用户确认拆分方案后自动执行 git commit/push。详见 `../fullchain-dev-workflow/references/security-policy.md` §1。

## 🆕 Git 链路追踪数据（v2.5）

GIT 步骤除了产出拆分方案（`git_output`），还需输出 `git_tracking` 数据，供 lark-doc 等后端写入 Git 链路追踪文档。

### 数据格式

```
git_tracking:
  task_description: "{任务简述（业务语言）}"
  task_date: "{YYYY-MM-DD}"
  task_type: "{Bug修复/功能开发/重构/微调/纯文档}"
  risk_level: "{low/medium/high}"
  units:
    - index: 1
      dimension: "logic"
      files: ["auth.service.ts", "session.ts"]
      summary: "修复登录 session 超时问题"
      business_context: "{业务上下文——为什么改、影响什么用户/场景}"
      risk_level: "medium"
      risk_introduced: "{引入风险——什么场景触发、影响范围、缓解措施}"
      verification_evidence: "{验证证据——测试覆盖场景 + 结果}"
      commit_message:
        type: "fix"
        scope: "auth"
        subject: "使用服务器时间判断 token 过期"
        body: "{改动原因}\n{风险说明}\n{验证方式}"
      developer_checklist:
        scope_correct: false
        no_side_effects: false
        test_coverage: false
        style_consistent: false
        docs_updated: false
      commit_hash: null
  examine_result:
    test_command: "{测试命令}"
    test_total: {N}
    test_passed: {N}
    test_failed: 0
    test_skipped: 0
    verdict: "pass"
```

### 输出位置

- git_tracking 数据随 `git_output` 一起产出
- Agent 在 GIT 步骤结束时将 git_tracking 写入 data-contract 的对应字段
- lark-doc 后端读取此数据写入飞书 Git 链路追踪文档
- 其他后端（local_html、markdown）在最终报告中引用此数据

### 模板参考

Git 链路追踪文档的完整结构和格式见 `assets/git-chain-tracking-template.md`。

## 反模式

- ❌ 所有文件塞一个提交——等于没拆
- ❌ 每个文件一个提交——碎片化过度，审查者要在提交间跳来跳去
- ❌ 核心逻辑和它的测试拆成两个提交——审查实现时需要看测试来理解预期行为
- ❌ 混合文件不标记——审查者以为只是配置改动，结果里面藏着逻辑变更
- ❌ 风险分析写"应该没问题"——等于没分析
- ❌ 提交消息写"fix bug"——提供零信息量，无法从 `git log` 理解变更历史
- ❌ 改动说明只写技术细节不写业务原因——后人不知道为什么要这样改
- ❌ 风险分析写"应该没问题"——要有具体场景、影响面、缓解措施
- ❌ 开发者 Check 清单全空——用户在 commit 前应至少检查范围正确性和测试覆盖
- ❌ Git 链路追踪数据缺失——后端无法写入追踪文档，链路断裂
