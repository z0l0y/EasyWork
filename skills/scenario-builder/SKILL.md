---
name: scenario-builder
description: >
  场景构建器。通过对话引导用户创建/编辑自定义场景工作流。
  六步构建流程：场景描述→技能推荐→画布编排→连线验证→策略选择→保存发布。
  也可使用 /easywork:canvas 在可视化画布中拖拽编排。
allowed-tools: Read, Write, Bash, Grep, Glob
model: sonnet
version: 3.0
capability:
  id: scenario-builder
  display_name: 场景构建器
  emoji: "🎨"
  category: orchestration
  tier: 2
  inputs:
    - { name: scenario_description, type: text, required: true, description: "场景描述（自然语言）" }
    - { name: existing_scenario, type: path, required: false, description: "基于现有场景编辑" }
  outputs:
    - { name: scenario_definition, type: yaml, description: "完整的场景定义 YAML 文件" }
  triggers:
    - "创建场景"
    - "新建场景"
    - "设计场景"
    - "构建场景"
    - "build scenario"
    - "scenario builder"
  related_skills:
    - { skill: scenario-runner, relationship: outbound, desc: "场景构建完成后可立即运行验证" }
  suggested_when:
    - "用户想为重复性任务创建可复用的工作流"
    - "用户描述了一个需要多个技能协作的真实场景"
  pipeline_placement:
    good_after: []
    good_before: ["scenario-runner"]
  autonomous:
    callable_by_other: false
    requires_confirmation: true
    max_depth: 0
  risk_level: "L0"
---

# 🎨 Scenario Builder（场景构建器）

> v3.0 · 对话式场景构建 · 六步引导流程

## 0. 两种构建方式

| 方式 | 入口 | 适用场景 |
|------|------|---------|
| **可视化画布** | `/easywork:canvas` → 浏览器打开 | 需要直观拖拽、查看 DAG |
| **对话式构建** | `/easywork:scenario create` | 不离开终端、快速构建 |

本 Skill 涵盖**对话式构建**。可视化画布打开 `tools/scenario-canvas/canvas.html`。

## 1. 六步构建流程

### Step 1: 场景上下文采集

引导用户描述真实场景：

```
Builder: "告诉我你的真实场景——你遇到了什么情况？你扮演什么角色？你期望得到什么结果？"

用户：{自然语言描述}
```

从用户描述中提取：
- `background`：场景背景（一句话）
- `persona`：用户角色
- `desired_outcome`：期望产出
- `trigger_examples`：用户会用什么自然语言触发这个场景

### Step 2: 技能推荐

根据场景描述，从 28 个技能中推荐相关性最高的 5-8 个：

```markdown
## 推荐技能组合

根据你的场景 "{situation_summary}"，建议以下技能：

| # | 技能 | 为什么需要 | 阶段 |
|---|------|-----------|------|
| 1 | 📐 read-project | 先理解项目结构 | understand |
| 2 | 🔬 trace-code | 再追踪核心链路 | deep-dive |
| 3 | 🧪 test-coverage | 检查测试覆盖 | verify |
| ... | ... | ... | ... |

建议执行策略：{quality-first / efficiency-first / simplicity-first}

→ 确认这些技能？还是需要增删调整？
```

### Step 3: DAG 编排

根据技能能力匹配自动生成初始 DAG：

```
算法：
1. 根据每个技能的 pipeline_placement 和 related_skills 推断顺序
2. 阶段顺序固定：understand → deep-dive → fix → verify → summarize → deliver
3. 同阶段内可并行（如 n3 和 n4 都可 summarize）
4. 数据流匹配：上游输出字段能覆盖下游输入字段的 → 建立连线
```

展示给用户：
```markdown
## DAG 编排

{自动生成的节点列表 + 连线}

→ 需要调整顺序吗？需要增加/移除节点吗？
```

### Step 4: 连线验证

对每条边进行校验：

- 上游节点的输出类型与下游节点的输入类型是否兼容？
- 下游节点的 required 输入是否都被覆盖？
- 是否有循环依赖？

如有问题报告给用户并建议修复。

### Step 5: 策略选择

```
选择执行策略：
1. quality-first    — 串行，每步审查（适合代码改动、安全审计）
2. efficiency-first — 最大并行（适合理解/学习/研究）
3. simplicity-first — 最小流程（适快速修复/简单任务）

> _
```

### Step 6: 保存发布

```
场景构建完成！

📋 场景 ID：{id}
📁 保存位置：scenarios/user/{id}.yaml

下一步：
- 运行：/easywork:scenario run {id}
- 可视化编辑：/easywork:canvas
- 分享：将此 YAML 复制到 team 的 scenarios/ 目录
```

## 2. 编辑已有场景

如果用户说 "edit <id>" 或 "修改场景"：
1. 加载 `scenarios/user/<id>.yaml`（如不存在则查 library/）
2. 展示当前状态（上下文 + 节点 + 连线）
3. 用户说明修改内容
4. 重新执行 Step 3-6

## 3. 反模式

- ❌ Builder 替用户做所有决策——用户必须确认每个步骤
- ❌ 推荐过多技能——最多推荐 10 个，实际使用 4-8 个
- ❌ 跳过上下文采集——没有场景背景就没有意义
