# HTML 输出模板与规范

## 默认输出规则

**当用户未指定输出格式时**（没有提供飞书文档链接、没有要求 md 文件、没有指定其他输出目标），
Agent 必须将工作流结果生成为一个**自包含的 HTML 文件**，包含所有执行步骤的完整产出。

**指定了输出格式时**：优先使用用户指定的格式（飞书文档、md 文件、PR 描述等），
但可以附加 HTML 文件作为可视化补充。

## HTML 文件规范

### 生成位置
- 在项目根目录生成 `EasyWork_Report_{YYYYMMDD_HHmmss}.html`
- 文件名包含时间戳，避免覆盖历史报告
- 同时生成到 `.claude/easywork/` 目录下，方便统一管理

### HTML 结构要求

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EasyWork 开发报告 — {日期}</title>
    <!-- ⚠️ v2.4 安全：标题使用通用描述"EasyWork 开发报告 — {日期}"，
         不包含具体任务摘要（如"修复微信支付回调漏洞"），防止报告分享时泄露内部信息 -->
    <style>
        /* 内联 CSS，不依赖外部文件 */
    </style>
</head>
<body>
    <!-- 报告头部：任务概览 + 分类信息 + 步骤进度 -->
    <!-- 各步骤产出（被跳过的步骤折叠显示） -->
    <!-- 报告尾部：生成信息 -->
</body>
</html>
```

### CSS 样式规范

使用以下样式基线，确保在任何浏览器中渲染一致：

```css
:root {
    --primary: #1a73e8;
    --success: #0d904f;
    --warning: #e37400;
    --danger: #d93025;
    --skip: #80868b;
    --bg: #f8f9fa;
    --card-bg: #ffffff;
    --border: #dadce0;
    --text: #202124;
    --text-secondary: #5f6368;
    --radius: 8px;
    --shadow: 0 1px 3px rgba(0,0,0,0.1);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 20px;
    max-width: 960px;
    margin: 0 auto;
}

