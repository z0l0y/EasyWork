# ADR-{NNNN}: {简短标题}

> 基于 [MADR v4.0](https://adr.github.io/madr/) 格式。
> 此 ADR 由 Tech Compare（技术方案选型对比）阶段 4-6 的产出自动生成。

- **状态**：{Proposed | Accepted | Deprecated | Superseded by ADR-XXXX}
- **日期**：{YYYY-MM-DD}
- **决策者**：{姓名/角色}
- **技术选型报告**：{报告文件链接}

---

## Context and Problem Statement

{一段话描述问题背景：我们在什么情况下，面临什么技术决策，约束是什么。}

## Decision Drivers

{影响决策的关键因素，按优先级排列。每项说明为什么重要。}

1. **{驱动因素 1}**：{为什么重要}
2. **{驱动因素 2}**：{为什么重要}
3. **{驱动因素 3}**：{为什么重要}

## Considered Options

### Option A: {方案名称}

{简要描述方案 A}

- **优点**：
  - {优点 1}
  - {优点 2}
- **缺点**：
  - {缺点 1}
  - {缺点 2}
- **在我们的场景**：{适配度评价}

### Option B: {方案名称}

{简要描述方案 B}

- **优点**：
  - {优点 1}
- **缺点**：
  - {缺点 1}
- **在我们的场景**：{适配度评价}

### Option C: {方案名称}

{同上}

## Decision Outcome

**选择方案：{X}**

{一段话解释为什么选择这个方案，而不是其他方案。}

### Positive Consequences

- {正面影响 1}
- {正面影响 2}
- {正面影响 3}

### Negative Consequences (Risks & Trade-offs)

- {负面影响/风险 1} —— 缓解措施：{...}
- {负面影响/风险 2} —— 缓解措施：{...}
- {负面影响/风险 3} —— 接受（因为 {...}）

### Implementation Plan

1. **Phase 1 (0-3 months)**：{...}
2. **Phase 2 (3-12 months)**：{...}
3. **Phase 3 (12-24 months)**：{...}

### Rollback Plan

如果 {触发条件} 发生，回退计划：
1. {回退步骤 1}
2. {回退步骤 2}
3. 预计回退时间：{N} 天/周
4. 回退成本：{人月/金额}

## Confirmation

{此决策如何被验证是正确的？}

- [ ] PoC 验证通过（{具体标准}）
- [ ] 性能基准达标（{具体指标}）
- [ ] 安全审查通过
- [ ] 团队培训完成
- [ ] 生产灰度验证通过

## References

- 技术选型报告：{链接}
- {相关论文/文档/Issue/PR 链接}
- 相关 ADR：ADR-{XXXX}, ADR-{YYYY}
