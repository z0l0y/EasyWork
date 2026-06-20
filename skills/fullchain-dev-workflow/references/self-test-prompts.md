# Skill 自测提示词集

> **用途**：修改 EasyWork 的任何 Skill 文件后，用以下提示词验证工作流是否仍然正确。
> 来自 claude-code-superpowers 的 6 测试质量标准（stranger / trigger / real code /
> before-after / over-application / domain connection）的实践落地。

---

## 测试标准说明

| 测试类型 | 问题 | 验证方式 |
|---------|------|---------|
| **Stranger Test** | 一个不了解 EasyWork 的 Agent 能正确执行吗？ | 给 Agent 任务但不提 EasyWork，看它是否自动加载编排中枢 |
| **Trigger Test** | 关键词触发是否精准（不误触、不漏触）？ | 用边界输入测试意图路由表 |
| **Real Code Test** | 在真实代码库中能否正确产出？ | 在真实项目中跑端到端 |
| **Before/After Test** | 改动前后行为是否一致（不该变的不变）？ | 对比修改前后的分类结果 |
| **Over-Application Test** | 简单任务是否被错误地走了完整流程？ | 用纯理解/微调任务测试是否正确裁剪 |
| **Domain Connection Test** | 步骤间数据传递是否完整？ | 检查每步产出是否被后续步骤正确引用 |

---

## 测试提示词集

### 测试 1：任务分类 — 纯理解

```prompt
用 EasyWork 帮我看下 src/services/auth.service.ts 里的登录流程是怎么实现的，我想理解一下。
```

**预期行为**：
- 用户说"用 EasyWork" → 加载 fullchain-dev-workflow
- 分类为 🔍 纯理解
- 步骤裁剪为：READ → GRAPH → SUM
- 不执行 CODE/REVIEW/EXAMINE/GIT/TALK/ASK
- 进度卡中 2-5、8、10 步标记 `[skip]`

**通过标准**：
- [ ] 仅在"用 EasyWork"触发后才加载（非自动加载）
- [ ] 分类正确（纯理解）
- [ ] 步骤裁剪正确（3步执行，6步跳过）
- [ ] 没有修改任何代码
- [ ] 产出包含 GRAPH（流程图/时序图）

---

### 测试 2：任务分类 — 纯审查

```prompt
用 EasyWork 帮我 review 下最近改的 src/utils/validator.ts，看有没有安全问题。
```

**预期行为**：
- 分类为 🔎 纯审查
- 步骤裁剪为：READ → REVIEW
- 不执行 CODE/EXAMINE/GIT/GRAPH/SUM/TALK/ASK
- 产出七维度审查报告

**通过标准**：
- [ ] 分类正确（纯审查）
- [ ] 只走了 READ + REVIEW 两步
- [ ] 没有修改代码
- [ ] 审查报告覆盖全部 6+1 维度

---

### 测试 3：任务分类 — 微调

```prompt
把 src/config/app.config.ts 里的 API_TIMEOUT 从 5000 改成 10000。
```

**预期行为**：
- 分类为 ⚡ 微调
- 步骤裁剪为：READ → CODE → REVIEW → GIT
- 如果改动 ≤ 2 文件且同维度，GIT 可能也跳过
- 不执行 EXAMINE/GRAPH/SUM/TALK/ASK

**通过标准**：
- [ ] 分类正确（微调）
- [ ] 步骤裁剪正确（4步）
- [ ] 改动精确（只改了 TIMEOUT 值，未碰其他配置）

---

### 测试 4：任务分类 — Bug 修复

```prompt
用户反馈登录接口 /api/auth/login 偶尔返回 500，帮我修一下。
```

**预期行为**：
- 分类为 🐛 Bug修复
- 步骤裁剪为：READ → CODE → REVIEW → EXAMINE → GIT → SUM → TALK → ASK（8步）
- GRAPH 被跳过
- TALK 执行 5-Whys 分析根因

**通过标准**：
- [ ] 分类正确（Bug修复）
- [ ] GRAPH 正确跳过，其余 8 步执行
- [ ] CODE 前请求用户确认 git stash（铁律#10，禁止倒计时）
- [ ] TALK 追溯到系统性根因（非表面原因）
- [ ] 如果 REVIEW 发现安全问题，EXAMINE 自动追加安全测试

