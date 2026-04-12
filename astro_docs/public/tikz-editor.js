// ─── State ─────────────────────────────────────────────────────────────────

const state = {
  nodes: [],
  edges: [],
  selected: null,        // { type: 'node'|'edge', id }
  mode: 'select',        // 'select' | 'node' | 'edge'
  edgeSource: null,
  nextNodeId: 1,
  nextEdgeId: 1,
  // Zoom & Pan
  zoom: 1,
  panX: 0,
  panY: 0,
  // Grid & Snap
  showGrid: true,
  snapEnabled: true,
  gridSize: 20,
  // History
  undoStack: [],
  redoStack: [],
  // Pyodide
  pyodide: null,
  pyodideReady: false,
  standaloneLaTeX: '',
};

// ─── DOM Refs ──────────────────────────────────────────────────────────────

const svgCanvas     = document.getElementById('svg-canvas');
const worldGroup    = document.getElementById('world');
const gridBg        = document.getElementById('grid-bg');
const nodesLayer    = document.getElementById('nodes-layer');
const edgesLayer    = document.getElementById('edges-layer');
const canvasArea    = document.getElementById('canvas-area');
const statusBar     = document.getElementById('status-bar');
const propPanel     = document.getElementById('properties-panel');
const pythonPre     = document.getElementById('python-code');
const tikzPre       = document.getElementById('tikz-code');
const compileBtn    = document.getElementById('compile-btn');
const pdfCanvas     = document.getElementById('pdf-canvas');
const pyodideStatus = document.getElementById('pyodide-status');
const resizer       = document.getElementById('resizer');
const rightPanelEl  = document.getElementById('right-panel');
const contextMenu   = document.getElementById('context-menu');
const zoomLabel     = document.getElementById('zoom-level');

function setStatus(msg) { statusBar.textContent = msg; }

// ─── History (Undo/Redo) ───────────────────────────────────────────────────

function snapshot() {
  return {
    nodes: JSON.parse(JSON.stringify(state.nodes)),
    edges: JSON.parse(JSON.stringify(state.edges)),
    nid: state.nextNodeId,
    eid: state.nextEdgeId,
  };
}

function restore(snap) {
  state.nodes = snap.nodes;
  state.edges = snap.edges;
  state.nextNodeId = snap.nid;
  state.nextEdgeId = snap.eid;
}

function saveHistory() {
  state.undoStack.push(snapshot());
  if (state.undoStack.length > 60) state.undoStack.shift();
  state.redoStack = [];
  updateHistoryButtons();
}

function undo() {
  if (!state.undoStack.length) return;
  state.redoStack.push(snapshot());
  restore(state.undoStack.pop());
  clearSelection();
  updateHistoryButtons();
  setStatus('Undone.');
}

function redo() {
  if (!state.redoStack.length) return;
  state.undoStack.push(snapshot());
  restore(state.redoStack.pop());
  clearSelection();
  updateHistoryButtons();
  setStatus('Redone.');
}

function updateHistoryButtons() {
  document.getElementById('btn-undo').disabled = !state.undoStack.length;
  document.getElementById('btn-redo').disabled = !state.redoStack.length;
}

// ─── Defaults ──────────────────────────────────────────────────────────────

function defaultNode(x, y) {
  return {
    id: `n${state.nextNodeId++}`,
    x, y,
    label: `Node ${state.nextNodeId - 1}`,
    shape: 'rectangle',
    fill: null,
    draw: null,
    textColor: null,
    minWidth: 60,
    minHeight: 30,
    opacity: null, fillOpacity: null, drawOpacity: null,
    minimumSize: null,
    innerSep: null, outerSep: null,
    nodeLineWidth: null,
    font: null, textWidth: null, align: null,
    anchor: null,
    rotate: null, xshift: null, yshift: null, scale: null,
    roundedCorners: null, dashPattern: null, doubleBorder: false,
    pattern: null, shading: null,
  };
}

function defaultEdge(sourceId, targetId) {
  return {
    id: `e${state.nextEdgeId++}`,
    sourceId, targetId,
    color: '#666666',
    lineWidth: 1,
    arrow: 'none',
    bendLeft: 0,
    bendRight: 0,
  };
}

// ─── Zoom & Pan ────────────────────────────────────────────────────────────

function updateWorldTransform() {
  worldGroup.setAttribute('transform', `translate(${state.panX},${state.panY}) scale(${state.zoom})`);
  zoomLabel.textContent = `${Math.round(state.zoom * 100)}%`;
}

function screenToWorld(cx, cy) {
  const r = svgCanvas.getBoundingClientRect();
  return {
    x: (cx - r.left - state.panX) / state.zoom,
    y: (cy - r.top  - state.panY) / state.zoom,
  };
}

svgCanvas.addEventListener('wheel', (e) => {
  e.preventDefault();
  const factor = e.deltaY > 0 ? 0.92 : 1.08;
  const r = svgCanvas.getBoundingClientRect();
  const sx = e.clientX - r.left;
  const sy = e.clientY - r.top;
  const wx = (sx - state.panX) / state.zoom;
  const wy = (sy - state.panY) / state.zoom;
  state.zoom = Math.max(0.15, Math.min(6, state.zoom * factor));
  state.panX = sx - wx * state.zoom;
  state.panY = sy - wy * state.zoom;
  updateWorldTransform();
}, { passive: false });

let panDrag = null;

svgCanvas.addEventListener('mousedown', (e) => {
  if (e.button === 1) {
    e.preventDefault();
    panDrag = { sx: e.clientX, sy: e.clientY, px: state.panX, py: state.panY };
  }
});

document.addEventListener('mousemove', (e) => {
  if (!panDrag) return;
  state.panX = panDrag.px + (e.clientX - panDrag.sx);
  state.panY = panDrag.py + (e.clientY - panDrag.sy);
  updateWorldTransform();
});

document.addEventListener('mouseup', () => { panDrag = null; });

document.getElementById('btn-zoom-in').onclick = () => {
  state.zoom = Math.min(6, state.zoom * 1.25);
  updateWorldTransform();
};
document.getElementById('btn-zoom-out').onclick = () => {
  state.zoom = Math.max(0.15, state.zoom / 1.25);
  updateWorldTransform();
};
document.getElementById('btn-zoom-reset').onclick = () => {
  state.zoom = 1; state.panX = 0; state.panY = 0;
  updateWorldTransform();
};

