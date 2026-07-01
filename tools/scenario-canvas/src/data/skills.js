// 28 skills with phase grouping, ports, and visual config

export const PHASE_COLORS = {
  understand: '#3b82f6',
  'deep-dive': '#10b981',
  fix: '#ef4444',
  verify: '#f59e0b',
  summarize: '#8b5cf6',
  deliver: '#f97316',
};

export const PHASE_LABELS = {
  understand: '🧠 理解类 (Understand)',
  'deep-dive': '🔬 深挖类 (Deep-dive)',
  fix: '🔴 实现类 (Fix)',
  verify: '🟡 验证类 (Verify)',
  summarize: '🟣 总结类 (Summarize)',
  deliver: '🟠 交付类 (Deliver)',
};

export const PHASE_ORDER = ['understand', 'deep-dive', 'fix', 'verify', 'summarize', 'deliver'];

export const SKILLS = {
  'read-project':       { emoji:'📐', label:'项目理解',     phase:'understand', inputs:[{name:'architecture',type:'object'},{name:'suggested_trace_targets',type:'array'}], outputs:[{name:'architecture',type:'object'},{name:'suggested_trace_targets',type:'array'}] },
  'read-paper':         { emoji:'📖', label:'论文阅读',     phase:'understand', inputs:[{name:'url',type:'string'}], outputs:[{name:'paper_report',type:'object'}] },
  'read-requirements':  { emoji:'👁️', label:'需求理解',     phase:'understand', inputs:[{name:'requirement',type:'string'}], outputs:[{name:'structured_requirement',type:'object'}] },
  'tech-radar':         { emoji:'🛰️', label:'技术雷达',     phase:'understand', inputs:[{name:'topic',type:'string'}], outputs:[{name:'radar_report',type:'object'},{name:'deep_read_targets',type:'array'}] },
  'learn-from-zero':    { emoji:'🧠', label:'从零学习',     phase:'understand', inputs:[{name:'concept',type:'string'}], outputs:[{name:'learning_report',type:'object'}] },
  'trace-code':         { emoji:'🔬', label:'代码追踪',     phase:'deep-dive',  inputs:[{name:'entry_function',type:'string'},{name:'project_report',type:'object'}], outputs:[{name:'trace_report',type:'object'}] },
  'requirement-decompose':{ emoji:'🧩', label:'需求拆解',   phase:'deep-dive', inputs:[{name:'requirement',type:'string'}], outputs:[{name:'decomposed_tasks',type:'array'}] },
  'code-implement':     { emoji:'✏️', label:'代码实现',     phase:'fix',       inputs:[{name:'requirement',type:'object'},{name:'trace_report',type:'object'}], outputs:[{name:'code_changes',type:'object'}] },
  'article-write':      { emoji:'📝', label:'文档编写',     phase:'fix',       inputs:[{name:'content',type:'object'},{name:'template',type:'string'}], outputs:[{name:'formatted_doc',type:'string'}] },
  'code-review':        { emoji:'🔍', label:'代码审查',     phase:'verify',    inputs:[{name:'code_changes',type:'object'}], outputs:[{name:'review_report',type:'object'}] },
  'examine-quality':    { emoji:'🧪', label:'测试验证',     phase:'verify',    inputs:[{name:'code_changes',type:'object'}], outputs:[{name:'quality_report',type:'object'}] },
  'test-coverage':      { emoji:'🧪', label:'测试覆盖',     phase:'verify',    inputs:[{name:'focus_module',type:'string'}], outputs:[{name:'coverage_report',type:'object'}] },
  'checklist':          { emoji:'✅', label:'清单审计',     phase:'verify',    inputs:[{name:'mode',type:'string'}], outputs:[{name:'checklist_report',type:'object'}] },
  'tech-compare':       { emoji:'⚖️', label:'技术选型',     phase:'verify',    inputs:[{name:'options',type:'array'}], outputs:[{name:'comparison_matrix',type:'object'}] },
  'graph-fullchain':    { emoji:'📊', label:'架构可视化',   phase:'summarize', inputs:[{name:'architecture',type:'object'},{name:'trace_report',type:'object'}], outputs:[{name:'mermaid_diagrams',type:'string'}] },
  'sum-session':        { emoji:'📋', label:'总结报告',     phase:'summarize', inputs:[{name:'findings',type:'array'},{name:'visuals',type:'string'}], outputs:[{name:'summary_report',type:'object'}] },
  'talk-retro':         { emoji:'🧠', label:'复盘分析',     phase:'summarize', inputs:[{name:'incident',type:'object'}], outputs:[{name:'retro_report',type:'object'}] },
  'self-check':         { emoji:'🥊', label:'CTO拷打',      phase:'summarize', inputs:[{name:'report_to_review',type:'object'}], outputs:[{name:'selfcheck_report',type:'object'}] },
  'git-split-commit':   { emoji:'📦', label:'提交拆分',     phase:'deliver',   inputs:[{name:'code_changes',type:'object'}], outputs:[{name:'commit_plan',type:'object'}] },
  'ask-change-questions':{ emoji:'❓', label:'变更确认',    phase:'deliver',   inputs:[{name:'change_summary',type:'object'}], outputs:[{name:'confirmation',type:'string'}] },
  'knowledge-base':     { emoji:'📚', label:'知识沉淀',     phase:'deliver',   inputs:[{name:'knowledge_entry',type:'object'}], outputs:[{name:'stored_id',type:'string'}] },
  'quick-answer':       { emoji:'⚡', label:'快问快答',     phase:'deliver',   inputs:[{name:'question',type:'string'}], outputs:[{name:'answer',type:'string'}] },
  'api-test':           { emoji:'🔌', label:'接口测试',     phase:'verify',    inputs:[{name:'api_spec',type:'object'}], outputs:[{name:'test_results',type:'object'}] },
  'slash-cmd':          { emoji:'💻', label:'命令管理',     phase:'fix',       inputs:[{name:'action',type:'string'}], outputs:[{name:'cmd_status',type:'string'}] },
  'diagram-generator':  { emoji:'🎨', label:'图表生成',     phase:'summarize', inputs:[{name:'diagram_type',type:'string'},{name:'source_data',type:'object'}], outputs:[{name:'diagram_output',type:'object'}] },
  'scenario-runner':    { emoji:'▶️', label:'场景执行',     phase:'deliver',   inputs:[{name:'scenario_id',type:'string'}], outputs:[{name:'execution_result',type:'object'}] },
  'scenario-builder':   { emoji:'🏗️', label:'场景构建',     phase:'fix',       inputs:[{name:'template',type:'string'},{name:'nodes_config',type:'array'}], outputs:[{name:'scenario_yaml',type:'string'}] },
};

// Helper: get all ports for a skill
export function getSkillPorts(skillId) {
  const skill = SKILLS[skillId];
  if (!skill) return { inputs: [], outputs: [] };
  return { inputs: skill.inputs || [], outputs: skill.outputs || [] };
}
