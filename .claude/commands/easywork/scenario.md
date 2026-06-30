---
description: "🎨 场景画板——list/view/run/create/edit/delete 场景工作流"
argument-hint: "[子命令: list|view|run|create|edit|delete] [场景ID]"
disable-model-invocation: false
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

加载并执行场景画板相关技能。

用户请求：$ARGUMENTS

## 子命令路由

根据用户输入自动路由：
- `list` / `列表` / 无参数 → Read `skills/scenario-runner/SKILL.md`，执行 list 流程
- `view <id>` / `查看 <id>` → Read `skills/scenario-runner/SKILL.md`，执行 view 流程
- `run <id>` / `执行 <id>` → Read `skills/scenario-runner/SKILL.md`，执行 run 流程
- `create` / `创建` / `新建` → Read `skills/scenario-builder/SKILL.md`，启动对话式构建
- `edit <id>` / `编辑 <id>` → Read `skills/scenario-runner/SKILL.md`，执行 edit 流程
- `delete <id>` / `删除 <id>` → Read `skills/scenario-runner/SKILL.md`，执行 delete 流程

场景文件位于：`scenarios/library/`（内置）和 `scenarios/user/`（自定义）

## 当前工作上下文
- 分支：!`git branch --show-current`
- 最近提交：!`git log --oneline -5`
- 工作区状态：!`git status --short`
- 可用场景：!`ls scenarios/library/*.yaml scenarios/user/*.yaml 2>/dev/null | wc -l` 个
