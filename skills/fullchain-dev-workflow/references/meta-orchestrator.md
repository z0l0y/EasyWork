# Meta-Orchestrator — 网模式执行引擎

> 版本：v1.0 | 日期：2026-06-25 | 依赖：skill-graph-orchestration.md v1.0, pipeline-composer.md v1.0

## 0. 概述

Meta-Orchestrator 是网模式（🌐）的执行引擎。它不按预设流程执行——而是像一个"技术主管"，分析用户意图，动态决定需要哪些技能，在技能执行过程中发现新问题时自动扩散调用相关技能。

```
用户: "帮我搞清楚这个项目的支付模块能不能扛住双11"

Meta-Orchestrator:
  意图分析 → 初始技能图 → 并行执行 → 技能 A 发现盲区 → 扩散调用技能 B
  → 技能 B 发现风险 → 扩散调用技能 C → 收敛 → 综合报告
```

---

## 1. 意图解析器

### 1.1 解析流程

```
输入: 用户的自然语言意图
  ↓
Step 1: 提取关键信号
  - 领域信号: "支付" / "认证" / "数据库" / "API" / ...
  - 动作信号: "能不能扛住" / "有没有风险" / "为什么慢" / ...
  - 范围信号: "这个项目" / "XX 模块" / "整个系统" / ...
  - 深度信号: "搞清楚" / "看一下" / "全面分析" / ...

  ↓
Step 2: 意图分类
  - 理解型: "这是什么" / "怎么工作的" → 偏 read-project + trace-code
  - 评估型: "有没有问题" / "能不能扛住" → 偏 test-coverage + self-check
  - 调查型: "为什么" / "根因" → 偏 trace-code + talk-retro
  - 综合型: "全面分析" / "帮我搞清楚" → 全技能网模式

  ↓
Step 3: 初始技能匹配
  从 Capability Registry 中匹配相关技能 → 构建初始技能图

  ↓
Step 4: 设定网模式参数
  - 最大扩散深度: 意图复杂度越高，允许越深（默认 3）
  - 审批严格度: 含代码改动则升级审批
  - 预算上限: 按意图复杂度分配 token
```

### 1.2 意图 → 初始技能图映射

| 意图类型 | 示例 | 初始技能 | 可能扩散方向 |
|---------|------|---------|------------|
| "能不能扛住高并发" | 性能评估 | 🔬 trace-code → 🧪 test-coverage | → 🥊 self-check |
| "有没有安全风险" | 安全审计 | 📐 read-project → 🔬 trace-code | → 🔍 code-review → 🧠 talk-retro |
| "为什么 XX 功能这么慢" | 性能排查 | 🔬 trace-code | → 🧪 test-coverage → 🧠 talk-retro |
| "帮我理解整个系统" | 全面理解 | 📐 read-project → 🔬 trace-code → 🧪 test-coverage | → 📊 graph-fullchain → 📋 sum-session |
| "这个方案可行吗" | 方案评估 | 👁️ read-requirements → 🥊 self-check | → 🛰️ tech-radar → 📖 read-paper |

---

## 2. 技能自治扩散

### 2.1 扩散触发器

每个技能在执行过程中，一旦检测到以下**扩散信号**，就触发 Skill Intercom 协议：

| 扩散信号 | 检测方式 | 建议扩散到 |
|---------|---------|----------|
| `coverage_gap_detected` | 某函数覆盖率 <30% + 圈复杂度 >10 | 🧪 test-coverage |
| `architecture_unknown` | 需要了解项目整体架构但缺少信息 | 📐 read-project |
| `high_risk_hotspot` | 发现高风险低覆盖代码 | 🥊 self-check |
| `root_cause_pattern` | 同一模式的问题重复出现 | 🧠 talk-retro |
| `deep_read_needed` | 扫描到高价值论文/项目 | 📖 read-paper / 📐 read-project |
| `visualization_needed` | 调用链复杂需要可视化 | 📊 graph-fullchain |
| `knowledge_gap` | 遇到不熟悉的领域/技术 | 🛰️ tech-radar |
| `review_needed` | 代码质量可疑 | 🔍 code-review |
| `summarization_needed` | 多路分析完成需要汇总 | 📋 sum-session |

### 2.2 扩散决策算法

```
function should_diffuse(signal, current_depth, budget_remaining):
  # 硬限制
  if current_depth >= MAX_DEPTH: return false
  if budget_remaining < BUDGET_PER_SKILL_ESTIMATE: return false
  
  # 循环检测
  if signal.target_skill in call_chain: return false
  
  # 相关性评分
  relevance = calculate_relevance(signal, original_intent)
  if relevance < RELEVANCE_THRESHOLD: return false
  
  # 审批判断
  if signal.target_skill.requires_confirmation and not user_approved:
    ask_user(signal)
    return user_response
  
  return true
```

