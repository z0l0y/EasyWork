---
description: "🎨 多引擎图表生成——Figma/Excalidraw/D2/Draw.io/Mermaid 自动选最优"
argument-hint: "[图表类型] [描述]"
disable-model-invocation: false
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
---

# /easywork:diagram

加载并执行多引擎图表生成器。

用户请求：$ARGUMENTS

## 引擎链

按优先级自动选择可用引擎：
1. Figma MCP → FigJam（需 Figma 账号）
2. Excalidraw MCP → 手绘风格（推荐）
3. D2 CLI → 最美架构图
4. Draw.io MCP → 多格式导出
5. Mermaid → 兜底

## 执行流程

1. [Read] skills/diagram-generator/SKILL.md
2. 检测可用引擎（检查 .mcp.json + which d2）
3. 按优先级选择引擎 → [Read] 对应引擎适配器
4. 生成图表 → 导出 → 返回链接/文件

## 当前工作上下文
- 分支：!`git branch --show-current`
- 可用引擎：请检查 `.mcp.json` 和 `d2 --version`
