---
name: diagram-generator
description: >
  多引擎图表生成器。支持 Figma/FigJam（专业团队协作）、Excalidraw（手绘风格/实时预览）、
  D2（最美架构图）、Draw.io（多格式导出）、Mermaid（零依赖兜底）。
  自动检测可用引擎，按优先级选择最优方案。覆盖架构图/流程图/序列图/ER图/C4模型/状态图/
  思维导图/甘特图 8 种图表类型。
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
model: sonnet
version: 1.0
capability:
  id: diagram-generator
  display_name: 图表生成
  emoji: "🎨"
  category: development
  tier: 2
  inputs:
    - { name: diagram_type, type: enum, required: false, description: "图表类型：architecture|flowchart|sequence|er|state|mindmap|gantt|c4" }
    - { name: description, type: text, required: true, description: "图表内容描述（自然语言）" }
    - { name: engine, type: enum, required: false, description: "强制指定引擎：figma|excalidraw|d2|drawio|mermaid|auto" }
  outputs:
    - { name: diagram_output, type: mixed, description: "图表 URL / 文件路径 / 嵌入代码" }
  triggers: ["帮我画架构图","画系统架构","画个流程图","画流程","画序列图","画调用链",
             "画ER图","画数据模型","画思维导图","画状态图","画甘特图",
             "可视化这个","生成拓扑图","generate diagram","导出到Figma",
             "手绘风格","用Excalidraw","用D2画","/easywork:diagram"]
  related_skills:
    - { skill: graph-fullchain, relationship: extends, desc: "diagram-generator 是 graph-fullchain 的升级版，支持多引擎，Mermaid 引擎兜底" }
    - { skill: learn-from-zero, relationship: upstream, desc: "learn-from-zero 生成的图解可交由此技能渲染为专业图表" }
    - { skill: article-write, relationship: downstream, desc: "生成的图表可嵌入 article-write 产出的文档" }
  suggested_when:
    - "需要画架构图、流程图、序列图等任何图表"
    - "对 Mermaid 默认样式不满意，想要更专业的效果"
    - "需要团队协作编辑图表（Figma/FigJam）"
    - "需要将图表嵌入正式文档或对外展示"
  pipeline_placement:
    good_after: ["read-project","trace-code","learn-from-zero","code-review"]
    good_before: ["article-write","sum-session","self-check"]
  autonomous:
    callable_by_other: true
    requires_confirmation: false
    max_depth: 1
  risk_level: L0
---

# 🎨 Diagram Generator（多引擎图表生成器）

> 引擎链 · v1.0 · 自动选择最优图表引擎，生成专业级可视化

## 0. 定位

diagram-generator 是 EasyWork 的**图表输出层**。它不替代 graph-fullchain（后者专注 Mermaid 的代码→图映射），
而是为所有需要"画图"的场景提供一个**统一的、自动选择最优引擎的入口**。

```
你说"帮我画架构图"
  → diagram-generator 检测可用引擎
  → Figma MCP 已配置? → ✅ FigJam（最专业）
  → 否，Excalidraw MCP? → ✅ Excalidraw（最灵活，推荐）
  → 否，D2 CLI 可用? → ✅ D2（最美架构图）
  → 否，Draw.io MCP? → ✅ Draw.io
  → 全否 → Mermaid（兜底，现有 graph-fullchain）
```

---

## 1. 引擎链

### 1.1 优先级

| 优先级 | 引擎 | 类型 | 输出格式 | 适用场景 |
|--------|------|------|---------|---------|
| P0 | **Figma/FigJam** | MCP | FigJam board (可编辑) | 团队协作、正式汇报、设计师参与 |
| P1 | **Excalidraw** | MCP | SVG/PNG/URL | 架构草图、技术讨论、快速迭代 |
| P2 | **D2** | CLI | SVG/PNG/PDF | 正式架构文档、对外发布 |
| P3 | **Draw.io** | MCP | XML/PNG/SVG | 多格式导出、企业环境 |
| P4 | **Mermaid** | 内置 | Markdown/HTML | 快速文档、GitHub 原生渲染 |

### 1.2 自动检测流程

```
Step 1: 检查 .mcp.json 是否有 figma → 有则 P0
Step 2: 检查 .mcp.json 是否有 excalidraw → 有则 P1
Step 3: 检查 `which d2` 或 `d2 --version` → 有则 P2
Step 4: 检查 .mcp.json 是否有 drawio → 有则 P3
Step 5: 兜底 → P4 (Mermaid)
```

