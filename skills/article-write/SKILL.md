---
name: article-write
description: >
  文档编写与输出格式化。将 Agent 生成的长文本输出写入格式良好的 Markdown 文档。
  底座能力——任何有长输出的技能均可调用此 skill。
  支持 6 种文档类型模板（技术报告/开发总结/变更日志/设计文档/分析报告/通用文档），
  自动检测输出长度并建议写入文件，YAML frontmatter + 可折叠目录 + 写后验证。
allowed-tools: Read, Write, Bash
model: sonnet
version: 1.0
capability:
  id: article-write
  display_name: 文档编写
  emoji: "📝"
  category: content
  tier: 1
  inputs:
    - { name: raw_content, type: text, required: true, description: "需要写入文档的原始内容（Agent 输出/用户提供）" }
    - { name: doc_type, type: enum, required: false, description: "文档类型：report|summary|changelog|design|analysis|general" }
    - { name: output_path, type: path, required: false, description: "输出文件路径（默认 workspace/{date}-{slug}.md）" }
    - { name: source_skill, type: string, required: false, description: "调用来源技能名称" }
  outputs:
    - { name: written_file_path, type: path, description: "写入的 .md 文件绝对路径" }
    - { name: doc_preview, type: text, description: "文档预览（前 15 行 + 统计信息）" }
  triggers: ["写文档","生成文档","输出文档","保存输出","导出报告","写文章",
             "write article","write doc","save output","generate doc","article-write"]
  related_skills:
    - { skill: all, relationship: outbound, desc: "底座能力——任何产出长文的技能均可调用 article-write 将结果写入 .md 文件" }
  suggested_when:
    - "Agent 输出超过 20 行，终端阅读体验差"
    - "用户需要保存/分享/审查 Agent 生成的结果"
    - "上游技能产出了结构性报告需要持久化"
    - "需要生成 ADR / 设计文档 / 变更日志等标准文档"
  pipeline_placement:
    good_after: [sum-session, read-paper, code-implement, tech-radar, code-review, read-requirements]
    good_before: []
  autonomous:
    callable_by_other: true
    requires_confirmation: false
    max_depth: 1
  risk_level: L0
---

# 📝 Article Write（文档编写）

> 底座能力 · v1.0 · 将 Agent 输出文章化为格式良好的 Markdown 文档

## 1. 定位

article-write 是 EasyWork 技能体系的**文章化输出底座能力**。它不替代 sum-session/read-paper/code-implement 等有领域逻辑的产出技能，而是为所有技能提供**统一的文档格式化 + 文件写入 + 写后验证**基础设施。

```
任何技能产生长输出（>20行）
  │
  ├── 简短（<20行）→ 直接终端输出，不调用 article-write
  │
  └── 长文（≥20行）
      ├── Auto-detect：提示"输出较长（{N}行），写入 .md 文件？"
      └── Explicit："写文档" / "保存输出" → 直接进入格式化→写入
```

**与现有产出技能的差异**：

| 技能 | 定位 | 文档类型 | article-write 的角色 |
|------|------|---------|---------------------|
| sum-session | 工作流步骤（SUM） | 六要素总结（1 种） | 可接管其文件写入/格式化（如用户要求） |
| read-paper | 学习技能 | 十段论文报告（1 种） | 可接管其文件写入/格式化（如用户要求） |
| code-implement | 开发技能 | 变更记录（1 种） | 可接管其文件写入/格式化（如用户要求） |
| **article-write** | **底座能力** | **6 种可选模板** | **自身的 5 阶段写流程** |

核心原则：**技能负责领域逻辑，article-write 负责格式化输出**。

## 2. 前置判断

### 2.1 自动检测模式

Agent 在即将输出长文本时执行此判断：

```
if 预期输出行数 < 20:
    → 直接终端输出，不触发 article-write
elif 20 ≤ 预期输出行数 ≤ 50:
    → 终端输出 + 末尾追加提示：
      "📝 以上内容已输出到终端。需要写入 .md 文件方便查看吗？[写文档/不用]"
elif 预期输出行数 > 50:
    → 自动建议（用户可拒绝）：
      "📝 输出较长（约{N}行），建议写入 .md 文件。写入吗？[写文档/不用/指定路径]"
```

### 2.2 显式调用模式

用户主动说触发词时进入此模式：

