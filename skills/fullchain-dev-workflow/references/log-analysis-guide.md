# JSONL 日志分析指南

> **🆕 v2.4 安全约束**：`workflow.log.jsonl` 只允许记录 7 个固定字段（session/step/status/skipped/tokens_est/duration_s/ts），
> 禁止包含文件名、函数名、改动内容、测试输出、错误日志详情、包名、URL 等任何项目具体信息。
> 详见 `references/security-policy.md` §2。

本文档帮助团队从 `.claude/easywork/workflow.log.jsonl` 中提取洞察，持续优化 EasyWork 的使用效率。

---

## 日志格式

每行一条 JSON，每步完成时追加：

```json
{"session":"20260619-task-001","step":"REVIEW","status":"pass","skipped":false,"tokens_est":4500,"duration_s":42,"ts":"2026-06-19T15:30:00Z"}
```

---

## 基础查询

### 统计总执行次数

```bash
wc -l .claude/easywork/workflow.log.jsonl
```

### 按步骤统计执行次数

```bash
cat workflow.log.jsonl | jq -r '.step' | sort | uniq -c | sort -rn
```

预期输出（9 步全执行的情况）：
```
3 READ
3 CODE
3 REVIEW
2 EXAMINE
2 GIT
1 GRAPH
1 SUM
1 TALK
1 ASK
```
> READ/CODE/REVIEW 次数可能偏高——回退修复导致的重复执行。

### 按 session 分组

```bash
cat workflow.log.jsonl | jq -r '.session' | sort | uniq -c | sort -rn
```

---

## 性能分析

### 各步骤平均耗时（秒）

```bash
cat workflow.log.jsonl | jq -r 'select(.skipped==false) | [.step, .duration_s] | @tsv' | awk '{sum[$1]+=$2; count[$1]++} END {for(s in sum) printf "%s\tavg=%.0fs\tn=%d\n", s, sum[s]/count[s], count[s]}' | sort -t'=' -k2 -rn
```

### 找出耗时异常的步骤（超过平均值 2 倍）

```bash
cat workflow.log.jsonl | jq -r 'select(.skipped==false) | [.step, .duration_s] | @tsv' | awk 'BEGIN {while(getline<"workflow.log.jsonl"){split($0,a,"\""); if(a[10]=="duration_s"){sum+=a[12];n++}}} {if($2 > (sum/n)*2) print $0}'
```

### 找出最耗 token 的步骤

```bash
cat workflow.log.jsonl | jq -r 'select(.skipped==false) | [.step, .tokens_est] | @tsv' | sort -t$'\t' -k2 -rn | head -5
```

---

## 质量分析

### 各步骤通过率

```bash
cat workflow.log.jsonl | jq -r '[.step, .status] | @tsv' | awk '{total[$1]++; if($2=="pass") pass[$1]++} END {for(s in total) printf "%s\t%.0f%%\n", s, (pass[s]/total[s])*100}'
```

预期：REVIEW 和 EXAMINE 通过率可能偏低（需要回退修复），其余步骤应 >90%。

### 跳过率最高的步骤

```bash
cat workflow.log.jsonl | jq -r 'select(.skipped==true) | .step' | sort | uniq -c | sort -rn
```

如果 GRAPH 和 TALK 跳过率 >80%，说明团队可能以微调和 Bug 修复为主——考虑降级到 L2 成熟度。

### 阻断率（status=blocked）

```bash
cat workflow.log.jsonl | jq -r 'select(.status=="blocked") | [.step, .session] | @tsv'
```

如果 CODE 频繁 blocked，可能是需求理解不够深（READ 阶段问题）。如果 EXAMINE 频繁 blocked，可能是测试环境不稳定。

---

## 会话分析

### 平均一个会话完成多少步骤

```bash
cat workflow.log.jsonl | jq -r '.session' | sort | uniq -c | awk '{sum+=$1; n++} END {printf "平均 %.1f 步/会话, 共 %d 个会话\n", sum/n, n}'
```

### 回退率（CODE 或 REVIEW 重复出现）

```bash
cat workflow.log.jsonl | jq -r 'select(.step=="CODE" or .step=="REVIEW") | [.session, .step] | @tsv' | sort | uniq -c | awk '$1 > 1 {print}'
```

如果同一 session 中 CODE 出现 >2 次，说明回退修复频繁——考虑改进 READ 阶段的深度。

---

## 优化方向

### 基于数据分析的常见优化

| 数据信号 | 含义 | 建议动作 |
|---------|------|---------|
| READ 平均 >60s | 读的文件太多 | 检查是否读了无关文件，收紧搜索范围 |
| CODE 平均 >120s | 改动范围过大 | 建议用户拆分任务 |
| REVIEW status=fail 率 >30% | 审查太松或代码质量差 | 调整审查严格度或检查 CODE 的铁律遵守 |
| GRAPH skip 率 >80% | 简单改动居多 | 考虑降级到 L2 |
| TALK skip 率 >80% | Bug/重构任务少 | 正常——TALK 只在 Bug 和重构时执行 |
| 同一 session CODE 出现 >3 次 | 回退循环 | 检查 READ 是否遗漏了关键约束 |

---

## 可视化建议

如果日志积累超过 50 条，建议导入以下工具做可视化：

- **Datasette**：`datasette workflow.log.jsonl` — 零配置 SQL 查询 + 图表
- **Google Sheets**：JSONL → CSV → 导入 → 数据透视表
- **Observable**：`d3.json("workflow.log.jsonl")` — 灵活的可视化
- **jq + termgraph**：`jq -r '[.step, .duration_s] | @tsv' | termgraph` — 终端柱状图
