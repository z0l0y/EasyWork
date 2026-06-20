---
name: local-html
description: >
  本地 HTML 产物后端。将 9 步工作流产出生成为自包含 HTML 文件。
  EasyWork 默认后端，所有环境下均可用，无需网络或额外依赖。
output_format: html
capabilities: [create_doc, append_blocks, share_link]
requires_mcp: []
requires_network: false
streaming: false
version: 1.0
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

local_html 后端**不支持流式追加**。所有步骤产出在内存中暂存，由 `write_final_report` 一次性写入。

如果需要渐进式保存（防止上下文丢失），可在每步完成后调用 `write_final_report` 做增量覆盖写入。

### Agent 执行指令

1. 将步骤产出按 data-contract 字段暂存
2. 不做文件写入（等待 write_final_report 批量写入）
3. 返回 `{ "success": true }`

---

## write_final_report

**触发时机**：SUM 步骤完成后。

### Agent 执行指令

1. 读取 HTML 骨架：`skills/fullchain-dev-workflow/assets/html-skeleton.html`
2. 按 `skills/fullchain-dev-workflow/assets/html-output-template.md` 的格式化规范，将各步骤产出填入骨架：
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
6. 返回 `{ "success": true, "doc_url": "{文件路径}" }`

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