// ─── Grid & Snap ───────────────────────────────────────────────────────────

function toggleGrid() {
  state.showGrid = !state.showGrid;
  gridBg.style.display = state.showGrid ? '' : 'none';
  document.getElementById('btn-grid').classList.toggle('active', state.showGrid);
}

function toggleSnap() {
  state.snapEnabled = !state.snapEnabled;
  document.getElementById('btn-snap').classList.toggle('active', state.snapEnabled);
}

function snap(v) {
  return state.snapEnabled ? Math.round(v / state.gridSize) * state.gridSize : Math.round(v);
}

document.getElementById('btn-grid').onclick = toggleGrid;
document.getElementById('btn-snap').onclick = toggleSnap;

// ─── Render ────────────────────────────────────────────────────────────────

function renderAll() {
  renderEdges();
  renderNodes();
  generateCode();
}

function renderNodes() {
  nodesLayer.innerHTML = '';
  for (const node of state.nodes) {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    const isSel = state.selected?.type === 'node' && state.selected.id === node.id;
    const isSrc = state.edgeSource === node.id;
    g.setAttribute('class', 'tikz-node' + (isSel ? ' selected' : '') + (isSrc ? ' edge-source' : ''));
    g.setAttribute('data-id', node.id);
    g.setAttribute('transform', `translate(${node.x}, ${node.y})`);

    const hw = node.minWidth / 2, hh = node.minHeight / 2;
    let shape;

    if (node.shape === 'circle') {
      shape = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      const r = Math.max(hw, hh);
      shape.setAttribute('r', r);
      shape.setAttribute('cx', 0); shape.setAttribute('cy', 0);
    } else if (node.shape === 'ellipse') {
      shape = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
      shape.setAttribute('rx', hw); shape.setAttribute('ry', hh);
      shape.setAttribute('cx', 0); shape.setAttribute('cy', 0);
    } else if (node.shape === 'diamond') {
      shape = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
      shape.setAttribute('points', `0,${-hh} ${hw},0 0,${hh} ${-hw},0`);
    } else {
      shape = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      shape.setAttribute('x', -hw); shape.setAttribute('y', -hh);
      shape.setAttribute('width', node.minWidth); shape.setAttribute('height', node.minHeight);
      if (node.roundedCorners) shape.setAttribute('rx', parseInt(node.roundedCorners) || 4);
    }

    shape.setAttribute('fill', node.fill || 'none');
    const strokeColor = isSel ? '#818cf8' : isSrc ? '#fbbf24' : (node.draw || '#555');
    shape.setAttribute('stroke', strokeColor);
    shape.setAttribute('stroke-width', isSel || isSrc ? 2 : 1);
    g.appendChild(shape);

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('dominant-baseline', 'central');
    text.setAttribute('fill', node.textColor || '#c0c4d0');
    text.textContent = node.label;
    g.appendChild(text);

    attachNodeEvents(g, node);
    nodesLayer.appendChild(g);
  }
}

function renderEdges() {
  edgesLayer.innerHTML = '';
  for (const edge of state.edges) {
    const src = state.nodes.find(n => n.id === edge.sourceId);
    const tgt = state.nodes.find(n => n.id === edge.targetId);
    if (!src || !tgt) continue;

    const isSel = state.selected?.type === 'edge' && state.selected.id === edge.id;
    const color = isSel ? '#818cf8' : edge.color;
    const d = edgePath(src, tgt, edge);

    // Invisible hit area
    const hit = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    hit.setAttribute('d', d);
    hit.setAttribute('stroke', 'transparent');
    hit.setAttribute('stroke-width', Math.max(12 / state.zoom, edge.lineWidth + 8));
    hit.setAttribute('fill', 'none');
    hit.style.cursor = 'pointer';
    hit.addEventListener('click', (ev) => { ev.stopPropagation(); selectEdge(edge.id); });
    hit.addEventListener('contextmenu', (ev) => { ev.preventDefault(); ev.stopPropagation(); selectEdge(edge.id); showContextMenu(ev, 'edge', edge); });
    edgesLayer.appendChild(hit);

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('class', 'tikz-edge' + (isSel ? ' selected' : ''));
    path.setAttribute('d', d);
    path.setAttribute('stroke', color);
    path.setAttribute('stroke-width', edge.lineWidth);
    if (edge.arrow !== 'none') {
      path.setAttribute('marker-end', isSel ? 'url(#arrowhead-sel)' : 'url(#arrowhead)');
    }
    edgesLayer.appendChild(path);
  }
}

function edgePath(src, tgt, edge) {
  if (edge.bendLeft !== 0 || edge.bendRight !== 0) {
    const bend = (edge.bendLeft - edge.bendRight) * 0.5;
    const mx = (src.x + tgt.x) / 2, my = (src.y + tgt.y) / 2;
    const dx = tgt.x - src.x, dy = tgt.y - src.y;
    const len = Math.sqrt(dx * dx + dy * dy) || 1;
    const cx = mx + (-dy / len) * bend * 1.5;
    const cy = my + (dx / len) * bend * 1.5;
    return `M ${src.x} ${src.y} Q ${cx} ${cy} ${tgt.x} ${tgt.y}`;
  }
  return `M ${src.x} ${src.y} L ${tgt.x} ${tgt.y}`;
}

// ─── Node Events ───────────────────────────────────────────────────────────

function attachNodeEvents(g, node) {
  let dragging = false, didDrag = false, startX, startY, origX, origY;

  g.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    if (state.mode === 'edge') { handleEdgeClick(node.id); e.stopPropagation(); return; }
    if (state.mode !== 'select') return;
    e.stopPropagation();
    dragging = true; didDrag = false;
    startX = e.clientX; startY = e.clientY;
    origX = node.x; origY = node.y;
    selectNode(node.id);

    const onMove = (ev) => {
      if (!dragging) return;
      const dx = (ev.clientX - startX) / state.zoom;
      const dy = (ev.clientY - startY) / state.zoom;
      if (Math.abs(dx) > 2 || Math.abs(dy) > 2) didDrag = true;
      node.x = snap(origX + dx);
      node.y = snap(origY + dy);
      renderAll();
    };
    const onUp = () => {
      if (didDrag) saveHistory();
      dragging = false;
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  });

  g.addEventListener('dblclick', (e) => {
    e.stopPropagation();
    startInlineEdit(node);
  });

  g.addEventListener('contextmenu', (e) => {
    e.preventDefault(); e.stopPropagation();
    selectNode(node.id);
    showContextMenu(e, 'node', node);
  });
}

