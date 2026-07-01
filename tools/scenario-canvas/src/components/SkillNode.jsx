import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { SKILLS, PHASE_COLORS } from '../data/skills';

export default memo(function SkillNode({ data, selected }) {
  const skillId = data?.skill || 'read-project';
  const skillDef = SKILLS[skillId] || {};
  const phase = data?.phase || skillDef.phase || 'understand';
  const phaseColor = PHASE_COLORS[phase] || '#6366f1';
  const emoji = data?.emoji || skillDef.emoji || '📦';
  const label = data?.label || skillDef.label || skillId;

  return (
    <div
      className={`skill-node${selected ? ' selected' : ''}`}
      style={{ '--phase-color': phaseColor }}
    >
      {/* Single input — left side, vertically centered */}
      <Handle
        type="target"
        position={Position.Left}
        id="in"
        style={{ background: phaseColor }}
      />

      {/* Header */}
      <div className="skill-node-header" style={{ background: phaseColor }}>
        <span className="skill-node-emoji">{emoji}</span>
        <span className="skill-node-title">{label}</span>
      </div>

      {/* Body — minimal: phase badge + optional HITL */}
      <div className="skill-node-body">
        <span className="skill-node-phase">{phase}</span>
        {data?.interaction_prompt && (
          <span className="skill-node-has-hitl" title={data.interaction_prompt}>💬</span>
        )}
      </div>

      {/* Single output — right side, vertically centered */}
      <Handle
        type="source"
        position={Position.Right}
        id="out"
        style={{ background: phaseColor }}
      />
    </div>
  );
});
