---
name: git-split-commit
description: >
  提交拆分。EXAMINE 之后执行。将大坨改动按维度（配置/核心逻辑/UI/测试）
  拆成可逐个审查的小提交单元。每个单元附带文件清单、改动说明、风险分析、
  验证方式。这是 HITL 的关键环节——让人类能轻松审查，而不是面对 40 个文件的 diff 直接点 Approve。
  ⚠️ 安全策略：禁止自动执行 git 命令，拆分方案和命令写入文件供用户手动执行。
allowed-tools: Bash, Read, Grep
model: haiku
version: 2.4
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
4. **body 解释做了什么、为什么**（而非怎么做的——代码已经说明怎么做的）
5. 如果关联 Issue/PR，在 body 末尾引用：`Closes #123` / `Refs #456`

### 提交示例

```
feat(favorite): add bookmark article API endpoint

Add POST /api/articles/:id/favorite and DELETE /api/articles/:id/favorite
endpoints. Users can bookmark articles for later reading.

- New table: user_favorites (user_id, article_id, created_at)
- Auth middleware applied to both endpoints
- Idempotent: favoriting an already-favorited article returns 200

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

1. **文件清单**：列出本单元的所有文件及一句话改动说明
2. **改动说明**：2-5 句话概括做了什么、为什么
3. **风险分析**：具体说明最大风险点（不是笼统的"可能有bug"，而是"如果 XX 条件不满足，YY 模块会返回空数组导致前端渲染空白"）
4. **验证方式**：引述 REVIEW 和 EXAMINE 的结果证明这个单元是可靠的
5. **提交消息**：按 Conventional Commits 格式给出建议的 commit message

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

## 反模式

- ❌ 所有文件塞一个提交——等于没拆
- ❌ 每个文件一个提交——碎片化过度，审查者要在提交间跳来跳去
- ❌ 核心逻辑和它的测试拆成两个提交——审查实现时需要看测试来理解预期行为
- ❌ 混合文件不标记——审查者以为只是配置改动，结果里面藏着逻辑变更
- ❌ 风险分析写"应该没问题"——等于没分析
- ❌ 提交消息写"fix bug"——提供零信息量，无法从 `git log` 理解变更历史
