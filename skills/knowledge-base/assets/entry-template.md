---
id: kb-{{DATE}}-{{SEQ}}
domain: {{DOMAIN}}              # integration | development | quarterly-o
source: {{SOURCE}}              # inner | outer | derived
dimension: {{DIMENSION}}        # prompt | output | analysis | reference | decision
status: draft                   # draft | stable | archived
created: {{TIMESTAMP}}
updated: {{TIMESTAMP}}
session: {{SESSION_ID}}
tags: [{{TAGS}}]
related: [{{RELATED_IDS}}]
source_files: [{{FILES}}]
source_urls: [{{URLS}}]
evidence:
  e: "{{EVIDENCE}}"             # 证据——代码位置/测试输出/日志/数据对比
  t: "{{THINKING}}"             # 推理——从现象到结论的逻辑链
  r: "{{RISK}}"                 # 风险——未覆盖/边界/假设/时效性
---

# {{TITLE}}——一句话概括本条知识的核心发现

## 背景

{{为什么产生这条知识——什么任务/什么问题触发的}}

## 核心内容

{{知识的实质内容——分析结论/代码理解/决策理由/问题解答}}

## 证据链

- **E (Evidence)**：{{证据——代码位置/测试输出/日志/数据对比}}
- **T (Thinking)**：{{推理——从现象到结论的逻辑链}}
- **R (Risk)** ：{{风险——未覆盖/边界/假设/时效性}}

## 关联

- 前置知识：{{kb-xxx——本条知识基于哪些已有条目}}
- 后续知识：{{kb-yyy——哪些条目引用了本条}}
- 矛盾知识：{{如有，标注冲突及解决方式}}

## 时效性

- **基于代码版本**：{{commit hash 或 branch}}
- **预计失效条件**：{{什么变更会导致本条知识需要重新验证}}
- **下次复查日期**：{{YYYY-MM-DD}}
