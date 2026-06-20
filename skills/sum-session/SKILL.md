---
name: sum-session
description: >
  结构化总结报告。GRAPH 之后执行。按六要素撰写：
  背景（为什么做）→ 发现过程（怎么定位的）→ 问题说明（本质是什么）→
  解决方案（怎么修的+为什么这样修）→ 最终效果（客观验证结果）→
  未来展望（遗留问题和后续建议）。是 PR 描述和团队交接的核心文档。
  v2.7: 报告深度感知(brief/standard/detailed)、MCR自检闸门(HARD/SOFT GATE)、
  流式增量写入保障。
  v2.9: 反水文闸门(6类信号检测→HARD GATE)、ETR证据链标准(Evidence/Thinking/Risk)、
  同行审查就绪六问自检、文档质量评分(100分制/<80分阻断)、写后Fetch验证(防截断/格式损毁)、
  禁止凭记忆写报告(必须基于step_output拼装)。
  v2.10: 文档拓扑闸门(7项检查→HARD GATE,铁律#28)、双模文档结构(审计日志Mode A/持续维护Mode B默认)、
  结构化合并(Fetch→Check→Distribute→Index→Mark→Verify,取代尾部追加更新记录)。
  v2.8: 文档迭代增量更新(铁律#25)→v2.10已升级为节点内版本合并,Mode B下禁止文档级更新记录块。
allowed-tools: Read, Search, Bash
model: sonnet
version: 2.10
---

# Sum Session（总结报告）

## 前置判断

**report_depth 感知（🆕 v2.7）**：
- **brief**：仅产出六要素概要（每要素1-2句），跳过详细发现过程和量化对比。最终报告约 1-2 页
- **standard**：产出完整六要素（=当前 v2.6 行为），含排查路径、量化对比。最终报告约 3-5 页
- **detailed**：完整六要素 + 逐步骤MCR自检 + 流式增量保障 + 代码摘录含路径行号。最终报告约 6-10 页

**必须执行**：任何产生了代码改动或分析结论的任务。

**可以跳过**：brief 模式 + 极微改动 + 用户明确说"不需要记录"。其他情况：SUM 不可跳过。

## 六要素

### 1. 背景 — 为什么做

- 说明触发原因：生产事故？用户反馈？需求单？技术债务？
- 说明不解决的后果
- 让一个完全不了解项目的人看完后能理解"为什么要花时间做这件事"

> ❌ "优化了登录" → ✅ "线上监控发现登录 P99 延迟达 2.8s，每日约 3000 用户在高峰期等待超 3s，客服收到大量投诉。根因定位到密码哈希使用 cost factor=14 的 bcrypt（单次 800ms）。"

### 2. 发现过程 — 怎么定位的（到代码行级根因）

- 最初的触发信号是什么（监控告警/用户投诉/Code Review）
- 排查路径：现象 → 初步判断 → 排除 X → 排除 Y → 定位到代码行
- 贴关键证据（日志片段、截图、数据对比）
- **止步点**：找到出问题的代码行即止（如 `auth.service.ts:88` 缺少空值判断）。不要继续追问"为什么当初没写空值判断"——那是 TALK 阶段 5-Whys 的职责。

### 3. 问题说明 — 本质是什么

- 直接原因（近因）：哪行代码、什么条件触发
- 影响范围：功能、用户、时长、数据
- **注意**：这里描述的是技术层面的"出了什么 bug"，不展开系统性根因。系统性根因留给 TALK 的 5-Whys。

### 4. 解决方案 — 怎么修的 + 为什么这样修

- 采用的方案及技术细节
- 方案选择理由（为什么选 A 不选 B）
- 关联 REVIEW 发现的问题和 EXAMINE 的测试结果

> "选择将 bcrypt cost factor 从 14 降到 10，而非换成 SHA-256：(1) bcrypt 是密码哈希标准，安全性有保障；(2) factor=10 时单次 60ms，仍在暴力破解安全阈值内；(3) 不换算法，兼容已有密码，无需用户重置。"

### 5. 最终效果 — 客观验证结果

- 引用 EXAMINE 的测试数据
- 验收标准逐项对照
- 量化对比（如有）：修改前 vs 修改后

> | 指标 | 修改前 | 修改后 | 变化 |
> |------|--------|--------|------|
> | 登录 P99 | 2.8s | 0.32s | ↓88.6% |
> | 单次验证 | 800ms | 60ms | ↓92.5% |

### 6. 未来展望 — 遗留和下一步

- 诚实列出本次局限性和未覆盖的场景
- 标记临时方案和技术债务
- 后续具体建议（附时间线和责任人）

> **详细检查清单**：六要素完整性检查、常见遗漏项、各要素的写作示例和反例，见 `references/summary-checklist.md`。

## 缺少背景信息时

如果用户一开始没说明需求背景（只甩了段报错说"修一下"），到了 SUM 阶段你对"为什么做"一无所知：

- **不要编造** "为了优化用户体验" 这种万能废话
- **询问用户**："总结报告的背景部分我缺少以下信息：这个问题的触发场景和影响范围是什么？需要补充还是标注为信息缺失？"

## 反模式

- ❌ PR 描述只写一句"Fixed login bug"——这等于什么都没写
- ❌ 效果部分写"应该没问题了"——用数据说话，不用感觉说话
- ❌ 未来展望写"继续优化"、"持续关注"——空洞无物的套话
- ❌ 解决方案不解释"为什么选这个方案"——后人不知道为什么代码长这样
- ❌ 不标遗留问题，假装改得完美——诚实的工程师标注 debt，不诚实的假装不存在
- ❌ v2.7：detailed 模式下产出 brief 级别的内容——深度不可自动降级
- ❌ v2.7：跳过 MCR 自检闸门直接写入——detailed 模式此为 HARD GATE，不通过不可写入
- ❌ v2.7：代码摘录不标文件路径和行号——"某处代码"不可追溯
- ❌ v2.7：用摘要表替代完整问答——SELFCHECK 产出必须保留完整 CTO 问答记录(cto_qa_transcript)
- ❌ v2.9：SUM 凭记忆自由发挥写报告——各步骤的详细产出被丢弃，只剩摘要。必须基于 step_output 拼装
- ❌ v2.9：跳过 Anti-Fluff Gate——detailed 模式此为 HARD GATE。空泛结论/无证据通过必须阻断
- ❌ v2.9：关键结论只有结果没有推理——"测试通过"不写测试了什么、为什么能覆盖。必须满足 ETR
- ❌ v2.9：SelfCheck 走过场——<8问/无反事实/接受"因为这样更合理"——不是拷打，是演戏
- ❌ v2.9：写后不 fetch 验证——内容转换后可能截断/代码块错误/中文乱码
- ❌ v2.9：质量评分放水——detailed <80 分仍写入。闸门存在是为了质量底线
- ❌ v2.9：brief 模式不标注免责声明——必须标注"简要摘要，不适合工程追溯"
- ❌ v2.10：Mode B 下追加 `## 📝 更新记录` 块——应拆入对应流程节点下 `### v{N}`
- ❌ v2.10：Mode B 下出现两个 `## 1. READ` 节点——必须合并。拓扑闸门会阻断
- ❌ v2.10：不 fetch 现有文档直接覆盖写入——破坏已有结构和版本历史
- ❌ v2.10：新版本内容全堆在"更新记录"里，节点内无新版本子节——典型的流水账
- ❌ v2.10：历史内容和当前内容混在同一段落无版本区分——后人不知道什么是当前有效的
- ❌ v2.10：跳过 Document Topology Gate——detailed 模式此为 HARD GATE（铁律 #28）
- ❌ v2.10：混合使用 Mode A 和 Mode B 顶层结构——必须统一为一种模式
- ❌ v2.10：Mode B 下所有节点都追加 v{N}（包括无变更的节点）——应只有变更节点新增版本子节

## 🆕 v2.8 文档迭代增量更新（铁律#25）— [已升级至 v2.10]

> **v2.10 升级说明**：v2.8 的"文档末尾追加更新记录"机制已被 v2.10 的"节点内版本合并"机制取代。
> 核心意图（可追溯演进历史）保留，但实现方式升级：
> - **旧（v2.8）**：在文档末尾 `## 📝 更新记录` 追加 `### 更新 v1.X` 块 → 导致"更新记录坟场"
> - **新（v2.10）**：在对应流程节点内追加 `### v{N} — {date}（{变更类型}）` → 节点内版本树
>
> Mode A（审计日志）下 v2.8 的更新记录格式仍可使用。Mode B（持续维护，默认）下禁止文档级更新记录块。
>
> 详见下方 🆕 v2.10 三个新专区：Document Modes / Document Topology Gate / Structured Merge。

## 🆕 v2.9 ETR 标准 — 贯穿报告全篇

每个关键结论必须满足 E/T/R 三元组，缺一不可：

- **E — Evidence（证据）**：有什么证据？测试输出片段/命令输出/日志/代码位置行号/数据对比表/截图描述
- **T — Thinking（推理）**：为什么这样判断？推理链条——从现象→排查→排除→定位→论证的逻辑链
- **R — Risk（风险）**：还有什么风险或限制？未覆盖场景/副作用/假设前提/已知何时会失效

**自检方法**：在拼装报告时，逐条扫描关键结论。任何一个结论缺少 E/T/R → 回退对应步骤补充。

**不合格示例**：
> "测试通过，功能正常，代码质量符合要求。"

**合格示例**：
> **[E]** `go test -v -run TestAuth ./auth/...` — 12 passed / 0 failed。关键输出：`TestLoginExpired: PASS (0.32s)`。
> **[T]** 这 12 个测试覆盖了正常登录、token 过期重试、EOF 退出、弱网降级、非法输入 5 类场景——是本次改动涉及的全部代码路径。
> **[R]** 未覆盖：极弱网（<100KB/s）下重试是否足够——未模拟此环境。缓解：重试失败降级为匿名访问。

## 🆕 v2.9 Anti-Memory Rule — 禁止凭记忆写报告

SUM 不得凭上下文自由发挥生成最终报告。**必须基于每个步骤的结构化 step_output 拼装报告。**

### 执行规则

1. 从 `all_step_outputs` 中提取每步骤的完整产出
2. 按报告模板将各步骤产出填入对应章节
3. **不可凭记忆**补写、概括、或省略步骤产出
4. 如果某步骤 step_output 不满足 MCR+（见编排中枢 §6 MCR+ 表）→ **回退该步骤补产出**，不可在 SUM 阶段自行补充
5. 报告中的任何结论必须能追溯到某个 step_output 的具体字段

**反例**：
- ❌ "CODE 阶段修改了 auth.go，增加了重试逻辑，通过了测试" —— 凭记忆概括，丢弃了详细产出
- ✅ SUM 从 code_output.files_changed 中提取变更表，从 code_output.code_excerpts 中提取代码摘录，从 examine_output.test_results 中提取测试数据

## 🆕 v2.9 Anti-Fluff Gate — 水文检测闸门（铁律 #27）

在调用 `write_final_report` **之前**，必须执行水文检测。加载 `skills/sum-session/references/anti-fluff-gate.md` 并按其规则逐段扫描。

### 执行流程

1. 加载 `references/anti-fluff-gate.md`
2. 获取待写入的完整报告内容
3. 按 6 类水文信号逐类扫描：
   - 类别1：空泛结论（关键词匹配）
   - 类别2：无证据通过（"通过"前后3行无命令/输出/位置）
   - 类别3：无位置描述（代码实体出现但无文件+函数+行号）
   - 类别4：无取舍（方案后无替代方案）
   - 类别5：无风险（报告无风险/限制章节）
   - 类别6：SelfCheck放水（<8问/无反事实/无认知缺口/含模糊词未追问）
4. 汇总命中项 → 输出检测报告
5. 按判定规则处理

### 判定规则

| 深度 | 闸门类型 | 命中处理 |
|------|---------|---------|
| **detailed** | **HARD GATE** | 拒绝写入 → 输出命中清单 → 回退补充 → 重新检测（最多2轮） |
| **standard** | **SOFT GATE** | 展示命中清单 → 用户确认是否继续 |
| **brief** | 跳过 | 标注 "⚠️ 简要摘要 — 未经水文检测，不适合工程追溯" |

### 检测报告格式

见 `references/anti-fluff-gate.md` §4。

## 🆕 v2.9 Peer Review Readiness — 同行审查就绪

在 Anti-Fluff Gate 通过后、写入前，执行六问自检。加载 `skills/sum-session/references/peer-review-standard.md`。

**六问**：
1. 另一个工程师能否根据报告复现问题？
2. 能否定位到改动代码？
3. 能否知道为什么这么改？
4. 能否知道测试覆盖了什么？
5. 能否知道还有什么没有覆盖？
6. 能否判断这次改动能不能合并？

**判定**：detailed→任一为否则拒绝写入。standard→用户确认。brief→跳过。

## 🆕 v2.9 Quality Scoring — 文档质量评分

加载 `skills/sum-session/references/quality-scoring.md`，对报告进行 100 分制评分。

**评分维度**：需求与背景 15 / 根因方案推理 20 / 代码位置与摘录 15 / 测试证据 20 / 风险与取舍 15 / SelfCheck拷打质量 15

**闸门**：detailed engineering_record <80分 → 禁止写入。standard <60分 → 警告+用户确认。

## 🆕 v2.9 Write-then-Fetch Verification — 写后验证

写入文档之后，**必须 fetch 回读**，验证内容完整性。

### 验证项

1. 内容未被截断（回读内容与写入内容比对）
2. 代码块格式正确（fenced code block 完整）
3. 表格完整（行列对齐，无破损）
4. 特殊字符无乱码（中文/emoji/ANSI/特殊符号）
5. 所有步骤产出均可见（READ/CODE/REVIEW/EXAMINE/GIT/GRAPH/SUM/TALK/SELFCHECK/ASK 章节齐全）

### 修复循环

如发现变形/截断 → 修复问题 → 重新写入 → 重新 fetch 验证（最多 3 轮）。3 轮后仍不通过 → 挂起用户，报告具体问题。

### 后端差异

| 后端 | fetch 方式 |
|------|-----------|
| local_html | `Read` 回读 HTML 文件 |
| markdown | `Read` 回读 .md 文件 |
| lark_doc | MCP `lark-cli` 读取文档内容 |

## 🆕 v2.10 Document Modes — 双模文档结构

EasyWork 产物支持两种文档模式。**Mode B（持续维护）是默认模式**。

### Mode A — 审计日志模式（Audit Log）

- 结构：`# 标题 ## 0. 版本索引 ## Run <date> v<N> ### 1. READ ### 2. CODE ... ## Run <date> v<N+1> ### 1. READ ...`
- 每个 Run 是自包含的完整 READ→CODE→REVIEW→EXAMINE→... 链路
- **仅在用户明确要求时使用**（"保留完整审计日志""审计模式""每次完整记录"）

### Mode B — 持续维护模式（Continuous Maintenance）

- 结构：`# 标题 ## 0. 版本索引 ## 1. READ ### v1 — date（初始）### v3 — date（补充）## 2. CODE ### v1 — date（初始）### v2 — date（变更）...`
- **默认模式**。新文档一律使用 Mode B
- 每个流程节点只出现一次，节点下按版本分层
- 版本号全局递增，只在有变更的节点下出现
- **不允许**重复顶层流程节点
- **不允许**独立的 `## 📝 更新记录` 块

### 模式选择

1. 检查是否存在已有产物文档 → Fetch
2. 解析已有文档拓扑 → 识别模式（Mode A / Mode B / 混乱）
3. 已有 Mode A → 保持 Mode A（追加新 Run）
4. 已有 Mode B → 保持 Mode B（节点内版本追加）
5. 新文档 → **Mode B**
6. 用户显式指示 → 按指示选择

> 完整模式定义、结构模板、选择决策树、Mode A→B 转换规则详见 `references/document-modes.md`。

---

## 🆕 v2.10 Document Topology Gate — 文档拓扑闸门（铁律 #28）

在 write_final_report **之前**，检查文档拓扑结构是否合法。加载 `skills/sum-session/references/document-topology-gate.md`。

### 七项拓扑检查

| # | 检查项 | 违规信号 | Mode B | Mode A |
|---|--------|---------|--------|--------|
| 1 | 重复顶层流程节点 | ≥2 个 `## 1. READ` 等 | **阻断→合并** | 允许 |
| 2 | 模式混用 | 同时存在 `## Run` 和 `## 1. READ` | **阻断→统一** | **阻断→统一** |
| 3 | 版本索引缺失 | Mode B 无 `## 0. 版本索引` | **阻断→补建** | N/A |
| 4 | 本轮内容未入节点 | 改动在"更新记录"块而非节点下 | **阻断→重分配** | 允许 |
| 5 | 孤儿更新记录块 | Mode B 顶层有 `## 📝 更新记录` | **阻断→拆入节点** | 允许 |
| 6 | 历史与当前混淆 | 过时内容无版本标记 | WARN→标注 | WARN→标注 |
| 7 | 索引与实际不一致 | 索引声称的版本节点内缺失 | **阻断→修复索引** | N/A |

### 判定规则

| 深度 | 闸门类型 | 命中处理 |
|------|---------|---------|
| **detailed** | **HARD GATE** | 拒绝写入 → 自动执行 structural merge repair → 重新检测（最多 2 轮） |
| **standard** | **SOFT GATE** | 展示违规清单 → 用户确认（默认修复） |
| **brief** | 跳过 | 标注 "⚠️ 简要摘要 — 文档拓扑未经检查，不适合工程追溯" |

### 自动修复能力

以下违规自动修复，不阻塞流程：
- 重复节点合并（算法 2）
- 孤儿更新记录→节点迁移（算法 1）
- 版本索引补建/修复（算法 3）
- 历史/当前区分标注

需用户确认的修复：
- 模式混用统一（需选择目标模式）
- Mode A→B 转换（不可逆）

> 完整检测规则、解析算法、修复算法详见 `references/document-topology-gate.md`。

---

## 🆕 v2.10 Structured Merge — 结构化合并流程

Mode B 下，每次更新执行 6 步结构化合并，**替代** v2.8 的"文档末尾追加更新记录"。

### Step 1 — Fetch 现有文档

- 通过后端接口读取已有文档完整内容
- 本地文件 → `Read`；飞书文档 → MCP lark-cli

### Step 2 — 解析拓扑结构

- 识别文档模式（Mode A / Mode B / 混乱）
- 提取所有顶层节点及其子版本
- 提取版本索引表，记录当前最大版本号

### Step 3 — Topology Gate 预检

- 执行 7 项拓扑检查
- 如命中违规 → 先执行结构修复 → 重新解析拓扑

### Step 4 — 按节点分配本轮内容

从 `all_step_outputs` 提取各步骤产出，分配到对应流程节点下：
- `read_output` → `## 1. READ` 下新增 `### v{N} — {date}（{变更类型}）`
- `code_output` → `## 2. CODE` 下
- `review_output` → `## 3. REVIEW` 下
- `examine_output` → `## 4. EXAMINE` 下
- ...以此类推（GIT→5, GRAPH→6, SUM→7, TALK→8, SELFCHECK→9, ASK→10）
- 被跳过的步骤不追加；未变更的步骤不追加（不写"无变更"占位）
- 首次创建该节点 → "初始"标签；修改已有内容 → "变更"标签

### Step 5 — 更新版本索引

- 在 `## 0. 版本索引` 表格追加新行（最新版本在最前）
- 标注影响节点、变更摘要、日期
- 更新"当前版本"字段

### Step 6 — 标注过时内容

- 旧版本小节前方追加 `[已过时 — v{N} 起]` 标记
- 不删除旧内容——保留演进历史
- 仅在涉及"修改已有结论"（非纯新增）时标注

### Mode A 差异

Mode A 不执行 structured merge。每次新任务 → 新 Run 块追加在版本索引之后、已有 Run 之前。

> 完整流程、版本号规则、变更类型标签、新文档初始化模板详见 `references/document-modes.md`。

---

## 🆕 Gotchas 候选检查（v2.4）

在 SUM 阶段，Agent 必须检查本次工作流是否满足 4 种 Gotchas 触发条件：

1. 耗时 >10 分钟定位的 bug
2. "看起来没问题"的写法导致实际 bug（反直觉陷阱）
3. 用户指出了 Agent 忽略的边界情况
4. 同一文件/模式在不同 session 中被反复问及

**如满足任一条件** → 生成 Gotchas 候选条目，展示给用户：

```
【Gotchas 候选】（待确认后写入 references/gotchas.md）

### {标题}
- **触发条件**：...
- **错误表现**：...
- **根因**：...
- **正确做法**：...
- **关联模块**：...
- **首次发现**：{日期} — {场景}

是否追加？→ 回复"确认"或"修改 {具体调整}"
```

**用户确认后**才写入 `references/gotchas.md`。未确认的候选记录在 SUM 产出中。

> 详见 `../fullchain-dev-workflow/references/security-policy.md` §6。

## 🆕 内容丰满度自检闸门 — MCR Gate（v2.7）

在调用 write_final_report 之前，SUM 必须执行 MCR 自检。

### 执行流程

1. 读取 report_depth（从 data-contract 顶层字段 `report_depth.level`）
2. 如果 report_depth = brief → 跳过此闸门
3. 逐步骤对照 MCR 表（见编排中枢 §6 "最小内容要求(MCR)表"）检查：
   - READ: 5项 → 检查 read_output 是否含 business_background / user_persona / mvp_scope / acceptance_criteria（≥2-3条）/ non_goals（≥1条）
   - CODE: 5项 → 检查 code_output 是否含 files_changed 表 / design_rationale / key_functions（≥2）/ edge_case_handling（≥1）/ code_excerpts（≥1段，含路径+行号）
   - REVIEW: 3项 → 检查 review_output.dimensions 每维度是否有 checkpoints（≥2条）/ blocking_issues_detail（有详情或说明为什么没有）/ issues 含代码位置
   - EXAMINE: 4项 → 检查 examine_output 是否含 test_command / test_coverage_matrix / test_output_snippet（非"全部通过"）/ uncovered_scenarios（≥1个含原因）
   - GIT: 5项 → 检查 git_output.units 每单元是否含 business_context / risk_introduced / verification_evidence / developer_checklist（5项齐全）
   - SELFCHECK: 3项 → 检查 selfcheck_output 是否含 cto_qa_transcript / gaps_identified（≥1或说明为什么没有）/ 每个gap有remediation
4. 记录检查结果到 sum_output.mcr_gate_result

### 判定

| 深度 | 闸门类型 | 不通过处理 |
|------|---------|-----------|
| detailed | **HARD GATE** | 拒绝写入 → 输出缺失清单 → 回退到标记步骤补充 → 重新自检。最多回退 2 轮。2 轮后仍不通过 → 挂起报告用户，列出已满足项和仍缺失项 |
| standard | **SOFT GATE** | 缺失项记录警告 → 在 SUM 产出中标注"以下 MCR 项未满足" → 允许写入但注明不完整 |
| brief | 跳过 | — |

### MCR 自检输出格式

```
【MCR 自检闸门】— report_depth={detailed/standard}

| 步骤 | 状态 | 缺失项 | 处理 |
|------|------|--------|------|
| READ | ✅ | — | — |
| CODE | ❌ | design_rationale, code_excerpts | 回退补充 |
| REVIEW | ✅ | — | — |
| EXAMINE | ⏭️ | 步骤已跳过 | — |
| GIT | ✅ | — | — |
| SELFCHECK | ❌ | cto_qa_transcript | 回退补充 |

总体判定：fail → 回退到 CODE、SELFCHECK 补充缺失内容
```

## 🆕 流式增量写入保障（v2.7）

### 策略

**后端支持流式追加（streaming: true，如 lark-doc）**：
- 每步骤完成后立即调用 write_step_output 追加到文档
- write_final_report 追加 SUM 六要素总结 + TALK + SELFCHECK + ASK + 文档尾注
- **不替换**已追加的步骤详情——文档可从前到后完整阅读

**后端不支持流式追加（streaming: false，如 local-html/markdown）**：
- 每步骤完成后在内存中保留**完整结构化产出**（不可精简为摘要）
- write_final_report 时将所有步骤的完整产出一次性写入
- **禁止**在最终报告中用"详见上文"或浓缩摘要替代步骤详情
- 确保最终报告可独立阅读——另一个工程师无需追问即理解完整上下文

### 禁止的反模式

- ❌ 流式后端：write_final_report 时替换/覆盖已追加的步骤详情
- ❌ 非流式后端：write_final_report 时只写 SUM 六要素，省略 READ/CODE/REVIEW 等步骤产出
- ❌ 任何后端：以"上下文不足"为由产出"浓缩版"替代完整步骤产出
- ❌ detailed 模式下产出 brief 级别的内容——深度不可自动降级

## 🆕 产物后端适配（v2.5）

SUM 步骤不再硬编码生成 HTML。Agent 调用当前激活的产物后端适配器完成最终报告写入。

### 执行流程

0. **🆕 v2.10 Document Mode Selection**：检查已有文档 → 确定 Mode A/B → 新文档默认 Mode B
0.5 **🆕 v2.10 Structured Merge**（Mode B）：Fetch 现有文档 → 解析拓扑 → 分配本轮内容到节点
1. **🆕 v2.9 Anti-Memory Rule**：确认报告是从 step_output 拼装（非凭记忆），任一步骤 MCR+ 不满足则回退
2. **执行 MCR 自检闸门（🆕 v2.7）**：调用 MCR Gate，detailed 模式必须通过才能继续
3. **🆕 v2.9 ETR 自检**：逐条扫描关键结论，确认 Evidence / Thinking / Risk 齐全
4. **🆕 v2.9 Anti-Fluff Gate**：加载 anti-fluff-gate.md，6 类水文信号逐类扫描 → HARD/SOFT GATE 判定
5. **🆕 v2.9 Peer Review Readiness**：加载 peer-review-standard.md，六问自检 → HARD/SOFT GATE 判定
6. **🆕 v2.9 Quality Scoring**：加载 quality-scoring.md，100 分制评分 → 闸门判定
7. **🆕 v2.10 Document Topology Gate（铁律 #28）**：加载 document-topology-gate.md，7 项拓扑检查 → HARD/SOFT GATE 判定。命中→structured merge repair
8. **确定当前后端**：从 data-contract 的 `output_backend` 字段读取（编排中枢在任务分类后确定）
9. **加载后端 SKILL.md**：读取 `../fullchain-dev-workflow/backends/{output_backend.output_format}/SKILL.md`
10. **调用 write_final_report**：按后端定义的指令，将全部 10 步产出写入产物容器
    - 传入：`doc_id`、`all_step_outputs`、`sum_output`、`skipped_steps`
    - 🆕 v2.7 传入：`report_depth`、`report_type`、`mcr_gate_result`、`streaming_status`
    - 🆕 v2.9 传入：`anti_fluff_gate_result`、`peer_review_ready`、`quality_score`
    - 🆕 v2.10 传入：`document_mode`、`topology_gate_result`、`structured_merge_plan`
11. **🆕 v2.9 Write-then-Fetch**：写入后 fetch 回读 → 验证完整性 → 修复循环（如需）
12. **调用 get_share_link**：获取可分享链接（如有），记录到 `output_share_link` 字段
13. **降级处理**：后端写入失败时，降级到 local_html 并记录错误

### 后端间差异

| 后端 | 写入方式 | 分享链接 |
|------|---------|---------|
| local_html | 生成自包含 HTML 文件到 `.claude/easywork/` | 本地文件路径 |
| markdown | 生成 .md 文件到 `.claude/easywork/` | 本地文件路径 |
| lark_doc | 通过 MCP 飞书 API 创建/追加文档 | 飞书文档 URL |

### 写作规范

所有后端的最终报告**必须**遵守 `../fullchain-dev-workflow/references/doc-writing-guide.md` 中的写作规范：
- 中文业务复盘口吻，像人工撰写
- 不在正文中使用反引号包裹文件名/命令名
- 段落自然，标题下最多 4 个子标题
- 表格仅用于结构化数据，不用于布局
- 命令集中展示，归类加说明

> 详见 `../fullchain-dev-workflow/references/output-backends.md`。

## 🆕 SELFCHECK 拷打预警（v2.6）

以上六要素总结将在 **SELFCHECK 步骤**接受 CTO 拷打。Agent 会以 CTO 角色对你的以下方面进行深度盘问：

- **业务背景**：你写下的"为什么做"是否经得起追问？有数据吗？还是编的？
- **发现过程**：你说"定位到代码行"——怎么定位的？排查路径清晰吗？
- **解决方案**：你说"选方案 A"——考虑过方案 B 吗？为什么不用？
- **最终效果**：你说的"效果"有数据支撑吗？还是自己觉得没问题？

**在写这份总结时，就想清楚这些问题。** 不要在 SELFCHECK 阶段被 CTO 问住。`../self-check/SKILL.md` 中有完整的拷打问题清单——建议你先看一眼，确保每个问题你都能回答。

---

## 🆕 HTML 报告脱敏检查（v2.4，v2.5 扩展至所有后端）

Agent 在生成最终报告后、保存前，**必须执行脱敏自检**。不论使用何种后端，报告/产物不得包含：

- API Key / Token / Secret / 密码（明文）
- 完整认证日志（>80 字符）
- 内部 URL / 内网 IP
- 大段源码（单个代码块 >30 行）
- 手机号 / 邮箱 / 用户帐号
- 数据库连接串

发现以上任一内容 → 立即脱敏，再保存文件。

> 详见 `../fullchain-dev-workflow/references/security-policy.md` §2。