---

### 测试 5：任务分类 — 重构

```prompt
把 src/services/ 下的订单处理逻辑重构一下，现在太乱了，但不要改外部行为。
```

**预期行为**：
- 分类为 🔧 重构
- 全部 10 步执行
- GRAPH 必须画图（因为结构有变化）

**通过标准**：
- [ ] 分类正确（重构）
- [ ] 全部 10 步执行（无跳过）
- [ ] GRAPH 产出包含旧架构 + 新架构对比
- [ ] TALK 分析为什么要重构（技术债务根因）

---

### 测试 6：任务分类 — 功能开发

```prompt
给用户表加一个"收藏文章"的功能，包括 API 接口和数据库迁移。
```

**预期行为**：
- 分类为 🚀 功能开发
- 步骤裁剪为：READ → CODE → REVIEW → EXAMINE → GIT → GRAPH → SUM → ASK（8步）
- TALK 正确跳过（功能开发没有现成问题可追问）

**通过标准**：
- [ ] 分类正确（功能开发）
- [ ] TALK 正确跳过（⏭️）
- [ ] GRAPH 产出新功能的流程图/时序图
- [ ] EXAMINE 包含新增功能的测试

---

### 测试 7：上下文管理 — 🟡 预警

```prompt
（在上下文已使用 ~65% 的情况下）
帮我修一下 src/services/payment.service.ts 的支付回调处理逻辑。
```

**预期行为**：
- 正常分类（Bug修复）
- 每步执行前评估上下文
- 输出精简为结构化摘要
- 每步后问"继续？"

**通过标准**：
- [ ] 识别到 🟡 预警状态
- [ ] 精简输出（每步 ≤ 5 行摘要）
- [ ] 每步后主动询问是否继续
- [ ] 至少一次建议保存状态快照

---

### 测试 8：异常处理 — 阻断挂起

```prompt
帮我把整个项目的日志系统从 console.log 改成 winston，所有文件。
```

**预期行为**：
- 分类为 🔧 重构
- READ 阶段识别为高风险（影响范围广）
- 输出干跑预览
- 在 CODE 阶段发现高耦合时挂起询问

**通过标准**：
- [ ] 正确触发干跑预览
- [ ] 高耦合时挂起而非强行修改
- [ ] 给出 3 个选项（硬改/适配器/解耦）
- [ ] 等待用户确认后再继续

---

### 测试 9：回退循环 — 上限控制

```prompt
（构造一个场景：CODE 产出有 bug → REVIEW 发现 → 回退 CODE → 修复后 REVIEW 又发现 → 循环 3 次）
```

**预期行为**：
- 第 1-2 轮：正常回退修复
- 第 3 轮：回退修复后重新审查
- 第 4 轮（如果触发）：挂起，输出所有问题和修复历程

**通过标准**：
- [ ] 回退循环正确计数
- [ ] 第 3 轮后如果仍失败 → 挂起
- [ ] 挂起时报告完整的问题和修复历程
- [ ] 请求用户确认后 git stash pop 恢复修改前状态

---

### 测试 10：干跑预览 — 中高风险

```prompt
重构 src/services/user.service.ts，把里面的业务逻辑拆到独立的 policy 类里。
```

**预期行为**：
- 分类为 🔧 重构（≥7步，触发干跑预览）
- 先输出分类 → 再输出干跑预览 → 等待用户"执行"确认
- 在用户确认前不修改任何代码

**通过标准**：
- [ ] 自动触发干跑预览（因为 ≥7 步）
- [ ] 预览中每步有预计操作、涉及文件、预计产出
- [ ] 在用户说"执行"前没有任何代码变更
- [ ] 预览中有风险提示

---

### 测试 11：v2.3 — 可访问性审查维度

```prompt
帮我在 src/components/LoginModal.vue 里给登录弹窗加一个"记住密码"复选框。
```

**预期行为**：
- REVIEW 阶段七维度审查包含可访问性维度
- 检查：语义化HTML（checkbox用`<input type="checkbox">`）、ARIA、键盘导航、色彩对比
- 纯后端任务则可访问性标注 `not_applicable`

