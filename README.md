# EasyWork — AI 全链路开发工作流技能包

## 这是什么？

EasyWork 是一套为 AI 编码助手（Claude Code、Cursor、GitHub Copilot）设计的标准化开发工作流。
它解决的核心问题是：**AI 写代码太快、太不可控**——它们跳过理解直接改代码、顺手重构无关模块、
不跑测试直接交付。EasyWork 通过**按需裁剪的 9 步工作流 + 全局异常 SOP + 人工确认闸门**，
让 AI 从"散漫的代码生成器"变成"严格按流程走的虚拟结对程序员"。

### v2.1 核心改进：智能裁剪 + HTML 输出 + 断点续传

- **任务分类器**：7 种任务类型（纯理解/纯审查/微调/Bug修复/重构/功能开发/纯文档），自动裁剪步骤
- **默认 HTML 输出**：用户未指定输出格式时，自动生成自包含的精美 HTML 报告
- **断点续传**：支持输出 JSON 状态快照，下次对话从中断处恢复
- **意图路由**：根据用户关键词（"帮我看看"/"修一下"/"加一个"）自动判断任务类型
- **术语统一**：全项目使用标准中文术语（异常处理流程/人工确认/检查清单等）

v1.0 强制所有任务走完 9 步，这很安全但也很烦——改一个文案不需要画架构图。
**v2.0 内置了任务分类器**：启动时先判断任务类型（纯理解/微调/Bug修复/功能开发等），
然后自动建议要执行和跳过的步骤。用户一键确认后，只走真正需要的流程。

## 工作流：9 步 → 按需裁剪

```
用户输入 → [任务分类器] → 确认裁剪方案 → 执行裁剪后的步骤
```

| 步骤 | 技能 | 核心职责 | Bug修复 | 功能开发 | 微调 | 纯理解 |
|------|------|---------|--------|---------|------|--------|
| 1 | READ | 理解需求（文档/图片/日志/代码） | ✅ | ✅ | ✅ | ✅ |
| 2 | CODE | 克制编码（中文注释/复用模式） | ✅ | ✅ | ✅ | ⏭️ |
| 3 | REVIEW | 六维度自审查 | ✅ | ✅ | ✅ | ⏭️ |
| 4 | EXAMINE | 跑测试/补测试 | ✅ | ✅ | ⏭️ | ⏭️ |
| 5 | GIT | 拆分提交（按维度） | ✅ | ✅ | ✅ | ⏭️ |
| 6 | GRAPH | Mermaid 图表 | ⏭️ | ✅ | ⏭️ | ✅ |
| 7 | SUM | 六要素总结 | ✅ | ✅ | ⏭️ | ✅ |
| 8 | TALK | 5-Whys 复盘 | ✅ | ⏭️ | ⏭️ | ⏭️ |
| 9 | ASK | 人工确认 | ✅ | ✅ | ⏭️ | ⏭️ |

> 上表是**默认建议**。用户可以随时追加或跳过步骤，Agent 不会强制执行不必要的流程。

## 核心设计原则

### 1. 任务分类前置（v2.0）
启动时先判断"这到底是个什么任务"（纯理解/纯审查/微调/Bug修复/重构/功能开发），再决定走哪些步骤。
改文案不需要架构图，看代码不需要写测试。**流程服务于任务，而非任务迁就流程。**
新增了回退循环限制（最多 3 轮）和步骤间数据传递契约，防止 Agent 在某个环节无限循环。

### 2. HITL（Human In The Loop）
三个强制人类确认点：READ（需求不确定时）、GIT（拆分方案确认）、ASK（最终上线确认）。
其他步骤遇到异常时挂起询问。Agent 的决策权和技术能力被尊重，但**否决权和最终判断权始终在人类手中**。

### 3. 异常处理 SOP
每个步骤都有标准异常处理流程：停止 → 描述问题 → 提供选项 → 等待人类指示 → 继续。
**严格禁止 Agent 在不确定时自行猜测。**

### 4. Checklist 打卡
每个步骤都有结构化 Checklist，Agent 逐项确认后打钩。长流程任务中有效防止遗漏。

### 5. 反模式显式化
每个技能不仅有"应该做什么"，更有"禁止做什么"。研究表明，AI 对"不要做 X"的遵循度高于"要做 Y"。

## 安装到 Claude Code

在目标项目的 `CLAUDE.md` 中添加：

