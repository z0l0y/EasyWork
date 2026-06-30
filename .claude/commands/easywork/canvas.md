---
description: "🎨 场景画布——打开可视化拖拽编辑器（浏览器）"
argument-hint: "[无参数]"
disable-model-invocation: false
allowed-tools: Read, Bash
---

# /easywork:canvas

打开 EasyWork 场景可视化画布——基于 LiteGraph.js（ComfyUI 同款引擎）的拖拽式技能编排工具。

## 操作

1. 检查 `tools/scenario-canvas/canvas.html` 是否存在
2. 告知用户画布将在浏览器中打开
3. 执行打开命令：
   - **Windows**: `start tools/scenario-canvas/canvas.html`
   - **macOS**: `open tools/scenario-canvas/canvas.html`
   - **Linux**: `xdg-open tools/scenario-canvas/canvas.html`

## 画布功能
- 从左侧面板**拖拽技能**到画布（或双击添加）
- **连线**：从输出端口拖到输入端口建立数据流
- **保存**：Ctrl+S → 导出为 scenarios/user/*.yaml
- **加载**：Ctrl+O → 从 YAML 加载已有场景
- **校验**：检查循环依赖、断开节点

保存的场景可通过 `/easywork:scenario run <id>` 执行。

## 当前工作上下文
- 分支：!`git branch --show-current`
