# 故障模式与预置 Runbook

> **用途**：当 Agent 在工作流中遇到特定故障模式时，按此 Runbook 处理，
> 而不是每次都重新发明应对方案。这些来自真实生产环境中反复出现的问题模式。

---

## Runbook 使用说明

每个 Runbook 包含：
- **症状识别**：怎么判断遇到了这个问题
- **诊断步骤**：如何定位根因
- **预置方案**：优先尝试的解决路径（按成功率排序）
- **升级条件**：什么时候从"Agent 自己修"升级到"挂起用户"

---

## Runbook 1：测试框架无法启动

### 症状识别
- `npm test` / `pytest` / `go test` 返回非零退出码但不是测试失败
- 错误信息包含 `cannot find module`、`worker_threads`、`incompatible version`
- 测试进程在 5 秒内退出（而非运行测试后退出）

### 诊断步骤
1. 检查测试框架版本与运行时版本是否兼容：
   ```bash
   node -v && npx jest --version          # Node.js
   python --version && pytest --version    # Python
   go version                              # Go
   ```
2. 检查依赖是否已安装：
   ```bash
   ls node_modules/.package-lock.json 2>/dev/null || echo "node_modules 不完整"
   ```
3. 检查测试配置文件是否有语法错误：
   ```bash
   npx jest --showConfig 2>&1 | head -5   # 看是否有解析错误
   ```

### 预置方案（按成功率排序）

| 方案 | 成功率 | 耗时 | 适用场景 |
|------|--------|------|---------|
| `npm ci` / `pip install -r requirements.txt` 重装依赖 | 60% | 2-5 分钟 | `node_modules` 不完整或版本不匹配 |
| 升级测试框架到兼容版本 | 25% | 5-15 分钟 | 明确的版本不兼容（如 Jest 27 vs Node 20） |
| 用 `--passWithNoTests` / `--ignore` 跳过无关 | 10% | 1 分钟 | 项目有测试文件但无相关测试 |
| 修复测试配置（`jest.config` / `pytest.ini`） | 5% | 10-30 分钟 | 配置文件损坏 |

### 升级条件
- 重装依赖后仍然失败 → 挂起用户
- 上一次 session 的测试可以跑，本次不能 → 可能是本次改动导致 → 检查 `code_output.files_changed` 是否涉及测试配置
- 超过 15 分钟无法修复 → 挂起用户，使用 SOP 模板

### SOP 输出
```
【EXAMINE 阻断 - 测试环境不可用】
问题：{具体错误信息}
已尝试：
  1. npm ci（重装依赖）— 结果：{成功/失败}
  2. 检查 Node/Jest 版本兼容性 — {兼容/不兼容}
这与本次代码修改{有关/无关}。
选项：
  A) 跳过测试，仅凭 REVIEW 静态审查继续
  B) 先修复测试环境，再继续工作流
  C) 你手动运行测试，我基于你提供的结果继续
→ 请选择。
```

---

## Runbook 2：依赖安装冲突

### 症状识别
- `npm install` / `pip install` 报 `ERESOLVE` / `dependency conflict`
- 错误信息包含 `unable to resolve dependency tree`
- 特定包的版本被多个父依赖要求不同版本

### 诊断步骤
1. 识别冲突的包：
   ```bash
   npm ls {package_name} 2>&1                    # 看哪些包依赖了它
   npm explain {package_name} 2>&1               # npm 7+ 的解释功能
   ```
2. 确认是否与本次改动有关：
   - 检查 `code_output.new_dependencies` 是否引入了新包
   - 检查 `code_output.files_changed` 是否修改了 `package.json`

### 预置方案

| 方案 | 成功率 | 风险 | 适用场景 |
|------|--------|------|---------|
| `npm install --legacy-peer-deps` | 50% | 中 | 本次未引入新依赖，冲突是已有问题 |
| 在 `package.json` 中固定冲突包的版本到兼容版本 | 30% | 低 | 有一个明确的兼容版本 |
| 升级冲突包的父依赖 | 15% | 高 | 父依赖的新版本已解决冲突 |
| 用 `overrides` / `resolutions` 强制版本 | 5% | 高 | 其他方案均失败 |

