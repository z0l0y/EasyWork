# 更新日志

EasyWork 的所有重要变更记录。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [2.1.0] — 2026-06-19

### 新增
- 一键安装脚本（`install.bat` for Windows, `install.sh` for Unix）
- HTML 骨架文件（`html-skeleton.html`）— Agent 可直接复制填空而非从头生成
- 故障排查与自救指南（`TROUBLESHOOTING.md`）
- 语言/技术栈适配速查（`references/language-matrix.md`）
- 功能开发端到端示例（walkthrough 新增示例 3）
- ASK 快速模式 — 轻量任务只需确认安全+回滚 2 个维度
- README 新增 Mermaid 工作流图、详细分平台安装指南、各平台功能对比表
- `LICENSE`（MIT）、`CHANGELOG.md`、`CONTRIBUTING.md`
- 技能模板（`skill-template/`）— 用户可据此创建自定义技能

### 修复
- 编排中枢 `SKILL.md` 中编号错误：两个 §4 已修正为 §4 和 §5，后续编号顺延
- 上下文管理 §3 中对状态快照的交叉引用更新为正确的节号

### 变更
- README 安装指南从 3 句简写扩展为分平台详细指南（含功能降级说明）
- `data-contract.md` 新增版本兼容性声明（§版本迁移）
- 编排中枢增引 `language-matrix.md` 和 `html-skeleton.html` 作为按需查阅资源

---

## [2.0.0] — 2026-06-18

### 新增
- **任务分类器**（任务分类器 + 步骤跳过机制）：7 种任务类型（纯理解/纯审查/纯文档/微调/Bug修复/重构/功能开发），自动建议裁剪方案
- **默认 HTML 输出**：用户未指定格式时自动生成自包含 HTML 报告（`html-output-template.md`）
- **断点续传**：JSON 状态快照机制，支持跨对话恢复
- **上下文管理策略**：四级预警（🟢→🟡→🟠→🔴）+ 单技能加载模式 + 精简模式
- **意图路由表**：根据用户关键词自动判断任务类型
- **回退循环限制**：CODE↔REVIEW 最多 3 轮
- **步骤间数据契约**（`data-contract.md`）：定义每步最小必填字段
- **端到端示例**（`walkthrough-example.md`）：Bug修复 + 纯理解 2 个完整场景
- **快速参考卡片**（`QUICKREF.md`）

### 变更
- 编排中枢从简单顺序调用重写为完整的任务分类 + 流程编排引擎
- 所有子技能 SKILL.md 重写（清理前版本中损坏的内容）
- 反模式章节全面强化（"禁止做"指令比"应该做"更有效）

### 移除
- v1.0 中"所有任务强制走 9 步"的硬性规则

---

## [1.0.0] — 2026-06-17

### 新增
- 初始版本：9 步全链路工作流（READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → TALK → ASK）
- 6 维度代码审查（正确性/安全性/兼容性/可维护性/性能/可观测性）
- 测试驱动质量验证（找→跑→补→修→重跑至全绿）
- 4 维度提交拆分（配置/核心逻辑/UI/测试）
- Mermaid 可视化图表（流程图/时序图/架构图）
- 5-Whys 根因分析 + Trade-offs 取舍
- 6 维度人工确认（HITL 最终闸门）
- 全局异常处理 SOP + Checklist 打卡机制
- Chinese 注释约束 + 反模式显式化
