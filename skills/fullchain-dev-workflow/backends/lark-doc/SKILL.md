---
name: lark-doc
description: >
  飞书文档后端适配器。将 EasyWork 10 步工作流产出生直接写入飞书文档，
  支持流式追加、Git 链路追踪、飞书画板集成。适用于使用飞书协作的团队。
  v1.1: 报告深度感知(brief/standard/detailed)、MCR闸门验证、流式增量保障强化。
output_format: lark_doc
capabilities: [create_doc, append_blocks, create_whiteboard, share_link, batch_write]
requires_mcp: [lark-cli]
requires_network: true
streaming: true
version: 1.3
---

# Lark Doc Backend（飞书文档后端适配器）

## 后端定位

lark-doc 后端将 EasyWork 工作流产物直接写入飞书文档，替代本地 HTML/Markdown 文件。

**核心价值**：
- 产物直接进入企业协作系统，发送一个飞书链接即可分享
- 支持流式追加——每个步骤完成即写入，团队成员可实时看到进展
- Git 链路追踪独立文档——任务→提交分组→Check→hash→测试 可追溯
- GRAPH 产出可选择嵌入飞书画板

**前置条件**：
- MCP `lark-cli` 已配置且可用
- 飞书 App 有文档创建权限（`docx:document:create`）
- 如使用 Wiki 功能，需 `wiki:node:write` 权限

> **API 参考**：飞书 API 端点、块类型、限流规则等详见 `references/lark-api-quickref.md`。
> Agent 在调用飞书 API 前应先查阅该速查表确认端点用法和限制。

---

## 前置检查

Agent 在初始化此后端时，必须执行：

1. **检查 MCP 可用性**：`lark-cli` MCP 服务是否已连接且正常响应
2. **检查配置**：从 `team-policy.md` 读取飞书配置段：
   - `lark_folder_token`：默认飞书目录（文档创建位置）
   - `lark_wiki_space_id`：知识库空间 ID（可选，如使用 Wiki）
   - `lark_git_tracking_doc_id`：Git 链路追踪母文档 ID（可选）
3. **不可用处理**：
   - MCP 不可用 → 告知用户"飞书 MCP 未连接，降级到 local_html"
   - 配置缺失 → 使用飞书根目录，告知用户可在 team-policy 中配置默认目录
   - 降级后将事件记录到 SUM 产出

---

## create_session_doc

**触发时机**：工作流启动后（或 READ 完成后）。

### Agent 执行指令

1. 确定文档标题：`{任务类型} — {日期} — {简短描述}`
   - 示例："Bug修复 — 2026-06-20 — 修复登录超时"
2. 调用 MCP 创建飞书文档：
   - 通过 `lark-cli` 的工具（如 `create_document`）创建文档
   - 指定 `folder_token`（来自 team-policy 配置或默认）
   - 文档标题为上述格式
3. 获取返回的 `document_id` 和文档 URL
4. 如有 Git 链路追踪需求（任务有代码改动 + GIT 步骤执行），检查 `lark_git_tracking_doc_id`：
   - 存在 → 记录母文档 ID，后续 write_step_output 时追加 git tracking 数据
   - 不存在 → 创建 Git 链路追踪母文档（标题："Git 链路追踪"），将新 doc_id 回写到 team-policy 配置提示
5. 返回：
   - `doc_id` = 飞书 document_id
   - `doc_url` = 飞书文档 URL（`https://{domain}/docx/{document_id}`）
   - `doc_title` = 文档标题

---

## write_step_output

**触发时机**：每个步骤完成后（lark-doc 支持流式追加）。

### Agent 执行指令

1. 将步骤产出按 data-contract 字段格式化为 Markdown（遵守 `references/doc-writing-guide.md`）
2. **🆕 v1.1 流式增量保障**：每步骤产出必须**完整**格式化后追加，**禁止**精简/截断以"节省文档空间"。detailed 模式代码摘录必须保留文件路径和行号
3. 调用飞书 Markdown 转块 API 将内容追加到文档：
   - 通过 `lark-cli` 的 `convert_markdown` 工具或等效调用
   - 追加到文档末尾
