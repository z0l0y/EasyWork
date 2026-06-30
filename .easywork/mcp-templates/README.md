# MCP 配置模板

> 一键配置图表 MCP Server。选择你需要的引擎，将模板内容合并到项目根目录的 `.mcp.json` 中。

## 推荐方案

| 引擎 | 模板文件 | 安装难度 | 输出质量 | 推荐场景 |
|------|---------|---------|---------|---------|
| ✏️ **Excalidraw** | `excalidraw-mcp.json` | ⭐ 低 | ⭐⭐⭐⭐ | 架构草图、技术讨论（推荐首选） |
| 🎯 **Figma** | `figma-mcp.json` | ⭐⭐ 中 | ⭐⭐⭐⭐⭐ | 团队协作、正式汇报 |
| 📐 **Draw.io** | `drawio-mcp.json` | ⭐ 低 | ⭐⭐⭐⭐ | 多格式导出、企业环境 |

## 使用步骤

### 1. 选择引擎

按推荐顺序：Excalidraw（免费首选）→ Figma（有账号时）→ Draw.io

### 2. 安装引擎

按模板文件顶部的 `_setup` 说明安装对应引擎。

### 3. 合并配置

打开项目的 `.mcp.json`，将模板中的 `mcpServers` 条目合并进去。

例如，添加 Excalidraw 后：

```json
{
  "mcpServers": {
    "easywork-knowledge": {
      "command": "python",
      "args": ["skills/knowledge-base/mcp-server/server.py", "--knowledge-dir", "knowledge"],
      "env": { "EASYWORK_KNOWLEDGE_DIR": "knowledge" }
    },
    "excalidraw": {
      "command": "node",
      "args": ["/path/to/mcp_excalidraw/dist/index.js"],
      "env": {
        "EXPRESS_SERVER_URL": "http://127.0.0.1:3000",
        "ENABLE_CANVAS_SYNC": "true"
      }
    }
  }
}
```

### 4. 验证

在 Claude Code 中说"帮我画个架构图"——系统会自动检测可用引擎并选择最优方案。

## 无 MCP 引擎

如果不想安装任何 MCP Server，还可以使用 **D2 CLI**（纯命令行，不需要 MCP）：

```bash
# macOS
brew install d2

# Linux
curl -fsSL https://d2lang.com/install.sh | sh -s -
```

D2 不需要 MCP 配置，diagram-generator 会自动检测 `d2` 命令是否可用。
