# 可插拔产物后端（Output Backends）

> **🆕 v2.5**：EasyWork 产物输出不再硬编码为 HTML。通过可插拔后端适配器，支持 local_html / markdown / lark_doc 等多种格式。
> 团队可按需扩展（Notion、Confluence、飞书 Wiki 等），无需修改编排中枢核心文件。

---

## 1. 后端发现机制

Agent 扫描 `skills/fullchain-dev-workflow/backends/*/SKILL.md`，读取每个后端 SKILL.md 的 YAML frontmatter：

```yaml
---
name: lark-doc
description: 飞书文档后端 — 产物直接写入飞书
output_format: lark_doc
capabilities: [create_doc, append_blocks, create_whiteboard, share_link, batch_write]
requires_mcp: [lark-cli]
requires_network: true
streaming: true
version: 1.0
---
```

**后端必须声明的能力**：

| 能力 | 说明 | 是否必须 |
|------|------|---------|
| `create_doc` | 创建会话产物容器（文档/文件） | ✅ 必须 |
| `append_blocks` | 追加内容块 | ✅ 必须 |
| `share_link` | 获取可分享的链接 | ✅ 必须 |
| `create_whiteboard` | 创建画板（用于 GRAPH 步骤） | 可选 |
| `update_blocks` | 更新已有内容块 | 可选 |
| `batch_write` | 批量写入（一次性写入全部 10 步产出） | 可选 |
| `full_detail_restore` | 🆕 v2.7 — 在最终报告中恢复完整步骤详情（非流式后端必须实现） | 非流式后端必须 |

**后端必须声明的约束**：

| 约束 | 类型 | 说明 |
|------|------|------|
| `requires_mcp` | string[] | 依赖的 MCP 服务名（如 `lark-cli`），空数组表示无依赖 |
| `requires_network` | bool | 是否需要网络连接 |
| `streaming` | bool | 是否支持流式追加（步骤完成即写入）vs 仅批量写入 |

---

## 2. 后端选择优先级

按以下顺序确定当前会话的产物后端：

1. **用户显式指定**（本轮对话中明确说"输出到飞书""生成 markdown""保存到本地 HTML"）→ 直接使用
2. **team-policy 配置**（`references/team-policy.md` 中 `output_backend.preferred`）→ 如果配置了且后端可用
3. **默认**：`local_html`（保持向后兼容，所有环境均可用）

**Agent 规则**：
- Agent **不得自行选择后端**——必须根据上述优先级确定
- 如果用户指定了某个后端但该后端不可用（如 MCP 未配置），Agent 必须告知用户并建议降级
- 用户可随时切换后端（"改用 markdown 输出"），Agent 在下一步骤开始使用新后端

---

## 3. 通用接口（Agent 指令契约）

每个后端 SKILL.md 必须定义以下 4 个操作的 Agent 执行指令。编排中枢（或 SUM 步骤）按这些接口调用后端：

### 3.1 create_session_doc

**触发时机**：工作流启动后、第一个需要记录产出的步骤前（通常在执行前或 READ 完成后）。

**输入**：
- `task_type`：任务类型
- `task_description`：任务简述（用于文档标题）
- `timestamp`：ISO 8601 时间戳

**输出**：
- `doc_id`：文档/文件标识符（飞书 doc_id、文件路径等）
- `doc_url`：文档访问 URL（如适用）
- `doc_title`：文档标题

**Agent 指令格式**：后端 SKILL.md 中以 `### create_session_doc` 为标题的子节，描述 Agent 应如何执行此操作。

### 3.2 write_step_output

**触发时机**：每个步骤完成后（如后端支持 streaming）或所有步骤完成后（批量写入）。

**输入**：
- `doc_id`：create_session_doc 返回的标识符
- `step_name`：步骤名（READ/CODE/REVIEW/EXAMINE/GIT/GRAPH/SUM/TALK/ASK）
- `step_output`：按 data-contract 结构化的步骤产出
- `step_status`：pass / pass_with_fixes / skip / blocked / fail

**输出**：
- `success`：是否写入成功
- `error`：失败原因（如有）

**🆕 v2.7 流式增量保障**：
- 后端支持流式追加（streaming: true）→ 此接口**必须**被调用，每步骤完成后立即追加
- 后端不支持流式追加（streaming: false）→ 此接口仅做内存暂存，**禁止精简/截断**步骤产出。write_final_report 时恢复完整产出
- **禁止**以"上下文不足"为由在 write_step_output 中精简步骤产出