4. GIT 步骤特殊处理（见下）
5. 返回 `{ "success": true }`

### 流式追加格式

每步产出的 Markdown 以步骤标题开头：

```markdown
---

## {N}. {步骤名} — {状态}

{步骤产出内容，按各后端共用格式}
```

步骤之间用分割线（`---`）分隔，便于飞书文档中视觉区分。

### GIT 步骤特殊处理

GIT 步骤产出在追加到主文档的同时，还需写入 Git 链路追踪文档：

**流程**：
1. 在主文档中追加 GIT 拆分概要（表格 + 各单元说明）
2. 如果 `lark_git_tracking_doc_id` 存在：
   - 在 Git 链路追踪母文档中追加本次任务的条目
   - 条目结构见 `../../git-split-commit/assets/git-chain-tracking-template.md`
   - 每个 commit unit 包含完整的 Check 清单（初始 unchecked）
3. 如果 `lark_git_tracking_doc_id` 不存在：
   - 在 SUM 产出中提示"Git 链路追踪文档未配置，链路数据已保留在主文档中"

---

## write_final_report

**触发时机**：SUM 步骤完成后。

**🆕 v1.1 新增输入**：
- `report_depth`：深度级别（"brief" | "standard" | "detailed"）
- `report_type`：报告类型（"executive_summary" | "engineering_record"）
- `mcr_gate_result`：MCR 自检闸门结果（detailed 模式必须已通过）
- `streaming_status`：已流式追加的步骤列表

### Agent 执行指令

0. **🆕 v1.1 验证 MCR 闸门**：如果 report_depth=detailed 且 mcr_gate_result.passed=false → **拒绝写入**，返回错误及缺失清单
1. 在文档开头插入目录导航（一级标题列表，飞书 Markdown 转换后的标题会自动生成锚点）
2. 按以下顺序追加（**不替换**已有内容）：
   - 如果 write_step_output 已逐步骤追加 → 只追加 SUM + TALK + SELFCHECK + ASK + 尾注
   - 如果未逐步骤追加（异常情况）→ 追加所有步骤的完整产出 + SUM + TALK + SELFCHECK + ASK + 尾注
3. 🆕 v1.1 report_depth=brief 时：SUM 使用精简格式（每要素1-2句）
4. 🆕 v1.1 report_type=executive_summary 时：在文档开头追加醒目提示 "> 本文为领导层摘要，技术细节请查看对应工程记录"
5. 如有 TALK 产出，追加到 SUM 之后
6. 如有 ASK 确认结果，追加到最后
7. 追加文档尾注：
   ```
   ---
   *本文档由 EasyWork v2.9 自动生成，使用 lark-doc 后端。*
   *报告深度：{report_depth} | 报告类型：{report_type} | 生成时间：{timestamp}*
   ```
8. 返回 `{ "success": true, "doc_url": "{飞书文档URL}" }`

---

## get_share_link

**触发时机**：最终报告写入完成后。

### Agent 执行指令

1. 返回飞书文档链接：
   ```
   {
     "share_url": "https://{domain}/docx/{document_id}",
     "access_level": "team_only"
   }
   ```
2. **提示用户**：分享文档需要在飞书客户端中手动开启分享开关（API 不支持权限设置）

---

## GRAPH 步骤 — 飞书画板集成

当执行 GRAPH 步骤且后端为 lark-doc 时：

### 决策树

```
GRAPH 产出 Mermaid 代码
    │
    ├─ 节点数 ≤15 → Mermaid 代码嵌入飞书文档（fenced code block）
    │               用户可在飞书文档中查看，或用 Mermaid Live Editor 渲染
    │
    ├─ 节点数 >15 → 尝试渲染为图片嵌入文档
    │               （通过 @larksuite/whiteboard-cli 或 mermaid-cli 生成 PNG）
    │
    └─ 飞书画板 → 未来增强。当前建议用户手动将图片上传到飞书画板
```