```markdown
# EasyWork 全链路工作流
当用户需要进行代码开发、Bug 修复、代码审查或需求分析时，
加载 F:\AIG\EasyWork\skills\fullchain-dev-workflow\SKILL.md
并严格遵循其任务分类与流程编排规则。

## 可单独调用的子技能
- 需求理解: F:\AIG\EasyWork\skills\read-requirements\SKILL.md
- 代码实现: F:\AIG\EasyWork\skills\code-implement\SKILL.md
- 代码审查: F:\AIG\EasyWork\skills\code-review\SKILL.md
- 质量验证: F:\AIG\EasyWork\skills\examine-quality\SKILL.md
- 提交拆分: F:\AIG\EasyWork\skills\git-split-commit\SKILL.md
- 图表绘制: F:\AIG\EasyWork\skills\graph-fullchain\SKILL.md
- 总结报告: F:\AIG\EasyWork\skills\sum-session\SKILL.md
- 深度复盘: F:\AIG\EasyWork\skills\talk-retro\SKILL.md
- 人工确认: F:\AIG\EasyWork\skills\ask-change-questions\SKILL.md
```

也可以将 `skills/` 目录复制到 `.claude/skills/` 下，Claude Code 会自动发现项目级 skills。

## 安装到其他平台

### GitHub Copilot
在 `.github/copilot-instructions.md` 中引用上述子技能路径和关键约束（中文注释、复用模式等）。

### Cursor / Windsurf
在 `.cursorrules` 或 `.windsurfrules` 中定义工作流规则，引用 EasyWork 的 skills 路径。

## 使用方式

**全链路**：触发 fullchain-dev-workflow → Agent 输出任务分类和裁剪方案 → 你确认 → Agent 按裁剪后的流程执行。

**单步**：直接说"帮我 review 下这段代码" → Agent 加载 code-review 技能。

**半链路**："代码已写好，从 REVIEW 开始走后续" → Agent 从步骤 3 开始。

## 项目结构

```
EasyWork/
├── README.md                          # 本文件
├── SKILL.md                           # 技能索引入口
└── skills/
    ├── fullchain-dev-workflow/        # 🔗 编排中枢（任务分类 + 步骤裁剪 + 流程编排）
    │   ├── SKILL.md                   #   核心行为指令
    │   ├── assets/
    │   │   ├── output-template.md     #   全链路输出模板
    │   │   └── walkthrough-example.md #   🆕 2个端到端完整示例
    │   └── references/
    │       ├── acceptance-gates.md    #   每步验收关卡
    │       └── data-contract.md       #   🆕 步骤间数据传递契约
    ├── read-requirements/             # 📖 步骤1：多态输入 → 结构化需求
    ├── code-implement/                # ⌨️ 步骤2：克制编码（中文注释/复用/反炫技）
    ├── code-review/                   # 🔍 步骤3：六维度自审查
    ├── examine-quality/               # 🧪 步骤4：测试执行与质量验证
    ├── git-split-commit/              # 📦 步骤5：多维提交拆分（HITL 关键环节）
    ├── graph-fullchain/               # 📊 步骤6：Mermaid/飞书 可视化图表
    ├── sum-session/                   # 📝 步骤7：六要素结构化总结
    ├── talk-retro/                    # 🔬 步骤8：5-Whys 根因分析 + Trade-offs
    └── ask-change-questions/          # ✅ 步骤9：人工确认问询（HITL 终极闸门）
```

每个 skill 目录包含：
- `SKILL.md` — 核心行为指令（前置条件 + 执行流程 + 反模式 + 异常SOP）
- `assets/` — 标准化输出模板
- `references/` — 深度参考指南（Agent 按需查阅，不占常驻上下文）

## 常见问题

**Q: 必须走 9 步吗？**
A: 不。v2.0 的任务分类器会根据任务类型自动建议裁剪方案。改一个文案可能只需要 READ + CODE + REVIEW。
但涉及核心逻辑的 Bug 修复和功能开发，强烈建议走完整流程。

**Q: AI 不遵守规则怎么办？**
A: 每个技能都有反模式清单（Never Do This），这些"禁止"指令对 AI 的约束力比"应该"更强。
如果 AI 偏离，可以直接说"遵守当前 skill 的反模式清单"来纠正。

**Q: 第一次使用，从哪里开始？**
A: 先看 `skills/fullchain-dev-workflow/assets/walkthrough-example.md`，里面有"修 Bug"和"纯理解代码"两个完整的端到端示例，展示了从任务分类到最终确认的全过程。看完就能上手。

**Q: 上下文满了怎么办？**
A: EasyWork 内置了四级上下文管理策略（🟢正常→🟡预警→🟠警戒→🔴危急）。
默认采用**单技能加载模式**——只加载当前步骤的 SKILL.md，而非一次性加载全部 9 个。
每一步完成后自动保存 JSON 状态快照，你可以随时 `/clear` 再粘贴快照从中断处继续。
如果某步骤特别重（大量测试、大量文件搜索），Agent 会主动建议拆分到子 Agent 执行。

**Q: 可以和现有项目规则共存吗？**
A: 可以。EasyWork 是叠加在现有规则（CLAUDE.md、ESLint 等）之上的工作流层，不会冲突。
相反，EasyWork 会在 READ 阶段主动读取这些规则作为约束条件。

**Q: 如何自定义某个步骤？**
A: 直接编辑对应 skill 的 SKILL.md。每个 skill 是独立文件，修改一个不影响其他。