**Agent 指令格式**：后端 SKILL.md 中以 `### write_step_output` 为标题的子节。

### 3.3 write_final_report

**触发时机**：SUM 步骤完成后，写入最终总结报告。

**输入**：
- `doc_id`：create_session_doc 返回的标识符
- `all_step_outputs`：全部步骤的结构化产出（含已跳过的步骤）
- `sum_output`：SUM 步骤的六要素总结
- `skipped_steps`：被跳过的步骤列表及原因
- `report_depth`：🆕 v2.7 — "brief" | "standard" | "detailed"
- `report_type`：🆕 v2.7 — "executive_summary" | "engineering_record"
- `mcr_gate_result`：🆕 v2.7 — MCR 自检闸门结果（detailed 模式必传，必须已通过）
- `streaming_status`：🆕 v2.7 — 流式写入状态（哪些步骤已流式追加到文档）

**输出**：
- `success`：是否写入成功
- `doc_url`：最终文档链接（如与 create 时返回的不同）

**🆕 v2.7 MCR 前置验证**：如果 report_depth=detailed 且 mcr_gate_result.passed=false → 后端必须拒绝写入，返回错误及缺失清单。

**Agent 指令格式**：后端 SKILL.md 中以 `### write_final_report` 为标题的子节。

### 3.4 get_share_link

**触发时机**：最终报告写入完成后。

**输入**：
- `doc_id`：文档标识符

**输出**：
- `share_url`：可公开分享的链接
- `access_level`：访问级别（如 "team_only" / "anyone_with_link"）

**Agent 指令格式**：后端 SKILL.md 中以 `### get_share_link` 为标题的子节。

---

## 4. 已注册后端

### local_html

| 属性 | 值 |
|------|-----|
| output_format | `html` |
| 文件位置 | `backends/local-html/SKILL.md` |
| 依赖 | 无 |
| 网络 | 不需要 |
| 流式追加 | 不支持（批量写入） |
| 适用场景 | 默认后端，所有环境均可使用 |

### markdown

| 属性 | 值 |
|------|-----|
| output_format | `markdown` |
| 文件位置 | `backends/markdown/SKILL.md` |
| 依赖 | 无 |
| 网络 | 不需要 |
| 流式追加 | 不支持（批量写入） |
| 适用场景 | 需要纯文本记录、导入其他系统 |

### lark_doc

| 属性 | 值 |
|------|-----|
| output_format | `lark_doc` |
| 文件位置 | `backends/lark-doc/SKILL.md` |
| 依赖 | MCP: `lark-cli` |
| 网络 | 需要 |
| 流式追加 | 支持（步骤完成即写入飞书文档） |
| 适用场景 | 飞书用户，需要团队协作和分享链接 |

---

## 5. 扩展新后端

添加新后端（如 Notion、Confluence）的步骤：

1. 在 `backends/` 下创建新目录（如 `backends/notion/`）
2. 编写 `SKILL.md`，声明 YAML frontmatter + 实现 4 个通用接口
3. 如需配置项，在 `team-policy.md` 的 `output_backend` 段追加对应字段
4. 如需 API 速查，在 `references/` 下创建对应 `xxx-api-quickref.md`

**无需修改**编排中枢、sum-session、或任何其他核心文件——后端之间完全解耦。

---

## 6. 降级策略

| 场景 | 处理 |
|------|------|
| 用户指定后端但 MCP 不可用 | 告知用户 → 降级到 local_html + 记录警告 |
| 后端写入中途失败 | 已写入部分保留 → 剩余内容保存为 local_html → SUM 中注明 |
| 网络不可用（需要网络的后端） | 自动降级 local_html → 告知用户 |
| team-policy 配置的后端不存在 | 回退到 local_html → SUM 中注明配置错误 |

降级时 Agent 必须：
1. 明确告知用户降级原因
2. 在 SUM 产出中记录降级事件
3. 使用降级后端完成后续写入

---

## 7. 与写入规范的联动

所有后端的最终报告写入都应遵守 `references/doc-writing-guide.md` 中的写作规范：
- 中文业务复盘口吻
- 不使用反引号包裹文件名/命令名
- 段落自然、表格仅结构化、标题下最多 4 子标题
- 命令集中展示

各后端 SKILL.md 在 `write_final_report` 指令中引用 `doc-writing-guide.md`。
