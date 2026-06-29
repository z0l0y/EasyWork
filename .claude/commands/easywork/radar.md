---
description: "🛰️ 技术雷达——技术动态扫描（点/面/体三级粒度）"
argument-hint: "[技术领域名 / 深扫 / 全面深扫]"
disable-model-invocation: false
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行 `skills/tech-radar/SKILL.md` 中定义的完整流程。

用户请求：$ARGUMENTS

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