// ─── Inline Label Editing ──────────────────────────────────────────────────

function startInlineEdit(node) {
  const old = document.getElementById('inline-edit');
  if (old) old.remove();

  const r = svgCanvas.getBoundingClientRect();
  const sx = node.x * state.zoom + state.panX + r.left;
  const sy = node.y * state.zoom + state.panY + r.top;

  const input = document.createElement('input');
  input.id = 'inline-edit';
  input.type = 'text';
  input.value = node.label;
  Object.assign(input.style, {
    position: 'fixed',
    left: `${sx - 50}px`, top: `${sy - 13}px`,
    width: '100px', height: '26px',
    textAlign: 'center', fontSize: '12px',
    background: '#1a1e2e', color: '#e0e4ec',
    border: '1px solid #818cf8', borderRadius: '4px',
    outline: 'none', zIndex: '1000', padding: '0 4px',
    fontFamily: 'inherit',
  });

  const finish = () => {
    if (!input.parentNode) return;
    saveHistory();
    node.label = input.value || node.label;
    input.remove();
    renderAll();
    showNodeProperties(node);
  };

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') finish();
    if (e.key === 'Escape') input.remove();
    e.stopPropagation();
  });
  input.addEventListener('blur', finish);
  document.body.appendChild(input);
  input.select();
}

// ─── Selection ─────────────────────────────────────────────────────────────

function selectNode(id) {
  state.selected = { type: 'node', id };
  renderAll();
  showNodeProperties(state.nodes.find(n => n.id === id));
  switchTab('props');
}

function selectEdge(id) {
  state.selected = { type: 'edge', id };
  renderAll();
  showEdgeProperties(state.edges.find(e => e.id === id));
  switchTab('props');
}

function clearSelection() {
  state.selected = null;
  propPanel.innerHTML = '<p class="hint">Select a node or edge to edit properties.</p>';
  renderAll();
}

// ─── Edge Creation ─────────────────────────────────────────────────────────

function handleEdgeClick(nodeId) {
  if (!state.edgeSource) {
    state.edgeSource = nodeId;
    setStatus('Click a target node to connect.');
    renderNodes();
  } else if (state.edgeSource === nodeId) {
    state.edgeSource = null;
    setStatus('Edge cancelled. Click a source node.');
    renderNodes();
  } else {
    saveHistory();
    const edge = defaultEdge(state.edgeSource, nodeId);
    state.edges.push(edge);
    state.edgeSource = null;
    setStatus(`Edge: ${edge.sourceId} \u2192 ${edge.targetId}`);
    renderAll();
  }
}

// ─── Canvas Events ─────────────────────────────────────────────────────────

canvasArea.addEventListener('mousedown', (e) => {
  if (e.button === 0 && state.mode === 'node' && !e.target.closest('.tikz-node')) {
    const pt = screenToWorld(e.clientX, e.clientY);
    saveHistory();
    const node = defaultNode(snap(pt.x), snap(pt.y));
    state.nodes.push(node);
    selectNode(node.id);
    setStatus(`Added "${node.label}".`);
    return;
  }
  if (e.button === 0 && state.mode === 'select') {
    const t = e.target;
    if (t === svgCanvas || t === gridBg || t.closest('#world') === worldGroup && !t.closest('.tikz-node') && !t.closest('.tikz-edge')) {
      clearSelection();
    }
  }
});

canvasArea.addEventListener('contextmenu', (e) => {
  e.preventDefault();
  if (!e.target.closest('.tikz-node')) showContextMenu(e, 'canvas', null);
});

// ─── Context Menu ──────────────────────────────────────────────────────────

function showContextMenu(e, type, item) {
  hideContextMenu();
  let items = [];

  if (type === 'node') {
    items = [
      { label: 'Edit Label', key: 'Dbl-click', action: () => startInlineEdit(item) },
      { label: 'Duplicate', key: 'Ctrl+D', action: () => duplicateNode(item) },
      { sep: true },
      { label: 'Delete', key: 'Del', action: deleteSelected, cls: 'danger' },
    ];
  } else if (type === 'edge') {
    items = [
      { label: 'Delete', key: 'Del', action: deleteSelected, cls: 'danger' },
    ];
  } else {
    items = [
      { label: 'Add Node Here', action: () => {
        const pt = screenToWorld(e.clientX, e.clientY);
        saveHistory();
        const n = defaultNode(snap(pt.x), snap(pt.y));
        state.nodes.push(n);
        selectNode(n.id);
      }},
      { sep: true },
      { label: (state.showGrid ? '\u2713 ' : '  ') + 'Grid', key: 'G', action: toggleGrid },
      { label: (state.snapEnabled ? '\u2713 ' : '  ') + 'Snap to Grid', action: toggleSnap },
      { sep: true },
      { label: 'Reset View', action: () => { state.zoom = 1; state.panX = 0; state.panY = 0; updateWorldTransform(); } },
    ];
  }

  contextMenu.innerHTML = items.map(it => {
    if (it.sep) return '<div class="ctx-sep"></div>';
    const keyHtml = it.key ? `<span class="ctx-shortcut">${it.key}</span>` : '';
    return `<button class="ctx-item${it.cls ? ' ' + it.cls : ''}">${it.label}${keyHtml}</button>`;
  }).join('');

  contextMenu.style.display = 'block';
  contextMenu.style.left = `${e.clientX}px`;
  contextMenu.style.top = `${e.clientY}px`;

  // Clamp to viewport
  requestAnimationFrame(() => {
    const rect = contextMenu.getBoundingClientRect();
    if (rect.right > window.innerWidth) contextMenu.style.left = `${window.innerWidth - rect.width - 4}px`;
    if (rect.bottom > window.innerHeight) contextMenu.style.top = `${window.innerHeight - rect.height - 4}px`;
  });

  let bi = 0;
  const btns = contextMenu.querySelectorAll('.ctx-item');
  items.forEach(it => { if (!it.sep) btns[bi++].addEventListener('click', () => { hideContextMenu(); it.action(); }); });

  setTimeout(() => document.addEventListener('click', hideContextMenu, { once: true }), 0);
}

