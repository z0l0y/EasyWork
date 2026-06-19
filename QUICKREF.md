# EasyWork 快速参考卡片

> 30 秒看懂怎么用。详细内容见各技能 SKILL.md 和 `walkthrough-example.md`。

## 触发方式

| 你说的话 | Agent 做什么 |
|---------|-------------|
| "帮我修一下 XX bug" / "实现 XX 功能" | → 全链路（分类 → 裁剪 → 执行） |
| "帮我看下这段代码在干嘛" | → 纯理解（只走 READ+GRAPH+SUM） |
| "帮我 review 下这段代码" | → 纯审查（只走 READ+REVIEW） |
| "帮我画下这个模块的流程图" | → 单步 GRAPH |
| "帮我拆分下这次提交" | → 单步 GIT |

## 任务类型 → 步骤裁剪

| 类型 | 步骤 |
|------|------|
| 🔍 纯理解 | READ → GRAPH → SUM |
| 🔎 纯审查 | READ → REVIEW |
| 📝 纯文档 | READ → CODE → REVIEW → GIT → SUM → ASK |
| ⚡ 微调 | READ → CODE → REVIEW → GIT |
| 🐛 Bug修复 | READ → CODE → REVIEW → EXAMINE → GIT → SUM → TALK → ASK |
| 🔧 重构 | READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → TALK → ASK |
| 🚀 功能开发 | READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → ASK（8步，跳过TALK） |

## 每步产出

| 步骤 | 产出物 |
|------|--------|
| READ | 五要素需求说明（目标/范围/约束/验收/不做） |
| CODE | 变更记录（文件清单 + 改动原因 + 影响面） |
| REVIEW | 审查报告（六维度扫描结果 + 问题清单） |
| EXAMINE | 质量报告（测试命令 + 结果 + 新增测试） |
| GIT | 拆分方案（按维度拆为多提交单元） |
| GRAPH | Mermaid 图表 + 节点对照表 |
| SUM | 六要素总结（背景→发现→问题→解决→效果→展望） |
| TALK | 5-Whys 追溯 + Trade-offs + 工程规范 |
| ASK | 六维度确认清单（需用户逐项确认） |

## 上下文满了怎么办

| 级别 | 操作 |
|------|------|
| 🟢 60%以下 | 正常执行 |
| 🟡 60-80% | 精简输出，每步后问"继续？" |
| 🟠 80-95% | 保存状态快照 → `/clear` → 粘贴快照恢复 |
| 🔴 95%以上 | 强制暂停，保存快照，等 `/clear` |

- **核心原则**：只加载当前步骤的 SKILL.md，不一次性加载全部
- **恢复方式**：每步完成自动输出 JSON 快照，清上下文后粘贴即可从中断处继续

## 四条救命规则

1. **不确定就挂起**：任何技术决策没有 100% 把握 → 停止 → 描述问题 → 给出选项 → 等用户指示
2. **回退不超 3 次**：CODE↔REVIEW 来回到第 4 轮 → 挂起，可能有更深层问题
3. **默认输出 HTML**：用户没指定输出格式 → 生成 `.claude/easywork/EasyWork_Report_{时间}.html`
4. **每步自检必填字段**：每步结束对照 data-contract 检查产出，缺失立即补全

## 🆕 v2.2 新特性

| 特性 | 怎么用 |
|------|--------|
| **干跑预览** | 中高风险任务自动先出预览，你说"执行"才开始 |
| **步骤自检** | 每步结束自动对照 data-contract 检查必填字段 |
| **交叉审查** | REVIEW 后自动切换视角做二次安全抽查 |
| **JSONL 日志** | 每步追加 `.claude/easywork/workflow.log.jsonl` |
| **模型分层** | 不同步骤推荐不同模型（Haiku/Sonnet/Opus） |
| **成熟度 L1/L2/L3** | 团队可按阶段选装 4/7/10 个技能 |

## 项目文件导航

| 想看什么 | 去这里 |
|---------|--------|
| 新手入门，端到端示例 | `skills/fullchain-dev-workflow/assets/walkthrough-example.md` |
| 完整输出模板 | `skills/fullchain-dev-workflow/assets/output-template.md` |
| HTML 输出格式规范 | `skills/fullchain-dev-workflow/assets/html-output-template.md` |
| HTML 骨架（可直接复制） | `skills/fullchain-dev-workflow/assets/html-skeleton.html` |
| 步骤间数据契约 | `skills/fullchain-dev-workflow/references/data-contract.md` |
| 每步验收标准 | `skills/fullchain-dev-workflow/references/acceptance-gates.md` |
| 语言/框架适配速查 | `skills/fullchain-dev-workflow/references/language-matrix.md` |
| 渐进式成熟度 L1/L2/L3 | `skills/fullchain-dev-workflow/references/maturity-levels.md` |
| 编排引擎机制（DAG/自检/日志） | `skills/fullchain-dev-workflow/references/orchestration-engine.md` |
| JSONL 日志分析 | `skills/fullchain-dev-workflow/references/log-analysis-guide.md` |
| 安装脚本 | `install.bat` (Win) / `install.sh` (Unix) |
| 故障排查 | `TROUBLESHOOTING.md` |
| 版本历史 | `CHANGELOG.md` |
| 创建自定义技能 | `skill-template/` |
