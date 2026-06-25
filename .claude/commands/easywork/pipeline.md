---
description: "🔗 流水线——7 条内置流水线+动态 DAG 编排"
argument-hint: "[流水线描述，如：先理解项目，再追踪支付模块]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/fullchain-dev-workflow/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