function hideContextMenu() { contextMenu.style.display = 'none'; }

// ─── Duplicate & Delete ────────────────────────────────────────────────────

function duplicateNode(node) {
  if (!node) {
    if (!state.selected || state.selected.type !== 'node') return;
    node = state.nodes.find(n => n.id === state.selected.id);
    if (!node) return;
  }
  saveHistory();
  const dup = JSON.parse(JSON.stringify(node));
  dup.id = `n${state.nextNodeId++}`;
  dup.label = node.label + ' copy';
  dup.x += 30; dup.y += 30;
  state.nodes.push(dup);
  selectNode(dup.id);
  setStatus(`Duplicated "${node.label}".`);
}

function deleteSelected() {
  if (!state.selected) return;
  saveHistory();
  if (state.selected.type === 'node') {
    const id = state.selected.id;
    state.nodes = state.nodes.filter(n => n.id !== id);
    state.edges = state.edges.filter(e => e.sourceId !== id && e.targetId !== id);
  } else {
    state.edges = state.edges.filter(e => e.id !== state.selected.id);
  }
  clearSelection();
  setStatus('Deleted.');
}

// ─── Mode & Toolbar ────────────────────────────────────────────────────────

function setMode(mode) {
  state.mode = mode;
  state.edgeSource = null;
  document.getElementById('btn-select').classList.toggle('active', mode === 'select');
  document.getElementById('btn-add-node').classList.toggle('active', mode === 'node');
  document.getElementById('btn-add-edge').classList.toggle('active', mode === 'edge');
  canvasArea.className = `mode-${mode}`;
  const msgs = {
    select: 'Select mode: click to select, drag to move. Double-click to edit label.',
    node: 'Node mode: click canvas to place a node.',
    edge: 'Edge mode: click source, then target node.',
  };
  setStatus(msgs[mode]);
  renderNodes();
}

document.getElementById('btn-select').onclick = () => setMode('select');
document.getElementById('btn-add-node').onclick = () => setMode('node');
document.getElementById('btn-add-edge').onclick = () => setMode('edge');
document.getElementById('btn-delete').onclick = deleteSelected;
document.getElementById('btn-duplicate').onclick = () => duplicateNode(null);
document.getElementById('btn-undo').onclick = undo;
document.getElementById('btn-redo').onclick = redo;

document.getElementById('btn-clear').onclick = () => {
  if (!confirm('Clear all nodes and edges?')) return;
  saveHistory();
  state.nodes = []; state.edges = [];
  state.nextNodeId = 1; state.nextEdgeId = 1;
  clearSelection();
  setStatus('Canvas cleared.');
};

// ─── Keyboard Shortcuts ────────────────────────────────────────────────────

document.addEventListener('keydown', (e) => {
  const tag = e.target.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

  if ((e.ctrlKey || e.metaKey) && !e.shiftKey) {
    if (e.key === 'z') { e.preventDefault(); undo(); return; }
    if (e.key === 'd') { e.preventDefault(); duplicateNode(null); return; }
  }
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'z' || e.key === 'Z')) {
    e.preventDefault(); redo(); return;
  }

  if (e.key === 'v' || e.key === 'V') setMode('select');
  if (e.key === 'n' || e.key === 'N') setMode('node');
  if (e.key === 'e' || e.key === 'E') setMode('edge');
  if (e.key === 'g' || e.key === 'G') toggleGrid();
  if (e.key === 'Delete' || e.key === 'Backspace') deleteSelected();
  if (e.key === 'Escape') { setMode('select'); clearSelection(); hideContextMenu(); }
});

// ─── Resizer ───────────────────────────────────────────────────────────────

resizer.addEventListener('mousedown', (e) => {
  e.preventDefault();
  const startX = e.clientX;
  const startWidth = rightPanelEl.offsetWidth;
  const onMove = (ev) => rightPanelEl.style.width = `${Math.max(180, startWidth + (startX - ev.clientX))}px`;
  const onUp = () => {
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onUp);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  };
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
  document.addEventListener('mousemove', onMove);
  document.addEventListener('mouseup', onUp);
});

// ─── Properties Panel Helpers ──────────────────────────────────────────────

function propRow(label, html) {
  return `<div class="prop-row"><label>${label}</label>${html}</div>`;
}

