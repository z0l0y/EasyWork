# 渐进式成熟度配置

不是每个团队都需要全 9 步。EasyWork 提供 L1/L2/L3 三个成熟度级别，
团队可以根据当前阶段选择合适的配置，并随着成熟度提升逐步升级。

---

## 级别对比总览

| 维度 | L1：入门 | L2：标准 | L3：完整 |
|------|---------|---------|---------|
| **适用团队** | 个人项目、原型开发、学习探索 | 5-20 人团队、有 CI/CD | 20+ 人团队、多服务、合规要求 |
| **技能数量** | 4 个核心技能 | 7 个（L1 + 3） | 全部 10 个 |
| **步骤数（功能开发）** | 4 步 | 7 步 | 9 步 |
| **强制执行** | 仅铁律 1-3 | 全部 10 条铁律 | 全部 10 条 + 干跑预览 |
| **ASK 确认** | 最小模式（2 维） | 快速模式（4 维） | 完整模式（6 维） |
| **上下文管理** | 基础（仅 🟢🟡） | 全部 4 级 | 全部 4 级 + 子 Agent |
| **安装目录** | 复制 4 个技能 | 复制 7 个技能 | 复制全部 |

---

## L1：入门（Essentials）

### 包含技能

| 技能 | 理由 |
|------|------|
| `fullchain-dev-workflow` | 编排中枢（分类 + 裁剪） |
| `read-requirements` | 理解需求是最低门槛 |
| `code-implement` | 写代码 |
| `code-review` | 写完自审查 |

### 工作流（功能开发为例）

```
READ → CODE → REVIEW → ASK（最小模式）
```

### 适用场景
- 个人 side project，快速迭代
- 刚开始尝试 AI 辅助工作流
- 原型 / PoC 阶段，正式项目尚未启动

### 安装

只复制以下目录到 `.claude/skills/easywork/`：
```
fullchain-dev-workflow/
read-requirements/
code-implement/
code-review/
```

---

## L2：标准（Standard）— 推荐大多数团队从此开始

### 包含技能

L1 的全部 + 以下 3 个：

| 新增技能 | 理由 |
|---------|------|
| `examine-quality` | 跑测试，验证代码正确性 |
| `git-split-commit` | 团队协作的基础——让别人能审查你的提交 |
| `sum-session` | 每次改动有记录，方便交接和回溯 |

### 工作流（功能开发为例）

```
READ → CODE → REVIEW → EXAMINE → GIT → SUM → ASK（快速模式）
```

### 适用场景
- 有 CI/CD 的正式团队
- 多人协作，有 Code Review 流程
- 项目有自动化测试框架

### 安装

复制以下目录到 `.claude/skills/easywork/`：
```
fullchain-dev-workflow/
read-requirements/
code-implement/
code-review/
examine-quality/
git-split-commit/
sum-session/
```

---

## L3：完整（Full）— 企业级

### 包含技能

L2 的全部 + 以下 3 个：

| 新增技能 | 理由 |
|---------|------|
| `graph-fullchain` | 复杂系统需要可视化辅助理解 |
| `talk-retro` | 从每个 Bug 中提炼工程规范，系统性改进 |
| `ask-change-questions` | 六维度完整确认，适合合规要求高的场景 |

### 工作流

全部 9 步，按任务类型裁剪（与当前 `fullchain-dev-workflow` 完全一致）。

### 适用场景
- 大规模协作（20+ 开发者）
- 金融/医疗/安全等合规行业
- 复杂微服务架构
- 核心基础设施模块

### 安装

执行完整安装脚本（`install.sh` 或 `install.bat`）——复制全部 10 个技能。

---

## 升级路径

```
L1 ──加入测试和团队协作──▶ L2 ──加入深度分析和可视化──▶ L3
```

### 升级信号

**从 L1 升级到 L2 的信号**：
- 你的项目开始有第二个贡献者
- Bug 修了又出现（因为没有测试回归）
- PR 的 diff 开始让人不敢审查

**从 L2 升级到 L3 的信号**：
- 系统有 5+ 个微服务，架构图开始变得必要
- 同一个类型的 Bug 反复出现（需要 TALK 挖根因）
- 有合规/审计要求，上线需要完整记录和确认

### 升级操作

1. 把新增的技能目录复制到 `.claude/skills/easywork/`
2. 如果是 L1→L2，把 `examine-quality/`、`git-split-commit/`、`sum-session/` 复制过去
3. 如果是 L2→L3，把 `graph-fullchain/`、`talk-retro/`、`ask-change-questions/` 复制过去
4. 无需修改 `CLAUDE.md`（编排中枢会自动识别新技能）
5. 在新对话中输入"我现在用的是 EasyWork 什么级别？"验证

---

## 降级

如果需要临时降级（如快速原型阶段不想走深度审查）：

```
"今天用 L1 模式"
```

Agent 会跳过 L2/L3 才有的步骤，等同于临时裁剪。不需要删除技能文件。
