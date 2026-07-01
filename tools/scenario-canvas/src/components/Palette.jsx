import { SKILLS, PHASE_ORDER, PHASE_LABELS, PHASE_COLORS } from '../data/skills';

export default function Palette({ onAddSkill }) {
  const onDragStart = (event, skillId) => {
    event.dataTransfer.setData('application/skill-id', skillId);
    event.dataTransfer.effectAllowed = 'move';
  };

  const onDoubleClick = (skillId) => {
    onAddSkill(skillId, null);
  };

  return (
    <div className="palette">
      <div className="palette-header">🎨 技能面板</div>
      <div className="palette-hint">拖拽到画布 或 双击添加</div>
      {PHASE_ORDER.map((phase) => {
        const phaseSkills = Object.entries(SKILLS).filter(([, def]) => def.phase === phase);
        if (phaseSkills.length === 0) return null;
        const phaseColor = PHASE_COLORS[phase];

        return (
          <div key={phase} className="palette-group">
            <div className="palette-group-title" style={{ borderLeftColor: phaseColor }}>
              {PHASE_LABELS[phase]}
            </div>
            {phaseSkills.map(([skillId, skillDef]) => (
              <div
                key={skillId}
                className="palette-item"
                draggable
                onDragStart={(e) => onDragStart(e, skillId)}
                onDoubleClick={() => onDoubleClick(skillId)}
                style={{ '--phase-color': phaseColor }}
              >
                <span className="palette-item-emoji">{skillDef.emoji}</span>
                <span className="palette-item-label">{skillDef.label}</span>
                <span className="palette-item-badge">{skillId}</span>
              </div>
            ))}
          </div>
        );
      })}
      <div className="palette-footer">
        {Object.keys(SKILLS).length} skills · React Flow
      </div>
    </div>
  );
}
