---
description: "📦 智能提交拆分——语义分组+Conventional Commits+风险分级"
argument-hint: "[提交范围或变更描述]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Grep, Glob
---

加载并执行 `skills/git-split-commit/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
