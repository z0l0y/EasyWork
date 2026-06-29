---
description: "🔍 代码审查——七维度代码审查（反合理化+供应链检查）"
argument-hint: "[文件路径或 PR 描述]"
disable-model-invocation: false
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/code-review/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
