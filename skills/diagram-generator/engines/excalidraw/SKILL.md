---
name: excalidraw-engine
description: >
  Excalidraw 图表引擎适配器。通过 mcp_excalidraw（26 个 MCP 工具）实现 AI 驱动的矢量图表创建、
  实时画布同步、元素级精确控制和多格式导出。手绘风格，适合架构草图、技术讨论和快速迭代。
engine_name: Excalidraw
priority: 1
requires_mcp: true
mcp_package: mcp_excalidraw (yctimlin) 或 @fromsko/excalidraw-mcp-server
output_formats: [SVG, PNG, Excalidraw URL, JSON]
version: 1.0
---

# ✏️ Excalidraw 引擎适配器

> MCP 驱动 · 手绘风格 · 实时预览 · 26 个工具

## 0. 为什么选 Excalidraw

| 优势 | 说明 |
|------|------|
| 🆓 免费开源 | 零成本，无账号 |
| 🔧 MCP 最成熟 | mcp_excalidraw 26 个工具，1800+ GitHub stars |
| 👁️ 实时预览 | WebSocket 同步，AI 画图你能实时看到 |
| 🔄 迭代改进 | AI 调用 `describe_scene` 查看 → `update_element` 调整 |
| 📤 多格式导出 | SVG、PNG、可分享 URL |
| 🔗 Mermaid 兼容 | `create_from_mermaid` 一键迁移 |

---

## 1. MCP 配置

### 1.1 安装

```bash
# 方式 A：源码安装（推荐，功能最全）
git clone https://github.com/yctimlin/mcp_excalidraw
cd mcp_excalidraw
npm ci && npm run build

# 方式 B：npx 一键
npx -y @fromsko/excalidraw-mcp-server
```

### 1.2 启动

务必**先启动画布服务**，再启动 MCP server：

```bash
# 终端 1：画布服务（WebSocket + 前端）
PORT=3000 npm run canvas
# 画布 UI 打开在 http://localhost:3000

# 终端 2：MCP Server
EXPRESS_SERVER_URL=http://127.0.0.1:3000 node dist/index.js
```

### 1.3 添加 MCP 配置

将 `.easywork/mcp-templates/excalidraw-mcp.json` 内容合并到项目 `.mcp.json` 中。

核心配置：
```json
{
  "mcpServers": {
    "excalidraw": {
      "command": "node",
      "args": ["/absolute/path/to/mcp_excalidraw/dist/index.js"],
      "env": {
        "EXPRESS_SERVER_URL": "http://127.0.0.1:3000",
        "ENABLE_CANVAS_SYNC": "true"
      }
    }
  }
}
```

---

## 2. 核心 MCP 工具（26 个）

### 2.1 元素 CRUD（最常用）

| 工具 | 用途 | 示例 |
|------|------|------|
| `create_element` | 创建单个元素 | 画矩形、圆形、文本框 |
| `batch_create_elements` | 批量创建 | 一次性画多个节点 + 连线 |
| `get_element` | 读取元素属性 | 检查某个元素的位置/大小 |
| `update_element` | 修改元素 | 调整位置、颜色、文字 |
| `delete_element` | 删除元素 | 移除不需要的节点 |
| `query_elements` | 搜索元素 | 按类型/文字查找 |
| `duplicate_elements` | 复制元素 | 批量复制节点 |

### 2.2 布局工具

| 工具 | 用途 |
|------|------|
| `align_elements` | 对齐（左/中/右/上/中/下） |
| `distribute_elements` | 等距分布（水平/垂直） |
| `group_elements` | 编组 |
| `ungroup_elements` | 解组 |
| `lock_elements` / `unlock_elements` | 锁定/解锁 |

### 2.3 场景感知（迭代改进的关键）

| 工具 | 用途 |
|------|------|
| `describe_scene` | 描述当前画布上的所有元素（AI 的"眼睛"） |
| `get_canvas_screenshot` | 截图画布当前状态（AI 的"视觉"） |

### 2.4 导入/导出

| 工具 | 用途 |
|------|------|
| `export_to_image` | 导出为 PNG/SVG |
| `export_to_excalidraw_url` | 生成可分享链接 |
| `export_scene` / `import_scene` | 场景 JSON 导出/导入 |
| `create_from_mermaid` | 从 Mermaid 代码生成 Excalidraw 图 |
| `clear_canvas` | 清空画布 |
| `snapshot_scene` / `restore_snapshot` | 快照/恢复 |

### 2.5 参考

| 工具 | 用途 |
|------|------|
| `read_diagram_guide` | 读取图表最佳实践指南 |

---

## 3. 图表类型适配映射

