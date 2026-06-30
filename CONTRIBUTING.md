# 贡献指南

感谢你考虑为 EasyWork 做出贡献！以下是一些帮助你上手的信息。

## 设计哲学

在提交贡献前，请理解 EasyWork 的核心理念：

1. **AI Agent 是用户**，不是人类。指令必须清晰、可执行、无歧义。
2. **U 型注意力曲线** — 最重要的规则放在文件开头和结尾，中间放详细说明。
3. **渐进式披露** — SKILL.md 自包含可执行，references/ 提供深度细节。Agent 不读 references 也能执行，读了能做得更好。
4. **反模式优先** — "禁止做 X"比"应该做 Y"对 AI 约束力更强。
5. **HITL（Human In The Loop）** — 关键技术决策始终由人类拍板，Agent 是建议者而非决策者。

## 项目结构

```text
EasyWork/
├── SKILL.md                     # 技能索引入口（给 Agent 看）
├── README.md                    # 人类阅读的项目说明
├── QUICKREF.md                  # 30 秒速查卡片
├── CHANGELOG.md                 # 版本更新记录
├── TROUBLESHOOTING.md           # 故障排查指南
├── LICENSE                      # MIT
├── install.bat / install.sh     # 安装脚本
├── skill-template/              # 技能模板（创建新技能的起点）
└── skills/
    ├── fullchain-dev-workflow/  # 编排中枢
    │   ├── SKILL.md             #   核心指令（Agent 执行入口）
    │   ├── assets/              #   模板与示例（Agent 复制后填空）
    │   └── references/          #   深度参考（Agent 按需查阅）
    └── {skill-name}/             # 28 个子技能（结构同上）
```

## 如何贡献

### 报告 Bug / 提建议

请确保描述：
- 使用的 AI 平台（Claude Code / Copilot / Cursor）和模型版本
- "期望的行为" vs "实际的行为"
- 触发场景（用户说了什么，Agent 做了什么）
- 如果可能，附上相关对话片段

### 改进现有技能

1. 先理解该技能的 SKILL.md — 它是 Agent 的执行入口
2. 确认你要改的内容属于哪个层级：
   - **核心指令**（必读的） → 放在 SKILL.md 中
   - **模板/示例**（复制填空的） → 放在 `assets/` 中
   - **深度参考**（按需查阅的） → 放在 `references/` 中
3. 保持与其他技能一致的术语和格式

### 创建新技能

1. 复制 `skill-template/` 到 `skills/{your-skill-name}/`
2. 按模板中的指引填写 SKILL.md、assets/、references/
3. 在 `SKILL.md`（索引入口）和编排中枢中添加对新技能的引用
4. 确保新技能的命名、术语、格式与现有技能保持一致

### 提交流程

1. Fork 本项目
2. 创建特性分支（`feat/xxx` 或 `fix/xxx`）
3. 修改完成后，检查：
   - [ ] 所有 md 文件无格式错误
   - [ ] 交叉引用路径正确
   - [ ] 术语与全项目统一
   - [ ] 技能之间的关系没有遗漏（编排中枢的引用、data-contract 的字段）
4. 提交 PR，描述改动内容和原因

## 写作规范

### 面向 AI Agent 的写作

- **命令式语气**："检查 X"、"确保 Y"而非"你应该检查 X"
- **具体而非抽象**："搜索 package.json → scripts → test"而非"找到测试命令"
- **好坏对比**：每个规则最好配一个正面示例和一个反面示例
- **边界清晰**：明确什么在范围内、什么在范围外

### 术语统一

| 中文 | 英文 | 含义 |
|------|------|------|
| 编排中枢 | Orchestrator | 流程调度中心 |
| 挂起 | Suspend | 暂停等待用户 |
| 阻断性问题 | Blocker | 必须修复才能继续 |
| 打卡 | Check off | 逐项确认完成 |
| 人工确认 | HITL | Human In The Loop |
| 裁剪 | Trim | 跳过不需要的步骤 |
| 取舍分析 | Trade-off | 方案代价评估 |
| 异常处理流程 | SOP | 非正常情况的处理步骤 |

### 文件大小指南

- **SKILL.md**：3000-6000 字节。太大 Agent 懒得逐字读，太小缺少执行细节
- **references/**：每个文件 3000-8000 字节。单一主题，便于 Agent 按需定位
- **assets/** 模板：不超过 5000 字节。模板太长 Agent 会跳过部分填空项

## 向后兼容

- `data-contract.md` 中的字段名和类型是稳定的 API。如果要修改，必须：
  1. 增加 `easywork_version` 新版本号
  2. 在 `data-contract.md` 的版本迁移节中记录差异
  3. 确保旧版本的状态快照可以被新版本解析

## 测试你的修改

提交前，在至少一个真实项目中验证：

1. 安装你的修改版本：`./install.sh /path/to/test-project`
2. 启动新对话，分别触发：全链路、单步、半链路三种模式
3. 确认每个步骤的 Checklist 和异常 SOP 正常运作
4. 检查推荐的任务分类是否符合预期
