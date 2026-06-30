# 🚀 5 分钟上手 EasyWork

> 不需要记任何命令名。直接说话就行。

---

## 第 1 分钟：忘掉命令名

EasyWork 有 28 条命令，但**你不需要记住任何一条**。

Agent 会根据你说的话自动匹配最合适的技能。你只需要描述你想做什么。

---

## 第 2 分钟：三种使用方式

### 🗣️ 自然语言（最推荐）

直接说出你的需求：

```
你：帮我理解这个项目
Agent：好的，我来分析项目结构...
（自动执行 read-project → 输出架构分析报告）

你：帮我修复登录页面的报错
Agent：我先理解一下相关代码...
（自动执行 read-requirements → code-implement → code-review → examine-quality → git-split-commit）

你：帮我 review 一下 src/auth/ 目录
Agent：我来做七维度代码审查...
（自动执行 code-review → 输出审查报告）

你：Docker 是什么，我不太懂
Agent：我来从零解释...
（自动执行 learn-from-zero → 四级解释阶梯）
```

### ⌨️ 斜杠命令

如果你更喜欢精确控制：输入 `/easywork:` 然后按 **Tab** 键 → 自动补全全部 28 条命令。

```
/easywork:radar       → 技术动态扫描
/easywork:compare     → 技术方案对比
/easywork:test        → 接口联调测试
/easywork:canvas      → 打开可视化画布
...
```

### 🎨 场景画板

适合需要**多个技能协同**的复杂场景。在浏览器中拖拽节点、连线、保存、一键执行。

```
/easywork:canvas
```

---

## 第 3 分钟：5 个最常见场景

| 场景 | 直接说 | Agent 自动执行的技能 |
|------|--------|---------------------|
| 📖 **接手新项目** | "帮我理解这个项目" | read-project → graph-fullchain → sum-session |
| 🐛 **修复 Bug** | "帮我修复用户登录失败的问题" | read-requirements → code-implement → code-review → examine-quality → git-split-commit |
| 🔍 **代码审查** | "帮我 review 最近改的代码" | code-review（七维度 + 安全 + 性能 + 兼容性） |
| ⚖️ **技术选型** | "帮我对比 React 和 Vue" | tech-compare（多维度评分矩阵 + 推荐方案） |
| 🧠 **学习新技术** | "我不懂 Kubernetes" | learn-from-zero（ELI5 → 图解 → 知识树 → 专家级） |

---

## 第 4 分钟：什么时候用"编排"模式

当单次对话需要**多个技能串联**时：

| 模式 | 触发方式 | 适合场景 |
|------|---------|---------|
| 🎯 **点模式** | 直接说一个需求 | 单个任务（理解代码、审查、测试） |
| 🔗 **线模式** | "先...再..." | 2-3 个技能串联（"先理解项目再追踪支付链路"） |
| 🌐 **网模式** | "全面分析 / 帮我搞清楚" | 深度排查（"支付模块能不能扛住双11"） |
| 🎨 **场景模式** | `/easywork:canvas` 或 `/easywork:scenario run` | 可视化编排多技能，可保存复用 |

---

## 第 5 分钟：了解更多

| 想了解 | 去看 |
|--------|------|
| 全部 28 条命令速查 | [QUICKREF.md](QUICKREF.md) |
| 版本演进历史 | [DEVLOG.md](DEVLOG.md) |
| 正式 Changelog | [CHANGELOG.md](CHANGELOG.md) |
| 遇到问题怎么办 | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

---

> 💡 **记住一条**：你不需要记住任何命令。直接告诉 Agent 你想做什么就行。
