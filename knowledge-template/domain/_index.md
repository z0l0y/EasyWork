# 📂 领域目录索引

> 领域由用户自定义，定义在 `.easywork/config.json` → `knowledge.domains`。
> 不再硬编码固定领域。初始化时根据 config 动态创建子目录。

## 配置示例

```json
{
  "knowledge": {
    "domains": [
      {"id": "backend", "name": "后端开发", "emoji": "💻", "keywords": ["api", "接口", ...], "ttl_days": 30},
      {"id": "frontend", "name": "前端开发", "emoji": "🎨", "keywords": ["组件", "css", ...], "ttl_days": 30},
      {"id": "data", "name": "数据工程", "emoji": "📊", "keywords": ["数据", "etl", ...], "ttl_days": 60}
    ]
  }
}
```

## 当前领域

| 领域 | 路径 | 条目数 | 说明 |
|------|------|--------|------|
| — | — | — | 由 config.json 动态生成 |

## 使用方式

- 新增领域：编辑 `.easywork/config.json` → `knowledge.domains` 添加新条目
- 删除领域：从 config 中移除对应条目（已有知识内容不会自动删除）
- 调整 TTL：修改对应领域的 `ttl_days` 值
