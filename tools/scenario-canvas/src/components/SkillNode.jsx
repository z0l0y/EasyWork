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
  const inputs = data?.inputs || skillDef.inputs || [];
  const outputs = data?.outputs || skillDef.outputs || [];

  return (
    <div
      className={`skill-node${selected ? ' selected' : ''}`}
      style={{ '--phase-color': phaseColor }}
    >
      {/* Input handles - left side */}
      {inputs.map((port, i) => (
        <Handle
          key={`in-${i}`}
          type="target"
          position={Position.Left}
          id={port.name}
          style={{ top: `${28 + i * 24}px`, background: phaseColor }}
          title={`${port.name} (${port.type})`}
        />
      ))}

      {/* Node body */}
      <div className="skill-node-header" style={{ background: phaseColor }}>
        <span className="skill-node-emoji">{emoji}</span>
        <span className="skill-node-title">{label}</span>
      </div>
      <div className="skill-node-body">
        {inputs.length > 0 && (
          <div className="skill-node-ports inputs">
            {inputs.map((p, i) => (
              <div key={`in-label-${i}`} className="port-label input-label">
                ← {p.name}
              </div>
            ))}
          </div>
        )}
        {outputs.length > 0 && (
          <div className="skill-node-ports outputs">
            {outputs.map((p, i) => (
              <div key={`out-label-${i}`} className="port-label output-label">
                {p.name} →
              </div>
            ))}
          </div>
        )}
        {inputs.length === 0 && outputs.length === 0 && (
          <div className="skill-node-no-ports">no ports</div>
        )}
        {data?.interaction_prompt && (
          <div className="skill-node-interaction" title={data.interaction_prompt}>
            💬 HITL
          </div>
        )}
      </div>

      {/* Output handles - right side */}
      {outputs.map((port, i) => (
        <Handle
          key={`out-${i}`}
          type="source"
          position={Position.Right}
          id={port.name}
          style={{ top: `${28 + i * 24}px`, background: phaseColor }}
          title={`${port.name} (${port.type})`}
        />
      ))}
    </div>
  );
});
