# 📚 EasyWork Knowledge Template

> 知识库结构模板 · 提交到 Git · `knowledge/` 是运行时目录（不提交）

## 这是什么

`knowledge-template/` 包含知识库的**骨架结构**（`_index.md` 索引文件）。
运行时 `knowledge/` 目录包含**用户对话数据**，不应提交到 Git。

## 如何初始化

**自动**（推荐）：SessionStart hook 首次启动时自动从模板引导。

**手动**：
```bash
python hooks/knowledge-hooks.py init
```

## 目录结构

```
knowledge-template/
├── README.md              ← 本文件
├── code/                  ← 代码分析
│   └── _index.md
├── decisions/             ← 架构决策 (ADR)
│   └── _index.md
├── domain/                ← 按领域分类
│   ├── integration/       ← 联调需求
│   │   └── _index.md
│   ├── development/       ← 开发需求
│   │   └── _index.md
│   └── quarterly-o/       ← 季度OKR
│       └── _index.md
├── source/                ← 按来源分类
│   ├── inner/             ← 用户提供的资料
│   │   └── _index.md
│   └── outer/             ← Agent搜索的外部资料
│       └── _index.md
├── conversation/          ← 会话存档
│   ├── prompts/           ← 用户提问
│   │   └── _index.md
│   ├── outputs/           ← Agent回答
│   │   └── _index.md
│   ├── raw/               ← Layer 0 原始转储 (7天TTL)
│   │   └── _index.md
│   └── daily/             ← 每日日志
│       └── _index.md
└── sessions/              ← 会话交接记录
    └── _index.md
```

## 重要的安全说明

⚠️ **永远不要**手动添加 `knowledge/` 目录下的文件到 Git。
运行时生成的所有数据（对话内容、代码分析、决策记录）都是**你的私有数据**。

如果想分享某个决策或分析，请手动复制到项目文档中，而不是提交整个 `knowledge/` 目录。
