import { useState, useRef } from 'react';

export default function Toolbar({
  scenarioName,
  onScenarioNameChange,
  onNew,
  onSave,
  onLoad,
  onValidate,
  onExportJSON,
  nodeCount,
  edgeCount,
}) {
  const fileInputRef = useRef(null);

  const handleLoadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      onLoad(ev.target.result, file.name);
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  return (
    <div className="toolbar">
      <span className="toolbar-title">🎨 EasyWork Scenario Canvas</span>
      <span className="toolbar-sep" />

      <input
        className="toolbar-name-input"
        value={scenarioName}
        onChange={(e) => onScenarioNameChange(e.target.value)}
        placeholder="场景名称"
        title="场景 ID"
      />

      <span className="toolbar-sep" />

      <button className="tb-btn" onClick={onNew} title="新建空白画布">🎯 新建</button>
      <button className="tb-btn primary" onClick={onSave} title="保存为 YAML">💾 保存</button>
      <button className="tb-btn" onClick={handleLoadClick} title="从文件加载">📂 加载</button>
      <input ref={fileInputRef} type="file" accept=".yaml,.yml,.json" style={{ display: 'none' }} onChange={handleFileChange} />

      <span className="toolbar-sep" />

      <button className="tb-btn" onClick={onValidate} title="校验 DAG">▶️ 校验</button>
      <button className="tb-btn" onClick={onExportJSON} title="导出为 JSON">📋 导出 JSON</button>

      <span className="toolbar-spacer" />

      <span className="toolbar-stats">
        {nodeCount} 节点 · {edgeCount} 连线
      </span>
    </div>
  );
}