### 2.3 相关性衰减

每次扩散时，计算新技能与原始意图的余弦距离：

```
原始意图: "支付模块能不能扛住双11"
  relevance(trace-code, intent) = 0.95  ← 直接相关
  relevance(test-coverage, intent) = 0.82  ← 通过 trace-code 间接关联
  relevance(self-check, intent) = 0.71  ← 通过 test-coverage 间接关联
  relevance(talk-retro, intent) = 0.58  ← 通过 self-check 间接关联
  relevance(read-paper, intent) = 0.12  ← 低于阈值 0.5，不扩散
```

---

## 3. Skill Intercom 协议

### 3.1 消息格式

技能间通过结构化的 **Skill Suggestion** 消息通信：

```json
{
  "protocol": "skill-intercom-v1",
  "message_id": "uuid",
  "timestamp": "2026-06-25T10:30:00Z",
  
  "from": {
    "skill": "trace-code",
    "stage": "deep-analysis",
    "finding": "ProcessRefund 覆盖率 12%，18 个分支仅覆盖 2 个"
  },
  
  "suggestion": {
    "type": "coverage_gap_detected",
    "severity": "high",
    "target_skill": "test-coverage",
    "reason": "支付核心函数覆盖严重不足，存在未被测试的双11极端场景风险",
    "urgency": "immediate"
  },
  
  "context_pass": {
    "focus_module": "payment",
    "focus_file": "order.go",
    "focus_function": "ProcessRefund",
    "risk_score": 86,
    "related_findings": [
      "该函数涉及资金操作",
      "被 23 个其他模块依赖",
      "上次修改在 3 个月前，之后再无测试更新"
    ]
  },
  
  "expected_outcome": "明确 ProcessRefund 的覆盖盲区清单 + 补测优先级",
  
  "diffusion_metadata": {
    "depth": 2,
    "chain": ["read-project", "trace-code"],
    "budget_remaining": 65000
  }
}
```

### 3.2 Suggestion Type 全集

| type | severity | target_skill | 描述 |
|------|---------|-------------|------|
| `coverage_gap_detected` | high/medium | test-coverage | 发现覆盖盲区 |
| `architecture_unknown` | medium | read-project | 需要架构上下文 |
| `high_risk_hotspot` | critical/high | self-check | 发现高风险代码 |
| `root_cause_pattern` | high | talk-retro | 发现重复问题模式 |
| `deep_read_needed` | medium | read-paper | 需要深读文献 |
| `project_understanding_needed` | medium | read-project | 需要理解项目 |
| `visualization_needed` | low | graph-fullchain | 需要可视化 |
| `knowledge_gap` | medium | tech-radar | 需要外部知识 |
| `review_needed` | high | code-review | 需要代码审查 |
| `summarization_needed` | low | sum-session | 需要汇总多路分析 |

---

## 4. 网模式执行引擎

### 4.1 执行模型

```
Net.exec(intent):
  # Phase 1: 意图解析
  intent_signal = IntentParser.parse(intent)
  initial_skills = SkillMatcher.match(intent_signal)
  
  # Phase 2: 初始执行
  active_skills = initial_skills
  completed = []
  suggestions = []
  depth = 0
  budget = NET_BUDGET_DEFAULT     # 100K tokens
  
  while active_skills and depth < MAX_DEPTH and budget > 0:
    # 并行执行当前层级的所有活跃技能
    results = parallel_execute(active_skills)
    
    for each result:
      completed.append(result)
      budget -= result.tokens_used
      
      # 检查技能产出的扩散信号
      if result.has_suggestions():
        suggestions.extend(result.suggestions)
    
    # 扩散决策
    next_skills = []
    for each suggestion in suggestions:
      if DiffusionController.approve(suggestion, depth, budget):
        next_skills.append(suggestion.target_skill)
        if suggestion.requires_user_approval:
          user_decision = ask_user(suggestion)
          if not user_decision: continue
    
    active_skills = next_skills
    suggestions = []
    depth += 1
  
  # Phase 3: 收敛
  if completed.length > 1:
    synthesize_report(completed)
```

### 4.2 进度展示

```
【🌐 网模式 — 支付模块双11容量评估】

📐 read-project ........... ✅ 完成 (识别到 3 个核心模块: payment/order/user)
🔬 trace-code ............. ✅ 完成
  └── 发现覆盖盲区 → 建议 🧪 test-coverage [自动扩散, depth=2]
🧪 test-coverage .......... 🔄 执行中 (分析 payment/order 模块)
  └── 扫描 120 个测试文件...

扩散链: read-project → trace-code → test-coverage
深度: 2/3 | 已用: 45K/100K tokens | 耗时: 2m 18s
待审批: 0 | 自动扩散: 1 | 已拒绝: 0
```

### 4.3 收敛策略

