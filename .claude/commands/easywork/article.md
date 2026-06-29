---
description: "📝 文档编写——Agent 输出→格式化 Markdown 文档（6 种模板）"
argument-hint: "[文档内容或主题]"
disable-model-invocation: false
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/article-write/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
