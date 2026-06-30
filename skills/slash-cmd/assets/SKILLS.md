# EasyWork 技能目录总览

> 28 个技能 · 7 个类别 · 29 条斜杠命令。输入 `/easywork:` 后按 **Tab** 自动补全。

## 🧠 学习类（Learning）

| 命令 | 技能 ID | 做什么 | 试一下 |
|------|---------|--------|--------|
| `/easywork:paper` | read-paper | 论文阅读→十段报告（速览/背景/方法/实验/局限/分享） | `/easywork:paper https://arxiv.org/abs/...` |
| `/easywork:project` | read-project | 项目架构理解（结构→模块→依赖→技术栈） | `/easywork:project src/` |
| `/easywork:trace` | trace-code | 函数调用链追踪（入口→路径→分支→数据流） | `/easywork:trace handlePayment` |
| `/easywork:radar` | tech-radar | 技术动态扫描（点/面/体三级粒度） | `/easywork:radar 深扫 MCP 协议` |
| `/easywork:coverage` | test-coverage | 测试覆盖率分析（五维覆盖+盲区检测） | `/easywork:coverage src/payment/` |
| `/easywork:learn` | learn-from-zero | 从零学习——四级解释阶梯（ELI5→专家）+ 图解 + 知识树 | `/easywork:learn Docker` |
| `/easywork:decompose` | requirement-decompose | 需求拆解——六阶段流水线（理解→拆解→边界→依赖→验收→检查清单） | `/easywork:decompose 用户邀请功能` |

## ✏️ 开发类（Development）

| 命令 | 技能 ID | 做什么 | 试一下 |
|------|---------|--------|--------|
| `/easywork:requirements` | read-requirements | 五要素需求说明+完成定义+可追溯矩阵 | `/easywork:requirements 用户故事...` |
| `/easywork:implement` | code-implement | 需求文档→代码变更 | `/easywork:implement 实现登录接口` |
| `/easywork:review` | code-review | 七维度代码审查（反合理化+供应链检查） | `/easywork:review src/auth/` |
| `/easywork:retro` | talk-retro | 5-Whys 根因分析+Trade-offs | `/easywork:retro 为什么支付模块反复出bug` |
| `/easywork:selfcheck` | self-check | 四阶段 CTO 盘问+认知缺口 | `/easywork:selfcheck 我刚改的登录逻辑` |
| `/easywork:graph` | graph-fullchain | Mermaid 架构图+节点对照表 | `/easywork:graph 支付系统` |
| `/easywork:diagram` | diagram-generator | 🆕 多引擎图表生成（Figma/Excalidraw/D2/Draw.io/Mermaid） | `/easywork:diagram 架构图 微服务系统` |
| `/easywork:sum` | sum-session | 六要素总结（背景→发现→问题→解决→效果→展望） | `/easywork:sum 本次迭代` |
| `/easywork:compare` | tech-compare | 技术方案选型对比（多维度+评分矩阵+推荐） | `/easywork:compare React vs Vue` |
| `/easywork:git` | git-split-commit | 智能提交拆分（语义分组+Conventional Commits） | `/easywork:git 拆分最近的改动` |

## ✅ 质量类（Quality）

| 命令 | 技能 ID | 做什么 | 试一下 |
|------|---------|--------|--------|
| `/easywork:checklist` | checklist | 开发清单审计（Pre-flight 就绪+Audit 交付） | `/easywork:checklist 开发前检查` |
| `/easywork:test` | api-test | 接口联调测试（curl/契约/自动化验证） | `/easywork:test POST /api/users` |
| `/easywork:examine` | examine-quality | 测试执行+质量验证（自动跑测试+覆盖检查） | `/easywork:examine 验证改动` |
| `/easywork:ask` | ask-change-questions | 六维度人工确认（HITL 终极闸门） | `/easywork:ask 确认上线变更` |

## 📝 内容类（Content）

| 命令 | 技能 ID | 做什么 | 试一下 |
|------|---------|--------|--------|
| `/easywork:article` | article-write | Agent 输出→格式化 Markdown 文档（6 种模板） | `/easywork:article 把刚才的分析写成报告` |
| `/easywork:quick` | quick-answer | 快问快答——TL;DR 前置+结构化压缩 | `/easywork:quick 什么是 CAP 定理` |

## 🔗 编排入口（Orchestration）

| 命令 | 模式 | 做什么 | 试一下 |
|------|------|--------|--------|
| `/easywork:pipeline` | 🔗 线模式 | 7 条内置流水线+动态 DAG 编排 | `/easywork:pipeline 先理解项目，再追踪支付` |
| `/easywork:meta` | 🌐 网模式 | Meta-Orchestrator 自治扩散+深度分析 | `/easywork:meta 支付模块能不能扛住双11` |
| `/easywork:scenario` | 🎨 场景模式 | 场景画板——list/view/run/create/edit 场景 | `/easywork:scenario run new-project-handover` |
| `/easywork:canvas` | 🖼 可视化 | 打开拖拽式场景编辑器（浏览器） | `/easywork:canvas` |
| `/easywork:slash-cmd` | 💻 命令管理 | 创建/更新/删除斜杠命令+技能索引 | `/easywork:slash-cmd sync` |

## 🔧 基础设施（Infrastructure）

| 命令 | 技能 ID | 做什么 | 试一下 |
|------|---------|--------|--------|
| `/easywork:knowledge` | knowledge-base | 知识库管理（搜索/存储/统计/维护+MCP Server） | `/easywork:knowledge search HBase` |

---

## 流水线组合速查

| 流水线名 | 命令示例 |
|---------|---------|
| 🔭 扫描→深读 | `/easywork:pipeline 扫技术动态并深读` |
| 🏗️ 理解→追踪 | `/easywork:pipeline 理解项目并追踪` |
| 🧪 覆盖→补测 | `/easywork:pipeline 分析覆盖率并补测试` |
| 🏗️🔬 全理解 | `/easywork:pipeline 全面理解这个项目` |

## 自然语言对照

不知道用哪个命令？直接用自然语言描述——编排中枢会自动匹配技能：

| 你说的话 | 自动匹配 |
|---------|---------|
| "帮我看看这篇论文" | 📖 read-paper |
| "这个项目的架构是怎样的" | 📐 read-project |
| "追踪一下这个函数的调用链" | 🔬 trace-code |
| "最近 AI Agent 有什么新东西" | 🛰️ tech-radar |
| "测试覆盖率怎么样" | 🧪 test-coverage |
| "对比一下这两个技术方案" | ⚖️ tech-compare |
| "帮我测试一下这个接口" | 🔌 api-test |
| "这个概念我不太懂" | 🧠 learn-from-zero |
| "说重点" | ⚡ quick-answer |

---

*命令文件位于 `.claude/commands/easywork/`，技能定义位于 `skills/`。*
*新增/删除技能后运行 `/easywork:slash-cmd` 或说"更新命令"同步命令文件。*
