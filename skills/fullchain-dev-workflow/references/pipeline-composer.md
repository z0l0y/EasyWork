# Pipeline Composer — 线模式执行引擎

> 版本：v1.0 | 日期：2026-06-25 | 依赖：skill-graph-orchestration.md v1.0

## 0. 概述

Pipeline Composer 是线模式（🔗）的执行引擎。它将用户的自然语言流水线描述转化为可执行的技能 DAG，管理技能间的数据传递，追踪执行进度。

```
用户: "先理解项目架构，然后追踪支付接口的调用链，最后检查测试覆盖"

Pipeline Composer:
  解析 → 匹配技能 → 构建 DAG → 检查数据对接 → 展示 → 执行
```

---

## 1. 内置流水线

### 1.1 流水线定义格式

```yaml
pipeline:
  id: scan-to-deep-read
  name: 扫描→深读
  emoji: "🔭"
  trigger_words: ["扫技术动态并深读", "scan and deep read"]
  description: "扫描最新技术动态，筛选高价值内容后深度阅读"
  strategy: efficiency-first  # quality-first / efficiency-first / simplicity-first
  
  stages:
    - stage: 1
      skill: tech-radar
      mode: standard
      description: "扫描 AI/后端/Java/Go/Agent 五个领域的最新动态"
      output_handoff:
        - target: read-paper
          data: "用户选择的深读条目（Tier 1 #N）"
          trigger: "用户交互选择后传递"
    
    - stage: 2
      skill: read-paper
      mode: standard
      description: "对用户选中的论文进行深度阅读"
      depends_on: [1]
      input_from: "stage 1 用户选择的条目"
  
  user_interaction_points:
    - between: [1, 2]
      prompt: "请选择要深读的条目（输入编号，如 #3 或 #1,#5）"
      type: selection
```

### 1.2 7 条内置流水线

#### 🔭 扫描→深读 (`scan-to-deep-read`)

```
触发: "扫技术动态并深读" / "scan and deep read"
策略: efficiency-first
DAG:  🛰️ tech-radar ──(用户选择条目)──→ 📖 read-paper
```

#### 🏗️ 理解→追踪 (`understand-then-trace`)

```
触发: "理解项目并追踪" / "understand and trace"
策略: quality-first
DAG:  📐 read-project ──(架构+模块信息)──→ 🔬 trace-code
交互点: read-project 完成后，确认要追踪哪个接口/函数
```

#### 🧪 覆盖→补测 (`coverage-then-fix`)

```
触发: "分析覆盖率并补测试" / "coverage and fix"
策略: quality-first
DAG:  🧪 test-coverage ──(补测优先级列表)──→ 👁️ read-requirements ──(需求理解)──→ ✏️ code-implement
交互点: test-coverage 完成后，确认补测范围；code-implement 执行前需用户审批
```

#### 📖 论文→分享 (`paper-to-share`)

```
触发: "读论文并准备分享" / "paper to share"
策略: quality-first
DAG:  
  📖 read-paper ──(阅读报告)──→ 📊 graph-fullchain
  📖 read-paper ──(阅读报告)──→ 📋 sum-session ──→ 🥊 self-check
```

#### 🔍 审查→复盘 (`review-then-retro`)

```
触发: "审查并复盘" / "review and retro"
策略: quality-first
DAG:  🔍 code-review ──(审查报告)──→ 🧠 talk-retro ──→ 🥊 self-check
```

#### 🧠 复盘→拷打 (`retro-then-cto`)

```
触发: "复盘并拷打" / "retro and CTO"
策略: quality-first
DAG:  🧠 talk-retro ──(根因分析)──→ 🥊 self-check
```

#### 🏗️🔬 全理解 (`full-understand`)

```
触发: "全面理解这个项目" / "full understand"
策略: efficiency-first
DAG:
  📐 read-project ──(架构)──┬──→ 📊 graph-fullchain
                             ├──→ 🔬 trace-code
                             └──→ 🧪 test-coverage
  
  read-project 并行扇出到 graph-fullchain + trace-code
  trace-code 完成后串行到 test-coverage（携带焦点文件）
```

---

## 2. 动态流水线

### 2.1 自然语言解析

用户不使用预设触发词时，Pipeline Composer 解析自然语言：

```
输入: "先帮我理解一下这个 Go 项目的架构，然后追踪支付相关的所有接口调用链"

解析步骤:
  1. 分词 + 动作识别
     "先" → 顺序标记
     "理解架构" → 匹配 read-project（trigger: 理解项目）
     "然后" → 顺序标记  
     "追踪支付接口调用链" → 匹配 trace-code（trigger: 追踪代码 + context: 支付）
     "Go 项目" → context 注入（语言=Go）

  2. 技能匹配（从 Capability Registry 查询）
     "理解架构" → 📐 read-project [confidence: 0.95]
     "追踪调用链" → 🔬 trace-code [confidence: 0.92]

  3. 构建 DAG
     read-project ──→ trace-code

  4. 检查数据对接
     read-project 产出: project_report (10段项目阅读报告)
     trace-code 需要: entry_function, entry_file
     ✅ project_report 中的架构信息可帮助定位 entry_function
     ⚠️ trace-code 还需要用户指定具体入口函数 → 在交互点询问

  5. 确定策略
     两个技能，串行依赖 → quality-first（默认）
```

