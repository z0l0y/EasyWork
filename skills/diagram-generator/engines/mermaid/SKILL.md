---
name: mermaid-engine
description: >
  Mermaid 图表引擎适配器（兜底引擎）。当无任何 MCP 引擎可用时自动启用。
  复用 graph-fullchain 技能的完整能力。零依赖，GitHub 原生渲染。
engine_name: Mermaid
priority: 4
requires_mcp: false
output_formats: [Markdown, HTML]
version: 1.0
---

# 📊 Mermaid 引擎适配器（兜底）

> 零依赖 · GitHub 原生渲染 · 复用 graph-fullchain

## 0. 定位

Mermaid 是引擎链的**最后一级兜底**。当没有任何 MCP 引擎（Figma/Excalidraw/Draw.io）且没有 D2 CLI 时，自动降级到 Mermaid。

Mermaid 引擎**不重复实现** graph-fullchain 的逻辑，而是**直接路由到 graph-fullchain 技能**。

---

## 1. 使用方式

### 自动路由

当 diagram-generator 检测到无可用高级引擎时：

```
Agent:
  ⚠️ 未检测到 Figma/Excalidraw/D2/Draw.io 引擎，降级到 Mermaid。
  如需更专业的图表，可以：
  1. 安装 Excalidraw MCP：npx -y @fromsko/excalidraw-mcp-server
  2. 安装 D2 CLI：https://d2lang.com
  3. 配置 Figma MCP：https://help.figma.com/hc/en-us/articles/39888612464151
  
  是否继续用 Mermaid 生成？（输入 yes 或指定其他引擎）
```

### 手动指定

```
用户：用 Mermaid 画个简单的流程图就行
Agent：[Read] skills/graph-fullchain/SKILL.md → 按流程生成 Mermaid 图表
```

---

## 2. 图表类型支持（Mermaid 原生支持）

| 图表类型 | Mermaid 语法 | 效果 |
|---------|-------------|------|
| 🏗️ 架构图 | `graph TD` + `subgraph` | ⭐⭐⭐ |
| 🔀 流程图 | `flowchart TD/LR` | ⭐⭐⭐⭐ |
| 🔗 序列图 | `sequenceDiagram` | ⭐⭐⭐⭐ |
| 📊 ER 图 | `erDiagram` | ⭐⭐⭐ |
| 🔄 状态图 | `stateDiagram-v2` | ⭐⭐⭐⭐ |
| 🧠 思维导图 | `mindmap` | ⭐⭐⭐ |
| 📅 甘特图 | `gantt` | ⭐⭐⭐ |

---

## 3. 路由指令

当需要 Mermaid 引擎时，Agent 应执行：

```
1. [Read] skills/graph-fullchain/SKILL.md
2. 按照 graph-fullchain 的流程生成 Mermaid 图表
3. 在输出中标注：⚠️ 此图表由 Mermaid 引擎生成。安装 Excalidraw/D2/Figma 可获得更专业的效果。
```

---

## 4. 升级建议

在 Mermaid 图表下方自动附加升级提示：

```markdown
---
> 💡 **想要更专业的图表？**
> - [Excalidraw](engines/excalidraw/SKILL.md) — 手绘风格，实时预览，免费
> - [Figma](engines/figma/SKILL.md) — 团队协作，专业汇报
> - [D2](engines/d2/SKILL.md) — 最美架构图，命令行生成
> - [Draw.io](engines/drawio/SKILL.md) — 多格式导出
```

---

## 5. 版本历史

- v1.0 (2026-07-01)：初始版本。作为引擎链 P4 兜底，路由到 graph-fullchain
