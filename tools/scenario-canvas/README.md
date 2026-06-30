# 🎨 Scenario Canvas — EasyWork 可视化场景编辑器

> 基于 LiteGraph.js（ComfyUI 同款引擎）的拖拽式技能编排画布。

## 核心特性

- **拖拽编排**：从左侧面板拖入技能到画布，自由排列
- **连线组合**：拖拽输出端口到输入端口，建立数据流
- **属性编辑**：点击节点，右侧面板编辑配置、标签、交互暂停点
- **保存/加载**：导出为 EasyWork YAML 场景格式，可加载已有场景
- **DAG 校验**：检测循环依赖、断开节点、未覆盖的必填输入
- **零安装**：单个 HTML 文件，全部依赖通过 CDN 加载

## 使用方式

### 从 Claude Code 启动
```
/easywork:canvas
```

### 手动打开
```bash
open tools/scenario-canvas/canvas.html
```

### 快捷键
| 快捷键 | 功能 |
|--------|------|
| 鼠标拖拽 | 从面板拖入技能到画布 |
| 双击面板项 | 在画布中央添加技能 |
| 输出→输入端口拖拽 | 建立连线 |
| Ctrl+S | 保存场景 |
| Ctrl+O | 加载场景 |
| Ctrl+N | 新建空白画布 |
| Delete | 删除选中节点 |
| 右键画布 | 搜索/添加节点 |

## 场景格式

保存产生的 YAML 文件位于 `scenarios/user/`，可在 EasyWork 中通过 `/easywork:scenario run <id>` 执行。

## 技术栈

- [LiteGraph.js](https://github.com/Comfy-Org/litegraph.js) — Canvas2D 节点编辑器
- 原生 JavaScript — 无 React/Vue/构建工具
- 全部依赖通过 CDN 加载
