# 飞书 API 速查表（Lark API Quick Reference）

> **🆕 v2.5**：供 lark-doc 后端适配器 Agent 执行时按需查阅。不要求记忆，用到哪个端点查哪个。
> 完整文档：https://open.feishu.cn/document

---

## 1. 区域与认证

### API 域名

| 平台 | 域名 | 适用区域 |
|------|------|---------|
| 飞书 | `https://open.feishu.cn` | 中国大陆 |
| Lark | `https://open.larksuite.com` | 国际版 |

### 获取 tenant_access_token（最常用）

```bash
curl -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d '{"app_id": "cli_xxx", "app_secret": "xxx"}'
```

响应：
```json
{
  "code": 0,
  "tenant_access_token": "t-xxx",
  "expire": 7200
}
```

**关键点**：
- Token 有效期 2 小时，需缓存复用
- 所有后续请求头：`Authorization: Bearer {token}`
- MCP 工具（`lark-mcp`）自动管理 token，Agent 无需手动获取

### 通过 MCP 调用

如果配置了 `@larksuiteoapi/lark-mcp`，Agent 通过 MCP 工具调用飞书 API，无需手动处理认证。MCP 自动管理 token 刷新。

---

## 2. 文档（Docx）API

### 创建文档

```
POST /open-apis/docx/v1/documents
```

请求体：
```json
{
  "folder_token": "fldcnXXX",
  "title": "文档标题"
}
```

响应：返回 `document_id`（同时也是 Page block 的 `block_id`）

### 追加内容块（Children）

```
POST /open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children?document_revision_id=-1
```

请求体：
```json
{
  "index": -1,
  "children": [
    {
      "block_type": 3,
      "heading1": {
        "elements": [{"text_run": {"content": "标题", "text_element_style": {}}}]
      }
    },
    {
      "block_type": 2,
      "text": {
        "elements": [{"text_run": {"content": "正文段落", "text_element_style": {}}}]
      }
    }
  ]
}
```

**限制**：每次最多 50 个 children block。

### Markdown 转块（推荐方式）

```
POST /open-apis/docx/v1/documents/{document_id}/convert
```

请求体：
```json
{
  "content": "# 标题\n\n正文内容\n\n- 列表项 1\n- 列表项 2",
  "content_type": "markdown"
}
```

**这是推荐的内容写入方式**：Agent 按 Markdown 准备内容，调用此 API 转为飞书块，无需手动构造块 JSON。

**支持 Markdown 元素**：
- 标题 H1-H9（`#` ~ `#########`）
- 段落、加粗、斜体、删除线
- 无序列表、有序列表
- 代码块（fenced code block）
- 引用（`>`）
- 分割线（`---`）

**不支持**：
- 表格（Table block_type=31，API 只读，无法通过 API 创建/写入）
- 图片（Image block，需先上传获取 image_key）

**替代方案处理表格**：使用多维表格（Bitable）代替飞书文档内表格，或使用格式化文本 + 缩进模拟表格结构。

### 常用 Block Type 速查

| block_type | JSON Key | 说明 | 可编辑 |
|---|---|---|---|
| 1 | page | 文档根节点 | 否 |
| 2 | text | 段落文本 | 是 |
| 3-11 | heading1 ~ heading9 | H1-H9 标题 | 是 |
| 12 | bullet | 无序列表 | 是 |
| 13 | ordered | 有序列表 | 是 |
| 14 | code | 代码块 | 是 |
| 15 | quote | 引用块 | 是 |
| 19 | callout | 高亮提示框 | 是 |
| 22 | divider | 分割线 | 否 |
| 27 | image | 图片 | 部分 |
| 31 | table | 表格 | API 只读 |
| 44 | board | 白板嵌入 | 否 |

---

## 3. Wiki（知识库）API

### 创建 Wiki 节点（页面）

```
POST /open-apis/wiki/v2/spaces/{space_id}/nodes
```