### 2.2 动态解析的关键词

| 关键词 | 含义 | 编排行为 |
|--------|------|---------|
| "先...再...然后...最后..." | 串行顺序 | 构建串行 DAG 边 |
| "同时 / 并行 / 一边...一边..." | 并行执行 | 无依赖边，parallel fan-out |
| "如果...就..." | 条件分支 | 添加条件边（condition edge） |
| "每个 / 逐一遍历" | 循环 | 对每个 item 执行同一技能 |
| "汇总 / 总结 / 合并" | 汇聚 | 多路输出汇总到一个技能 |

---

## 3. 执行引擎

### 3.1 执行模型

```
Pipeline.exec():
  for each topological level in DAG:
    parallel_execute(ready_stages)     # 同层无依赖的阶段并行执行
    for each completed stage:
      validate_output(stage)           # 检查产出是否完整
      handoff_data(stage, next_stages) # 传递数据到下游
      if user_interaction_point:
        pause_and_ask_user()
    advance_to_next_level()
  
  emit_pipeline_summary()
```

### 3.2 进度展示格式

```
【🔗 线模式 — {流水线名称}】

📐 read-project ........... ✅ 完成 (3.2s, 产出 450 行报告)
🔬 trace-code ............. 🔄 执行中 (追踪 ProcessRefund...)
🧪 test-coverage .......... ⏳ 等待 {trace-code 完成}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50% (1/2 阶段完成)
Token: 12K/50K | Time: 8s elapsed
```

### 3.3 数据传递协议

技能间通过标准化的 Context Pass 传递数据：

```json
{
  "from_stage": 1,
  "from_skill": "read-project",
  "to_stage": 2,
  "to_skill": "trace-code",
  "context": {
    "project_summary": "这是一个 Go 写的电商后端服务...",
    "architecture": {
      "entry_points": ["cmd/server/main.go"],
      "key_modules": ["handler/", "service/", "repository/"],
      "external_services": ["payment-gateway: gRPC", "redis: cache"]
    },
    "suggested_trace_targets": [
      "POST /api/order/create → handler/order.go:CreateOrder",
      "POST /api/refund → handler/refund.go:ProcessRefund"
    ]
  },
  "source_report_path": "/reports/read-project-20260625.md"
}
```

---

## 4. 三种编排策略

### 4.1 质量优先（Quality-First）

```yaml
strategy: quality-first
behavior:
  execution: serial         # 严格串行，每步验证后前进
  parallel_max: 1           # 不并行
  validation: strict        # 每步产出经 MCR 自检
  user_checkpoints: all     # 每个阶段间都可能有交互点
  timeout: 30min            # 单阶段超时
use_when:
  - 涉及代码改动
  - 涉及安全/资金
  - 重要决策需要逐阶段确认
```

### 4.2 效率优先（Efficiency-First）

```yaml
strategy: efficiency-first
behavior:
  execution: parallel_max   # 最大化并行度
  parallel_max: 5           # 最多 5 个技能并行
  validation: basic         # 仅检查产出完整，不做深度验证
  user_checkpoints: minimal # 仅在关键交互点暂停
  timeout: 15min            # 总流水线超时
use_when:
  - 纯理解/分析任务
  - 时间敏感
  - 多维度独立分析（各维度互不依赖）
```

### 4.3 简洁优先（Simplicity-First）

```yaml
strategy: simplicity-first
behavior:
  execution: serial         # 串行但无验证等待
  max_stages: 3             # 最多 3 个技能
  validation: skip          # 跳过中间验证
  user_checkpoints: none    # 无人机交互
  timeout: 5min             # 快速收敛
use_when:
  - 简单问题，只需 1-3 个技能
  - 用户明确说"快速"
  - 探索性分析，不需要精确结果
```

---

## 5. 错误处理

### 5.1 单阶段失败

```
如果某阶段的技能执行失败：
  1. 记录失败原因和上下文
  2. 判断是否可重试：
     - 可重试错误（网络超时/API 限流）→ 自动重试 1 次
     - 不可重试错误（输入不合法/技能不支持）→ 暂停并向用户报告
  3. 询问用户：跳过此阶段 / 重试 / 终止流水线
```

### 5.2 数据传递失败

```
如果上游产出无法满足下游需求：
  1. 标注缺失字段
  2. 尝试用其他方式弥补（如从原始输入重新提取）
  3. 如果无法弥补 → 暂停，向用户说明缺口并请求补充信息
```

---

## 6. 反模式

- ❌ 流水线阶段超过 5 个——超过 5 个技能的流水线容易失控，建议拆分为多个子流水线
- ❌ 循环依赖（A 需要 B 的输出，B 需要 A 的输出）——DAG 不允许环
- ❌ 数据传递用"全文复制"——只传递下游需要的结构化 context，不传完整报告
- ❌ 并行执行不分优先级——关键路径的技能应该优先分配资源
- ❌ 用户交互点过多——每条流水线不超过 3 个交互点
