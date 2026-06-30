---
name: d2-engine
description: >
  D2 图表引擎适配器。通过 D2 CLI 实现声明式文本→专业架构图转换。
  D2 是当下最受好评的 Diagram-as-Code 工具，专为软件架构图设计，支持 TALA 布局引擎、
  C4 模型、多格式导出。适合正式架构文档和对外发布。
engine_name: D2
priority: 2
requires_mcp: false
requires_cli: true
cli_tool: d2 (https://d2lang.com)
output_formats: [SVG, PNG, PDF]
version: 1.0
---

# 🏗️ D2 引擎适配器

> 最美架构图 · 声明式文本 · CLI 驱动 · TALA 布局

## 0. 为什么 D2 是最美架构图

| 优势 | 说明 |
|------|------|
| 🎨 TALA 布局引擎 | 专为软件架构图优化，自动对齐分层 |
| 📐 Grid/Stack 布局 | 原生支持分层架构（网关→服务→数据），Mermaid 做不到 |
| 🔧 工程化 | 支持 imports、variables、globs，大型架构图可拆分模块 |
| 👁️ Watch Mode | `d2 --watch` 存盘即刷新，开发体验极佳 |
| 📤 多格式导出 | SVG / PNG / PDF |
| 🎯 C4 模型 | v0.7.0+ 原生支持 person shape |

---

## 1. 安装检测

```bash
# 检测 D2 是否可用
which d2 && d2 --version

# 安装（如不可用）
# macOS
brew install d2

# Linux/macOS
curl -fsSL https://d2lang.com/install.sh | sh -s --

# Windows
# 下载二进制：https://github.com/terrastruct/d2/releases
```

---

## 2. 图表类型适配映射

| 图表类型 | D2 适配度 | 推荐 shape | 说明 |
|---------|----------|-----------|------|
| 🏗️ 系统架构图 | ⭐⭐⭐⭐⭐ | `layers` + `stack` | TALA 布局专为架构优化 |
| 🔀 流程图 | ⭐⭐⭐⭐ | `shape: rectangle/diamond` | connections 语法 |
| 🔗 序列图 | ⭐⭐⭐⭐⭐ | `shape: sequence_diagram` | D2 原生序列图支持 |
| 📊 ER 图 | ⭐⭐⭐⭐⭐ | `shape: sql_table` | 原生 SQL 表 shape |
| 🏛️ C4 模型 | ⭐⭐⭐⭐⭐ | `shape: person` | v0.7.0+ 支持 |
| 🔄 状态图 | ⭐⭐⭐ | `scenarios` | 不如 Mermaid 直接 |
| 🌐 部署拓扑 | ⭐⭐⭐⭐⭐ | `icon` + `grid` | ELK 布局处理复杂网络 |

---

## 3. 生成方法

### 3.1 标准工作流

```
1. 根据用户描述生成 .d2 文件
2. [Bash] d2 layout 架构图.d2 架构图.svg  ← 先用默认布局
3. 检查 SVG → 如果布局不理想 → d2 --layout=elk/tala 重试
4. [Bash] d2 --theme=200 架构图.d2 架构图.svg  ← 应用主题
5. 展示 SVG 给用户
6. 可选：导出 PNG（d2 架构图.d2 架构图.png）
```

### 3.2 架构图生成示例

```d2
# 微服务电商系统架构.d2
direction: right

layers: {
  gateway: {
    label: "入口层"
    style.fill: "#E3F2FD"
  }
  services: {
    label: "服务层"
    style.fill: "#E8F5E9"
  }
  data: {
    label: "数据层"
    style.fill: "#FFF3E0"
  }
}

gateway.api: "API Gateway" {
  shape: rectangle
  style.fill: "#BBDEFB"
}

services.user: "User Service" {
  shape: rectangle
  style.fill: "#C8E6C9"
}

services.order: "Order Service" {
  shape: rectangle
  style.fill: "#C8E6C9"
}

services.payment: "Payment Service" {
  shape: rectangle
  style.fill: "#C8E6C9"
}

data.mysql: "MySQL" {
  shape: cylinder
  style.fill: "#FFCCBC"
}

data.redis: "Redis" {
  shape: cylinder
  style.fill: "#FFCCBC"
}

# 连线
gateway.api -> services.user: "route"
gateway.api -> services.order: "route"
services.order -> services.payment: "checkout"
services.user -> data.mysql: "read/write"
services.order -> data.mysql: "read/write"
services.payment -> data.redis: "cache"
```

### 3.3 执行命令

```bash
# 生成 SVG（矢量，适合嵌入文档）
d2 --layout=tala --theme=200 --sketch=false 架构图.d2 架构图.svg

# 生成 PNG（位图，适合对外展示）
d2 --layout=tala --theme=200 --sketch=false 架构图.d2 架构图.png --pad=20
```

### 3.4 常用主题

```bash
--theme=0    # 默认（浅色）
--theme=1    # 深色
--theme=100  # 蓝色主题（适合技术文档）
--theme=200  # 绿色主题（适合架构图）
--theme=300  # 橙色主题
```

---

## 4. 注意事项

- **TALA 布局引擎**：D2 核心开源，但 TALA 布局引擎为专有（免费使用）。如需纯开源布局，用 `--layout=elk` 或 `--layout=dagre`
- **GitHub 不原生渲染 D2**：不像 Mermaid 那样在 GitHub Markdown 中直接渲染。需导出 SVG 后嵌入
- **中文支持**：D2 对中文支持良好，但建议主要标签用英文，说明用中文
- **大型图表**：>50 个节点时建议拆分为多个 .d2 文件，用 `imports` 组合

---

## 5. 版本历史

- v1.0 (2026-07-01)：初始版本。基于 D2 v0.7.x，支持 TALA/ELK/Dagre 三布局引擎
