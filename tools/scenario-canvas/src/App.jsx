import { useState, useCallback, useEffect } from 'react';
import {
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from '@xyflow/react';
import Canvas from './components/Canvas';
import Palette from './components/Palette';
import PropertiesPanel from './components/PropertiesPanel';
import Toolbar from './components/Toolbar';
import ToastContainer, { useToast } from './components/Toast';
import { SKILLS, PHASE_COLORS } from './data/skills';
import { toYAML, parseSimpleYAML, downloadFile } from './utils/yaml';
import { validateDAG } from './utils/dag';
import './App.css';

let nodeIdCounter = 0;
function genNodeId() {
  return `node_${Date.now()}_${++nodeIdCounter}`;
}

// Default edge style
const defaultEdgeOptions = {
  type: 'smoothstep',
  animated: true,
  markerEnd: { type: MarkerType.ArrowClosed, color: '#6c5ce7', width: 16, height: 16 },
  style: { stroke: '#6c5ce7', strokeWidth: 3 },
};

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [scenarioName, setScenarioName] = useState('my-scenario');
  const { toasts, addToast } = useToast();

  // Get selected node
  const selectedNode = nodes.find((n) => n.id === selectedNodeId) || null;

  // Handle connections
  const onConnect = useCallback(
    (connection) => {
      const edge = {
        ...connection,
        ...defaultEdgeOptions,
        markerEnd: { type: MarkerType.ArrowClosed, color: '#00cec9', width: 16, height: 16 },
      };
      setEdges((eds) => addEdge(edge, eds));
    },
    [setEdges]
  );

  // Handle node click
  const onNodeClick = useCallback((_event, node) => {
    setSelectedNodeId(node.id);
  }, []);

  // Handle pane click (deselect)
  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
  }, []);

  // Add skill to canvas
  const addSkillToCanvas = useCallback(
    (skillId, position) => {
      const skillDef = SKILLS[skillId];
      if (!skillDef) return;

      const pos = position || { x: 200 + Math.random() * 300, y: 150 + Math.random() * 250 };

      const newNode = {
        id: genNodeId(),
        type: 'skillNode',
        position: pos,
        data: {
          skill: skillId,
          label: skillDef.label,
          phase: skillDef.phase,
          emoji: skillDef.emoji,
          config: {},
          interaction_prompt: '',
        },
      };

      setNodes((nds) => [...nds, newNode]);
      addToast(`已添加: ${skillDef.emoji} ${skillDef.label}`, 'info');
    },
    [setNodes, addToast]
  );

  // Drop handler from palette
  const onDropOnCanvas = useCallback(
    (skillId, position) => {
      addSkillToCanvas(skillId, position);
    },
    [addSkillToCanvas]
  );

  // Delete node
  const onDeleteNode = useCallback(
    (nodeId) => {
      if (!window.confirm(`确定删除此节点吗？`)) return;
      setNodes((nds) => nds.filter((n) => n.id !== nodeId));
      setEdges((eds) => eds.filter((e) => e.source !== nodeId && e.target !== nodeId));
      setSelectedNodeId(null);
      addToast('节点已删除', 'info');
    },
    [setNodes, setEdges, addToast]
  );

  // Save scenario
  const saveScenario = useCallback(() => {
    const id = scenarioName.trim() || 'my-scenario';
    const nodeMap = {};
    const yamlNodes = [];
    const yamlEdges = [];

    nodes.forEach((n, i) => {
      const yId = `n${i + 1}`;
      nodeMap[n.id] = yId;
      yamlNodes.push({
        id: yId,
        skill: n.data?.skill || 'unknown',
        label: n.data?.label || '',
        phase: n.data?.phase || 'understand',
        config: n.data?.config || {},
        interaction_point: n.data?.interaction_prompt
          ? { prompt: n.data.interaction_prompt, type: 'input' }
          : undefined,
        depends_on: [],
        pos: [n.position.x, n.position.y],
      });
    });

    edges.forEach((e) => {
      const fromId = nodeMap[e.source];
      const toId = nodeMap[e.target];
      if (fromId && toId) {
        yamlEdges.push({ from: fromId, to: toId });
        const targetNode = yamlNodes.find((n) => n.id === toId);
        if (targetNode && !targetNode.depends_on.includes(fromId)) {
          targetNode.depends_on.push(fromId);
        }
      }
    });

    // Clean up
    yamlNodes.forEach((n) => {
      if (!n.depends_on.length) delete n.depends_on;
      if (!n.interaction_point) delete n.interaction_point;
      delete n.pos;
    });

    const yaml = toYAML({
      scenario: {
        id,
        name: id,
        emoji: '🎯',
        version: '1.0',
        situation: {
          background: '',
          trigger_examples: [],
          desired_outcome: '',
        },
        canvas: {
          strategy: 'quality-first',
          nodes: yamlNodes,
          edges: yamlEdges.length ? yamlEdges : undefined,
          litegraph_state: {
            zoom: 1.0,
            offset: [0, 0],
          },
        },
        meta: {
          tags: [],
          skills_used: [...new Set(yamlNodes.map((n) => n.skill))],
        },
      },
    });

    downloadFile(`scenario-${id}.yaml`, yaml);
    navigator.clipboard.writeText(yaml).catch(() => {});
    addToast(`场景 "${id}" 已导出 (${yamlNodes.length} 节点, ${yamlEdges.length} 连线)`, 'success');
  }, [nodes, edges, scenarioName, addToast]);

  // Load scenario from text
  const loadScenario = useCallback(
    (content, filename) => {
      let data;
      try {
        if (filename?.endsWith('.json')) {
          data = JSON.parse(content);
        } else {
          data = parseSimpleYAML(content);
        }
      } catch (err) {
        addToast('解析失败: ' + err.message, 'error');
        return;
      }

      if (!data?.scenario?.canvas?.nodes) {
        addToast('无效的场景文件: 缺少 scenario.canvas.nodes', 'error');
        return;
      }

      setNodes([]);
      setEdges([]);
      setSelectedNodeId(null);

      const yamlNodes = data.scenario.canvas.nodes || [];
      const yamlEdges = data.scenario.canvas.edges || [];
      const nodeMap = {};
      const newNodes = [];
      const newEdges = [];

      yamlNodes.forEach((n) => {
        const skillId = n.skill || 'read-project';
        const skillDef = SKILLS[skillId] || {};
        const nodeId = genNodeId();
        nodeMap[n.id] = nodeId;

        const posX = Array.isArray(n.pos) ? n.pos[0] : 150 + Math.random() * 300;
        const posY = Array.isArray(n.pos) ? n.pos[1] : 150 + Math.random() * 300;

        newNodes.push({
          id: nodeId,
          type: 'skillNode',
          position: { x: posX, y: posY },
          data: {
            skill: skillId,
            label: n.label || skillDef.label || '',
            phase: n.phase || skillDef.phase || 'understand',
            emoji: skillDef.emoji || '',
            config: n.config || {},
            interaction_prompt: n.interaction_point?.prompt || '',
          },
        });
      });

      yamlEdges.forEach((e) => {
        const fromId = nodeMap[e.from];
        const toId = nodeMap[e.to];
        if (fromId && toId) {
          newEdges.push({
            id: `e-${fromId}-${toId}`,
            source: fromId,
            target: toId,
            sourceHandle: 'out',
            targetHandle: 'in',
            ...defaultEdgeOptions,
          });
        }
      });

      setNodes(newNodes);
      setEdges(newEdges);
      setScenarioName(data.scenario.id || 'loaded');
      addToast(`已加载: ${data.scenario.name || data.scenario.id} (${newNodes.length} 节点, ${newEdges.length} 连线)`, 'success');
    },
    [setNodes, setEdges, addToast]
  );

  // Validate scenario
  const validateScenario = useCallback(() => {
    const issues = validateDAG(nodes, edges);

    if (issues.length === 0) {
      addToast(`✅ 校验通过 — ${nodes.length} 节点, ${edges.length} 连线, 无环`, 'success');
    } else {
      alert('校验结果:\n\n' + issues.join('\n'));
      addToast(`⚠️ ${issues.length} 个问题`, 'error');
    }
  }, [nodes, edges, addToast]);

  // New canvas
  const newCanvas = useCallback(() => {
    if (nodes.length > 0) {
      if (!window.confirm('新建画布会清空当前内容，确定吗？')) return;
    }
    setNodes([]);
    setEdges([]);
    setSelectedNodeId(null);
    setScenarioName('my-scenario');
    addToast('已新建空白画布', 'info');
  }, [nodes.length, setNodes, setEdges, addToast]);

  // Export JSON
  const exportJSON = useCallback(() => {
    const data = { nodes, edges, scenarioName };
    const json = JSON.stringify(data, null, 2);
    downloadFile('canvas-export.json', json);
    navigator.clipboard.writeText(json).catch(() => {});
    addToast('已导出 JSON 并复制到剪贴板', 'success');
  }, [nodes, edges, scenarioName, addToast]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveScenario();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'o') {
        e.preventDefault();
        document.querySelector('input[type="file"]')?.click();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        newCanvas();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [saveScenario, newCanvas]);

  return (
    <div className="app">
      <Toolbar
        scenarioName={scenarioName}
        onScenarioNameChange={setScenarioName}
        onNew={newCanvas}
        onSave={saveScenario}
        onLoad={loadScenario}
        onValidate={validateScenario}
        onExportJSON={exportJSON}
        nodeCount={nodes.length}
        edgeCount={edges.length}
      />

      <div className="main-layout">
        <Palette onAddSkill={addSkillToCanvas} />

        <Canvas
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          onDropOnCanvas={onDropOnCanvas}
        />

        <PropertiesPanel
          selectedNode={selectedNode}
          onDeleteNode={onDeleteNode}
        />
      </div>

      <ToastContainer toasts={toasts} />
    </div>
  );
}
