---
name: markdown
description: >
  Markdown 产物后端。将 9 步工作流产出生成为单个 Markdown 文件。
  适用于需要纯文本记录、导入 Git 仓库文档、或作为其他系统输入源的场景。
output_format: markdown
capabilities: [create_doc, append_blocks, share_link]
requires_mcp: []
requires_network: false
streaming: false
version: 1.0
---

# Markdown Backend（Markdown 产物后端）

## 后端定位

markdown 后端将 EasyWork 工作流产出生成为 `.md` 文件。适用于：
- 需要将工作流记录纳入 Git 版本控制
- 导入飞书文档（作为 Markdown 源材料）
- PR 描述生成
- 纯文本归档需求

---

## 前置条件

- 文件系统可写（项目目录内）
- 无网络依赖
- 无 MCP 依赖

---

## create_session_doc

**触发时机**：工作流启动后、第一个产出步骤前。

### Agent 执行指令

1. 确保 `.claude/easywork/` 目录存在（不存在则 `mkdir -p`）
2. 生成文件名：`EasyWork_Report_{YYYYMMDD_HHmmss}.md`
3. 文件路径：`{项目根目录}/.claude/easywork/{文件名}`
4. 返回：
   - `doc_id` = 文件绝对路径
   - `doc_url` = 文件路径
   - `doc_title` = 文件名

---

## write_step_output

**触发时机**：每个步骤完成后。

markdown 后端**不支持流式追加**。所有步骤产出在内存中暂存，由 `write_final_report` 一次性写入。

### Agent 执行指令

1. 将步骤产出按 data-contract 字段暂存
2. 不做文件写入
3. 返回 `{ "success": true }`

---

## write_final_report

**触发时机**：SUM 步骤完成后。

### Agent 执行指令

**格式规范**：遵守 `references/doc-writing-guide.md`。

#### 文档结构模板

```markdown
# {任务类型}报告 — {日期}

**任务**：{task_description}
**风险等级**：{risk_level}
**产物后端**：markdown
**生成时间**：{timestamp}

---

## 执行概览

| 步骤 | 状态 | 耗时(秒) | 备注 |
|------|------|---------|------|
| 1. READ | {status} | {duration} | — |
| 2. CODE | {status} | {duration} | — |
| ... | ... | ... | ... |

{如有跳过步骤}
### 已跳过步骤

- {步骤名}：{跳过理由}
```

#### 各步骤内容格式化

**READ（需求理解）**：
```markdown
## 1. 需求理解

### 业务目标
{goal}

### 修改范围
- 文件：{files}
- 模块：{modules}

### 约束条件
{constraints 列表}

### 验收标准
{acceptance_criteria 列表}

### 不做什么
{non_goals 列表}
```

**CODE（代码实现）**：
```markdown
## 2. 代码实现

### 变更文件

{每个文件的改动说明——结合业务上下文，不是泛泛的"修改了某函数"}

### 影响评估
{impact_assessment}

### 实现说明
{implementation_notes}

### 新增依赖
{如有——标注名称、版本、必要性}
```

**REVIEW（代码审查）**：
```markdown
## 3. 代码审查

### 审查结论
{verdict}

### 七维度结果

| 维度 | 结果 | 发现问题 |
|------|------|---------|
| 正确性 | {status} | {issues} |
| 安全性 | {status} | {issues} |
| 兼容性 | {status} | {issues} |
| 可维护性 | {status} | {issues} |
| 性能 | {status} | {issues} |
| 可观测性 | {status} | {issues} |
| 可访问性 | {status} | {issues} |

### 阻断问题
{blocking_issues 列表——如有}
```

**EXAMINE（质量验证）**：
```markdown
## 4. 质量验证

### 测试执行
- 命令：{test_command}
- 结果：{total} 个测试，{passed} 通过，{failed} 失败，{skipped} 跳过

### 测试输出摘要
{test_output_snippet——最多 80 字符，敏感信息已脱敏}
```

**GIT（提交拆分）**：
```markdown
## 5. 提交拆分

### 拆分方案

| # | 维度 | 文件数 | 风险 | 说明 |
|---|------|--------|------|------|
{每个 unit 一行}

### 各单元详情

#### {index}. {dimension} — {summary}

改动文件：
{文件清单}

改动说明（业务上下文）：
{business_context——结合项目业务，说明为什么要改这些文件、这些改动在业务上达成了什么}

引入风险：
{risk_introduced——具体风险，不是泛泛的"可能影响稳定性"}

验证证据：
{verification_evidence——来自 EXAMINE 的测试结果引用}

开发者 Check：
- [ ] 改动范围符合需求
- [ ] 无意外副作用
- [ ] 测试覆盖充分
- [ ] 代码风格一致

建议 Commit Message：
{type}({scope}): {subject}

{body}
```

**GRAPH（可视化图表）**：
```markdown
## 6. 架构可视化

### 图表类型
{diagram_type}

### Mermaid 代码
{嵌入 mermaid fenced code block}

### 节点与代码对照表

| 节点 | 代码实体 | 位置 |
|------|---------|------|
```

**SUM（总结报告）**：
```markdown
## 7. 总结报告

### 背景
{background}

### 发现过程
{discovery}

### 问题说明
{problem}

### 解决方案
{solution}

### 最终效果
{outcome——含验收标准和量化对比}

### 未来展望
{future 列表}
```

**TALK（复盘分析）**：
```markdown
## 8. 复盘分析

### 5-Whys 根因追溯
{逐层追问}

### 根因
{root_cause}（{root_cause_type}）

### Trade-offs 分析

| 选择 | 收益 | 代价 | 是否明知 | 后续计划 |
|------|------|------|---------|---------|
```

**ASK（人工确认）**：
```markdown
## 9. 人工确认

{questions 列表，每项含维度/问题/为什么问/如果否则}
```

#### 保存前检查

1. **脱敏自检**（v2.4 延续）：检查并移除 Token/密钥/密码/内部 URL/大段源码(>30行)/手机号/邮箱/帐号/数据库连接串
2. **写作规范自检**（v2.5）：不在正文中使用反引号包裹文件名；段落自然；标题下不超过 4 子标题；表格仅用于结构化信息
3. 写入文件到 `doc_id` 对应路径
4. 返回 `{ "success": true, "doc_url": "{文件路径}" }`

---

## get_share_link

**触发时机**：最终报告写入完成后。

### Agent 执行指令

Markdown 文件无可公开分享的 URL。返回文件路径。

```
{ "share_url": "{文件绝对路径}", "access_level": "local_only" }
```

---

## 错误处理

| 场景 | 处理 |
|------|------|
| 目录创建失败 | 报告错误，尝试写入当前工作目录 |
| 文件写入失败 | 报告错误路径，要求用户检查权限 |
| Markdown 中有特殊字符导致格式化异常 | 使用纯文本替代，标注异常 |

---

## 反模式

- ❌ 在正文中使用反引号包裹文件名/命令名——违反复盘口吻约束
- ❌ 生成内容使用模板套话（"综上所述""经过严谨分析"）
- ❌ 表格用于布局排版——表格仅用于结构化数据
- ❌ 跳过写作规范自检直接保存
