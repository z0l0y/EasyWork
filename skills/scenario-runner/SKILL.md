---
name: scenario-runner
description: >
  场景执行引擎。加载 scenarios/library/ 或 scenarios/user/ 下的场景 YAML 定义，
  按 DAG 拓扑顺序执行技能节点，支持并行执行、HITL 交互暂停、产出验证。
  场景 = 真实上下文(situation) + 执行图(nodes + edges) → 目标驱动的技能编排。
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
model: sonnet
version: 3.0
capability:
  id: scenario-runner
  display_name: 场景执行器
  emoji: "▶️"
  category: orchestration
  tier: 2
  inputs:
    - { name: scenario_id, type: string, required: true, description: "场景 ID（library/ 或 user/ 下的 YAML 文件名，不含扩展名）" }
    - { name: action, type: enum, required: false, description: "list|view|run|edit|delete" }
  outputs:
    - { name: execution_trace, type: markdown, description: "场景执行追踪报告" }
    - { name: outcome_verification, type: markdown, description: "产出 vs 预期目标对比" }
  triggers:
    - "场景执行"
    - "执行场景"
    - "运行场景"
    - "scenario run"
    - "run scenario"
    - "/easywork:scenario"
  related_skills:
    - { skill: scenario-builder, relationship: inbound, desc: "Builder 创建的场景由 Runner 执行" }
    - { skill: fullchain-dev-workflow, relationship: outbound, desc: "场景可嵌入 Pipeline 线模式执行" }
    - { skill: all, relationship: outbound, desc: "场景中包含的所有技能节点依次执行" }
  suggested_when:
    - "用户想运行一个预置场景（如 接手遗留项目 / 线上故障定位）"
    - "用户在 Canvas 中创建了自定义场景并保存为 YAML"
    - "用户想复用之前设计的技能组合流程"
  pipeline_placement:
    good_after: ["scenario-builder"]
    good_before: ["sum-session", "knowledge-base"]
  autonomous:
    callable_by_other: true
    requires_confirmation: true
    max_depth: 1
  risk_level: "L1"
---

# ▶️ Scenario Runner（场景执行引擎）

> v3.0 · 加载场景 YAML → 展示上下文 → 拓扑排序 → 按 DAG 执行 → 验证产出

## 0. 核心定位

Scenario Runner 和 Pipeline Composer 互补：
- **Pipeline**：7 条固定流水线 + 自然语言动态解析 → 适合一次性或不确定的情况
- **Scenario**：用户创建的可持久化场景 → 适合重复性任务、团队共享、画布可视化编排

## 1. 场景加载

### 1.1 确定场景来源

```
用户输入 $ARGUMENTS
  ├── "list" / "列表" → 列出所有可执行场景（Step 0）
  ├── "view <id>" / "查看 <id>" → 显示场景 DAG + 上下文（不执行）
  ├── "run <id>" / "执行 <id>" → 完整执行
  ├── "edit <id>" / "编辑 <id>" → 加载YAML → 用户编辑
  └── "delete <id>" / "删除 <id>" → 确认 → 删除 YAML → 更新 _index.md
```

### 1.2 查找场景文件

搜索顺序：
1. `scenarios/user/<id>.yaml`（用户自定义优先）
2. `scenarios/library/<id>.yaml`（内置库）
3. 如都不存在 → 列出可用场景 + 提示

### 1.3 解析 YAML

读 YAML → 提取：
- `scenario.situation`：场景上下文（背景/角色/触发/期望产出）
- `scenario.canvas.nodes[]`：节点列表（skill / phase / depends_on / config / interaction_point）
- `scenario.canvas.edges[]`：边列表（from → to）
- `scenario.canvas.strategy`：执行策略（quality-first / efficiency-first / simplicity-first）

## 2. 场景上下文展示（锚定目标）

执行前**必须**向用户展示场景上下文，将技能编排锚定到真实目标：

```markdown
## 🎯 场景：{scenario.name} {scenario.emoji}

**背景**：{scenario.situation.background}
**角色**：{scenario.situation.persona}
**期望产出**：{scenario.situation.desired_outcome}

**执行计划**：
{按阶段分组的节点列表}

策略：{strategy} | 节点数：{N} | 预计时间：{estimated_time}

→ 开始执行？(yes/no/调整)
```

## 3. DAG 拓扑排序

### 3.1 算法

```
function topological_sort(nodes, edges):
  in_degree = {node.id: 0 for node in nodes}
  for edge in edges:
    in_degree[edge.to] += 1

  queue = [node for node in nodes if in_degree[node.id] == 0]
  result = []

  while queue not empty:
    level = []  # nodes at same topological level (can run in parallel)
    for each node in queue:
      level.append(node)
      for each edge where edge.from == node.id:
        in_degree[edge.to] -= 1
        if in_degree[edge.to] == 0:
          next_queue.append(edge.to)
    result.append(level)
    queue = next_queue

  if total_nodes(result) != len(nodes):
    ERROR: "场景存在循环依赖，无法执行"

  return result  # [[level1_nodes], [level2_nodes], ...]
```

