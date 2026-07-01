import { SKILLS, PHASE_COLORS } from '../data/skills';

export default function PropertiesPanel({ selectedNode, onDeleteNode }) {
  if (!selectedNode) {
    return (
      <div className="properties-panel">
        <div className="properties-header">📋 节点信息</div>
        <div className="properties-empty">
          点击画布上的节点<br />查看技能说明
        </div>
      </div>
    );
  }

  const data = selectedNode.data || {};
  const skillId = data.skill || 'read-project';
  const skillDef = SKILLS[skillId] || {};
  const phase = data.phase || skillDef.phase || 'understand';
  const phaseColor = PHASE_COLORS[phase] || '#6366f1';

  return (
    <div className="properties-panel">
      <div className="properties-header">📋 节点信息</div>

      {/* Skill identity */}
      <div className="prop-skill-hero" style={{ borderLeftColor: phaseColor }}>
        <span className="prop-skill-emoji">{skillDef.emoji || '📦'}</span>
        <div>
          <div className="prop-skill-name">{skillDef.label || skillId}</div>
          <div className="prop-skill-id">{skillId}</div>
        </div>
      </div>

      {/* Description */}
      <div className="prop-group">
        <label>做什么</label>
        <p className="prop-desc">{skillDef.desc || '（暂无描述）'}</p>
      </div>

      {/* How it fits in the workflow */}
      <div className="prop-group">
        <label>在工作流中的位置</label>
        <div className="prop-flow-hint">
          <div className="flow-hint-row">
            <span className="flow-dot" style={{ background: phaseColor }} />
            <span>阶段：{phase}</span>
          </div>
          <div className="flow-hint-row">
            <span className="flow-icon">←</span>
            <span>接收上游节点的执行结果</span>
          </div>
          <div className="flow-hint-row">
            <span className="flow-icon">→</span>
            <span>产出结果传递给下游节点</span>
          </div>
          {data.interaction_prompt && (
            <div className="flow-hint-row hitl">
              <span className="flow-icon">💬</span>
              <span>执行到此暂停，等待用户输入</span>
            </div>
          )}
        </div>
      </div>

      <button className="btn-delete" onClick={() => onDeleteNode(selectedNode.id)}>
        🗑 删除节点
      </button>
    </div>
  );
}