用户可通过参数强制指定引擎：
- "用 Figma 画" / "导出到 Figma" → 强制 P0
- "手绘风格" / "用 Excalidraw" → 强制 P1
- "用 D2 画" → 强制 P2

### 1.3 引擎适配器

每个引擎的具体用法见独立适配器文件：

| 引擎 | 适配器 |
|------|--------|
| Figma/FigJam | [engines/figma/SKILL.md](engines/figma/SKILL.md) |
| Excalidraw | [engines/excalidraw/SKILL.md](engines/excalidraw/SKILL.md) |
| D2 | [engines/d2/SKILL.md](engines/d2/SKILL.md) |
| Draw.io | [engines/drawio/SKILL.md](engines/drawio/SKILL.md) |
| Mermaid | [engines/mermaid/SKILL.md](engines/mermaid/SKILL.md) |

---

## 2. 图表类型 → 最优引擎映射

不同引擎对不同图表类型的支持度不同。以下是推荐映射：

| 图表类型 | 最佳引擎 | 次选 | 说明 |
|---------|---------|------|------|
| 🏗️ 系统架构图 | D2 / Figma | Excalidraw | D2 的 TALA 布局专为架构图优化 |
| 🔀 流程图 | Excalidraw / Figma | Draw.io | 手绘风格流程图最直观 |
| 🔗 序列图 | D2 / Figma | Mermaid | D2 的 sequence 语法最简洁 |
| 📊 ER 图 / 数据模型 | D2 | Draw.io | D2 的 sql_table shape 原生支持 |
| 🏛️ C4 模型 | D2 / Figma | Excalidraw | D2 v0.7.0+ 支持 C4 person shape |
| 🔄 状态图 | Figma / Excalidraw | Mermaid | 状态转换可视化 |
| 🧠 思维导图 | Excalidraw / Figma | Mermaid | 手绘风格思维导图最自然 |
| 📅 甘特图 | Figma | Mermaid | FigJam 甘特图可协作编辑 |
| 🎯 部署拓扑图 | D2 | Excalidraw | D2 的 grid/stack 布局天然适合 |
| 🌐 网络拓扑图 | D2 | Draw.io | ELK 布局引擎处理复杂网络 |

---

## 3. 使用流程

### 3.1 自然语言触发（推荐）

```
用户：帮我画一下这个项目的系统架构图
Agent：
  1. 检测可用引擎 → Excalidraw MCP 可用
  2. [Read] engines/excalidraw/SKILL.md
  3. 调用 MCP 工具生成图表
  4. 返回 Excalidraw 链接 + 导出 SVG
```

### 3.2 斜杠命令

```
/easywork:diagram 架构图 微服务电商系统
/easywork:diagram 流程图 用户注册登录流程
/easywork:diagram --engine=figma 序列图 支付回调
/easywork:diagram --engine=d2 ER图 订单系统
```

### 3.3 与现有技能协作

```
graph-fullchain（Mermaid 代码→图）
  → 如果用户不满意效果
  → 调用 diagram-generator 用更好的引擎重新生成
```

---

## 4. MCP 配置

### 快速开始（推荐 Excalidraw）

```bash
# 1. 安装 Excalidraw MCP
git clone https://github.com/yctimlin/mcp_excalidraw
cd mcp_excalidraw && npm ci && npm run build

# 2. 启动画布服务（终端 1）
PORT=3000 npm run canvas

# 3. 添加 MCP 配置到 .mcp.json（见 .easywork/mcp-templates/excalidraw-mcp.json）
```

或使用一键 npx：
```bash
npx -y @fromsko/excalidraw-mcp-server
```

### 其他引擎

配置模板位于 `.easywork/mcp-templates/`：
- `excalidraw-mcp.json` — Excalidraw（推荐）
- `figma-mcp.json` — Figma/FigJam（需 Figma 账号）
- `drawio-mcp.json` — Draw.io

---

## 5. 反模式

- ❌ 用户明确说"用 Mermaid 就行"时强行用高级引擎
- ❌ 没有检查 MCP 可用性就直接调用 MCP 工具（导致报错）
- ❌ 生成图表后不提供导出选项（SVG/PNG/URL）
- ❌ 对简单流程图（3-5 个节点）使用复杂引擎——Mermaid 足够
- ❌ 不告知用户当前使用的是哪个引擎
- ❌ 引擎不可用时静默降级——必须告知用户并确认

---

## 6. 版本历史

- v1.0 (2026-07-01)：初始版本。5 引擎链（Figma/Excalidraw/D2/Draw.io/Mermaid）、8 种图表类型支持、自动检测 + 手动指定双模式
