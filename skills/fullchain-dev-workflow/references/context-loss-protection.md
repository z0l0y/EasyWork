# Context Loss Protection（上下文丢失防护）

> **铁律 #40**：每轮 EasyWork 产出机器可读状态文件 `.claude/easywork/state-v{N}.json`。每次 EasyWork 会话启动时读取此状态文件作为初始上下文。不可仅依赖聊天上下文恢复状态——`/clear` 和 `compact` 会导致信息永久丢失。

---

## 1. 状态文件定义

### 路径

```
{项目根目录}/.claude/easywork/state-v{N}.json
```

其中 `{N}` 为当前版本号（2.12）。

### 格式

JSON。UTF-8 编码。每步完成后增量更新。启动时全量读取。

### 生命周期

```
会话启动 → 读取 state file（如存在）→ 恢复上下文
   ↓
每步完成后 → 写入/更新 state file 对应字段
   ↓
上下文 🟠 警戒（80-95%）→ 强制写入完整快照 → 提示用户 /clear
   ↓
上下文 🔴 危急（>95%）→ 强制写入完整快照 → 停止执行
   ↓
/clear 后新会话 → 重新读取 state file → 从 current_step 继续
   ↓
任务完成（ASK 通过）→ 写入最终 state file → 标注 status: "completed"
```

---

## 2. 状态文件字段规范

### 2.1 task_identity（任务标识）

```json
{
  "task_identity": {
    "task_id": "20260621-fix-login-timeout",
    "task_type": "Bug修复",
    "task_description": "修复登录超时问题：P99 延迟从 2.8s 降到 300ms",
    "created_at": "2026-06-21T10:30:00+08:00",
    "updated_at": "2026-06-21T11:45:00+08:00"
  }
}
```

### 2.2 version_tracking（版本追踪）

```json
{
  "version_tracking": {
    "easywork_version": "2.12",
    "doc_version": "v3",
    "baseline_revision": "abc1234",
    "latest_revision": "def5678",
    "doc_url": "https://xxx.feishu.cn/docx/abc123",
    "doc_mode": "continuous_maintenance",
    "document_scope": "engineering_active",
    "write_mode": "normal"
  }
}
```

### 2.3 artifact_inventory（产出物清单）

```json
{
  "artifact_inventory": {
    "known_artifacts": [
      {
        "type": "doc",
        "path": ".claude/easywork/EasyWork_Report_20260621_103000.html",
        "description": "主产物文档"
      },
      {
        "type": "state_file",
        "path": ".claude/easywork/state-v2.12.json",
        "description": "状态文件"
      },
      {
        "type": "git_commands",
        "path": ".claude/easywork/git-commands.sh",
        "description": "待执行的 Git 命令"
      }
    ]
  }
}
```

### 2.4 gate_progress（闸门进度）

```json
{
  "gate_progress": {
    "current_step": 3,
    "completed_steps": ["READ", "CODE", "REVIEW"],
    "skipped_steps": ["GRAPH"],
    "step_outputs_available": ["read_output", "code_output", "review_output"],
    "rollback_history": [
      {
        "from_step": "REVIEW",
        "to_step": "CODE",
        "round": 1,
        "reason": "阻断性安全问题：SQL 注入风险"
      }
    ],
    "gates_passed": [
      {"gate": "risk_classification", "level": "L2", "passed": true},
      {"gate": "delivery_definition", "passed": true},
      {"gate": "traceability_matrix", "passed": true}
    ],
    "gates_pending": [
      "test_adequacy",
      "environment_fidelity",
      "historical_version_coverage",
      "source_provenance",
      "evidence_ledger"
    ]
  }
}
```

### 2.5 risk_tracking（风险追踪）

```json
{
  "risk_tracking": {
    "risk_level": "L2",
    "open_risks": [
      {
        "id": "RISK-001",
        "description": "并发场景下缓存失效未充分测试",
        "severity": "medium",
        "mitigation": "已在 EXAMINE 阶段计划补充并发测试",
        "status": "open"
      }
    ],
    "repeated_failure_count": 0,
    "repeated_failure_details": []
  }
}
```

### 2.6 evidence_index（证据索引）

