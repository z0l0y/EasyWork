# 🎨 Scenario Canvas — EasyWork 可视化场景编辑器

> 基于 React Flow（30k+ GitHub Stars，SVG 渲染）的拖拽式技能编排画布。

## 核心特性

- **拖拽编排**：从左侧面板拖入技能到画布，自由排列
- **连线组合**：拖拽端口建立数据流，支持 smoothstep 动画连线
- **属性编辑**：点击节点，右侧面板编辑配置、标签、交互暂停点
- **保存/加载**：导出为 EasyWork YAML 场景格式，可加载已有场景
- **DAG 校验**：检测循环依赖、断开节点、未覆盖的必填输入
- **SVG 渲染**：无模糊、无 DPR 问题，矢量级清晰度
- **内置组件**：Minimap 小地图、Controls 缩放控件、Background 网格

## 对比旧版

| 特性 | 旧版 (LiteGraph.js) | 新版 (React Flow) |
|------|-------------------|-------------------|
| 渲染引擎 | Canvas2D | **SVG** |
| 画质 | 模糊（DPR 问题） | **矢量清晰** |
| 拖拽体验 | 手动处理事件拦截 | **HTML5 Drag API 原生支持** |
| 连线样式 | 基础直线 | **Smoothstep 动画 + 箭头** |
| 节点拖拽 | 不稳定 | **丝滑** |
| 代码量 | ~1120 行单文件 | 模块化 React 组件 |
| 社区 | ~8k stars | **~30k stars** |
| 维护 | 需手动修复 | **开箱即用** |

## 使用方式

### 启动开发服务器
```bash
cd tools/scenario-canvas
npm install
npm run dev
```

### 生产构建
```bash
npm run build
# 产出在 dist/ 目录，可直接部署
```

### 快捷键
| 快捷键 | 功能 |
|--------|------|
| 鼠标拖拽 | 从面板拖入技能到画布 |
| 双击面板项 | 在画布中央添加技能 |
| 端口拖拽 | 建立连线 |
| Ctrl+S | 保存场景 (YAML) |
| Ctrl+O | 加载场景 |
| Ctrl+N | 新建空白画布 |
| Delete | 删除选中节点 |
| 滚轮 | 缩放画布 |
| 中键拖拽 | 平移画布 |

## 场景格式

保存产生的 YAML 文件位于 `scenarios/user/`，可在 EasyWork 中通过 `/easywork:scenario run <id>` 执行。

## 技术栈

- [React Flow](https://github.com/xyflow/xyflow) (~30k⭐) — SVG 节点编辑器
- [React 19](https://react.dev) — UI 框架
- [Vite](https://vitejs.dev) — 构建工具
- 原生 CSS — 无 CSS 框架依赖
