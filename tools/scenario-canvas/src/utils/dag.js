// DAG validation — checks execution order validity

/**
 * Validate a directed graph for common issues.
 * @param {Array} nodes - Node objects from React Flow
 * @param {Array} edges - Edge objects from React Flow
 * @returns {Array} Array of issue strings (empty = valid)
 */
export function validateDAG(nodes, edges) {
  const issues = [];

  if (nodes.length === 0) {
    issues.push('⚠️ 画布为空，请从左侧面板添加技能节点');
    return issues;
  }

  // Check for disconnected nodes
  const connectedNodes = new Set();
  edges.forEach(e => {
    connectedNodes.add(e.source);
    connectedNodes.add(e.target);
  });

  if (nodes.length > 1) {
    nodes.forEach(n => {
      if (!connectedNodes.has(n.id)) {
        issues.push(`⚠️ "${n.data?.label || n.id}" 没有连线，可能被遗漏`);
      }
    });
  }

  // Cycle detection (DFS)
  const adj = {};
  nodes.forEach(n => { adj[n.id] = []; });
  edges.forEach(e => {
    if (adj[e.source]) adj[e.source].push(e.target);
  });

  function hasCycle(nodeId, visited, recStack) {
    visited.add(nodeId);
    recStack.add(nodeId);
    for (const neighbor of (adj[nodeId] || [])) {
      if (!visited.has(neighbor)) {
        if (hasCycle(neighbor, visited, recStack)) return true;
      } else if (recStack.has(neighbor)) {
        return true;
      }
    }
    recStack.delete(nodeId);
    return false;
  }

  const visited = new Set();
  for (const n of nodes) {
    if (!visited.has(n.id)) {
      if (hasCycle(n.id, visited, new Set())) {
        issues.push(`🔴 检测到循环依赖 (涉及 "${n.data?.label || n.id}")`);
        break;
      }
    }
  }

  return issues;
}