```json
{
  "evidence_index": {
    "total_evidence_count": 2,
    "evidence_entries": [
      {
        "id": "EVD-001",
        "conclusion": "登录 P99 延迟 2.8s",
        "type": "TEST_OUTPUT",
        "location": "EXAMINE step output: ab -n 1000 -c 10 /login",
        "reproducible": true,
        "collected_at": "2026-06-21T11:30:00+08:00"
      }
    ],
    "minimum_required": 3,
    "remaining_needed": 1
  }
}
```

### 2.7 execution_state（执行状态）

```json
{
  "execution_state": {
    "status": "in_progress",
    "context_usage_pct": 65,
    "context_warnings": 0,
    "last_step_completed_at": "2026-06-21T11:45:00+08:00",
    "next_step": "EXAMINE",
    "estimated_steps_remaining": 3,
    "session_restart_count": 0
  }
}
```

---

## 3. 读写算法

### 3.1 读取（会话启动时）

```
Algorithm: LOAD_STATE

Input: 项目根目录路径
Output: 恢复的上下文状态 或 null

1. state_path = "{项目根目录}/.claude/easywork/state-v2.12.json"
2. if state_path 不存在:
      return null  // 新任务，无历史状态
3. state = Read(state_path) → 解析 JSON
4. if state.task_identity.updated_at < 24小时前:
      // 旧任务，提示用户
      输出: "发现 24 小时前的状态文件（最后更新：{updated_at}）。
             是继续之前的任务，还是开始新任务？"
      等待用户选择
5. if state.execution_state.status == "completed":
      提示: "上一任务已完成。开始新任务将覆盖状态文件。"
6. 从 state 恢复:
      - task_identity → 设置当前任务上下文
      - version_tracking → 恢复文档版本和 URL
      - artifact_inventory → 恢复已知文件路径
      - gate_progress.current_step → 确定从哪一步继续
      - risk_tracking.open_risks → 恢复未关闭的风险
7. return state
```

### 3.2 写入（每步完成后）

```
Algorithm: SAVE_STATE

Input: 当前 state 对象, 更新的字段
Output: 写入成功确认

1. state.updated_at = now()
2. 更新对应字段:
      - task_identity.updated_at = now()
      - version_tracking.latest_revision = 当前 HEAD
      - gate_progress.current_step = 当前步骤
      - gate_progress.completed_steps.append(刚完成的步骤)
      - gate_progress.gates_passed.append(刚通过的闸门)
      - evidence_index.evidence_entries.append(新收集的证据)
      - execution_state.last_step_completed_at = now()
3. 序列化为 JSON（缩进 2 空格）
4. 写入 .claude/easywork/state-v2.12.json（原子写入：先写 .tmp → rename）
5. 确认写入成功
```

### 3.3 强制写入（上下文🟠/🔴警戒时）

```
Algorithm: FORCE_SAVE

1. 收集所有当前已知信息 → 填充所有 state 字段
2. execution_state.context_usage_pct = 当前上下文使用率
3. execution_state.context_warnings += 1
4. 写入 state file
5. 输出简洁提示:
   "【状态已保存】当前进度已写入 .claude/easywork/state-v2.12.json。
    执行 /clear 后，在新会话中说"继续 EasyWork"即可恢复。"
```

---

## 4. 合并规则

### 新轮次（不同 task_id）

```
if state.task_identity.task_id != 当前 task_id:
    // 新任务
    从 state 读取:
      - version_tracking（复用文档 URL 和版本信息）
      - artifact_inventory.known_artifacts（复用已有文档路径）
    重置:
      - gate_progress（新任务，新闸门）
      - risk_tracking.open_risks（新风险列表）
      - evidence_index（新证据索引）
    保留:
      - version_tracking.baseline_revision（作为历史基线）
```

### 同轮次继续（相同 task_id）

```
if state.task_identity.task_id == 当前 task_id:
    // 从中断处恢复
    current_step = state.gate_progress.current_step
    跳过已完成的步骤（completed_steps 中的步骤）
    从 current_step + 1 继续执行
    恢复已关闭的风险为"已关闭"状态
```

---

