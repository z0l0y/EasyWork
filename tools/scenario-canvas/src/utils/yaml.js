// YAML serializer & parser for scenario format
// Handles the specific scenario structure used by EasyWork

export function toYAML(obj, indent = 0) {
  const prefix = '  '.repeat(indent);
  let result = '# EasyWork Scenario Canvas Export\n';

  function serialize(val, depth) {
    const p = '  '.repeat(depth);
    if (val === null || val === undefined) return 'null';
    if (typeof val === 'boolean') return val ? 'true' : 'false';
    if (typeof val === 'number') return String(val);
    if (typeof val === 'string') {
      if (val.includes('\n') || val.includes(':') || val.includes('#') || val.includes('"') || val.includes("'")) {
        return `"${val.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"`;
      }
      if (val === '') return '""';
      return val;
    }
    if (Array.isArray(val)) {
      if (val.length === 0) return '[]';
      return val.map(item => `\n${p}- ${serialize(item, depth + 1).trimStart()}`).join('');
    }
    if (typeof val === 'object') {
      const keys = Object.keys(val).filter(k => val[k] !== undefined && val[k] !== null);
      if (keys.length === 0) return '{}';
      return keys.map(k => `${p}${k}: ${serialize(val[k], depth + 1).trimStart()}`).join('\n');
    }
    return String(val);
  }

  result += serialize(obj, 0);
  return result;
}

export function parseSimpleYAML(text) {
  const lines = text.split('\n');
  const root = {};
  const stack = [{ obj: root, indent: -1, key: null }];

  for (const line of lines) {
    if (!line.trim() || line.trim().startsWith('#')) continue;

    const indent = line.search(/\S/);
    const trimmed = line.trim();

    // Pop stack to correct indent
    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) {
      stack.pop();
    }
    const current = stack[stack.length - 1].obj;

    if (trimmed.startsWith('- ')) {
      const value = trimmed.substring(2).trim();
      let parsed = parseValue(value);
      if (!Array.isArray(current)) {
        continue;
      }
      current.push(parsed);
    } else if (trimmed.includes(':')) {
      const colonIdx = trimmed.indexOf(':');
      const key = trimmed.substring(0, colonIdx).trim();
      const value = trimmed.substring(colonIdx + 1).trim();

      if (value === '' || value === '{}' || value === '[]') {
        const newObj = value === '[]' ? [] : {};
        current[key] = newObj;
        stack.push({ obj: newObj, indent, key });
      } else {
        current[key] = parseValue(value);
      }
    }
  }

  return root;
}

function parseValue(value) {
  if (value === 'true') return true;
  if (value === 'false') return false;
  if (value === 'null' || value === '~') return null;
  if (/^-?\d+(\.\d+)?$/.test(value)) return Number(value);
  if (value.startsWith('"') && value.endsWith('"')) return value.slice(1, -1);
  return value;
}

export function downloadFile(filename, content) {
  const blob = new Blob([content], { type: 'text/yaml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
