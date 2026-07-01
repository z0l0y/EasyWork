import { useCallback, useRef } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useReactFlow,
  ReactFlowProvider,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import SkillNode from './SkillNode';
import { SKILLS } from '../data/skills';

const nodeTypes = { skillNode: SkillNode };

// MiniMap node color by phase
const miniMapNodeColor = (node) => {
  const phase = node.data?.phase || 'understand';
  const colors = {
    understand: '#3b82f6',
    'deep-dive': '#10b981',
    fix: '#ef4444',
    verify: '#f59e0b',
    summarize: '#8b5cf6',
    deliver: '#f97316',
  };
  return colors[phase] || '#6366f1';
};

function CanvasInner({ nodes, edges, onNodesChange, onEdgesChange, onConnect, onNodeClick, onPaneClick, onDropOnCanvas }) {
  const reactFlowInstance = useReactFlow();
  const reactFlowWrapper = useRef(null);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();
      const skillId = event.dataTransfer.getData('application/skill-id');
      if (!skillId || !SKILLS[skillId]) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      onDropOnCanvas(skillId, position);
    },
    [reactFlowInstance, onDropOnCanvas]
  );

  return (
    <div ref={reactFlowWrapper} className="canvas-wrapper" onDragOver={onDragOver} onDrop={onDrop}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        deleteKeyCode={['Delete', 'Backspace']}
        multiSelectionKeyCode="Shift"
        selectionKeyCode="Shift"
        snapToGrid
        snapGrid={[20, 20]}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
          style: { stroke: '#6c5ce7', strokeWidth: 3 },
        }}
        connectionLineStyle={{ stroke: '#00cec9', strokeWidth: 2 }}
        connectionLineType="smoothstep"
        className="react-flow-canvas"
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#2d2d4a" gap={24} size={1} />
        <Controls
          className="flow-controls"
          position="bottom-right"
          style={{ background: '#1a1a2e', border: '1px solid #2d2d4a', borderRadius: 8 }}
        />
        <MiniMap
          nodeColor={miniMapNodeColor}
          maskColor="rgba(15, 15, 26, 0.7)"
          style={{ background: '#1a1a2e', border: '1px solid #2d2d4a', borderRadius: 8 }}
          pannable
          zoomable
        />
        {nodes.length === 0 && (
          <div className="canvas-empty-hint">
            <div className="canvas-empty-icon">🎨</div>
            <div className="canvas-empty-title">从左侧面板拖入技能开始编排</div>
            <div className="canvas-empty-steps">
              <span>① 拖拽或双击左侧技能</span>
              <span>② 从右端口拖线到下个节点左端口</span>
              <span>③ Ctrl+S 保存场景</span>
            </div>
          </div>
        )}
      </ReactFlow>
    </div>
  );
}

export default function Canvas(props) {
  return (
    <ReactFlowProvider>
      <CanvasInner {...props} />
    </ReactFlowProvider>
  );
}