| 图表类型 | Excalidraw 适配度 | 推荐元素 | 说明 |
|---------|------------------|---------|------|
| 🏗️ 系统架构图 | ⭐⭐⭐⭐ | 矩形 + 箭头 + 分组 | 用 group 表示边界上下文 |
| 🔀 流程图 | ⭐⭐⭐⭐⭐ | 菱形(判断) + 矩形(步骤) + 箭头 | 手绘风格流程图最自然 |
| 🔗 序列图 | ⭐⭐⭐ | 矩形(参与者) + 虚线箭头 | 不如 D2 专业，但够用 |
| 📊 ER 图 | ⭐⭐⭐ | 矩形(实体) + 连线(关系) | 手动标注关系类型 |
| 🔄 状态图 | ⭐⭐⭐⭐ | 圆角矩形 + 箭头 | 手绘风格状态图很清晰 |
| 🧠 思维导图 | ⭐⭐⭐⭐⭐ | 矩形 + 树形连线 | 手绘思维导图最佳 |
| 🌐 部署拓扑图 | ⭐⭐⭐⭐ | 容器(虚线框) + 矩形(节点) | stack 布局模拟 |
| 📅 甘特图 | ⭐⭐ | 矩形条 + 时间轴 | 手动绘制，不如 FigJam |

---

## 4. 生成方法

### 4.1 标准工作流

```
1. [MCP] clear_canvas  ← 清空画布
2. [MCP] batch_create_elements  ← 一次性创建所有节点和连线
3. [MCP] get_canvas_screenshot  ← 截图检查效果
4. [MCP] update_element  ← 逐个调整不满意的地方
5. [MCP] align_elements + distribute_elements  ← 自动排版
6. [MCP] export_to_excalidraw_url  ← 生成可分享链接
7. [MCP] export_to_image(format="svg")  ← 导出 SVG 文件
```

### 4.2 架构图生成示例

```json
// Step 2: batch_create_elements
{
  "elements": [
    { "type": "rectangle", "x": 100, "y": 50,  "width": 160, "height": 60, "backgroundColor": "#e3f2fd", "strokeColor": "#1976d2", "text": "API Gateway" },
    { "type": "rectangle", "x": 400, "y": 50,  "width": 160, "height": 60, "backgroundColor": "#e8f5e9", "strokeColor": "#388e3c", "text": "User Service" },
    { "type": "rectangle", "x": 400, "y": 160, "width": 160, "height": 60, "backgroundColor": "#e8f5e9", "strokeColor": "#388e3c", "text": "Order Service" },
    { "type": "rectangle", "x": 400, "y": 270, "width": 160, "height": 60, "backgroundColor": "#fff3e0", "strokeColor": "#f57c00", "text": "Payment Service" },
    { "type": "rectangle", "x": 700, "y": 50,  "width": 140, "height": 60, "backgroundColor": "#fce4ec", "strokeColor": "#c62828", "text": "MySQL" },
    { "type": "rectangle", "x": 700, "y": 160, "width": 140, "height": 60, "backgroundColor": "#fce4ec", "strokeColor": "#c62828", "text": "Redis" },
    { "type": "arrow", "x": 260, "y": 80,  "width": 140, "height": 0,  "text": "route" },
    { "type": "arrow", "x": 560, "y": 110, "width": 140, "height": 0 },
    { "type": "arrow", "x": 560, "y": 190, "width": 140, "height": 0,  "text": "write" },
    { "type": "arrow", "x": 560, "y": 80,  "width": 140, "height": 0,  "text": "read" }
  ]
}
```

### 4.3 流程图生成示例

```json
{
  "elements": [
    { "type": "ellipse", "x": 300, "y": 20,  "width": 120, "height": 50, "text": "Start", "backgroundColor": "#e8f5e9" },
    { "type": "rectangle", "x": 300, "y": 100, "width": 120, "height": 50, "text": "验证输入" },
    { "type": "diamond",  "x": 280, "y": 190, "width": 160, "height": 80, "text": "有效?" },
    { "type": "rectangle", "x": 450, "y": 190, "width": 120, "height": 50, "text": "处理请求", "backgroundColor": "#e3f2fd" },
    { "type": "rectangle", "x": 150, "y": 190, "width": 120, "height": 50, "text": "返回错误", "backgroundColor": "#ffebee" },
    { "type": "ellipse", "x": 450, "y": 300, "width": 120, "height": 50, "text": "End", "backgroundColor": "#fce4ec" }
  ]
}
```

---

## 5. 从 Mermaid 迁移

如果已有 Mermaid 图表（如 graph-fullchain 产出），可一键迁移：

```
[MCP] create_from_mermaid(code="graph TD\n  A-->B\n  B-->C")
```

Excalidraw 会自动解析 Mermaid 并生成对应的手绘风格元素。

---

## 6. 注意事项

- **画布服务必须先启动**：否则 MCP 工具调用会失败，必须先 `PORT=3000 npm run canvas`
- **坐标计算**：x 从左到右增大，y 从上到下增大。节点间距建议 60-80px
- **颜色语义**：蓝色（服务）、绿色（数据/缓存）、红色（数据库/外部依赖）、橙色（第三方服务）
- **连线方向**：`arrow` 元素默认从左到右。需要垂直或斜向连线时调整坐标
- **文本限制**：Excalidraw 文本框不支持 Markdown，纯文本为主

---

## 7. 版本历史

- v1.0 (2026-07-01)：初始版本。基于 mcp_excalidraw v2.0，26 个 MCP 工具全适配