| 用户说 | 行为 |
|--------|------|
| "写文档" / "生成文档" / "write article" | 进入模板选择 → 用户提供/确认内容 → 格式化 → 写入 |
| "保存输出" / "导出报告" / "save output" | 提取上一步/当前对话输出 → 自动推断 doc_type → 写入 |
| "把{内容}写成{类型}" | 直接指定 doc_type → 格式化 → 写入 |
| "输出到文件" / "写个{类型}" | 询问内容来源（当前对话/重新生成/用户粘贴） |

### 2.3 可跳过场景

- 输出 < 20 行且用户未主动要求写文件 → **跳过**
- 用户正在终端交互式操作（如逐行确认） → **跳过**
- 内容是临时调试信息/一次性查询 → **跳过**
- 用户明确说"不用写文件"/"直接输出"

### 2.4 任务类型 → 默认文档类型映射

| 上游技能/场景 | 默认 doc_type | 说明 |
|-------------|-------------|------|
| sum-session 产出 | summary | 六要素开发总结 |
| tech-radar 产出 | report | 技术雷达报告 |
| read-paper 产出 | report | 论文阅读报告 |
| code-review 产出 | analysis | 代码审查分析报告 |
| code-implement 产出 | changelog | 变更记录 |
| read-requirements 产出 | design | 需求文档→设计文档 |
| 用户自由内容 | general | 通用文档 |
| 架构/方案讨论 | design | 设计文档 |

## 3. 核心流程

### 完整五阶段流程

```
Phase 1: 内容获取
  ├── 上游技能 step_output（优先级最高——有结构，有证据）
  ├── 当前对话内容提取（用户说"把刚才的结论写成文档"）
  ├── 用户直接提供（粘贴/描述要写的内容）
  └── Agent 重新生成（用户给主题，Agent 生成内容后再写入）
      ↓
Phase 2: 文档类型判定
  ├── 用户显式指定 → 直接使用
  ├── 从上游技能自动映射（见表 §2.4）
  ├── 从内容关键词推断（含"版本/发布/CHANGELOG"→changelog）
  └── 无法推断 → general（通用文档）
      ↓
Phase 3: 格式化（详见 §4 各类型模板）
  ├── 生成 YAML frontmatter（title/date/tags/status/source）
  ├── 生成可折叠目录（仅当 ≥3 个 H2 标题时）
  ├── 套用选定类型的模板骨架
  ├── 代码块标注语言（```bash / ```json / ```yaml / ```log / ```diff）
  ├── 表格对齐（| 列 | 列 | 列 | 格式，确保每行列数一致）
  ├── 标题层级连贯（H1 → H2 → H3，不跳跃层级）
  └── 文件名/路径包裹在反引号中（`path/to/file.ts`）
      ↓
Phase 4: 写入文件
  ├── 默认路径：{workspace}/docs/{date}-{slug}.md
  │   其中 slug = title 的 kebab-case 版本（≤50字符）
  ├── 用户指定路径 → 使用用户路径（相对路径基于 workspace）
  ├── 文件名冲突 → 追加 -2, -3...（如 2026-06-26-架构审查-2.md）
  └── 确保父目录存在（Bash mkdir -p）
      ↓
Phase 5: 写后验证
  ├── Read 回文件前 20 行 + 最后 5 行（验证未截断）
  ├── 检查：YAML frontmatter 完整？标题无跳跃？代码块闭合？
  ├── 如发现截断/损坏 → 重新写入（最多 3 轮修复）
  └── 输出：文件路径 + 文档预览（前 15 行 + 统计信息）
```

### Phase 3 格式化细则

#### 3.1 YAML frontmatter 字段

| 字段 | 生成规则 | 示例 |
|------|---------|------|
| `title` | 用户提供 / 从内容首行提取 / "无标题文档" | `"Q3 微服务拆分方案评审"` |
| `date` | 当天日期 ISO 8601 | `2026-06-26` |
| `author` | 固定 `claude-code` | `claude-code` |
| `model` | 当前使用的模型名 | `claude-sonnet-4-20250514` |
| `tags` | 从内容自动提取关键词（2-5个） | `["架构","微服务","评审"]` |
| `status` | 默认 `draft`，用户可指定 | `draft` / `review` / `final` |
| `source` | 来源技能名 / `user-input` | `tech-radar` / `sum-session` |
| `sessionId` | 从上下文获取（如有） | `session-7f3a-...` |

#### 3.2 可折叠目录

仅当文档有 ≥3 个 H2 标题时生成：

```markdown
<details>
<summary><strong>📑 目录</strong></summary>

