---
name: drawio-engine
description: >
  Draw.io（diagrams.net）图表引擎适配器。通过 mcp-diagram-generator 实现多格式图表生成。
  支持 Draw.io 原生 XML 格式，可在 diagrams.net 中打开编辑。适合企业环境和多格式导出需求。
engine_name: Draw.io
priority: 3
requires_mcp: true
mcp_package: mcp-diagram-generator
output_formats: [XML (Draw.io), PNG, SVG]
version: 1.0
---

# 📐 Draw.io 引擎适配器

> 多格式导出 · 企业主流 · 可编辑 XML

## 0. 定位

Draw.io 是业界最广泛使用的图表工具之一。通过 mcp-diagram-generator MCP server，可以在 Draw.io 中生成专业图表，导出为可编辑的 XML 文件（在 diagrams.net 中打开编辑）。

---

## 1. MCP 配置

### 1.1 安装

```bash
npx -y mcp-diagram-generator
```

### 1.2 添加 MCP 配置

将 `.easywork/mcp-templates/drawio-mcp.json` 内容合并到项目 `.mcp.json` 中。

核心配置：
```json
{
  "mcpServers": {
    "drawio": {
      "command": "npx",
      "args": ["-y", "mcp-diagram-generator"]
    }
  }
}
```

---

## 2. 核心 MCP 工具

### `generate_diagram`

唯一的入口工具。接受一个结构化的 `diagram_spec` JSON：

```json
{
  "format": "drawio",
  "title": "系统架构图",
  "elements": {
    "containers": [
      { "id": "c1", "label": "服务层", "type": "layer", "bounds": {"x": 50, "y": 50, "width": 600, "height": 200} }
    ],
    "nodes": [
      { "id": "n1", "label": "API Gateway", "type": "rectangle", "container": "c1", "bounds": {"x": 100, "y": 100, "width": 120, "height": 60} }
    ],
    "edges": [
      { "from": "n1", "to": "n2", "label": "route" }
    ]
  }
}
```

---

## 3. 优势与限制

| 优势 | 限制 |
|------|------|
| ✅ 导出格式多（XML/PNG/SVG） | ⚠️ MCP 生态不如 Excalidraw 成熟 |
| ✅ 可在 diagrams.net 手动编辑 | ⚠️ 无实时预览 |
| ✅ 企业主流工具 | ⚠️ 工具数少（主要是 generate_diagram） |
| ✅ 支持容器/嵌套结构 | |

---

## 4. 版本历史

- v1.0 (2026-07-01)：初始版本。基于 mcp-diagram-generator