**通过标准**：
- [ ] 审查报告包含 7 个维度
- [ ] 可访问性维度有具体检查项（非空洞的"通过"）
- [ ] 前端代码检查了 ARIA/键盘/色彩

---

### 测试 12：v2.3 — 供应链安全检查

```prompt
给项目加一个数据导出功能，用 exceljs 这个包生成 Excel 文件。
```

**预期行为**：
- CODE 产出 `new_dependencies` 包含 `exceljs`
- REVIEW 阶段自动触发供应链检查（5 步）
- 审查报告 `supply_chain_check` 字段非空

**通过标准**：
- [ ] 供应链检查 5 步全部执行
- [ ] `supply_chain_check.checked = true`
- [ ] 如有 CVE/许可证问题，计入 `blocking_issues`

---

### 测试 13：v2.3 — Conventional Commits

```prompt
修复 src/services/order.service.ts 里订单金额计算错误。
```

**预期行为**：
- GIT 阶段每个拆分单元包含 `commit_message` 字段
- 提交消息遵循 `type(scope): subject` 格式
- 类型正确（Bug修复→`fix`）

**通过标准**：
- [ ] 每个单元有 `commit_message.type`（fix）
- [ ] `commit_message.subject` ≤50字符/25汉字
- [ ] 提交消息可直接用于 `git commit -m`

---

### 测试 14：v2.3 — Gotchas 自动追加

```prompt
（构造 Agent 耗时 >10min 定位的 bug，或用户指出了 Agent 不知道的边界）
```

**预期行为**：
- SUM 步骤自检时检查是否满足 Gotchas 追加条件
- 如满足，自动追加到 `references/gotchas.md`
- 追加格式遵循规范（触发条件/错误表现/根因/正确做法）

**通过标准**：
- [ ] Gotchas 追加条件被正确识别
- [ ] 新 Gotchas 格式完整（4 必填字段）
- [ ] 追加位置在"项目 Gotchas"段落下

---

### 测试 15：v2.3 — 团队策略覆盖

```prompt
（配置 team-policy.md 设置 comment_language: english）
新建 src/services/notification.service.ts 实现邮件通知功能。
```

**预期行为**：
- CODE 阶段注释使用英文
- 干跑预览标注"已加载团队策略"
- 强制规则（MUST）违反时挂起

**通过标准**：
- [ ] 注释语言为英文
- [ ] 违反团队强制规则时挂起
- [ ] 建议规则（SHOULD）触发警告但不阻断

---

### 测试 16：v2.3 — 自定义步骤注入

```prompt
（在 .claude/skills/easywork/custom/ 下放置安全扫描技能）
重构 src/middleware/auth.ts 的认证逻辑。
```

**预期行为**：
- 任务分类后自动扫描 `.claude/skills/easywork/custom/`
- 自定义步骤以 `[+]` 前缀出现在进度卡
- 按 `insert_after` 和 `insert_condition` 正确插入

**通过标准**：
- [ ] 自定义步骤在进度卡显示为 `[+]`
- [ ] 插入位置正确（在 `insert_after` 步骤之后）
- [ ] 触发条件为 false 时标注 `[+][skip]`
- [ ] 自定义步骤失败不阻塞主流程

---

## 追加自定义测试

如果你的团队有特定的工作流变化（如自定义步骤、团队策略覆盖），在此追加对应的测试提示词。

### 添加格式

```markdown
### 测试 N：{场景名称}

```prompt
{提示词}
```

**预期行为**：
- {行为描述}

**通过标准**：
- [ ] {标准1}
- [ ] {标准2}
```

---

## 运行建议

- **每次发布前**：至少运行测试 1-6（覆盖全部 7 种任务类型）
- **修改编排中枢后**：追加运行测试 7-10（上下文/异常/回退/干跑）
- **修改 v2.3 特性后**：追加运行测试 11-16（可访问性/供应链/Conventional Commits/Gotchas/团队策略/自定义步骤）
- **添加新条件分支后**：追加对应的场景测试
- **CI 集成**：将关键测试提示词放入 CI pipeline，用 Claude Code API 批量验证
