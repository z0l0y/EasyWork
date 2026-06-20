---
name: code-implement
description: >
  克制化代码实现。在 READ 阶段确认需求后执行。四条铁律：
  注释语言可配置（默认中文）、复用现有模式不许造新轮子、禁止过度设计、不碰范围外代码。
  改最少的代码，做最精准的事。写操作限于当前项目目录内。
allowed-tools: Read, Write, Edit, Search, Grep, Glob, Bash
model: sonnet
version: 2.7
---

# Code Implement（代码实现）

## 前置判断

**必须执行**：READ 阶段产出了明确的修改需求，需要新增或修改代码。

**可以跳过**：纯理解任务、代码已由人类写好只需审查的任务。

## 注释语言配置（🆕 v2.3）

代码注释的默认语言为**中文**。如果项目配置了其他语言，以此处为准：

### 配置方式

编排中枢在 READ 阶段读取 `references/team-policy.md` 中的 `comment_language` 设置：

| 配置值 | 含义 | 行为 |
|--------|------|------|
| `chinese`（默认） | 中文注释 | 所有注释使用中文，解释"为什么这么做" |
| `english` | 英文注释 | 所有注释使用英文，适合国际化团队 |
| `auto` | 自动检测 | Agent 分析项目现有注释语言，跟随主流 |

### 检测规则（auto 模式）

1. 扫描项目中最近 10 次非 AI 提交的注释语言
2. 以多数语言为准
3. 如果中英混用 → 优先中文（因为这是 EasyWork 的发源语言）

## 四条铁律

### 铁律 1：注释说明"为什么"，语言可配置

对每处新增或修改的逻辑，用注释说明"为什么这么做"。注释语言遵循上述 `comment_language` 配置。

```typescript
// ✅ 好注释（中文 — 默认）
// 此处用 findIndex 而非 find，因为 users 列表可能包含已软删除的记录（status=-1），
// 需同时匹配 id 和 status 才能准确定位活跃用户
const idx = users.findIndex(u => u.id === targetId && u.status !== -1);

// ✅ 好注释（英文 — comment_language: english）
// Use findIndex instead of find because users list may contain soft-deleted records
// (status=-1). Must match both id and status to locate the active user.
const idx = users.findIndex(u => u.id === targetId && u.status !== -1);

// ❌ 差注释（任何语言）
// set user name — 没说明为什么，只是翻译了代码
```

### 铁律 2：复用现有模式

- 写新函数前，先搜索项目中是否已有类似功能 → 扩展现有函数，不要新建
- 项目用 `TimeFormatTool.js` 处理日期 → 在里面加方法，别引入 dayjs
- 项目用 class 组件 → 新代码也用 class 组件，别切函数组件
- 项目用回调风格 → 检查 team-policy 是否有迁移计划。有迁移计划 → 用新模式；无计划 → 继续用回调

### 铁律 3：禁止过度设计

- 一行 if-else 能解决的，不引入策略模式
- 不为"可能以后有用"创建抽象
- 函数不超过 50 行，嵌套不超过 4 层
- 让刚入职三天的开发者能看懂，比"优雅"重要

### 铁律 4：边界止步

- 看到旁边代码有明显 bug → 告诉用户，但别自己改
- 看到 import 顺序乱 → 别顺手整理（会让 diff 变脏）
- 看到不统一的代码风格 → 别顺手统一（超出范围）

> **详细实施指导**：代码风格适配、注释规范、错误处理、性能意识的详细指南，见 `references/implementation-guidelines.md`。

## 遇到高耦合时

如果修改 A 文件会导致 B、C、D 连锁崩溃，**立刻停手**：

```
【CODE 阻断 - 高耦合风险】
要改：{文件A} 的 {逻辑}
牵连：文件 B 被 N 个模块引用，改动会影响 {影响面}
选项：
  A) 硬改A，同步修改所有下游（风险：范围大）
  B) 加适配层隔离修改（风险：增加间接层）
  C) 先解耦再改（风险：工作量大）
→ 请选择方案。
```

## 反模式

- ❌ 为了修复一个空指针，顺手把整个模块重构成策略模式
- ❌ 觉得 `TimeFormatTool.js` "太丑"，引入 moment.js 替换——团队不欠你的审美
- ❌ 用 reduce/map/filter 连环套写一行"精妙"代码——这不是炫技场
- ❌ 看到旁边代码少分号，顺手补上——收住你的手
- ❌ 注释写"设置name为John"——这在说废话，要解释为什么设这个名字
- ❌ 在不支持 async/await 的项目中引入 async/await——除非 team-policy 有明确迁移计划
