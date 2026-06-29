---
description: "❓ 变更确认——六维度人工确认（HITL 终极闸门）"
argument-hint: "[变更描述或上线检查范围]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/ask-change-questions/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
