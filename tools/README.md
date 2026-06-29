# 🧰 EasyWork Tools

> 对话生成的实用工具集 — 手动调用，不被编排中枢自动发现。

## 与 `skills/` 的区别

| | `skills/`（核心流程） | `tools/`（实用工具） |
|---|---|---|
| **定位** | 质量受控的工作流步骤 | 对话中生成的零散工具 |
| **发现方式** | 编排中枢自动发现 + 斜杠命令 | 手动 Read 调用 |
| **质量要求** | 必须有 references/ + 完整 frontmatter | 宽松，允许轻量级 |
| **典型用途** | code-review, code-implement, fullchain-dev-workflow | 一次性脚本、格式转换、特定技术栈工具 |
| **生命周期** | 长期维护，版本迭代 | 按需创建，不用时可归档 |

## 使用方式

1. 在对话中对 Agent 说："把这个功能做成一个工具 skill，放到 tools/ 下面"
2. Agent 自动在 `tools/` 下创建 `SKILL.md`
3. 需要用时手动 Read 调用，或创建斜杠命令指向它
4. 如果工具使用频率高，质量稳定 → 可升级到 `skills/` 核心流程

## 目录结构

```
tools/
├── README.md          ← 当前文件
├── .gitkeep
└── <tool-name>/       ← 每个工具一个目录
    └── SKILL.md       ← 遵循 EasyWork Skill 规范（可简化）
```

## 前端用户示例

- `tools/figma-to-component/` — Figma 设计稿 → 前端组件
- `tools/color-palette-gen/` — 品牌色 → CSS 变量 + Tailwind 配置

## 数据工程师示例

- `tools/sql-formatter/` — SQL 格式化 + 注释标准化
- `tools/pipeline-deploy/` — 数据管道部署检查清单

## DevOps 工程师示例

- `tools/k8s-health-check/` — K8s 集群健康检查
- `tools/terraform-plan-review/` — Terraform 计划审查

---

> **提示**：你也可以在 `.easywork/config.json` 的 `paths.tools` 字段自定义 tools 目录路径。
