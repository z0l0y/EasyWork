// DAG validation utilities

/**
 * Validate a directed graph for common issues
 * @param {Array} nodes - Node objects with { id, data: { skill, label } }
 * @param {Array} edges - Edge objects with { source, target }
 * @param {Function} getSkillDef - (skillId) => skill definition with { inputs }
 * @returns {Array} Array of issue strings
 */
export function validateDAG(nodes, edges, getSkillDef) {
  const issues = [];

  if (nodes.length === 0) {
    issues.push('⚠️ 画布为空，请添加节点');
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
        issues.push(`⚠️ 节点 "${n.data?.label || n.id}" 没有连线`);
      }
    });
  }

  // Check for nodes with required inputs but no incoming edges
  nodes.forEach(n => {
    const skillId = n.data?.skill;
    const skillDef = getSkillDef ? getSkillDef(skillId) : null;
    if (skillDef?.inputs?.length > 0 && nodes.length > 1) {
      const hasIncoming = edges.some(e => e.target === n.id);
      if (!hasIncoming) {
        issues.push(`⚠️ 节点 "${n.data?.label || n.id}" 有必填输入但无上游节点`);
      }
    }
  });

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
        issues.push(`🔴 检测到循环依赖 (涉及节点 "${n.data?.label || n.id}")`);
        break;
      }
    }
  }

  return issues;
}