### Mermaid 嵌入飞书文档

将 Mermaid 代码以 fenced code block 格式通过 Markdown 转块 API 写入文档：

```markdown
## 6. 架构可视化

### Mermaid {diagram_type}

{mermaid 代码块}

### 节点对照表

| 节点 | 代码实体 | 位置 |
|------|---------|------|
{node_mapping 表格行}
```

### 飞书画板（未来增强）

当前飞书画板 API 的 MCP 支持尚不完整。建议方案：
- Agent 提示用户"GRAPH 图已嵌入飞书文档，建议手动创建画板并粘贴图片以提升可读性"
- 后续 MCP 支持完善后，可通过 `board-v1` API 直接创建飞书画板

---

## Git 链路追踪文档操作

### 文档结构

母文档是一个飞书文档，标题为"Git 链路追踪"。每次 EasyWork 任务追加一个新条目。

### 追加条目

GIT 步骤完成后，Agent 在母文档末尾追加：

```markdown
---

## {任务描述} — {日期}

### 提交分组概览

| # | 维度 | 文件数 | 风险 | Check | Commit Hash | 测试 |
|---|------|--------|------|-------|-------------|------|
{每个 unit 一行，Check 和 Commit Hash 初始为空}

### 分组详情

{每个 unit 的详细说明，含 developer_checklist}

### 测试结果

{EXAMINE 步骤的测试数据引用}
```

### 回填 Commit Hash

用户执行 commit 后，在后续会话中 Agent 可以更新 Git 链路追踪文档中的 hash 列（通过 `update_blocks` 或重新写入）。

**当前限制**：飞书文档 API 不支持原地更新表格单元格。当前方案是在 Git 链路追踪文档中逐次追加，每个任务条目独立。

---

## 错误处理

| 场景 | 处理 |
|------|------|
| MCP 不可用 | 告知用户 → 降级 local_html → SUM 中记录 |
| 文档创建失败（权限不足） | 检查 App 权限配置 → 告知用户需要 docx:document:create 权限 |
| 块追加失败（文档被锁定） | 重试 1 次 → 如仍失败，剩余内容降级到 local_html |
| Markdown 转换 API 失败 | 改用原始块 API（手动构造 block JSON）重试 |
| 速率限制（HTTP 429） | 等待 1 秒重试，最多 3 次 → 仍失败则降级 |
| 网络超时 | 等待 3 秒重试 1 次 → 仍失败则降级到 local_html |
| Git 追踪文档不可用 | 在主文档中保留链路数据 → SUM 中注明"Git 追踪文档未配置" |

### 降级时的用户通知

```
⚠️ 飞书后端写入失败：{具体原因}
已降级到 local_html 后端，产物保存在 .claude/easywork/ 目录。
{已成功写入飞书的部分} 保留在飞书文档中，其余内容在 HTML 文件中。
```

---

## 反模式

- ❌ 飞书 MCP 不可用但 Agent 静默降级——必须告知用户
- ❌ 创建文档时不指定 folder_token——文档散落在飞书根目录
- ❌ 文档标题用纯技术术语——标题应包含任务类型 + 日期 + 业务简述
- ❌ GIT 数据不写入链路追踪文档——链路断裂
- ❌ 流式追加时忘记步骤间分割线——文档变成一大坨难读的文本
- ❌ 降级后不记录降级原因——用户回顾时不知道为什么产物在本地
- ❌ API 调用前不检查 MCP 可用性——白白浪费上下文
- ❌ v1.1：write_final_report 覆盖/替换已流式追加的步骤详情——文档应从前到后完整可读
- ❌ v1.1：流式追加时精简步骤产出以"节省飞书文档空间"——MCR 要求的内容一项不能少
- ❌ v1.1：detailed 模式下 MCR 未通过仍写入——必须先回退补充再写入
