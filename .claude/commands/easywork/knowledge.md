---
description: "📚 知识库管理——沉淀/检索/维护/交接，跨上下文复用知识"
argument-hint: "[操作：查/存/整理/交接 或 自然语言描述]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/knowledge-base/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
