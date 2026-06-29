---
description: "✏️ 代码实现——需求文档→代码变更（文件清单+改动原因+影响面）"
argument-hint: "[需求说明或变更描述]"
disable-model-invocation: false
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/code-implement/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