### 3.2 并行策略

| 策略 | 同层节点 |
|------|---------|
| quality-first | 串行执行（按 skill 排序），确保每步可审查 |
| efficiency-first | 并行执行（最多 5 个），加速 |
| simplicity-first | 串行，跳过验证 |

## 4. 节点执行

### 4.1 单节点执行

对每个节点：
```
1. 打印执行头部
   ┌─────────────────────────────────────┐
   │ ▶️ [{phase}] {emoji} {label}         │
   │   技能: {skill} · 阶段 {N}/{total}   │
   └─────────────────────────────────────┘

2. 注入场景上下文
   → 传递给技能：场景背景、角色、期望产出、上游产出

3. 检查交互暂停点 (interaction_point)
   ├── 有 prompt → 暂停 → 向用户显示 prompt → 等待输入 → 注入到技能
   └── 无 → 直接执行

4. 执行技能
   → Read skills/{skill}/SKILL.md → 按其中定义的流程执行
   → 传入：config + 上游数据 + interaction_input (如有)

5. 收集产出
   → 保存节点的关键产出（用于传递给下游节点 + 最终验证）
```

### 4.2 数据传递协议

上游节点的产出通过"上下文传递块"传给下游：

```markdown
## 📤 上游产出（来自 {from_node_label}）
- **{output_name}**: {摘要或文件路径}
---
## 📥 输入要求（当前节点）
- 需要的输入：{list inputs from skill capability}
```

### 4.3 交互暂停点

YAML 中定义的 `interaction_point` 在节点执行前触发：

```
⏸️  执行暂停 — {node.label} 需要确认

{prompt}

请输入你的选择/回答：
> _

→ 收到输入后继续执行该节点
```

## 5. 执行追踪

实时显示执行进度：

```
【{scenario.emoji} 场景执行中 — {scenario.name}】

📐 n1: 理解项目架构 ........ ✅ 完成 (3.2s, 450行报告)
🔬 n2: 追踪核心调用链 ..... 🔄 执行中 (追踪 ProcessRefund...)
🧪 n3: 检查测试覆盖 ....... ⏳ 等待 n2 完成
📊 n4: 画架构图 ........... ⏳ 等待 n1,n2 完成
📋 n5: 生成综合报告 ....... ⏸️  等待上游

阶段: 2/4 | 进度: ████░░░░░░ 40% | 策略: quality-first
```

## 6. 产物验证

所有节点执行完成后，对照 `scenario.situation.desired_outcome` 验证：

```markdown
## ✅ 场景产物验证

| 期望产出 | 达成状态 | 证据 |
|---------|---------|------|
| {outcome_1} | ✅ 达成 | {文件/内容引用} |
| {outcome_2} | ⚠️ 部分 | {说明缺失的部分} |

### 场景执行摘要
- 开始时间：{start_time}
- 结束时间：{end_time}
- 总耗时：{duration}
- 执行节点：{N}/{total} 成功
- 跳过的 HITL 点：{M}
```

## 7. 场景操作（非执行）

### 7.1 list — 列出所有场景

```
Read scenarios/_index.md → 展示场景目录表
```

### 7.2 view — 显示场景详情

```
读 YAML → 生成 Mermaid DAG → 展示上下文 + 节点列表 + 连线 → 不执行
```

### 7.3 edit — 编辑场景

```
读 YAML → 展示当前内容 → 用户说明修改内容 → 更新文件
提示："或使用 /easywork:canvas 在可视化画布中编辑"
```

### 7.4 delete — 删除场景

```
确认 → 删除 scenarios/user/<id>.yaml → 更新 _index.md
内置库场景不可删除（提示"内置场景不可删除，如需定制请复制到 user/"）
```

---

## 8. 错误处理

| 情况 | 处理 |
|------|------|
| 场景文件不存在 | 列出可用场景 + 建议可用 ID |
| YAML 解析失败 | 报告错误行 + 建议在 Canvas 中重新编辑 |
| 循环依赖 | 报告环中节点列表 + 拒绝执行 |
| 节点 skill 不存在 | 报告坏节点 + 可跳过继续(?) |
| 节点执行失败 | 记录失败原因 → 询问：跳过/重试/中止 |
| 交互暂停超时(5min) | 使用默认值或跳过该暂停点 |

## 9. 反模式

- ❌ 把场景当作一次性脚本——场景的价值在于可复用、可共享
- ❌ 跳过上下文展示——没有场景锚定就失去了"目标驱动"
- ❌ 交互暂停点设计过多——每个场景最多 3 个交互点（规则：每 4 个节点最多 1 个交互点）
- ❌ 忽略产出验证——执行完不等于达成目标
