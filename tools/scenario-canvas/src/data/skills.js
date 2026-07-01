// 28 skills with phase grouping, ports, visual config, and human-readable descriptions

export const PHASE_COLORS = {
  understand: '#3b82f6',
  'deep-dive': '#10b981',
  fix: '#ef4444',
  verify: '#f59e0b',
  summarize: '#8b5cf6',
  deliver: '#f97316',
};

export const PHASE_LABELS = {
  understand: '🧠 理解类',
  'deep-dive': '🔬 深挖类',
  fix: '🔴 实现类',
  verify: '🟡 验证类',
  summarize: '🟣 总结类',
  deliver: '🟠 交付类',
};

export const PHASE_ORDER = ['understand', 'deep-dive', 'fix', 'verify', 'summarize', 'deliver'];

export const SKILLS = {
  // ── 理解类 ──
  'read-project': {
    emoji: '📐', label: '项目理解', phase: 'understand',
    desc: '分析项目整体结构、模块依赖和技术栈，输出架构概览和建议的代码追踪目标。',
    inputs: [], outputs: [],
  },
  'read-paper': {
    emoji: '📖', label: '论文阅读', phase: 'understand',
    desc: '阅读并分析技术论文/文档，提取关键观点、方法、结论，生成结构化论文报告。',
    inputs: [], outputs: [],
  },
  'read-requirements': {
    emoji: '👁️', label: '需求理解', phase: 'understand',
    desc: '解析产品需求文档或用户描述，识别模糊点、冲突和隐含假设，输出结构化需求规格。',
    inputs: [], outputs: [],
  },
  'tech-radar': {
    emoji: '🛰️', label: '技术雷达', phase: 'understand',
    desc: '扫描指定技术领域的现状、趋势、竞品，识别值得深入调研的方向。',
    inputs: [], outputs: [],
  },
  'learn-from-zero': {
    emoji: '🧠', label: '从零学习', phase: 'understand',
    desc: '用 ELI5→新手→熟练→专家四个层次解释一个陌生概念，帮你快速建立认知。',
    inputs: [], outputs: [],
  },

  // ── 深挖类 ──
  'trace-code': {
    emoji: '🔬', label: '代码追踪', phase: 'deep-dive',
    desc: '从入口函数出发，逐层追踪完整调用链，记录每层的数据流转和关键逻辑。',
    inputs: [], outputs: [],
  },
  'requirement-decompose': {
    emoji: '🧩', label: '需求拆解', phase: 'deep-dive',
    desc: '把一条复杂需求拆解成可独立执行的子任务，标注优先级和依赖关系。',
    inputs: [], outputs: [],
  },

  // ── 实现类 ──
  'code-implement': {
    emoji: '✏️', label: '代码实现', phase: 'fix',
    desc: '根据需求和上下文，生成符合项目规范的代码实现，包括类型定义、逻辑和注释。',
    inputs: [], outputs: [],
  },
  'article-write': {
    emoji: '📝', label: '文档编写', phase: 'fix',
    desc: '根据结构化内容生成格式化的技术文档、API 文档或操作手册。',
    inputs: [], outputs: [],
  },
  'slash-cmd': {
    emoji: '💻', label: '命令管理', phase: 'fix',
    desc: '管理 EasyWork 斜杠命令的创建、更新、删除，确保命令文件格式规范。',
    inputs: [], outputs: [],
  },
  'scenario-builder': {
    emoji: '🏗️', label: '场景构建', phase: 'fix',
    desc: '根据模板和节点配置，构建可供场景执行引擎运行的 YAML 场景定义。',
    inputs: [], outputs: [],
  },

  // ── 验证类 ──
  'code-review': {
    emoji: '🔍', label: '代码审查', phase: 'verify',
    desc: '七维度代码审查：正确性、安全性、性能、可维护性、兼容性、可测试性、可读性。',
    inputs: [], outputs: [],
  },
  'examine-quality': {
    emoji: '🧪', label: '测试验证', phase: 'verify',
    desc: '生成并执行测试用例，覆盖正常路径、边界条件、异常情况和回归场景。',
    inputs: [], outputs: [],
  },
  'test-coverage': {
    emoji: '🧪', label: '测试覆盖', phase: 'verify',
    desc: '分析指定模块的测试覆盖率，识别未测试的代码路径和风险区域。',
    inputs: [], outputs: [],
  },
  'checklist': {
    emoji: '✅', label: '清单审计', phase: 'verify',
    desc: '按检查清单逐项审计代码或流程，输出通过/失败/不适用结果和修复建议。',
    inputs: [], outputs: [],
  },
  'tech-compare': {
    emoji: '⚖️', label: '技术选型', phase: 'verify',
    desc: '多维度对比多个技术方案，生成评分矩阵和推荐结论，E/T/R 证据支撑。',
    inputs: [], outputs: [],
  },
  'api-test': {
    emoji: '🔌', label: '接口测试', phase: 'verify',
    desc: '根据 API 规格自动生成测试请求，验证响应结构、状态码和边界行为。',
    inputs: [], outputs: [],
  },

  // ── 总结类 ──
  'graph-fullchain': {
    emoji: '📊', label: '架构可视化', phase: 'summarize',
    desc: '将代码结构或调用链转换为 Mermaid 架构图、流程图、序列图或 ER 图。',
    inputs: [], outputs: [],
  },
  'sum-session': {
    emoji: '📋', label: '总结报告', phase: 'summarize',
    desc: '汇总所有上游节点的产出（审查报告、测试结果、图表），生成一份完整的项目总结。',
    inputs: [], outputs: [],
  },
  'talk-retro': {
    emoji: '🧠', label: '复盘分析', phase: 'summarize',
    desc: '对故障、事故或项目问题做结构化复盘：时间线还原 → 根因分析 → 改进措施。',
    inputs: [], outputs: [],
  },
  'self-check': {
    emoji: '🥊', label: 'CTO拷打', phase: 'summarize',
    desc: '模拟 CTO 视角，对产出物做尖锐质疑和压力测试，找出逻辑漏洞和未覆盖风险。',
    inputs: [], outputs: [],
  },
  'diagram-generator': {
    emoji: '🎨', label: '图表生成', phase: 'summarize',
    desc: '多引擎图表生成（Figma > Excalidraw > D2 > Draw.io > Mermaid），自动选最优引擎。',
    inputs: [], outputs: [],
  },

  // ── 交付类 ──
  'git-split-commit': {
    emoji: '📦', label: '提交拆分', phase: 'deliver',
    desc: '将代码变更拆分成多个语义清晰的 Git commit，每个 commit 有规范的 message。',
    inputs: [], outputs: [],
  },
  'ask-change-questions': {
    emoji: '❓', label: '变更确认', phase: 'deliver',
    desc: '在提交前做最终确认：变更范围是否正确？是否有遗漏？是否需要同步更新文档/测试？',
    inputs: [], outputs: [],
  },
  'knowledge-base': {
    emoji: '📚', label: '知识沉淀', phase: 'deliver',
    desc: '将本次会话中的关键发现、技术决策、踩坑记录写入知识库，下次可复用。',
    inputs: [], outputs: [],
  },
  'quick-answer': {
    emoji: '⚡', label: '快问快答', phase: 'deliver',
    desc: '快速回答一个具体的技术问题，不做展开分析，直接给答案。',
    inputs: [], outputs: [],
  },
  'scenario-runner': {
    emoji: '▶️', label: '场景执行', phase: 'deliver',
    desc: '按场景定义执行完整工作流：DAG 拓扑排序 → 并行执行 → HITL 交互暂停。',
    inputs: [], outputs: [],
  },
};
