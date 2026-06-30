# Scenario ↔ Pipeline / Meta 集成桥梁

> v3.1 · 场景（Scenario）与现存点-线-网模型的三层集成

## 1. 三层关系

```
                   ┌──────────────────────────┐
                   │  🎨 场景画布 (canvas.html) │← 视觉层
                   │  拖拽 · 连线 · 配置 · 保存  │
                   └──────────┬───────────────┘
                              │ 读写 YAML
                   ┌──────────▼───────────────┐
                   │  📋 scenarios/*.yaml      │← 数据层
                   └──────────┬───────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
 🎯 Point Mode         🔗 Line Mode          🌐 Net Mode
 单技能                场景→Pipeline          场景→自治扩散种子
```

## 2. 场景 → 线模式（Pipeline）

Pipeline Composer 可将场景 YAML 作为输入直接执行：

```
加载 pipeline-composer.md
  → 检查 input 是否为有效的 scenario YAML 路径
  → 解析 YAML → 提取 nodes + edges
  → 拓扑排序 → 按顺序执行
  → 场景的 interaction_point 映射为 HITL 暂停
```

## 3. 场景 → 网模式（Meta）

Meta-Orchestrator 可将场景作为种子图进行自治扩散：

```
加载 meta-orchestrator.md
  → seed_scenario = scenarios/library/new-project-handover.yaml
  → 场景 DAG 作为初始技能图
  → 每个节点完成后检测扩散信号
  → 可扩散到场景以外的技能（如 tech-radar, talk-retro）
  → 收敛条件满足时停止
```

## 4. 场景触发词匹配

场景的 `situation.trigger_examples` 注册到编排中枢的自然语言匹配表：

| 用户自然语言 | 匹配场景 |
|------------|---------|
| "我刚接手这个项目" | new-project-handover |
| "线上报错了帮我排查" | bug-localization |
| "这个接口好慢" | performance-tuning |
| "帮我对比一下技术方案" | tech-stack-evaluation |
| "帮我做安全审计" | security-audit |
| "准备上线了" | pre-release-checklist |
| "帮我学习 Docker" | learning-new-domain |
