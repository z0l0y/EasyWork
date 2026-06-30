---
name: graph-fullchain
description: >
  架构可视化。GIT 之后、SUM 之前执行。将代码结构和调用关系转成
  Mermaid 图表（流程图/时序图/架构图）。图中的每个节点必须在实际代码中有对应实体。
  人脑处理图像比文字快 10 倍——好的图表让审查者瞬间理解你在做什么。

  > 🆕 v3.3：如需更专业的图表（Figma/Excalidraw/D2/Draw.io），使用 [diagram-generator](../diagram-generator/SKILL.md) 技能。graph-fullchain 的 Mermaid 引擎作为兜底保留。
allowed-tools: Read, Search
model: haiku
version: 3.0
capability:
  id: graph-fullchain
  display_name: 可视化画图
  emoji: "📊"
  category: development
  tier: 1
  inputs:
    - { name: project_report, type: markdown, required: true, description: "项目阅读报告或架构描述" }
  outputs:
    - { name: mermaid_diagrams, type: mermaid_markdown, description: "Mermaid 图表（C4/时序图/ER图/流程图）+ 节点对照表" }
  triggers: ["画架构图", "画个图", "可视化", "mermaid", "架构图"]
  related_skills:
    - { skill: read-project, relationship: inbound, desc: "项目架构信息可直接用于画图" }
    - { skill: read-paper, relationship: inbound, desc: "论文方法可画 Mermaid 图辅助分享" }
  suggested_when:
    - "需要将架构/流程可视化"
    - "分享准备中需要配图"
  pipeline_placement:
    good_after: [read-project, read-paper, trace-code]
    good_before: [sum-session]
  autonomous:
    callable_by_other: true
    requires_confirmation: false
    max_depth: 2
  risk_level: L0
---

# Graph Fullchain（架构可视化）

## 前置判断

**必须执行**：改动涉及多个模块交互、复杂流程判断、新增模块/服务/组件。

**可以跳过**：改动 ≤ 1 个文件且逻辑简单（改常量、修拼写）、纯文档任务。

## 🆕 产物后端分流（v2.5）

GRAPH 步骤根据当前产物后端决定可视化输出方式：

| 后端 | 输出方式 |
|------|---------|
| local_html | Mermaid 代码嵌入 HTML（自包含 CDN 渲染） |
| markdown | Mermaid fenced code block 嵌入 .md 文件 |
| lark_doc | Mermaid 代码通过 Markdown 转块嵌入飞书文档；复杂架构图可选飞书画板 |

### 飞书后端特殊处理

当产物后端为 lark_doc 时：

1. **节点数 ≤ 15**：Mermaid 代码以 fenced code block 嵌入飞书文档，用户可在文档中查看或用 Mermaid Live Editor 渲染
2. **节点数 > 15 的复杂架构图**：Agent 建议用户手动将图表渲染后上传到飞书画板（飞书白板 API 的 MCP 支持尚不完善，当前采用建议而非自动创建方案）
3. **节点对照表**：一律以结构化文本嵌入文档（表格用格式化文本 + 缩进模拟）

Agent 在 GRAPH 步骤结束时提示：
> 架构图已写入飞书文档。如需在飞书画板中展示，可将 Mermaid 代码复制到 Mermaid Live Editor 渲染后截图上传画板。

### 非飞书后端

按原有方式处理——Mermaid 代码嵌入产物，带节点对照表和文字说明。

## 图表类型选择

根据本次改动的**核心动作**选择图表类型：

| 改动的核心动作 | 选这种图 | Mermaid 语法 |
|--------------|---------|-------------|
| 数据在多个处理阶段间流转、有多层判断分支 | **流程图** | `flowchart TD` |
| 前端→后端→数据库→缓存等多层调用 | **时序图** | `sequenceDiagram` |
| 新增了模块/服务，或改变了组件间的依赖关系 | **架构图** | `graph TD` + `subgraph` |

**一张图不够？画两张。**流程图+时序图的组合很常见。

## 图表规则

### 规则 1：节点必须能在代码中找到

图中的每个节点名称，必须对应本次改动代码中的真实实体（文件名/函数名/类名/API 路径）。
**禁止虚构**不存在的"理想架构"节点。图表反映实际，不是设计稿。

### 规则 2：附节点对照表

Mermaid 代码下方必须跟一个对照表：

| 图中节点 | 代码实体 | 文件位置 |
|---------|---------|---------|
| 校验Token | `validateToken()` | `src/middleware/auth.ts:42` |
| 查询用户 | `UserModel.findById()` | `src/models/user.ts:108` |

### 规则 3：控制复杂度

- 单张图 >20 个节点 → 自动拆为主图 + 子图（而非硬截断）。主图展示顶层模块关系，子图展开关键模块内部细节
- 连线交叉 >3 处 → 重排节点顺序
- 嵌套 >5 层 → 用 subgraph 归组

**主图+子图拆分示例**：
```
主图（顶层）:
flowchart TD
    A[API Gateway] --> B[Auth Service]
    B --> C[User DB]
    B --> D[Cache]

子图（Auth Service 内部）:
flowchart TD
    B1[login()] --> B2[validateToken()]
    B2 --> B3{角色检查}
    B3 -->|admin| B4[返回全部权限]
    B3 -->|user| B5[返回基础权限]
```

### 规则 4：验证渲染

Mermaid 代码写完，复制到 [Mermaid Live Editor](https://mermaid.live/) 确认能正常渲染。

**语法速查**：
```
flowchart TD
  A[矩形：操作步骤] --> B{菱形：判断}
  B -->|标签| C([圆角：开始/结束])
  B -->|标签| D[(圆柱：数据库)]

sequenceDiagram
  Alice->>Bob: 同步调用
  Bob-->>Alice: 返回
  Note over Alice,Bob: 注释
```

> **Mermaid 样式指南**：图表类型选择、节点命名规范、连线布局、复杂度控制、常见问题，见 `references/mermaid-style-guide.md`。

## 反模式

- ❌ 画的是"理想架构"而不是"实际代码结构"——图表和代码对不上，不如不画
- ❌ 节点用 A/B/C/D 命名——渲染出来没人看得懂
- ❌ 一张图塞 30+ 个节点——信息过载等于没信息
- ❌ 只画图不加文字解释——图表是辅助理解的，不能完全替代文字
- ❌ 画完不验证能不能渲染——渲染失败的 Mermaid 比没画更糟糕
