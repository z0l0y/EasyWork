---
name: figma-engine
description: >
  Figma/FigJam 图表引擎适配器。通过 Figma 官方 MCP Server 实现双向交互——Claude 可直接在 FigJam
  画布上创建和编辑图表（架构图、流程图、序列图、甘特图等）。输出为可编辑的 FigJam board。
engine_name: Figma/FigJam
priority: 0
requires_mcp: true
mcp_package: figma@claude-plugins-official (官方远程) 或 figma-ui-mcp (本地)
output_formats: [FigJam Board URL, 可编辑原生 Figma 图层]
version: 1.0
---

# 🎯 Figma/FigJam 引擎适配器

> 最高优先级 · 专业级 · 团队协作 · 双向交互

## 0. 为什么 FigJam 是最高优先级

| 优势 | 说明 |
|------|------|
| 🏢 团队协作 | 多人实时编辑同一 FigJam board |
| 🎨 专业外观 | 设计工具级别的视觉效果 |
| 🔄 双向交互 | Claude 可读取 Figma 设计 → 生成代码；也可将代码 → 推入 Figma |
| 📋 图表类型全 | 支持用户旅程图、甘特图、序列图、状态图、决策树 |
| 🤖 AI 原生 | Claude 可直接在 FigJam 中生成图表（2025 年新功能） |

---

## 1. MCP 配置

### 1.1 安装 Figma 官方 MCP

```bash
# Claude Code 中安装官方插件
claude plugin install figma@claude-plugins-official

# 或手动配置 Figma Desktop MCP
# 详见 https://help.figma.com/hc/en-us/articles/39888612464151
```

### 1.2 添加 MCP 配置

将 `.easywork/mcp-templates/figma-mcp.json` 内容合并到项目 `.mcp.json` 中。

核心配置（官方远程 MCP）：
```json
{
  "mcpServers": {
    "figma": {
      "type": "remote",
      "url": "https://mcp.figma.com/mcp"
    }
  }
}
```

或使用本地 MCP（无需 API Key）：
```json
{
  "mcpServers": {
    "figma-ui": {
      "command": "npx",
      "args": ["-y", "figma-ui-mcp"]
    }
  }
}
```

### 1.3 认证

首次使用需授权：
1. Claude Code 中运行 Figma 相关操作
2. 弹出 Figma 授权页面
3. 点击"Allow access"
4. 之后无需重复认证

---

## 2. FigJam 图表类型

Claude + FigJam 原生支持以下图表类型：

| 图表类型 | 输入来源 | 效果 |
|---------|---------|------|
| 🗺️ 用户旅程图 | 文字描述 / PRD | FigJam 原生旅程图模板 |
| 📅 甘特图 | PRD / 时间线描述 | 自动生成可编辑甘特图 |
| 🔗 序列图 | 系统描述 / 代码 | 服务间调用时序 |
| 🔄 状态图 | 状态描述 | 状态转换可视化 |
| 🌳 决策树 | 决策逻辑描述 | 交互式决策树 |
| 🏗️ 系统架构图 | 架构描述 | 服务+数据库+依赖关系 |
| 🧠 思维导图 | 主题描述 | 层级展开思维导图 |

---

## 3. 生成方法

### 3.1 标准工作流

```
1. 确认 Figma MCP 已连接
2. 用自然语言描述需要的图表
3. Agent 调用 Figma MCP 在 FigJam 中创建图表
4. 返回 FigJam Board URL（可分享）
5. 用户可在 FigJam 中手动编辑调整
```

### 3.2 提示词示例

```
用户：帮我用 Figma 画一个微服务架构图
Agent：
  [检查 Figma MCP 连接 ✅]
  正在 FigJam 中创建图表...
  
  图表包含：
  - API Gateway（入口层）
  - User Service / Order Service / Payment Service（服务层）
  - MySQL / Redis / Kafka（数据层）
  - 箭头表示调用关系
  
  ✅ 已创建 FigJam Board：https://www.figma.com/board/xxx
  你可以在 FigJam 中编辑或分享此图表。
```

---

## 4. 注意事项

- **需要 Figma 账号**：免费账号即可使用 FigJam
- **首次需授权**：OAuth 流程，1 分钟完成
- **网络要求**：需要访问 Figma API（api.figma.com）
- **图表可编辑**：生成后可在 FigJam 中手动调整，所有修改实时同步
- **协作**：分享 FigJam URL 即可邀请团队成员协作编辑

---

## 5. 版本历史

- v1.0 (2026-07-01)：初始版本。基于 Figma 官方 MCP，支持 7 种 FigJam 图表类型
