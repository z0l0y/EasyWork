# Mermaid 图类型选择指南

> 用于 graph-fullchain 技能 · 根据内容自动选择最佳图类型

## 选择决策树

```
需要展示什么？
├── 步骤/流程顺序 → flowchart TD / flowchart LR
├── 组件间消息交互 → sequenceDiagram
├── 状态变化/生命周期 → stateDiagram-v2
├── 层级/依赖关系 → mindmap / graph TD
├── 时间线/里程碑 → gantt / timeline
├── 数据结构/ER 关系 → erDiagram
├── 类/接口关系 → classDiagram
└── 数值对比/趋势 → pie / xychart-beta
```

## 场景映射速查

| 内容类型 | 推荐图 | 示例 |
|---------|--------|------|
| API 调用链 | `sequenceDiagram` | 前端→网关→服务A→数据库 |
| 部署架构 | `graph TD` + `subgraph` | VPC/子网/实例关系 |
| 算法流程 | `flowchart TD` | 排序/搜索/状态机 |
| 数据模型 | `erDiagram` | 表关系/外键 |
| 发版计划 | `gantt` | Sprint 时间线 |
| 方案对比 | `graph LR` + 表格 | A vs B 架构对比 |
| 代码架构 | `classDiagram` / `graph TD` | 模块依赖/分层 |
| 知识依赖 | `mindmap` | 概念前置关系 |

## 美观规则

1. **节点数** ≤ 15（过多拆分子图或用 `subgraph` 分组）
2. **方向**：流程用 `TD`（上→下），架构用 `LR`（左→右）
3. **颜色**：关键路径用 `#f96` 标注，正常路径用 `#58a`
4. **标注**：每个箭头至少有一个标签说明"传递了什么"

## 反模式

- ❌ 用 flowchart 画 API 调用（应用 sequenceDiagram）
- ❌ 用 sequenceDiagram 画类关系（应用 classDiagram）
- ❌ 超 15 个节点不分组（信息过载，用户看不懂）
- ❌ 纯框无标注（箭头无意义）
