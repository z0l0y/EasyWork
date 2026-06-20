# 团队策略覆盖（Team Policy Overlay）

> **用途**：允许团队在不修改核心 Skill 文件的前提下，声明项目特定的规则覆盖。
> 编排中枢在 READ 阶段加载此文件，将规则注入到对应步骤的执行约束中。

---

## 设计原则

1. **覆盖而非替换**：团队策略追加约束，而非移除 EasyWork 的内置规则
2. **可审计**：每条策略需注明提出人和生效日期，方便追溯"为什么有这个规则"
3. **分层级**：强制规则（MUST）vs 建议规则（SHOULD）vs 信息提示（INFO）
4. **不依赖平台**：策略文件是纯 Markdown，在任何 Agent 平台均可读取

---

## 策略配置

### 注释语言（可配置）

```yaml
comment_language: chinese  # chinese | english | auto
# auto = 跟随项目现有注释语言，Agent 自动检测
```

**说明**：v2.3 默认值为 `chinese`（中文注释）。国际化团队或英文项目设置为 `english`。

---

### 自定义步骤

```yaml
custom_steps:
  - name: "SECURITY_SCAN"
    skill_path: ".claude/skills/easywork/custom/security-scan/SKILL.md"
    after_step: "REVIEW"
    condition: "review_output.dimensions.security.status == 'issues_found'"
    description: "当 REVIEW 发现安全问题时，自动运行 SAST 扫描"

  - name: "I18N_CHECK"
    skill_path: ".claude/skills/easywork/custom/i18n-check/SKILL.md"
    after_step: "CODE"
    condition: "code_output.files_changed 中包含 .vue/.tsx/.jsx 文件"
    description: "前端文件变更时检查国际化 key 是否完整"
```

**说明**：自定义步骤插入到 `after_step` 之后。Agent 在执行完该步骤后，检查 `condition` 是否满足，满足则加载 `skill_path` 执行。

---

## 团队规则覆盖

### 强制规则（MUST）

> 违反这些规则 → 阻断，必须修复才能继续。

```markdown
<!-- 在此添加团队强制规则 -->
<!-- 示例：
### 所有 API 变更必须包含 OpenAPI 文档更新
- **适用范围**：src/api/ 下的所有变更
- **检查点**：CODE 步骤完成后
- **验证方式**：检查 openapi.yaml 是否有对应变更
- **提出人**：@tech-lead
- **生效日期**：2026-06-20
-->
```

### 建议规则（SHOULD）

> 违反这些规则 → 警告，不阻断流程，但在 SUM 中注明。

```markdown
<!-- 在此添加团队建议规则 -->
<!-- 示例：
### 新增依赖应优先使用团队已审批的包
- **适用范围**：所有 package.json 变更
- **检查点**：CODE 步骤完成后
- **白名单**：lodash, dayjs, zod, axios, prisma
- **白名单外**：警告但允许，需在 implementation_notes 中说明理由
- **提出人**：@architect
- **生效日期**：2026-06-20
-->
```

### 信息提示（INFO）

> 不产生警告，仅在干跑预览中提示。

```markdown
<!-- 在此添加团队信息提示 -->
<!-- 示例：
### 核心模块提醒
- **src/services/auth.service.ts**：认证服务——改动前确认影响面
- **src/db/schema.ts**：数据库 schema——需要 DBA 审查迁移
- **src/middleware/rate-limit.ts**：限流中间件——改动前和 SRE 确认
-->
```

---

## 步骤约束覆盖

### READ 约束

```markdown
<!-- 追加到此步骤的约束条件 -->
<!-- 示例：我们的服务必须兼容 Node 18/20 两个版本 -->
```

### CODE 约束

```markdown
<!-- 追加到铁律之外的编码约束 -->
<!-- 示例：禁止使用 any 类型（TypeScript strict mode） -->
<!-- 示例：所有 SQL 查询必须使用参数化查询 -->
```

### REVIEW 约束

```markdown
<!-- 追加到七维度之外的审查维度 -->
<!-- 示例：所有 PR 必须至少有一个人类审批人（非 AI） -->
```

### EXAMINE 约束

```markdown
<!-- 追加的测试要求 -->
<!-- 示例：核心逻辑变更的测试覆盖率不得低于 80% -->
```

### GIT 约束

```markdown
<!-- 追加的提交规范 -->
<!-- 示例：commit message 必须遵循 Conventional Commits -->
<!-- 示例：禁止提交到 main 分支（必须 PR） -->
```

---

### 产物后端配置（🆕 v2.5）

```yaml
output_backend:
  preferred: "local_html"          # 团队默认产物后端：local_html | markdown | lark_doc
  lark:                            # 飞书配置（preferred: lark_doc 时需要）
    folder_token: ""               # 飞书文件夹 token（文档创建位置）
    wiki_space_id: ""              # 飞书知识库空间 ID（可选，使用 Wiki 功能时填写）
    git_tracking_doc_id: ""        # Git 链路追踪母文档 ID（可选，自动生成如不填）
```

**说明**：
- `preferred`：团队默认产物格式。用户可随时显式覆盖（"输出到飞书""生成 markdown"）
- `lark.folder_token`：飞书文档创建的默认目录。在飞书客户端中打开目标文件夹，URL 中 `folder_token` 参数即为此值
- `lark.wiki_space_id`：如使用飞书知识库，填写空间 ID
- `lark.git_tracking_doc_id`：如已创建 Git 链路追踪母文档，填写其 document_id。留空则 Agent 首次运行 lark-doc 后端时自动创建
- 使用飞书后端前需先配置 `lark-cli` MCP 服务

---

## 使用方式

1. **团队 fork 此文件**到 `.claude/skills/easywork/team-policy.md`
2. **编辑上述各段的规则**，删除模板注释，填入实际规则
3. **编排中枢自动加载**：Agent 在 READ 阶段读取此文件，将规则注入到对应步骤
4. **版本控制**：将此文件纳入 Git，变更通过 PR 审查

---

## 与 Gotchas 的关系

| 知识类型 | 文件 | 性质 | 来源 |
|---------|------|------|------|
| 团队策略 | `team-policy.md` | 规则型（"必须/应该做 X"） | 团队主动制定 |
| 项目陷阱 | `gotchas.md` | 事实型（"做 Y 会踩坑"） | 实践中积累 |

当同一条陷阱被反复触发，考虑在 team-policy 中增加对应的强制规则。