### 升级条件
- 冲突的包是本次新增的 → 考虑替代方案（换一个包 / 自己实现）
- 冲突的包是已有的 → 这是项目基础设施问题，挂起用户

---

## Runbook 3：Git 工作区不干净

### 症状识别
- `git status` 显示有未跟踪或已修改的文件
- 这些文件不是本次 EasyWork 产生的
- `git stash` 可能覆盖用户之前的改动

### 诊断步骤
1. 列出所有非本次改动的变更：
   ```bash
   git status --short
   ```
2. 区分来源：
   - EasyWork 产生（`.claude/easywork/` 下的文件）→ 安全，可以继续
   - 用户之前的改动 → 需要和用户确认
   - 构建产物（`dist/`、`node_modules/`）→ 通常在 `.gitignore` 中

### 预置方案

| 方案 | 适用场景 |
|------|---------|
| 只 stash EasyWork 产生的文件 | 混合了用户改动和 EasyWork 输出 |
| 向用户报告并请求清理 | 工作区有用户未提交的改动 |
| 创建临时分支保存用户改动 | 用户之前有在进行的修改 |

### SOP 输出
```
【GIT 阻断 - 工作区不干净】
检测到以下非本次改动的变更：
  M src/services/payment.service.ts  ← 可能你的未提交改动
  ?? .claude/easywork/report.html    ← EasyWork 产出

选项：
  A) 我只 stash EasyWork 产出文件，保留你的改动
  B) 全部 stash，用 git stash pop 可恢复
  C) 你手动清理后再继续
→ 请选择。
```

---

## Runbook 4：Agent 自我怀疑循环

### 症状识别
- Agent 在同一决策上来回纠结
- 反复修改同一段代码（改了又改回）
- 输出中出现"也许……不过……但是……"

### 诊断步骤
这不是技术问题，是 Agent 缺乏足够信息来做决策。检查：
1. READ 阶段的 `constraints` 是否不够具体？
2. 用户是否没有给出明确的偏好？
3. 是否有两种方案确实优劣相当？

### 预置方案

**唯一正确方案：挂起用户。**

```
【决策挂起 — 信息不足】
在 {决策点} 上，有两个方案优劣相当：

方案 A：{描述} — 优点：{X} / 风险：{Y}
方案 B：{描述} — 优点：{P} / 风险：{Q}

我需要的额外信息：{问题}
→ 请选择，或提供更多上下文。
```

**禁止行为**：抛硬币、选一个然后不告知用户、继续纠结消耗上下文。

---

## Runbook 5：上下文窗口濒临溢出

### 症状识别
- 上下文使用 > 80%
- 剩下的步骤 ≥ 3 步
- 每步都需要加载新的 SKILL.md + 产出物

### 诊断步骤
1. 评估剩余步骤的上下文消耗估算
2. 计算在 🔴 之前能完成几步骤
3. 决定是否需要提前保存状态

### 预置方案

| 上下文 | 剩余步骤 | 方案 |
|--------|---------|------|
| 🟠 80-90% | ≤ 2 步 | 精简输出，继续 |
| 🟠 80-90% | ≥ 3 步 | 保存状态快照 + 建议 `/clear` |
| 🔴 > 90% | 任意 | 强制保存 + 停止 |

### 快照保存检查清单
- [ ] `easywork_version` 已记录
- [ ] `task_type` + `risk_level` 已记录
- [ ] `current_step` 指向下一步（已完成的最后一步 + 1）
- [ ] `completed_steps` 完整列表
- [ ] `skipped_steps` 及跳过原因
- [ ] `step_outputs` 包含已完成步骤的关键产出（至少必填字段）

---

## 追加 Runbook 模板

团队遇到新的重复故障模式时，按此模板追加：

```markdown
## Runbook N：{故障名称}

### 症状识别
- {症状1}
- {症状2}

### 诊断步骤
1. {检查步骤1}
2. {检查步骤2}

### 预置方案（按成功率排序）

| 方案 | 成功率 | 耗时 | 适用场景 |
|------|--------|------|---------|
| {方案A} | {X}% | {耗时} | {场景} |
| {方案B} | {Y}% | {耗时} | {场景} |

### 升级条件
- {什么情况下挂起用户}
```