/* 报告头部 */
.report-header {
    background: linear-gradient(135deg, #1a73e8, #1557b0);
    color: white;
    padding: 32px 40px;
    border-radius: var(--radius);
    margin-bottom: 24px;
}
.report-header h1 { font-size: 24px; margin-bottom: 8px; }
.report-header .meta { opacity: 0.85; font-size: 14px; }
.report-header .meta span { margin-right: 20px; }
.report-header .classification {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
}
.classification.bug { background: #fce8e6; color: #c5221f; }
.classification.feature { background: #e8f0fe; color: #1967d2; }
.classification.understand { background: #e6f4ea; color: #137333; }
.classification.refactor { background: #fef7e0; color: #b06000; }

/* 进度条 */
.progress-bar {
    display: flex;
    gap: 4px;
    margin-bottom: 24px;
}
.progress-step {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: var(--border);
}
.progress-step.done { background: var(--success); }
.progress-step.skip { background: var(--skip); }
.progress-step.current { background: var(--primary); }

/* 步骤卡片 */
.step-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 20px;
    overflow: hidden;
}
.step-card.skipped { opacity: 0.6; }
.step-card-header {
    display: flex;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
}
.step-number {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 14px;
    margin-right: 12px;
    flex-shrink: 0;
}
.step-number.done { background: var(--success); color: white; }
.step-number.skip { background: var(--skip); color: white; }
.step-number.current { background: var(--primary); color: white; }
.step-title { font-weight: 600; font-size: 16px; flex: 1; }
.step-badge {
    padding: 2px 10px; border-radius: 10px;
    font-size: 12px; font-weight: 600;
}
.badge-done { background: #e6f4ea; color: #137333; }
.badge-skip { background: #f1f3f4; color: #5f6368; }
.badge-blocked { background: #fce8e6; color: #c5221f; }

.step-card-body { padding: 20px 24px; }

/* 表格样式 */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
}
th, td {
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}
th {
    background: var(--bg);
    font-weight: 600;
    font-size: 13px;
    color: var(--text-secondary);
}
td { font-size: 14px; }

/* Mermaid 图表容器 */
.mermaid-container {
    background: #fafafa;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    margin: 16px 0;
    overflow-x: auto;
}

/* 代码块 */
pre {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px 20px;
    border-radius: var(--radius);
    overflow-x: auto;
    font-size: 13px;
    line-height: 1.5;
}
code { font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace; }
:not(pre) > code {
    background: #f1f3f4;
    color: #d93025;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 90%;
}

/* 风险标签 */
.risk-low { color: #137333; background: #e6f4ea; }
.risk-med { color: #b06000; background: #fef7e0; }
.risk-high { color: #c5221f; background: #fce8e6; }

/* 确认清单 */
.checklist-item {
    display: flex; align-items: flex-start;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
}
.checklist-item:last-child { border-bottom: none; }
.checklist-status {
    width: 60px; flex-shrink: 0;
    font-weight: 600; font-size: 13px;
}

/* 报告尾部 */
.report-footer {
    text-align: center;
    padding: 24px;
    color: var(--text-secondary);
    font-size: 13px;
    border-top: 1px solid var(--border);
    margin-top: 24px;
}

/* 响应式 */
@media (max-width: 640px) {
    body { padding: 10px; }
    .report-header { padding: 20px; }
    .report-header h1 { font-size: 20px; }
}
```

### 每步骤的 HTML 内容结构

Agent 在生成 HTML 时，为每个步骤创建结构化的卡片：

**步骤卡片通用结构**：
```html
<div class="step-card {skipped}">
    <div class="step-card-header">
        <div class="step-number {done|skip|current}">{序号}</div>
        <div class="step-title">{步骤名称}</div>
        <div class="step-badge {badge-done|badge-skip}">{通过/跳过/阻断}</div>
    </div>
    <div class="step-card-body">
        <!-- 各步骤特定内容 -->
    </div>
</div>
```

**READ 步骤内容块**：
```html
<h3>📖 核心目标</h3>
<p>{goal}</p>

<h3>修改范围</h3>
<table>
    <tr><th>文件/模块</th><th>修改类型</th><th>说明</th></tr>
    <tr><td>...</td><td>修改</td><td>...</td></tr>
</table>

<h3>验收标准</h3>
<ul>
    <li>✅/⏳ {标准}</li>
</ul>

<h3>约束与不做什么</h3>
<p><strong>约束</strong>：{constraints}</p>
<p><strong>不做什么</strong>：{non_goals}</p>
```

**CODE 步骤内容块**：
```html
<h3>变更清单</h3>
<table>
    <tr><th>文件</th><th>改动类型</th><th>行数</th><th>原因</th></tr>
    <tr><td><code>path/to/file</code></td><td>修改</td><td>~15</td><td>...</td></tr>
</table>

<h3>影响面评估</h3>
<p>{impact_assessment}</p>
```

**REVIEW 步骤内容块**：
```html
<h3>审查结论：<span style="color: #137333">✅ 通过</span></h3>

<table>
    <tr><th>维度</th><th>结果</th><th>发现问题</th></tr>
    <tr><td>正确性</td><td>✅</td><td>无</td></tr>
    <tr><td>安全性</td><td>✅</td><td>无</td></tr>
    <tr><td>兼容性</td><td>✅</td><td>无</td></tr>
    <tr><td>可维护性</td><td>✅</td><td>无</td></tr>
    <tr><td>性能</td><td>✅</td><td>无</td></tr>
    <tr><td>可观测性</td><td>⚠️</td><td>catch块缺少日志</td></tr>
    <tr><td>可访问性</td><td>✅</td><td>N/A（本次为后端变更）</td></tr>
</table>

<h3>供应链安全检查（🆕 v2.3 — 如有新增依赖）</h3>
<p>检查结论：{无新增依赖 / 通过 / ⚠️ 发现问题}</p>
<ul>
    <li>依赖必要性：{结论}</li>
    <li>版本稳定性：{结论}</li>
    <li>已知漏洞：{结论}</li>
    <li>许可证兼容：{结论}</li>
    <li>维护状态：{结论}</li>
</ul>

<h3>二次独立抽查</h3>
<table>
    <tr><th>抽查维度</th><th>原结论</th><th>交叉结论</th><th>新发现</th></tr>
    <tr><td>{维度A}</td><td>✅ pass</td><td>✅ 一致</td><td>无</td></tr>
    <tr><td>{维度B}</td><td>✅ pass</td><td>⚠️ 发现问题</td><td>{描述}</td></tr>
</table>

<!-- 🆕 v2.3 仅高风险任务启用并行审查时显示 -->
<h3>并行审查结果</h3>
<table>
    <tr><th>审查者</th><th>结论</th><th>阻断数</th><th>发现</th></tr>
    <tr><td>🔒 安全审查者</td><td>✅ pass</td><td>0</td><td>无</td></tr>
    <tr><td>⚡ 性能审查者</td><td>⚠️ issues_found</td><td>0</td><td>N+1查询一处（非阻断）</td></tr>
    <tr><td>🔄 兼容性审查者</td><td>✅ pass</td><td>0</td><td>无</td></tr>
</table>
```

**EXAMINE 步骤内容块**：
```html
<h3>测试命令</h3>
<pre><code>npm test -- --testPathPattern="auth"</code></pre>

<h3>测试结果</h3>
<table>
    <tr><th>总数</th><th>通过</th><th>失败</th><th>跳过</th></tr>
    <tr><td>12</td><td style="color:#137333">12</td><td>0</td><td>0</td></tr>
</table>

<h3>测试输出凭据</h3>
<pre><code>...</code></pre>
```

**GIT 步骤内容块**：
```html
<h3>拆分概览</h3>
<table>
    <tr><th>#</th><th>维度</th><th>文件数</th><th>风险</th></tr>
    <tr><td>1</td><td>配置/构建</td><td>3</td><td><span class="risk-low">低</span></td></tr>
    <tr><td>2</td><td>核心逻辑</td><td>5</td><td><span class="risk-high">高 ⚠️</span></td></tr>
</table>

<!-- 每个单元详情 -->
<h3>单元 2：核心逻辑 <span class="risk-high">⚠️ 重点审查</span></h3>
<table>
    <tr><th>文件</th><th>改动说明</th></tr>
    <tr><td><code>auth.service.ts</code></td><td>新增用户空值判断</td></tr>
</table>
<p><strong>风险分析</strong>：...</p>
<p><strong>验证方式</strong>：...</p>
<p><strong>🆕 建议提交消息</strong>：<code>fix(auth): handle null user in login flow</code></p>
<pre><code>Add null check for user object in auth.service.ts login() method.
Previously would throw 500 when user lookup returned null.
Now returns 401 with unified error message.

Closes #123</code></pre>
```

**GRAPH 步骤内容块**：
```html
<h3>{流程图/时序图/架构图}</h3>
<div class="mermaid-container">
    <pre class="mermaid">
{图表的 Mermaid 代码}
    </pre>
</div>

<h3>节点对照表</h3>
<table>
    <tr><th>图中节点</th><th>代码实体</th><th>位置</th></tr>
    <tr><td>校验Token</td><td><code>validateToken()</code></td><td>auth.ts:42</td></tr>
</table>
```

**SUM 步骤内容块**：
```html
<section>
    <h3>📌 背景</h3>
    <p>{background}</p>
</section>
<section>
    <h3>🔍 发现过程</h3>
    <p>{discovery}</p>
</section>
<section>
    <h3>🐛 问题说明</h3>
    <p>{problem}</p>
</section>
<section>
    <h3>🔧 解决方案</h3>
    <p>{solution}</p>
</section>
<section>
    <h3>✅ 最终效果</h3>
    <p>{outcome}</p>
</section>
<section>
    <h3>🔮 未来展望</h3>
    <p>{future}</p>
</section>
```

**TALK 步骤内容块**：
```html
<h3>5-Whys 根因追溯</h3>
<table>
    <tr><th>层级</th><th>追问</th><th>答案</th></tr>
    <tr><td>Why 1</td><td>为什么返回500？</td><td>user为null时访问了.password</td></tr>
</table>
<p><strong>系统性根因</strong>：{root_cause}</p>

<h3>取舍分析</h3>
<table>
    <tr><th>取舍项</th><th>好处</th><th>代价</th><th>主动/被迫</th></tr>
    <tr><td>...</td><td>...</td><td>...</td><td>主动</td></tr>
</table>

<h3>工程规范建议</h3>
<ol>
    <li>{rule}</li>
</ol>
```

**ASK 步骤内容块**：
```html
<h3>六维度确认清单</h3>

<div class="checklist-item">
    <div class="checklist-status" style="color:#137333">✅ 已确认</div>
    <div>
        <strong>需求与验收</strong>
        <p>修复了用户不存在的场景，返回401。确认符合预期。</p>
    </div>
</div>
<!-- 重复 6 个维度 -->
```

### 跳过步骤的显示

```html
<div class="step-card skipped">
    <div class="step-card-header">
        <div class="step-number skip">{序号}</div>
        <div class="step-title">{步骤名称}</div>
        <div class="step-badge badge-skip">已跳过</div>
    </div>
    <div class="step-card-body" style="display:none">
        <p><strong>跳过原因</strong>：{跳过理由}</p>
    </div>
</div>
```

### 步骤自检记录（v2.2）

```html
<h2>每步产出自检</h2>
<table>
    <tr><th>步骤</th><th>必填字段</th><th>状态</th></tr>
    <tr><td>1. READ</td><td>goal, scope, constraints, acceptance_criteria, non_goals</td><td>✅</td></tr>
    <tr><td>2. CODE</td><td>files_changed, impact_assessment, implementation_notes</td><td>✅</td></tr>
    <tr><td>3. REVIEW</td><td>verdict, dimensions, blocking_issues</td><td>✅</td></tr>
    <tr><td>...</td><td>...</td><td>✅ / ⚠️ 缺 {N} 项</td></tr>
</table>
```

### 干跑预览（v2.2 — 中高风险任务）

```html
<div class="card" style="background: #e8f0fe; border-left: 4px solid #1a73e8;">
    <h2>🔍 执行预览</h2>
    <p><em>以下内容在用户确认前仅做展示，不实际执行。</em></p>
    <table>
        <tr><th>步骤</th><th>预计操作</th><th>涉及文件</th><th>预计产出</th></tr>
        <tr><td>1. READ</td><td>阅读 3 个文件，提取需求</td><td>auth.service.ts, user.model.ts</td><td>五要素需求说明</td></tr>
        <tr><td>2. CODE</td><td>修改 2 个文件，约 30 行</td><td>auth.service.ts, auth.test.ts</td><td>变更记录</td></tr>
        <tr><td>...</td><td>...</td><td>...</td><td>...</td></tr>
    </table>
    <p>⚠️ <strong>风险提示</strong>：{风险点及缓解措施}</p>
</div>
```

## Agent 生成指令

当触发 HTML 输出时，Agent 必须：

1. **生成完整的 HTML 文件**，包含上述所有结构和样式
2. **文件路径**：`{项目根目录}/.claude/easywork/EasyWork_Report_{YYYYMMDD_HHmmss}.html`
3. **跳过步骤**：仍然在 HTML 中渲染为折叠的卡片（不隐藏），方便追溯
4. **Mermaid 图表**：在 HTML 中嵌入 Mermaid 代码并使用 `<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>` 加载 Mermaid 渲染库
5. **代码块**：使用 `<pre><code>` 包裹，语法高亮使用纯 CSS 实现
6. **不依赖外部 CSS 文件**：所有样式内联在 `<style>` 标签中

## ⛔ HTML 注入防护（🆕 v2.4）

**Agent 在替换 HTML 占位符时必须进行 HTML 转义。** 所有数据契约字段在嵌入 HTML 前，必须对以下字符做实体编码：

| 字符 | 替换为 |
|------|--------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | `&#39;` |
| `&` | `&amp;` |

**特别关注的字段**（来自 data-contract，可直接含用户或代码内容）：
- `test_output_snippet` — 可能含 `<` `>` 标签
- `sum_output.discovery` — 可能含粘贴的日志/代码片段
- `code_output.files_changed[].path` — 文件路径
- `review_output.dimensions.*.issues[]` — 审查发现描述
- `read_output.goal` / `read_output.acceptance_criteria[]` — 用户输入
- 所有 `{summary}` / `{body}` / `{description}` 类自由文本字段

**反例**（会导致 XSS）：
```html
<p>发现：<script>alert(1)</script></p>
```

**正确做法**：
```html
<p>发现：&lt;script&gt;alert(1)&lt;/script&gt;</p>
```

> 详细规则见 `../references/security-policy.md` §2.5。

## ⛔ 敏感信息脱敏（🆕 v2.4）

**Agent 在保存 HTML 报告前，必须执行脱敏自检。** 报告内容不得包含以下任何信息：

| 禁止内容 | 检测规则 | 脱敏方式 |
|---------|---------|---------|
| API Key / Token / Secret | `key=`、`token=`、`secret=`、`Bearer` + 长字符串 | 替换为 `***REDACTED***` |
| 密码（明文） | `password`、`passwd` + 非空值 | 替换为 `***REDACTED***` |
| 完整认证日志 | 包含 token/jwt/session 的日志行 >80 字符 | 截断为前 80 字符 + `...[TRUNCATED]` |
| 内部 URL | 含内网 IP（192.168/10./172.16-31）/内部域名的 URL | 仅保留路径（如 `/api/users`） |
| 大段源码（>30行） | 连续 code block | 保留文件路径+变更行号，不贴完整源码 |
| 手机号 | 连续 11 位数字（中国）/类似模式 | 替换为 `138****1234` |
| 邮箱地址 | `xxx@xxx.xx` 模式 | 替换为 `u***@***.com` |
| 用户帐号/ID | 非文档示例的真实帐号名 | 替换为 `user_***` |
| 内部 IP 地址 | `192.168.*`、`10.*`、`172.16-31.*` | 替换为 `[internal_ip]` |
| 数据库连接串 | `jdbc:`、`mongodb://`、`postgres://`、`redis://` 等 | 替换为 `***REDACTED***` |

### 脱敏自检清单

```
【HTML 报告脱敏自检】（保存前执行）
- [ ] 无 API Key / Token / Secret 明文
- [ ] 无密码硬编码
- [ ] 无完整认证日志（>80 字符已截断）
- [ ] 无内部 URL / IP
- [ ] 代码块每个 ≤ 30 行
- [ ] 无手机号 / 邮箱 / 帐号
- [ ] 无数据库连接串

如发现以上任一内容 → 立即脱敏处理，再保存文件。
```

> 详细规则见 `../references/security-policy.md` §2。

## Mermaid 渲染方案

### 安全约束（v2.4）

1. **固定版本**：使用 `mermaid@10`，不得使用 `@latest`
2. **HTTPS 协议**：CDN URL 必须使用 `https://`，不得使用 `http://`
3. **离线后备**：`<pre class="mermaid">` 中保留原始代码，CDN 不可用时用户可手动查看
4. **无外部追踪**：不引入 Google Analytics、外部字体、社交按钮等第三方资源
5. 详见 `../references/security-policy.md` §2.4

### 实现

```html
<!-- 在 </body> 前添加 -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({ startOnLoad: true, theme: 'default' });
</script>
```

如果 CDN 不可用（离线环境），在 `<pre class="mermaid">` 中保留原始 Mermaid 代码，用户可手动复制到 [mermaid.live](https://mermaid.live/) 查看。

> ⚠️ **供应链提醒**：HTML 报告通过第三方 CDN 加载 JS 库。团队可在 `team-policy.md` 中覆盖 CDN 策略（如指定内部镜像或禁用 CDN 完全离线）。