function hexColor(c) {
  if (!c || c === 'none') return '#888888';
  if (/^#[0-9a-fA-F]{6}$/.test(c)) return c;
  try {
    const ctx = document.createElement('canvas').getContext('2d');
    ctx.fillStyle = c;
    const s = ctx.fillStyle;
    if (/^#/.test(s)) return s;
    const m = s.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (m) return '#' + [m[1],m[2],m[3]].map(x => parseInt(x).toString(16).padStart(2,'0')).join('');
  } catch {}
  return '#888888';
}

function upd() { renderAll(); if (state.pyodideReady) scheduleCodeGen(); }

function bindStr(id, obj, key) {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', () => { obj[key] = el.value || null; upd(); });
}
function bindNum(id, obj, key) {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', () => { obj[key] = el.value === '' ? null : Number(el.value); upd(); });
}
function bindNumReq(id, obj, key) {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', () => { const v = parseFloat(el.value); if (!isNaN(v)) { obj[key] = v; upd(); } });
}
function bindColor(noneId, colorId, obj, key, def = '#000000') {
  const noneEl = document.getElementById(noneId);
  const colorEl = document.getElementById(colorId);
  if (!noneEl || !colorEl) return;
  noneEl.addEventListener('change', () => {
    if (noneEl.checked) { obj[key] = null; colorEl.disabled = true; }
    else { obj[key] = colorEl.value || def; colorEl.disabled = false; }
    upd();
  });
  colorEl.addEventListener('input', () => { obj[key] = colorEl.value; upd(); });
}
function bindBool(id, obj, key) {
  const el = document.getElementById(id);
  if (el) el.addEventListener('change', () => { obj[key] = el.checked; upd(); });
}

// ─── Node Properties ───────────────────────────────────────────────────────

function showNodeProperties(node) {
  if (!node) return;
  const shapes = ['rectangle','circle','ellipse','diamond','star','regular polygon','trapezium','cloud','cylinder','kite'];
  const anchors = ['center','north','south','east','west','north east','north west','south east','south west'];
  const aligns = ['left','center','right','justify'];
  const patterns = ['horizontal lines','vertical lines','north east lines','north west lines','grid','crosshatch','dots','crosshatch dots','bricks','checkerboard'];

  propPanel.innerHTML = `
    <span class="prop-node-id">Node: ${node.id}</span>

    <details class="prop-group" open>
      <summary>Basic</summary>
      <div class="prop-group-body">
        ${propRow('Content', `<input type="text" id="p-label" value="${node.label.replace(/"/g,'&quot;')}">`)}
        ${propRow('Shape', `<select id="p-shape">${shapes.map(s=>`<option value="${s}"${node.shape===s?' selected':''}>${s}</option>`).join('')}</select>`)}
        ${propRow('X', `<input type="number" id="p-x" value="${node.x}" step="${state.gridSize}">`)}
        ${propRow('Y', `<input type="number" id="p-y" value="${node.y}" step="${state.gridSize}">`)}
      </div>
    </details>

    <details class="prop-group" open>
      <summary>Colors</summary>
      <div class="prop-group-body">
        ${propRow('Fill', `<label class="color-none-wrap"><input type="checkbox" id="p-fill-none"${!node.fill?' checked':''}>none</label><input type="color" id="p-fill" value="${hexColor(node.fill)}"${!node.fill?' disabled':''}>`)}
        ${propRow('Border', `<label class="color-none-wrap"><input type="checkbox" id="p-draw-none"${!node.draw?' checked':''}>none</label><input type="color" id="p-draw" value="${hexColor(node.draw)}"${!node.draw?' disabled':''}>`)}
        ${propRow('Text', `<label class="color-none-wrap"><input type="checkbox" id="p-text-none"${!node.textColor?' checked':''}>none</label><input type="color" id="p-text" value="${hexColor(node.textColor)}"${!node.textColor?' disabled':''}>`)}
        ${propRow('Opacity', `<input type="number" id="p-opacity" value="${node.opacity??''}" min="0" max="1" step="0.05" placeholder="0\u20131">`)}
        ${propRow('Fill opacity', `<input type="number" id="p-fillopacity" value="${node.fillOpacity??''}" min="0" max="1" step="0.05" placeholder="0\u20131">`)}
        ${propRow('Draw opacity', `<input type="number" id="p-drawopacity" value="${node.drawOpacity??''}" min="0" max="1" step="0.05" placeholder="0\u20131">`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Size & Spacing</summary>
      <div class="prop-group-body">
        ${propRow('Min width', `<input type="number" id="p-mw" value="${node.minWidth}" min="10" step="5">`)}
        ${propRow('Min height', `<input type="number" id="p-mh" value="${node.minHeight}" min="10" step="5">`)}
        ${propRow('Min size', `<input type="text" id="p-minsize" value="${node.minimumSize??''}" placeholder="e.g. 2cm">`)}
        ${propRow('Inner sep', `<input type="text" id="p-innersep" value="${node.innerSep??''}" placeholder="e.g. 5pt">`)}
        ${propRow('Outer sep', `<input type="text" id="p-outersep" value="${node.outerSep??''}" placeholder="e.g. 5pt">`)}
        ${propRow('Line width', `<input type="text" id="p-nlw" value="${node.nodeLineWidth??''}" placeholder="e.g. 1pt">`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Text</summary>
      <div class="prop-group-body">
        ${propRow('Font', `<input type="text" id="p-font" value="${node.font??''}" placeholder="\\\\tiny">`)}
        ${propRow('Text width', `<input type="text" id="p-textwidth" value="${node.textWidth??''}" placeholder="e.g. 3cm">`)}
        ${propRow('Align', `<select id="p-align"><option value=""${!node.align?' selected':''}>---</option>${aligns.map(a=>`<option value="${a}"${node.align===a?' selected':''}>${a}</option>`).join('')}</select>`)}
        ${propRow('Anchor', `<select id="p-anchor"><option value=""${!node.anchor?' selected':''}>---</option>${anchors.map(a=>`<option value="${a}"${node.anchor===a?' selected':''}>${a}</option>`).join('')}</select>`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Transform</summary>
      <div class="prop-group-body">
        ${propRow('Rotate', `<input type="number" id="p-rotate" value="${node.rotate??''}" step="5" placeholder="degrees">`)}
        ${propRow('X shift', `<input type="text" id="p-xshift" value="${node.xshift??''}" placeholder="e.g. 1cm">`)}
        ${propRow('Y shift', `<input type="text" id="p-yshift" value="${node.yshift??''}" placeholder="e.g. 1cm">`)}
        ${propRow('Scale', `<input type="number" id="p-scale" value="${node.scale??''}" min="0.1" step="0.1" placeholder="1.0">`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Border Style</summary>
      <div class="prop-group-body">
        ${propRow('Rounded', `<input type="text" id="p-rounded" value="${node.roundedCorners??''}" placeholder="e.g. 5pt">`)}
        ${propRow('Double', `<input type="checkbox" id="p-double"${node.doubleBorder?' checked':''}>`)}
        ${propRow('Dash', `<input type="text" id="p-dash" value="${node.dashPattern??''}" placeholder="on 2pt off 2pt">`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Pattern / Shading</summary>
      <div class="prop-group-body">
        ${propRow('Pattern', `<select id="p-pattern"><option value=""${!node.pattern?' selected':''}>none</option>${patterns.map(p=>`<option value="${p}"${node.pattern===p?' selected':''}>${p}</option>`).join('')}</select>`)}
        ${propRow('Shading', `<select id="p-shading"><option value=""${!node.shading?' selected':''}>none</option>${['axis','radial','ball'].map(s=>`<option value="${s}"${node.shading===s?' selected':''}>${s}</option>`).join('')}</select>`)}
      </div>
    </details>
  `;

  // Bind all
  const labelEl = document.getElementById('p-label');
  if (labelEl) labelEl.addEventListener('input', () => { node.label = labelEl.value; upd(); });
  const shapeEl = document.getElementById('p-shape');
  if (shapeEl) shapeEl.addEventListener('input', () => { node.shape = shapeEl.value; upd(); });
  bindNumReq('p-x', node, 'x');
  bindNumReq('p-y', node, 'y');
  bindColor('p-fill-none', 'p-fill', node, 'fill', '#e2e8f0');
  bindColor('p-draw-none', 'p-draw', node, 'draw', '#475569');
  bindColor('p-text-none', 'p-text', node, 'textColor', '#1e293b');
  bindNum('p-opacity', node, 'opacity');
  bindNum('p-fillopacity', node, 'fillOpacity');
  bindNum('p-drawopacity', node, 'drawOpacity');
  bindNumReq('p-mw', node, 'minWidth');
  bindNumReq('p-mh', node, 'minHeight');
  bindStr('p-minsize', node, 'minimumSize');
  bindStr('p-innersep', node, 'innerSep');
  bindStr('p-outersep', node, 'outerSep');
  bindStr('p-nlw', node, 'nodeLineWidth');
  bindStr('p-font', node, 'font');
  bindStr('p-textwidth', node, 'textWidth');
  bindStr('p-align', node, 'align');
  bindStr('p-anchor', node, 'anchor');
  bindNum('p-rotate', node, 'rotate');
  bindStr('p-xshift', node, 'xshift');
  bindStr('p-yshift', node, 'yshift');
  bindNum('p-scale', node, 'scale');
  bindStr('p-rounded', node, 'roundedCorners');
  bindBool('p-double', node, 'doubleBorder');
  bindStr('p-dash', node, 'dashPattern');
  bindStr('p-pattern', node, 'pattern');
  bindStr('p-shading', node, 'shading');
}

// ─── Edge Properties ───────────────────────────────────────────────────────

function showEdgeProperties(edge) {
  if (!edge) return;
  const src = state.nodes.find(n => n.id === edge.sourceId);
  const tgt = state.nodes.find(n => n.id === edge.targetId);

  propPanel.innerHTML = `
    <span class="prop-node-id">Edge: ${edge.id}</span>
    <p style="font-size:0.68rem;color:#4a4f62;margin:0 0 0.4rem;">${src?.label || edge.sourceId} \u2192 ${tgt?.label || edge.targetId}</p>
    ${propRow('Color', `<input type="color" id="p-ecolor" value="${hexColor(edge.color)}">`)}
    ${propRow('Line width', `<input type="number" id="p-elw" value="${edge.lineWidth}" min="0.5" step="0.5">`)}
    ${propRow('Arrow', `<select id="p-earrow">
      <option value="none"${edge.arrow==='none'?' selected':''}>None</option>
      <option value="stealth"${edge.arrow==='stealth'?' selected':''}>Stealth</option>
      <option value="to"${edge.arrow==='to'?' selected':''}>To</option>
      <option value="latex"${edge.arrow==='latex'?' selected':''}>LaTeX</option>
    </select>`)}
    ${propRow('Bend left', `<input type="number" id="p-ebl" value="${edge.bendLeft}" min="-90" max="90" step="5">`)}
    ${propRow('Bend right', `<input type="number" id="p-ebr" value="${edge.bendRight}" min="-90" max="90" step="5">`)}
  `;

  const bind = (id, key, parse = v => v) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', () => { edge[key] = parse(el.value); upd(); });
  };
  bind('p-ecolor', 'color');
  bind('p-elw', 'lineWidth', Number);
  bind('p-earrow', 'arrow');
  bind('p-ebl', 'bendLeft', Number);
  bind('p-ebr', 'bendRight', Number);
}

// ─── Code Generation ───────────────────────────────────────────────────────

const PX_PER_UNIT = 30;

function worldToTikz(wx, wy) {
  return { cx: +(wx / PX_PER_UNIT).toFixed(2), cy: +((600 - wy) / PX_PER_UNIT).toFixed(2) };
}

function cssColorToLatex(hex) {
  if (!hex || hex === 'none') return null;
  if (/^#[0-9a-fA-F]{6}$/.test(hex)) {
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    return `{rgb,255:red,${r};green,${g};blue,${b}}`;
  }
  return hex;
}

function arrowToTikz(arrow) {
  return { stealth: '-Stealth', to: '->', latex: '-latex', none: '-' }[arrow] || '-';
}

function generatePythonCode() {
  if (!state.nodes.length) return '# Add nodes to the canvas to generate code';
  const lines = ['from tikzfigure import TikzFigure', '', 'fig = TikzFigure()'];

  const colorDefs = [];
  state.nodes.forEach(node => {
    const fl = cssColorToLatex(node.fill);
    const dl = cssColorToLatex(node.draw);
    if (fl && fl.startsWith('{rgb')) colorDefs.push(`fig.colorlet("${node.id}_fill", "${fl.slice(1,-1)}")`);
    if (dl && dl.startsWith('{rgb')) colorDefs.push(`fig.colorlet("${node.id}_draw", "${dl.slice(1,-1)}")`);
  });
  if (colorDefs.length) { lines.push(''); lines.push('# Define colors'); colorDefs.forEach(l => lines.push(l)); }

  lines.push(''); lines.push('# Add nodes');
  state.nodes.forEach(node => {
    const { cx, cy } = worldToTikz(node.x, node.y);
    const mw = (node.minWidth / PX_PER_UNIT).toFixed(1) + 'cm';
    const mh = (node.minHeight / PX_PER_UNIT).toFixed(1) + 'cm';
    const fillArg = node.fill && node.fill !== 'none' ? `, fill="${node.id}_fill"` : '';
    const drawArg = node.draw && node.draw !== 'none' ? `, draw="${node.id}_draw"` : '';
    const shapeArg = node.shape !== 'rectangle' ? `, shape="${node.shape}"` : '';
    const textArg = node.textColor ? `, text="${cssColorToLatex(node.textColor)}"` : '';
    const extra = [];
    if (node.opacity != null) extra.push(`opacity=${node.opacity}`);
    if (node.fillOpacity != null) extra.push(`fill_opacity=${node.fillOpacity}`);
    if (node.drawOpacity != null) extra.push(`draw_opacity=${node.drawOpacity}`);
    if (node.minimumSize) extra.push(`minimum_size="${node.minimumSize}"`);
    if (node.innerSep) extra.push(`inner_sep="${node.innerSep}"`);
    if (node.outerSep) extra.push(`outer_sep="${node.outerSep}"`);
    if (node.nodeLineWidth) extra.push(`line_width="${node.nodeLineWidth}"`);
    if (node.font) extra.push(`font="${node.font}"`);
    if (node.textWidth) extra.push(`text_width="${node.textWidth}"`);
    if (node.align) extra.push(`align="${node.align}"`);
    if (node.anchor) extra.push(`anchor="${node.anchor}"`);
    if (node.rotate != null) extra.push(`rotate=${node.rotate}`);
    if (node.xshift) extra.push(`xshift="${node.xshift}"`);
    if (node.yshift) extra.push(`yshift="${node.yshift}"`);
    if (node.scale != null) extra.push(`scale=${node.scale}`);
    if (node.roundedCorners) extra.push(`rounded_corners="${node.roundedCorners}"`);
    if (node.doubleBorder) extra.push(`double="none"`);
    if (node.dashPattern) extra.push(`dash_pattern="${node.dashPattern}"`);
    if (node.pattern) extra.push(`pattern="${node.pattern}"`);
    if (node.shading) extra.push(`shading="${node.shading}"`);
    const extraStr = extra.length ? ', ' + extra.join(', ') : '';
    lines.push(`fig.add_node(x=${cx}, y=${cy}, label="${node.id}", content="${node.label}"${fillArg}${drawArg}${shapeArg}${textArg}, minimum_width="${mw}", minimum_height="${mh}"${extraStr})`);
  });

  if (state.edges.length) {
    lines.push(''); lines.push('# Add edges');
    state.edges.forEach(edge => {
      const arrowOpt = arrowToTikz(edge.arrow);
      const colorArg = edge.color ? `, color="${cssColorToLatex(edge.color)}"` : '';
      const lwArg = `, line_width="${edge.lineWidth}pt"`;
      const blArg = edge.bendLeft !== 0 ? `, bend_left=${edge.bendLeft}` : '';
      const brArg = edge.bendRight !== 0 ? `, bend_right=${edge.bendRight}` : '';
      lines.push(`fig.draw(["${edge.sourceId}", "${edge.targetId}"]${colorArg}${lwArg}${blArg}${brArg}, options=["${arrowOpt}"])`);
    });
  }

  lines.push(''); lines.push('tikz_code = fig.generate_tikz()');
  return lines.join('\n');
}

let codeGenTimer = null;
function scheduleCodeGen() {
  clearTimeout(codeGenTimer);
  codeGenTimer = setTimeout(runCodeGen, 300);
}

function generateCode() {
  const pyCode = generatePythonCode();
  pythonPre.textContent = pyCode;
  if (state.pyodideReady) scheduleCodeGen();
  else tikzPre.textContent = '% Pyodide loading \u2014 TikZ will appear when ready';
}

async function runCodeGen() {
  if (!state.pyodideReady || !state.nodes.length) return;
  const pyCode = generatePythonCode();
  const fullCode = `
import sys
from io import StringIO
sys.stdout = mystdout = StringIO()
${pyCode}
print(tikz_code)
tikz_result = mystdout.getvalue()
standalone_result = fig.generate_standalone()
`;
  try {
    await state.pyodide.runPythonAsync(fullCode);
    tikzPre.textContent = state.pyodide.globals.get('tikz_result') || '% (empty)';
    state.standaloneLaTeX = state.pyodide.globals.get('standalone_result') || '';
    compileBtn.disabled = false;
  } catch (err) {
    tikzPre.textContent = `% Error: ${err}`;
    state.standaloneLaTeX = '';
    compileBtn.disabled = true;
  }
}

// ─── Tab System ────────────────────────────────────────────────────────────

const tabState = {
  tabs: [
    { id: 'props', label: 'Properties' },
    { id: 'code',  label: 'Code' },
    { id: 'pdf',   label: 'PDF' },
  ],
  visible: new Set(['props', 'code', 'pdf']),
  active: 'props',
};

function switchTab(id) {
  if (!tabState.visible.has(id)) tabState.visible.add(id);
  tabState.active = id;
  renderTabs();
}

function renderTabs() {
  const tabBar = document.getElementById('tab-bar');
  const visible = tabState.tabs.filter(t => tabState.visible.has(t.id));
  const hidden  = tabState.tabs.filter(t => !tabState.visible.has(t.id));

  if (tabState.active && !tabState.visible.has(tabState.active))
    tabState.active = visible[0]?.id ?? null;

  tabBar.innerHTML = visible.map(t => `
    <button class="tab-btn${t.id === tabState.active ? ' active' : ''}" data-tab="${t.id}" draggable="true">
      ${t.label}<span class="tab-hide-btn" data-hide="${t.id}">\u00d7</span>
    </button>
  `).join('') + (hidden.length ? '<button id="tab-restore-btn" title="Restore hidden tabs">+</button>' : '');

  tabState.tabs.forEach(t => {
    const pane = document.getElementById(`tab-pane-${t.id}`);
    if (!pane) return;
    const show = t.id === tabState.active;
    pane.style.display = show ? 'flex' : 'none';
    pane.classList.toggle('active-pane', show);
  });

  tabBar.querySelectorAll('.tab-btn[draggable]').forEach(btn => {
    const id = btn.dataset.tab;
    btn.addEventListener('dragstart', e => { e.dataTransfer.setData('text/plain', id); btn.classList.add('dragging'); });
    btn.addEventListener('dragend', () => btn.classList.remove('dragging'));
    btn.addEventListener('dragover', e => { e.preventDefault(); btn.classList.add('drag-over'); });
    btn.addEventListener('dragleave', () => btn.classList.remove('drag-over'));
    btn.addEventListener('drop', e => {
      e.preventDefault(); btn.classList.remove('drag-over');
      const from = e.dataTransfer.getData('text/plain'), to = id;
      if (from === to) return;
      const fi = tabState.tabs.findIndex(t => t.id === from);
      const ti = tabState.tabs.findIndex(t => t.id === to);
      const [moved] = tabState.tabs.splice(fi, 1);
      tabState.tabs.splice(ti, 0, moved);
      renderTabs();
    });
  });
}

document.getElementById('tab-bar').addEventListener('click', e => {
  const hide = e.target.closest('[data-hide]');
  if (hide) {
    e.stopPropagation();
    const id = hide.dataset.hide;
    tabState.visible.delete(id);
    if (tabState.active === id)
      tabState.active = tabState.tabs.find(t => tabState.visible.has(t.id))?.id ?? null;
    renderTabs();
    return;
  }
  if (e.target.id === 'tab-restore-btn') { showRestoreMenu(e.target); return; }
  const btn = e.target.closest('.tab-btn[data-tab]');
  if (btn) { tabState.active = btn.dataset.tab; renderTabs(); }
});

function showRestoreMenu(anchor) {
  document.getElementById('tab-restore-menu')?.remove();
  const hidden = tabState.tabs.filter(t => !tabState.visible.has(t.id));
  if (!hidden.length) return;
  const menu = document.createElement('div');
  menu.id = 'tab-restore-menu';
  hidden.forEach(tab => {
    const b = document.createElement('button');
    b.textContent = tab.label;
    b.onclick = ev => { ev.stopPropagation(); tabState.visible.add(tab.id); tabState.active = tab.id; renderTabs(); menu.remove(); };
    menu.appendChild(b);
  });
  document.getElementById('tab-bar').appendChild(menu);
  setTimeout(() => document.addEventListener('click', () => menu.remove(), { once: true }), 0);
}

renderTabs();

// ─── Pyodide ───────────────────────────────────────────────────────────────

async function initPyodide() {
  pyodideStatus.textContent = 'Loading Pyodide\u2026';
  try {
    state.pyodide = await loadPyodide();
    pyodideStatus.textContent = 'Installing tikzfigure\u2026';
    await state.pyodide.loadPackage('micropip');
    await state.pyodide.runPythonAsync(`
import micropip
await micropip.install("tikzfigure")
`);
    state.pyodideReady = true;
    pyodideStatus.style.color = '#6ee7b7';
    pyodideStatus.textContent = '\u2713 Ready';
    setStatus('Pyodide ready. Add nodes and edges to generate TikZ code.');
    if (state.nodes.length) runCodeGen();
  } catch (err) {
    pyodideStatus.style.color = '#f87171';
    pyodideStatus.textContent = `\u2717 ${err.message}`;
  }
}

initPyodide();

// ─── Copy Helpers ──────────────────────────────────────────────────────────

function copyCode(type) {
  const text = type === 'python' ? pythonPre.textContent : tikzPre.textContent;
  navigator.clipboard.writeText(text).then(
    () => setStatus(`Copied ${type === 'python' ? 'Python' : 'TikZ'} code.`),
    () => setStatus('Copy failed.')
  );
}
window.copyCode = copyCode;

document.getElementById('btn-compile-toolbar').addEventListener('click', () => {
  if (!compileBtn.disabled) compileBtn.click();
  else setStatus('No TikZ code ready \u2014 add nodes first.');
});

// ─── PDF Compilation ───────────────────────────────────────────────────────

const compileLogDetails = document.getElementById('compile-log-details');
const compileLog        = document.getElementById('compile-log');

if (typeof pdfjsLib !== 'undefined') {
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
}

function showLog(text, hasError) {
  if (!text) { compileLogDetails.style.display = 'none'; return; }
  const html = text.split('\n').map(line => {
    if (/^!/.test(line) || /error/i.test(line) && !/File:/.test(line))
      return `<span class="log-error">${esc(line)}</span>`;
    return esc(line);
  }).join('\n');
  compileLog.innerHTML = html;
  compileLog.className = hasError ? 'has-error' : '';
  compileLogDetails.style.display = '';
  compileLogDetails.open = hasError;
}

function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

async function renderPdfToCanvas(buf) {
  if (typeof pdfjsLib === 'undefined') return false;
  try {
    const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
    const page = await pdf.getPage(1);
    const cw = pdfCanvas.parentElement?.clientWidth || 280;
    const vp = page.getViewport({ scale: 1 });
    const scale = (cw - 2) / vp.width;
    const sv = page.getViewport({ scale });
    pdfCanvas.width = sv.width; pdfCanvas.height = sv.height;
    pdfCanvas.style.display = 'block';
    await page.render({ canvasContext: pdfCanvas.getContext('2d'), viewport: sv }).promise;
    return true;
  } catch (err) {
    console.error('PDF.js error:', err);
    return false;
  }
}

compileBtn.addEventListener('click', async () => {
  if (!state.standaloneLaTeX) { setStatus('No LaTeX to compile.'); return; }

  compileBtn.disabled = true;
  compileBtn.textContent = 'Compiling\u2026';
  setStatus('Sending to latex.ytotech.com\u2026');
  showLog('', false);

  const pdfDl = document.getElementById('pdf-download');
  try {
    const resp = await fetch('https://latex.ytotech.com/builds/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ compiler: 'pdflatex', resources: [{ main: true, content: state.standaloneLaTeX }] }),
    });

    if (resp.status === 201) {
      const buf = await resp.arrayBuffer();
      await renderPdfToCanvas(buf);
      if (state._prevPdfUrl) URL.revokeObjectURL(state._prevPdfUrl);
      const blob = new Blob([buf], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      state._prevPdfUrl = url;
      pdfDl.href = url;
      pdfDl.style.display = 'inline-block';
      setStatus('PDF compiled successfully.');
      showLog('Compilation successful.', false);
    } else {
      const json = await resp.json().catch(() => ({}));
      const log = (json.log_files || {})['__main_document__.log'] || JSON.stringify(json);
      showLog(log, true);
      const errLine = log.split('\n').find(l => l.startsWith('!') || /TeX capacity exceeded/i.test(l)) || `HTTP ${resp.status}`;
      setStatus(`Compilation error: ${errLine.trim()}`);
    }
  } catch (err) {
    setStatus(`Network error: ${err.message}`);
    showLog(err.message, true);
  } finally {
    compileBtn.disabled = false;
    compileBtn.textContent = 'Compile to PDF (latex-on-http)';
  }
});

// ─── Init ──────────────────────────────────────────────────────────────────

updateWorldTransform();