## 5. JSON Schema 模板

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EasyWork State File",
  "type": "object",
  "required": ["task_identity", "version_tracking", "gate_progress", "execution_state"],
  "properties": {
    "task_identity": {
      "type": "object",
      "required": ["task_id", "task_type", "created_at"],
      "properties": {
        "task_id": {"type": "string", "pattern": "^[0-9]{8}-[a-z0-9-]+$"},
        "task_type": {"type": "string"},
        "task_description": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    },
    "version_tracking": {
      "type": "object",
      "required": ["easywork_version", "doc_version"],
      "properties": {
        "easywork_version": {"type": "string"},
        "doc_version": {"type": "string"},
        "baseline_revision": {"type": "string"},
        "latest_revision": {"type": "string"},
        "doc_url": {"type": "string"},
        "doc_mode": {"type": "string", "enum": ["audit_log", "continuous_maintenance"]},
        "document_scope": {"type": "string", "enum": ["round_report", "engineering_active"]},
        "write_mode": {"type": "string", "enum": ["quick_fix", "normal", "full_archive"]}
      }
    },
    "artifact_inventory": {
      "type": "object",
      "properties": {
        "known_artifacts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": {"type": "string"},
              "path": {"type": "string"},
              "description": {"type": "string"}
            }
          }
        }
      }
    },
    "gate_progress": {
      "type": "object",
      "required": ["current_step", "completed_steps"],
      "properties": {
        "current_step": {"type": "integer", "minimum": 0, "maximum": 10},
        "completed_steps": {"type": "array", "items": {"type": "string"}},
        "skipped_steps": {"type": "array", "items": {"type": "string"}},
        "step_outputs_available": {"type": "array", "items": {"type": "string"}},
        "gates_passed": {"type": "array"},
        "gates_pending": {"type": "array", "items": {"type": "string"}}
      }
    },
    "risk_tracking": {
      "type": "object",
      "properties": {
        "risk_level": {"type": "string", "enum": ["L0", "L1", "L2", "L3", "L4"]},
        "open_risks": {"type": "array"},
        "repeated_failure_count": {"type": "integer", "minimum": 0},
        "repeated_failure_details": {"type": "array"}
      }
    },
    "evidence_index": {
      "type": "object",
      "properties": {
        "total_evidence_count": {"type": "integer"},
        "evidence_entries": {"type": "array"},
        "minimum_required": {"type": "integer"},
        "remaining_needed": {"type": "integer"}
      }
    },
    "execution_state": {
      "type": "object",
      "required": ["status", "next_step"],
      "properties": {
        "status": {"type": "string", "enum": ["in_progress", "completed", "blocked", "abandoned"]},
        "context_usage_pct": {"type": "integer"},
        "last_step_completed_at": {"type": "string", "format": "date-time"},
        "next_step": {"type": "string"},
        "estimated_steps_remaining": {"type": "integer"},
        "session_restart_count": {"type": "integer"}
      }
    }
  }
}
```

---

## 6. Gate Judgment Rules

| 条件 | 闸门类型 | 处理 |
|------|---------|------|
| 启动时无 state 文件 | **SOFT GATE** | 标注"新任务，无历史状态"，从 READ 开始 |
| 启动时 state 文件存在但 > 24 小时 | **SOFT GATE** | 提示用户：继续旧任务还是开始新任务 |
| 启动时 state 文件存在且 status=completed | **SOFT GATE** | 提示用户：上一任务已完成，新任务将覆盖状态 |
| 上下文中断（/clear）后恢复 | **HARD GATE** | 必须先读取 state file，不可凭记忆继续 |
| state 文件不可读（JSON 解析失败）| **HARD GATE** | 挂起并报告：状态文件损坏，需手动恢复 |
| state 文件字段缺失必填项 | **SOFT GATE** | 警告但允许继续（缺失字段视为 null） |

---

## 7. 反模式

- ❌ **只依赖聊天上下文恢复**：`/clear` 后信息全部丢失，Agent 凭记忆猜测之前的步骤产出
- ❌ **state 文件内容不完整**：只记了 current_step=3，不记 step_outputs 和 artifact 路径——恢复后仍需用户手动告知
- ❌ **state 文件从不更新**：READ 阶段初始化后就不再写入——后续步骤的产出物和风险没有记录
- ❌ **多个 state 文件版本混乱**：新旧版本 state 文件共存，Agent 读了旧版本导致错误恢复
- ❌ **忘记写 state 文件**：Agent 在上下文充足时跳过 STATE SAVE——等到上下文紧张时来不及保存
- ❌ **state 文件当作快照 JSON 用**：把 state 文件的全部内容粘贴到聊天里——state 文件是机器读的，快照是给人读的，两者格式不同
- ❌ **state 文件中的绝对路径**：机器 A 的路径在机器 B 上无效——应使用项目根目录相对路径
