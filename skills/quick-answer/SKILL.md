---
name: quick-answer
description: >
  快问快答——TL;DR 优先的结构化精简回答。答案先行、要点为辅、展开按需。
  解决 Agent 回复又慢又长、用户不知道从哪里开始看的问题。
  参考 layman（结构化摘要）、stenographer-mode（多级简洁+字面保护）、
  cc-simpler-token-saver（output style 注入 prompt）的业界实践。
allowed-tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
model: haiku
version: 3.0
capability:
  id: quick-answer
  display_name: 快问快答
  emoji: "⚡"
  category: content
  tier: 1
  inputs:
    - { name: user_question, type: text, required: true, description: "用户的问题/困惑" }
  outputs:
    - { name: quick_answer, type: text, description: "结构化精简回答——答案先行，要点 ≤4 条" }
  triggers: ["快问快答", "quick question", "tldr", "说重点", "别废话", "直接说", "一句话",
             "快点回答", "quick-answer", "别啰嗦", "讲核心", "核心问题是", "快速回答"]
  related_skills:
    - { skill: article-write, relationship: outbound, desc: "如果回答内容过长需要写入文件，建议调用 article-write" }
    - { skill: sum-session, relationship: outbound, desc: "如果用户后续需要完整汇总，进入 sum-session" }
  suggested_when:
    - "用户明确要求简短/快速回答"
    - "用户说 TLDR / 说重点 / 别废话 / 直接说"
    - "用户的问题被淹没在长回复中"
    - "用户需要快速确认一个点，而非全面分析"
  pipeline_placement:
    good_after: []
    good_before: ["article-write", "sum-session"]
  autonomous:
    callable_by_other: true
    requires_confirmation: false
    max_depth: 0
  risk_level: L0
---

# Quick Answer（快问快答）

## 1. 核心理念：不是压缩，是重排

普通 Agent 回复的问题不是"字太多"，而是**结构太差**——铺垫 3 段才进入正题，用户根本找不到答案在哪。

Quick Answer 不压缩文字，而是**重构信息顺序**：答案放最前面，支撑放后面。用户读完第一行就知道结论，有兴趣再看细节。

> **与上一次"压缩"方案的关键区别**：上次的方案试图缩短文本（用户说"别压缩"），本次方案不缩短文本，只改变结构——完整句子、完整代码、完整路径，只是把最重要的放在最前面。

### 参考实现

