---
description: "🔬 代码追踪——函数调用链追踪（入口→路径→分支→数据流）"
argument-hint: "[入口函数名或文件路径]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/trace-code/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
