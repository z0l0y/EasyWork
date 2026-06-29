---
description: "💻 命令管理——斜杠命令的创建/更新/删除/同步/索引"
argument-hint: "[list|create|update|delete|sync|docs]"
disable-model-invocation: false
allowed-tools: Read, Write, Bash, Grep, Glob
---

加载并执行 `skills/slash-cmd/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
