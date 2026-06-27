# 📝 Raw Conversation Dumps (Layer 0)

> 全量对话原始转储 · 7 天 TTL · 自动生成 · 不手动编辑
> 最后更新：2026-06-27 | 会话数：0

## 存储规则

- 每次会话结束时，SessionEnd hook 自动将完整工具调用事件写入此目录
- 文件格式：`{YYYYMMDD}/{session-id}.json`
- 保留期限：**7 天**（超期自动清理）
- 此层是"先全部沉淀"的底层——不经筛选，不经加工

## 会话列表

| 日期 | 会话 ID | 领域 | 工具调用数 | 涉及文件数 |
|------|---------|------|-----------|-----------|
| — | — | — | — | — |

## 生命周期

```
raw/ (Layer 0, 7天)
  ↓ 定时巡检清理（/easywork:knowledge 整理知识库）
  ├── 去重合并 → prompts/ + outputs/ (Layer 1, 手动策展)
  ├── 会话总结 → sessions/ (Layer 2, 自动生成)
  └── 模式升级 → patterns/ (Layer 3, 长期知识)
```

## 清理命令

Agent 说"整理知识库"时触发清理流程。详见 `skills/knowledge-base/SKILL.md` §知识维护。
