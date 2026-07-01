import { useState, useEffect } from 'react';
import { SKILLS, PHASE_COLORS, PHASE_ORDER } from '../data/skills';

export default function PropertiesPanel({ selectedNode, onUpdateNode, onDeleteNode }) {
  const [config, setConfig] = useState('{}');
  const [configError, setConfigError] = useState(false);

  useEffect(() => {
    if (selectedNode?.data?.config) {
      setConfig(JSON.stringify(selectedNode.data.config, null, 2));
    } else {
      setConfig('{}');
    }
    setConfigError(false);
  }, [selectedNode?.id]);

  if (!selectedNode) {
    return (
      <div className="properties-panel">
        <div className="properties-header">⚙️ 节点属性</div>
        <div className="properties-empty">
          点击画布上的节点<br />查看和编辑属性
        </div>
      </div>
    );
  }

  const data = selectedNode.data || {};
  const skillId = data.skill || 'read-project';
  const skillDef = SKILLS[skillId] || {};
  const phase = data.phase || 'understand';

  const handleSkillChange = (newSkillId) => {
    const newDef = SKILLS[newSkillId];
    if (!newDef) return;
    onUpdateNode(selectedNode.id, {
      ...data,
      skill: newSkillId,
      label: newDef.label,
      phase: newDef.phase,
      emoji: newDef.emoji,
      inputs: newDef.inputs,
      outputs: newDef.outputs,
    });
  };

  const handleLabelChange = (newLabel) => {
    onUpdateNode(selectedNode.id, { ...data, label: newLabel });
  };

  const handlePhaseChange = (newPhase) => {
    onUpdateNode(selectedNode.id, { ...data, phase: newPhase });
  };

  const handleConfigChange = (newConfigStr) => {
    setConfig(newConfigStr);
    try {
      const parsed = JSON.parse(newConfigStr);
      setConfigError(false);
      onUpdateNode(selectedNode.id, { ...data, config: parsed });
    } catch {
      setConfigError(true);
    }
  };

  const handleInteractionChange = (prompt) => {
    onUpdateNode(selectedNode.id, { ...data, interaction_prompt: prompt });
  };

  return (
    <div className="properties-panel">
      <div className="properties-header">⚙️ 节点属性</div>

      <div className="prop-group">
        <label>技能</label>
        <select value={skillId} onChange={(e) => handleSkillChange(e.target.value)}>
          {Object.entries(SKILLS).map(([id, def]) => (
            <option key={id} value={id}>{def.emoji} {def.label}</option>
          ))}
        </select>
      </div>

      <div className="prop-group">
        <label>节点标签</label>
        <input type="text" value={data.label || ''} onChange={(e) => handleLabelChange(e.target.value)} placeholder="自定义标签" />
      </div>

      <div className="prop-group">
        <label>阶段</label>
        <select value={phase} onChange={(e) => handlePhaseChange(e.target.value)}>
          {PHASE_ORDER.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <div className="prop-phase-preview" style={{ color: PHASE_COLORS[phase] }}>
          ● {phase}
        </div>
      </div>

      <div className="prop-group">
        <label>配置 (JSON)</label>
        <textarea
          value={config}
          onChange={(e) => handleConfigChange(e.target.value)}
          placeholder='{"key": "value"}'
          className={configError ? 'error' : ''}
          rows={4}
        />
        {configError && <span className="prop-error">JSON 格式错误</span>}
      </div>

      <div className="prop-group">
        <label>交互暂停提示词 (HITL)</label>
        <textarea
          value={data.interaction_prompt || ''}
          onChange={(e) => handleInteractionChange(e.target.value)}
          placeholder="输入提示文本，执行到此节点时会暂停等待用户确认..."
          rows={2}
        />
      </div>

      <button className="btn-delete" onClick={() => onDeleteNode(selectedNode.id)}>
        🗑 删除节点
      </button>
    </div>
  );
}
