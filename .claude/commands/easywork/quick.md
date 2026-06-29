---
description: "⚡ 快问快答——答案先行，要点为辅，直击核心问题"
argument-hint: "[你的问题]"
disable-model-invocation: false
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/quick-answer/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`