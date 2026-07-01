---
description: "🎨 场景画布——打开可视化拖拽编辑器（React Flow）"
argument-hint: "[无参数]"
disable-model-invocation: false
allowed-tools: Read, Bash
---

# /easywork:canvas

打开 EasyWork 场景可视化画布 — 基于 React Flow（SVG 渲染，30k+ Stars）的拖拽式技能编排工具。

## 操作

1. 检查 `tools/scenario-canvas/package.json` 是否存在
2. 检查 `tools/scenario-canvas/node_modules/` 是否存在：
   - 不存在 → 执行 `cd tools/scenario-canvas && npm install`
3. 告知用户画布将在浏览器中打开
4. 执行：`cd tools/scenario-canvas && npm run dev`

## 画布功能
- 从左侧面板**拖拽技能**到画布（或双击添加）
- **连线**：从输出端口拖到输入端口建立数据流（smoothstep 动画连线）
- **保存**：Ctrl+S → 导出为 YAML 格式
- **加载**：Ctrl+O → 从 YAML 加载已有场景
- **校验**：检查循环依赖、断开节点、缺失输入
- **小地图**：右下角 Minimap 快速导航
- **缩放**：滚轮缩放，中键拖拽平移

保存的场景可通过 `/easywork:scenario run <id>` 执行。

## 当前工作上下文
- 分支：!`git branch --show-current`