| 项目 | 核心思路 | 我们借鉴了什么 |
|------|---------|--------------|
| [layman](https://github.com/vamsi920/layman) | Done / Why / What changed / Check this 四段式结构化摘要 | 可预测的固定格式，用户知道每个位置写什么 |
| [stenographer-mode](https://github.com/AkashAi7/stenographer-mode) | lite/brief/court/machine 四级压缩，代码/路径原样保护 | 字面保护原则——代码、路径、命令绝不缩写 |
| [cc-simpler-token-saver](https://github.com/tim-hub/cc-simpler-token-saver) | output style 注入 system prompt，缓存友好 | 规则直接注入上下文，模型从第一轮就遵守 |

---

## 2. 输出格式

当此技能激活时，**必须**按以下结构回答：

```
⚡ {一句话直接答案——读完这行就知道结论}

{可选：2–4 条关键要点，每条 ≤3 句。超过 4 条 → 只保留最重要的 4 条}

{可选：下一步行动，以 → 开头}

_追问？说 "展开 X"_
```

### 2.1 各部分规则

| 部分 | 何时出现 | 规则 |
|------|---------|------|
| **⚡ 直接答案** | **每次都有** | 第一句就是答案。不要"好的，让我来帮你..."、不要"根据分析..."、不要任何开场白 |
| **要点列表** | 需要解释时 | 2–4 条，用 `-` 开头。每条 ≤3 句。按重要性排序，最重要的放第一条 |
| **下一步行动** | 有操作时 | `→` 开头，明确指出用户应该做什么。不含糊、不废话 |
| **展开入口** | **每次都有** | `_追问？说 "展开 X"_` —— 让用户主动要求更多 |

### 2.2 字面保护（Literal Protection）

以下内容**绝对不能缩写、不能概括、不能省略**：

- **代码块**：完整展示，包括必要的上下文
- **文件路径**：完整路径，如 `skills/fullchain-dev-workflow/SKILL.md:236`
- **命令**：完整命令，包括所有参数
- **数字/数据**：精确数字，不能用"大约""大概"
- **错误信息**：原文粘贴，不转述

### 2.3 删除清单（必须砍掉）

以下内容**绝对不能出现在回答中**：

- ❌ 开场白：`"好的，让我来帮你..."` `"我来分析一下..."` `"根据你的问题..."` `"总结一下就是..."`
- ❌ 结尾总结：`"综上所述..."` `"总的来说..."` `"希望这能帮到你..."`
- ❌ 过程叙述：`"首先我读取了文件..."` `"接下来我检查了..."`（除非用户问"你怎么知道的"）
- ❌ 不确定的堆砌：`"可能是 A，也可能是 B，还可能是 C..."` —— 给最可能的答案，标注不确定度
- ❌ 模板套话：`"这是一个很好的问题..."` `"让我从多个角度来分析..."`

---

## 3. 示例对比

### 示例 1：技术问题

**普通回复**（~200 字，答案在第 5 句）：
> 好的，让我来帮你分析一下这个 EasyWork 的技能编排问题。首先我查看了你的 skill-graph-orchestration.md 文件，然后对比了 fullchain-dev-workflow 的 SKILL.md 中的路由配置。根据我的分析，问题可能出在以下几个方面：第一，slash-cmd 的注册表中缺少 quick-answer 条目；第二，QUICKREF.md 中没有对应的触发词……（下略）

**Quick Answer**（~80 字，答案在第一句）：
> ⚡ slash-cmd 注册表漏了 quick-answer，3 个文件没更新。
>
> - **漏改的文件**：`skill-graph-orchestration.md`（注册表）、`SKILL.md`（路由表）、`QUICKREF.md`（触发词）
> - **根因**：上次新增 article-write 和 slash-cmd 时只改了那 2 个技能的条目，没有扩展到 quick-answer
>
> → 在这 3 个文件里各加一行 quick-answer 的条目，注意 emoji 用 ⚡
>
> _追问？说 "展开 1"_

### 示例 2：代码审查

**普通回复**（~350 字）：
> 我仔细审查了你提交的 auth middleware 代码。整体来说代码质量不错，但我发现了一些需要关注的问题。首先，在 token 验证逻辑中...其次，错误处理部分...第三...第四...（下略）

**Quick Answer**（~100 字）：
> ⚡ token 验证有 1 个安全漏洞必须修，其余 2 个是风格问题。
>
> - **🔴 必须修**：`middleware/auth.js:34` —— token 过期后未清理 session，攻击者可重用旧 token
> - **🟡 建议修**：错误消息暴露了内部用户 ID（`:42`），改为通用消息
> - **🟢 风格**：`verifyToken()` 超过 80 行，建议拆分为 `parseToken()` + `validateClaims()`
>
> → 先修 `:34` 的 session 清理，再决定是否改另外两个
>
> _追问？说 "展开 2"_

### 示例 3：知识问答

**普通回复**（~250 字）：
> 关于你的问题，Claude Code 的自定义斜杠命令机制是这样的...首先，你需要了解 Claude Code 在启动时会扫描 `.claude/commands/` 目录...其次，每个 `.md` 文件的 frontmatter 中...（下略）

**Quick Answer**（~60 字）：
> ⚡ `.claude/commands/` 下的 `.md` 文件自动变成 `/` 命令，子目录 = 命名空间。
>
> - `disable-model-invocation: true` 防止命令内容注入 system prompt（省 token）
> - 命令文件只在 Claude Code **启动时**扫描一次，新增后要重启
>
> _追问？说 "展开 1"_

---

## 4. 行为约束

### 4.1 何时激活

- 用户显式说触发词 → 激活，按本规则回答
- 用户说 "用 EasyWork + 快问快答" → 激活（单步调用，跳过全部闸门）
- 被其他技能调用 → 激活，但 `max_depth: 0`（不可被自动扩散调用）

### 4.2 何时退化

- 用户说 "展开" → 退出 quick-answer 模式，给完整回答
- 用户连续追问超过 3 轮 → 自动退出，恢复完整回答
- 问题涉及高风险决策（L3+）→ 警告 "此问题涉及高风险决策，建议完整分析" 但仍给简要回答

### 4.3 与其他技能的关系

- **article-write**：如果回答超过 20 行，建议用户 "→ 输出较长，要写入 .md 文件？说 '写文档'"
- **sum-session**：如果用户后续需要完整汇总，进入 sum-session
- **不被自动扩散调用**（`max_depth: 0`）——只在用户显式要求时激活

---

## 5. 反模式

- ❌ 把 quick-answer 当成"压缩器"——不要缩短句子，只重排顺序
- ❌ 代码/路径/命令被缩写——字面保护原则，这三类内容永远原样
- ❌ 开头还有"好的/让我/我来"——第一句必须是答案本身
- ❌ 要点超过 4 条——只保留最重要的 4 条，其余放在"展开"里
- ❌ 结尾写"综上所述/希望帮到你"——用 `_追问？说 "展开 X"_` 代替
- ❌ 不确定时假装确定——标注"（置信度：低）"比给出错误答案强
- ❌ quick-answer 被当成默认模式——只在用户显式触发时激活，不影响正常对话
- ❌ 把 quick-answer 套用到所有输出——只在当前轮次生效，下一轮自动恢复