请求体：
```json
{
  "obj_type": "docx",
  "parent_node_token": "父节点token或省略",
  "node_type": "origin",
  "title": "页面标题"
}
```

### 获取空间列表

```
GET /open-apis/wiki/v2/spaces
```

### 获取节点信息

```
GET /open-apis/wiki/v2/spaces/get_node?token={node_token}
```

### 限制
- 每个空间最多 400k 节点
- 最多 50 层深度
- 每个父节点最多 2000 个子节点

---

## 4. 多维表格（Bitable）API

用于替代飞书文档内表格（文档表格 API 只读）。

### 创建数据表

```
POST /open-apis/bitable/v1/apps/{app_token}/tables
```

### 批量新增记录

```
POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create
```

**适用场景**：Git 链路追踪数据（提交分组、Check 状态、hash、测试结果）→ 用多维表格记录，支持筛选和视图。

---

## 5. 白板（Board）API

### 适用范围
- 飞书白板/画板是一个独立的协作绘图工具
- 在文档中可通过 block_type=44 嵌入
- Mermaid 可通过 `@larksuite/whiteboard-cli` 渲染成图片后嵌入文档

### 当前限制
- 白板 API 较新，MCP 支持可能不完整
- GRAPH 步骤优先使用 Mermaid 渲染图片嵌入方案（稳定可靠）
- 白板创建作为未来增强功能

---

## 6. 权限与分享

### 文档默认权限
- 创建文档时默认继承文件夹权限
- 可通过飞书 UI 手动设置分享权限（"任何人可查看""团队内可查看"等）
- API 目前不提供分享设置接口（需用户在飞书 UI 中操作）

### 获取分享链接
- 文档创建后，分享链接格式：`https://{domain}/docx/{document_id}`
- 飞书文档分享需要用户在飞书 UI 中开启分享开关
- Agent 生成的链接是文档直链，用户可手动复制发送

---

## 7. 限流与重试

### 通用限流规则

| API | 限制 |
|-----|------|
| 获取 token | 1000 次/小时/App |
| 文档创建 | 100 次/分钟/App |
| 块追加 | 100 次/分钟/App |
| Markdown 转换 | 100 次/分钟/App |
| Wiki 操作 | 100 次/分钟/App |

### 重试策略

当返回 HTTP 429 或错误码 99991400（频率限制）时：
1. 等待 `Retry-After` 响应头指定的时间
2. 如无 Retry-After，默认等待 1 秒后重试
3. 最多重试 3 次
4. 3 次后仍失败 → 降级到 local_html 后端

---

## 8. 常见错误码

| 错误码 | 含义 | 处理 |
|--------|------|------|
| 99991400 | 频率限制 | 等待后重试 |
| 99991663 | folder_token 无效 | 检查配置的飞书目录是否正确 |
| 1260001 | 文档不存在 | doc_id 可能过期或被删除 |
| 1280003 | 无权限操作此文档 | 检查 App 权限范围 |
| 99991667 | 文档不可编辑 | 文档可能被锁定或为只读 |

---

## 9. MCP 工具速查（lark-mcp）

如果使用 `@larksuiteoapi/lark-mcp`，常用工具：

| 工具 | 对应 API | 用途 |
|------|---------|------|
| `create_document` | POST /docx/v1/documents | 创建飞书文档 |
| `append_blocks` | POST /docx/v1/documents/{id}/blocks/{id}/children | 追加块到文档 |
| `convert_markdown` | POST /docx/v1/documents/{id}/convert | Markdown 转文档块 |
| `create_wiki_node` | POST /wiki/v2/spaces/{id}/nodes | 创建 Wiki 页面 |
| `list_spaces` | GET /wiki/v2/spaces | 列出知识空间 |

**注意**：具体工具名以 MCP 注册为准。Agent 应先用 MCP 工具搜索确认可用工具名，而非假设。
