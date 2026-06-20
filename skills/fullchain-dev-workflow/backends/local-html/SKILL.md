---
name: local-html
description: >
  本地 HTML 产物后端。将 10 步工作流产出生成为自包含 HTML 文件。
  EasyWork 默认后端，所有环境下均可用，无需网络或额外依赖。
  v1.1: 报告深度感知(brief/standard/detailed)、MCR闸门验证、完整步骤详情增量恢复。
output_format: html
capabilities: [create_doc, append_blocks, share_link, full_detail_restore]
requires_mcp: []
requires_network: false
streaming: false
version: 1.2
---

# Local HTML Backend（本地 HTML 产物后端）

## 后端定位

local_html 是 EasyWork 的默认产物后端。当用户未指定输出格式、team-policy 未配置其他后端时，使用此后端。

产物为单个自包含 HTML 文件，保存在 `.claude/easywork/` 目录下。

---

## 前置条件

- 文件系统可写（项目目录内）
- 无网络依赖
- 无 MCP 依赖

---

## create_session_doc

**触发时机**：工作流启动后、第一个产出步骤前。

### Agent 执行指令

1. 确保 `.claude/easywork/` 目录存在（不存在则 `mkdir -p`）
2. 生成文件名：`EasyWork_Report_{YYYYMMDD_HHmmss}.html`
3. 文件路径：`{项目根目录}/.claude/easywork/{文件名}`
4. 返回：
   - `doc_id` = 文件绝对路径
   - `doc_url` = 文件路径（本地文件无 URL，可填路径）
   - `doc_title` = 文件名

---

## write_step_output

**触发时机**：每个步骤完成后。

local_html 后端**不支持流式追加**（streaming: false）。每步骤产出在内存中保留**完整结构化数据**。

**🆕 v1.1 增量保障**：
- 每步骤完成后，Agent 将步骤产出**完整暂存**（按 data-contract 完整字段，不可精简为摘要）
- 被跳过的步骤：显式标记 [skip] 及理由
- 最终 write_final_report 将所有暂存的完整步骤产出一次性写入 HTML
- **禁止**：因上下文紧张而精简步骤产出。如果上下文确实不足 → 使用策略二（子Agent隔离）或策略三（状态快照），但不丢失步骤详情

### Agent 执行指令

1. 将步骤产出按 data-contract 字段**完整暂存**（非摘要、非浓缩）
2. 不做文件写入（等待 write_final_report 批量写入）
3. 返回 `{ "success": true }`

---

## write_final_report

**触发时机**：SUM 步骤完成后。

**🆕 v1.1 新增输入**：
- `report_depth`：深度级别（"brief" | "standard" | "detailed"）
- `report_type`：报告类型（"executive_summary" | "engineering_record"）
- `mcr_gate_result`：MCR 自检闸门结果
- `streaming_status`：流式状态（对 local_html 始终为 steps_streamed=[]）

### Agent 执行指令

0. **🆕 v1.1 验证 MCR 闸门**：如果 report_depth=detailed 且 mcr_gate_result.passed=false → **拒绝写入**，返回错误及缺失清单
1. 读取 HTML 骨架：`skills/fullchain-dev-workflow/assets/html-skeleton.html`
2. 按格式化规范将各步骤产出填入骨架：
   - **🆕 v1.1 关键变更**：每个已执行步骤的**完整产出**必须填入对应占位符。即使上下文紧张，也不可用摘要替代步骤详情
   - brief 模式：步骤卡片使用精简模板(仅关键结论)
   - standard/detailed 模式：步骤卡片使用完整模板(含所有 data-contract 字段)
   - 🆕 v1.1 report_type=executive_summary 时：在报告顶部添加醒目提示条"领导层摘要 — 技术细节请联系研发团队"
   - 🆕 v1.1 report_depth 和 report_type 写入报告元数据区
   - 替换 `{{TASK_TYPE}}`、`{{RISK_LEVEL}}`、`{{TIMESTAMP}}` 等元数据占位符
   - 为每个步骤生成对应的 HTML 卡片内容，替换 `{{READ_CONTENT}}`、`{{CODE_CONTENT}}` 等
   - 被跳过的步骤：保留 `{{STEP_SKIP_BLOCK}}` 注释标记，填入跳过理由
   - 生成进度条 HTML，替换 `{{PROGRESS_BAR}}`
   - 生成跳过步骤汇总，替换 `{{SKIPPED_STEPS}}`
3. **写入前安全检查（v2.4 延续）**：
   - ⛔ HTML 注入防护：所有 `{{PLACEHOLDER}}` 替换值中的 `<` `>` `"` `'` `&` 必须做 HTML 实体编码
   - ⛔ 敏感信息脱敏：检查并移除 Token/密钥/密码/内部 URL/大段源码(>30行)/手机号/邮箱/帐号/数据库连接串
   - ⛔ Mermaid CDN：使用 `https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js`，固定版本
4. **写作规范检查**：遵守 `references/doc-writing-guide.md`：
   - 不使用反引号包裹文件名/命令名
   - 中文业务复盘口吻，段落自然
   - 标题下最多 4 个子标题
   - 表格仅用于结构化信息
5. 写入文件到 `doc_id` 对应路径
6. 返回 `{ "success": true, "doc_url": "{文件路径}", "report_depth": "...", "report_type": "..." }`

---

## get_share_link

**触发时机**：最终报告写入完成后。

### Agent 执行指令

本地 HTML 文件无可公开分享的 URL。返回文件路径作为引用。

```
{ "share_url": "{文件绝对路径}", "access_level": "local_only" }
```

---

## 错误处理

| 场景 | 处理 |
|------|------|
| 目录创建失败 | 报告错误，尝试写入当前工作目录 |
| 文件写入失败（权限不足） | 报告错误路径，要求用户检查权限 |
| 磁盘空间不足 | 报告错误，建议清理空间 |

---

## 反模式

- ❌ 跳过 HTML 实体编码导致 XSS 风险
- ❌ 不执行脱敏自检就直接保存
- ❌ 修改 html-skeleton.html 的结构（应在本后端中覆盖格式，不动骨架）
- ❌ 生成 HTML 时使用外部 CSS/字体/追踪脚本
- ❌ v1.1：write_final_report 省略步骤详情只写 SUM 摘要——非流式后端必须恢复全部步骤完整产出
- ❌ v1.1：因上下文紧张而精简步骤产出——完整暂存，不丢细节。上下文不足用子Agent或状态快照
- ❌ v1.1：detailed 模式下 MCR 未通过仍写入——必须先回退补充再写入