```
当以下任一条件满足时，网模式收敛（停止扩散）：
  1. 所有活跃技能完成，且无新的扩散信号
  2. 扩散深度达到 MAX_DEPTH（3 层）
  3. Token 预算消耗 ≥ 90%（100K 中已用 90K）
  4. 所有扩散信号都被用户拒绝
  5. 执行超时（30 分钟）
  6. 检测到扩散循环（A→B→A）

收敛后：
  - 汇总所有阶段的发现
  - 标注未深入的分支（"因预算限制，未对 XX 模块进行深度分析"）
  - 提供"继续扩散"选项让用户手动触发下一轮
```

---

## 5. 扩散控制

### 5.1 硬限制

| 参数 | 默认值 | 说明 |
|------|--------|------|
| MAX_DEPTH | 3 | 从初始技能算起，最多扩散 3 层 |
| BUDGET_CAP | 100K tokens | 网模式总预算 |
| TIMEOUT | 30 min | 总执行时间上限 |
| SKILLS_MAX | 8 | 单次网模式最多调用 8 个技能 |

### 5.2 审批矩阵

| 技能类别 | 自动扩散 | 需用户确认 |
|---------|---------|-----------|
| 🟢 纯分析 (read-paper/read-project/trace-code/tech-radar/test-coverage) | ✅ 允许 | 否 |
| 🟡 质量检查 (self-check/talk-retro/code-review/sum-session/graph-fullchain) | ✅ 允许 | 否（仅通知） |
| 🟠 含副作用 (read-requirements: 会产出开发需求) | ⚠️ 通知 | 是 |
| 🔴 代码改动 (code-implement/examine-quality/git-split-commit) | ❌ 不允许 | 必须确认 |

### 5.3 循环检测

```
call_chain: [read-project, trace-code, test-coverage]
new_suggestion: trace-code  ← ❌ 已在调用链中 → 拒绝扩散

call_chain: [trace-code, test-coverage]
new_suggestion: self-check  ← ✅ 不在调用链中 → 允许扩散
```

---

## 6. 典型网模式场景

### 场景 1: 新项目接手

```
用户: "我刚接手这个 Go 支付项目，帮我全面了解一下"

Meta-Orchestrator 分析:
  意图: 全面理解 (理解型)
  初始技能: 📐 read-project
  策略: quality-first

执行过程:
  1. 📐 read-project 完成 (5.2s, 产出 450 行报告)
     ├── 发现支付模块架构复杂，建议追踪
     └── → 扩散: 🔬 trace-code (自动, depth=2)
  
  2. 🔬 trace-code 完成 (追踪 ProcessRefund + CreateOrder)
     ├── 发现 ProcessRefund 覆盖率极低
     └── → 扩散: 🧪 test-coverage (自动, depth=3)
  
  3. 🧪 test-coverage 完成
     └── 无新扩散信号 → 收敛

  最终产出: 3 份独立报告 + 综合摘要
  总耗时: 8m 42s | 总 token: 52K
```

### 场景 2: 性能瓶颈排查

```
用户: "为什么用户登录接口这么慢？"

Meta-Orchestrator 分析:
  意图: 性能排查 (调查型)
  初始技能: 🔬 trace-code (入口: POST /api/login)
  策略: quality-first

执行过程:
  1. 🔬 trace-code 完成
     ├── 发现登录流程调用了 4 个外部服务
     ├── 密码哈希计算耗时 800ms
     └── → 扩散 #1: 🧪 test-coverage (检查登录模块测试)
         → 扩散 #2: 🧠 talk-retro (分析为什么密码哈希在请求路径上)

  2. 🧪 test-coverage 完成
     └── 无覆盖盲区 → 不扩散

  3. 🧠 talk-retro 完成
     └── 根因: bcrypt cost factor=14 但业务只需要 10
     → 扩散: 🥊 self-check (验证 cost factor 降低安全性)

  4. 🥊 self-check 完成
     └── cost=14→10 安全性下降可接受 → 收敛

  最终产出: 4 份报告 + 优化建议 (降低 cost factor 到 10, 异步化日志写入)
```

---

## 7. 反模式

- ❌ 网模式用于简单问题——"这个函数干嘛的"不需要网模式，点模式就够了
- ❌ 扩散不设深度限制——3 层是硬上限，超过就是无限递归
- ❌ 自动扩散涉及代码改动——code-implement 永远需要用户审批
- ❌ 扩散信号不区分优先级——`coverage_gap_detected` (high) 应该优先于 `visualization_needed` (low)
- ❌ 收敛后不总结——用户不想看 5 份独立报告，需要一份综合摘要
- ❌ 循环检测只检查技能名不检查函数级——同一个函数被两个不同技能分析可能不是循环
- ❌ 预算用完了硬性截断不告知——标注"因预算限制未分析 XX"，给继续选项