- [1. 背景](#1-背景)
- [2. 发现过程](#2-发现过程)
  - [2.1 代码审查](#21-代码审查)
  - [2.2 性能测试](#22-性能测试)
- [3. 结论与建议](#3-结论与建议)

</details>

---
```

锚点规则：中文标题 → 拼音或保留中文（GitHub 兼容），英文标题 → 小写+连字符。

#### 3.3 代码块标注

| 内容类型 | 标注 |
|---------|------|
| Shell 命令 | ` ```bash ` |
| JSON 数据 | ` ```json ` |
| YAML 配置 | ` ```yaml ` |
| 日志输出 | ` ```log ` |
| Diff 对比 | ` ```diff ` |
| 程序代码 | 按实际语言标注（` ```python ` / ` ```typescript ` 等） |
| 纯文本输出 | ` ```text ` |

#### 3.4 表格规范

- 表头与分隔符对齐（`| 列 | 列 |`）
- 每行相同列数
- 不使用合并单元格（Markdown 不支持）
- 长内容用 `<br>` 换行而非破坏表格结构

## 4. 6 种文档类型模板

### 类型 1：📊 技术报告（report）

适用：tech-radar、read-paper、技术调查、评估结果

```markdown
# {标题}

*{一句话摘要——本文档是什么，给谁看，解决什么问题}*

<details>
<summary><strong>📑 目录</strong></summary>
[TOC]
</details>

---

## 1. 摘要

{3-5 句摘要——背景、方法、关键发现、主要结论}

## 2. 背景

{为什么要做这个分析/调查？技术上下文是什么？}

## 3. 方法论

{用什么方法/工具/数据源进行分析？扫描范围/时间跨度/搜索策略}

## 4. 发现

### 4.1 {发现类别 1}

{描述 + 数据支撑}

| 维度 | 结果 | 说明 |
|------|------|------|
| {维度名} | {结果} | {说明} |

### 4.2 {发现类别 2}

{描述 + 数据支撑}

## 5. 分析

{对发现的深层分析——模式识别、趋势判断、因果关系}

## 6. 结论与建议

- [ ] 建议 1：{可操作性建议}
- [ ] 建议 2：{可操作性建议}
- [ ] 建议 3：{可操作性建议}

---

*此文档由 claude-code 生成于 {YYYY-MM-DD}。来源：{技能名}。状态：draft。*
```

### 类型 2：📋 开发总结（summary）

适用：sum-session 产出、迭代结束总结

```markdown
# {标题}

*{一句话摘要}*

<details>
<summary><strong>📑 目录</strong></summary>
[TOC]
</details>

---

## 1. 背景

{为什么做这件事？业务/技术驱动力}

## 2. 发现过程

{如何发现问题/实现需求的？关键步骤和决策点}

## 3. 问题描述

{核心问题是什么？影响范围？}

## 4. 解决方案

{怎么解决的？为什么选这个方案？}

## 5. 最终效果

{客观验证——测试结果、性能对比、用户反馈}

## 6. 未来展望

{接下来做什么？已知局限？技术债务？}

---

## 变更清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| {path} | {add/modify/delete} | {说明} |

---

*此文档由 claude-code 生成于 {YYYY-MM-DD}。*
```

### 类型 3：📝 变更日志（changelog）

适用：版本发布、PR 描述

```markdown
# {版本号} — {日期}

*{一句话版本摘要}*

---

## 新增

- {新增功能/特性}

## 变更

- {行为变更/接口变更}

## 已弃用

- {即将移除的功能}

## 修复

- {Bug 修复描述}

## 安全

- {安全相关修复/加固}

---

## 升级指南

{如有破坏性变更，说明迁移步骤}

## 贡献者

- {贡献者列表}

---

*此变更日志遵循 [Keep a Changelog](https://keepachangelog.com/) 格式。*
```

### 类型 4：🏗️ 设计文档（design）

适用：架构设计、技术方案、ADR

```markdown
# {设计标题}

**状态**：{提议 / 已接受 / 已弃用 / 已取代}

*{一句话——在什么背景下，选择了什么方案，放弃了什么替代方案}*

<details>
<summary><strong>📑 目录</strong></summary>
[TOC]
</details>

---

## 1. 摘要

{3-5 句设计概述}

## 2. 目标与非目标

### 目标
- {目标 1}
- {目标 2}

### 非目标
- {明确不在此次范围内的}

## 3. 当前状态

{现有系统/方案的描述，什么在推动改变}

## 4. 设计方案

{提议的方案——架构、组件、数据流、接口}

## 5. 替代方案

| 方案 | 优点 | 缺点 | 为何放弃 |
|------|------|------|---------|
| 方案 A | ... | ... | ... |
| 方案 B | ... | ... | ... |

## 6. 权衡分析

| 维度 | 选择 | 代价 | 缓解措施 |
|------|------|------|---------|
| 性能 | ... | ... | ... |
| 复杂度 | ... | ... | ... |
| 可维护性 | ... | ... | ... |

## 7. 实施计划

- [ ] 步骤 1：{描述}
- [ ] 步骤 2：{描述}
- [ ] 步骤 3：{描述}

## 8. 测试策略

{如何验证设计正确性？}

---

*此设计文档遵循 [ADR](https://adr.github.io/) 格式。*
```

### 类型 5：🔍 分析报告（analysis）

适用：code-review 产出、安全审计、质量分析

```markdown
# {分析标题}

*{一句话——分析范围、方法、关键发现}*

<details>
<summary><strong>📑 目录</strong></summary>
[TOC]
</details>

---

## 1. 分析范围

{分析了什么、哪些文件/模块/系统}

## 2. 分析方法

{审查维度、使用的工具/标准、评分体系}

## 3. 发现

| # | 严重程度 | 位置 | 描述 | 建议修复 |
|---|---------|------|------|---------|
| 1 | 🔴 高 | `file:line` | {描述} | {建议} |
| 2 | 🟡 中 | `file:line` | {描述} | {建议} |
| 3 | 🟢 低 | `file:line` | {描述} | {建议} |

## 4. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| {风险描述} | 高/中/低 | 高/中/低 | {措施} |

## 5. 建议

- [ ] 高优先级：{建议}
- [ ] 中优先级：{建议}
- [ ] 低优先级：{建议}

## 6. 后续行动

{谁、什么时候、做什么}

---

*分析标准：{使用的标准/框架}。工具：{使用的工具}。*
```

### 类型 6：📄 通用文档（general）

适用：无特定类型匹配时，自由格式兜底

```markdown
# {标题}

*{一句话摘要}*

<details>
<summary><strong>📑 目录</strong></summary>
[TOC]
</details>

---

{自由格式内容——Agent 自动从内容中提取结构，生成目录和章节}

---

*此文档由 claude-code 生成于 {YYYY-MM-DD}。*
```

## 5. 写入路径规则

### 5.1 默认路径

```
{workspace}/docs/{date}-{slug}.md
```

- `{workspace}` = 当前 git 仓库根目录（如 `~/project`）
- `{date}` = YYYY-MM-DD
- `{slug}` = 标题的 kebab-case（英文/拼音，≤50 字符）

### 5.2 路径优先级

1. 用户显式指定的路径（最高优先级）
2. `{workspace}/docs/` 目录（如果存在）
3. `{workspace}/` 根目录（如果 docs/ 不存在）

### 5.3 文件命名约定

| 文档类型 | 命名模式 | 示例 |
|---------|---------|------|
| report | `{date}-{topic}-report.md` | `2026-06-26-mcp-protocol-report.md` |
| summary | `{date}-{feature}-summary.md` | `2026-06-26-payment-refactor-summary.md` |
| changelog | `CHANGELOG-{version}.md` | `CHANGELOG-v2.14.0.md` |
| design | `{date}-ADR-{number}-{title}.md` | `2026-06-26-ADR-001-payment-split.md` |
| analysis | `{date}-{scope}-analysis.md` | `2026-06-26-auth-module-analysis.md` |
| general | `{date}-{slug}.md` | `2026-06-26-meeting-notes.md` |

### 5.4 文件名去重

如果目标路径已存在：
1. 追加 `-2` → `2026-06-26-report-2.md`
2. 如果 `-2` 也存在 → `-3`...递增到第一个不存在的编号
3. 最多尝试 10 次，之后报告错误

## 6. 写后验证（Quality Self-Check）

写入后必须执行以下 6 项检查：

```
✅ Check 1：YAML frontmatter 存在且格式有效？
   → Read 文件前 10 行，确认 --- 开头和闭合

✅ Check 2：标题层级逻辑连贯？
   → 扫描所有 # 标题，确认无 H1→H3 跳跃（H1 下必须是 H2）

✅ Check 3：代码块正确闭合？
   → 计数 ``` 出现次数，必须为偶数

✅ Check 4：表格列数一致？
   → 每个表格的每行列数相同

✅ Check 5：文件未截断？
   → Read 最后 5 行，确认有结尾标记或完整句子

✅ Check 6：目录锚点有效？
   → 目录中每个链接的锚点 ID 与正文标题匹配（如生成了目录）
```

任一检查失败 → 修复后重新写入（最多 3 轮）。3 轮后仍失败 → 报告具体问题给用户，让用户决定。

## 7. 与其他技能的集成

### 7.1 技能间通信协议（Intercom）

article-write 新增一个 suggestion type 供其他技能使用：

```json
{
  "from_skill": "tech-radar",
  "suggestion_type": "long_output_needs_writing",
  "severity": "info",
  "target_skill": "article-write",
  "reason": "雷达报告约 150 行，建议写入 .md 文件便于查看",
  "context_pass": {
    "raw_content": "{上一步输出的结构化内容}",
    "doc_type": "report",
    "source_skill": "tech-radar"
  },
  "requires_confirmation": true
}
```

### 7.2 被调用方式

| 调用来源 | 方式 | 示例 |
|---------|------|------|
| 用户直接触发 | 说触发词 | "把刚才的分析写成文档" |
| 其他技能 Intercom | 技能执行中发现长输出，建议调用 | tech-radar → article-write |
| Meta-Orchestrator | 网模式感知到长输出，自动调度 | 自动 → article-write |

### 7.3 作为底座能力的使用约束

- `callable_by_other: true` —— 任何技能均可调用
- `requires_confirmation: false` —— 被调用时不需要额外确认（用户已同意写入）
- `max_depth: 1` —— 仅一层调用（article-write 不再调用其他技能）
- `risk_level: L0` —— 纯文档写入，无副作用

## 8. 反模式

- ❌ **文章化≠水文化** —— 格式化是让内容更易读，不是灌水扩充篇幅。禁止为了"看起来像一篇文章"而添加空洞内容。
- ❌ **不要跳过内容获取直接瞎编** —— Phase 1 必须获取到实际内容再格式化。不能凭记忆/想象"模拟"上游技能的输出。
- ❌ **不要在不合适的场景强制写文件** —— 用户正在终端交互（如逐行确认、调试）时，不要打断用户建议写文件。
- ❌ **不要跳过写后验证** —— 长文本写入后必须 Fetch 验证，防截断/格式损毁/中文乱码。最多 3 轮修复，超限报告用户。
- ❌ **不要破坏上游技能的内容结构** —— article-write 只做格式化，不做内容改写。不能为了套模板而删除/歪曲上游的内容。
- ❌ **YAML frontmatter 不要嵌套** —— `capability:` 在 SKILL.md 中是顶级的，但在文档 frontmatter 中只有一级键值对。不把 frontmatter 当 capability block。
- ❌ **不要生成原始 HTML 表格** —— 用 Markdown 表格语法（`| col | col |`），不回退到 `<table>` 标签。
- ❌ **不要在文档中使用内联样式** —— Markdown 不是 HTML。不使用 `style=""`、`<font>`、`<div align="">` 等。
- ❌ **不要跳过标题层级** —— 必须 H1 → H2 → H3，不能 H1 下直接 H3。这会导致目录生成错误。
- ❌ **不要用表情符号做主要视觉元素** —— 表格/标题中可以适度使用 emoji 前缀区分章节，但不能用 emoji 替代文字描述。
- ❌ **文件名不要包含特殊字符** —— 只使用字母、数字、连字符、下划线。中文文件名在 Windows/Mac/Linux 间兼容性差，title 用中文，文件名用拼音或英文 slug。
- ❌ **不要覆盖已有文件不提示** —— 写入前检查目标路径是否存在。如存在 → 告知用户，用 `-2` 策略去重或让用户选择覆盖。

## 9. 版本历史

- v1.0 (2026-06-26)：初始版本。6 种文档类型模板、5 阶段写流程、自动检测+显式调用双模式、写后 6 项验证、YAML frontmatter + 可折叠目录、12 条反模式。底座能力——任何产出长文的技能均可调用。
