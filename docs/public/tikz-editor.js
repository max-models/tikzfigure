// ─── State ─────────────────────────────────────────────────────────────────

const state = {
  nodes: [],
  paths: [],
  selected: [],              // array of { type: 'node'|'path', id }
  mode: 'select',            // 'select' | 'node' | 'edge'
  pathBuilder: [],            // node IDs being connected
  nextNodeId: 1,
  nextPathId: 1,
  // Layers
  layers: [{ id: 0, name: 'Default', visible: true, locked: false }],
  activeLayer: 0,
  nextLayerId: 1,
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
  // Raw TikZ
  rawTikz: '',
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
const pdfViewer     = document.getElementById('pdf-viewer');
const pdfDl         = document.getElementById('pdf-download');
const pyodideStatus = document.getElementById('pyodide-status');
const canvasResizer = document.getElementById('canvas-resizer');
const rightResizer  = document.getElementById('right-resizer');
const rightPanel    = document.getElementById('right-panel');
const contextMenu   = document.getElementById('context-menu');
const zoomLabel     = document.getElementById('zoom-level');
const layersPanel   = document.getElementById('layers-panel');
const rawTikzInput  = document.getElementById('raw-tikz-input');
const marqueeEl     = document.getElementById('selection-marquee');

function setStatus(msg) { statusBar.textContent = msg; }
function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// ─── Selection Helpers ────────────────────────────────────────────────────

function isSelected(type, id) {
  return state.selected.some(s => s.type === type && s.id === id);
}

function primarySelection() {
  return state.selected.length === 1 ? state.selected[0] : null;
}

function addToSelection(type, id) {
  if (!isSelected(type, id)) state.selected.push({ type, id });
}

function removeFromSelection(type, id) {
  state.selected = state.selected.filter(s => !(s.type === type && s.id === id));
}

function toggleInSelection(type, id) {
  if (isSelected(type, id)) removeFromSelection(type, id);
  else addToSelection(type, id);
}

// ─── History (Undo/Redo) ───────────────────────────────────────────────────

function snapshot() {
  return {
    nodes: JSON.parse(JSON.stringify(state.nodes)),
    paths: JSON.parse(JSON.stringify(state.paths)),
    layers: JSON.parse(JSON.stringify(state.layers)),
    activeLayer: state.activeLayer,
    nid: state.nextNodeId,
    pid: state.nextPathId,
    lid: state.nextLayerId,
    rawTikz: state.rawTikz,
  };
}

function restore(snap) {
  state.nodes = snap.nodes;
  state.paths = snap.paths;
  state.layers = snap.layers;
  state.activeLayer = snap.activeLayer;
  state.nextNodeId = snap.nid;
  state.nextPathId = snap.pid;
  state.nextLayerId = snap.lid;
  state.rawTikz = snap.rawTikz;
  if (rawTikzInput) rawTikzInput.value = state.rawTikz;
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
  renderLayersPanel();
  updateHistoryButtons();
  setStatus('Undone.');
}

function redo() {
  if (!state.redoStack.length) return;
  state.undoStack.push(snapshot());
  restore(state.redoStack.pop());
  clearSelection();
  renderLayersPanel();
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
    label: '',
    shape: 'circle',
    fill: null,
    draw: null,
    textColor: null,
    minWidth: 40,
    minHeight: 40,
    opacity: null, fillOpacity: null, drawOpacity: null,
    minimumSize: null,
    innerSep: null, outerSep: null,
    nodeLineWidth: null,
    font: null, textWidth: null, align: null,
    anchor: null,
    rotate: null, xshift: null, yshift: null, scale: null,
    roundedCorners: null, dashPattern: null, doubleBorder: false,
    pattern: null, shading: null,
    layer: state.activeLayer,
    comment: null,
  };
}

function defaultPath(nodeIds) {
  return {
    id: `p${state.nextPathId++}`,
    nodeIds,
    cycle: false,
    color: '#666666',
    lineWidth: 1,
    fill: null,
    fillOpacity: null,
    arrow: 'none',
    opacity: null,
    drawOpacity: null,
    dashPattern: null,
    dashPhase: null,
    double: false,
    doubleDistance: null,
    roundedCorners: null,
    bendLeft: null,
    bendRight: null,
    decoration: null,
    lineCap: null,
    lineJoin: null,
    center: false,
    layer: state.activeLayer,
    comment: null,
  };
}

// ─── Layer Helpers ─────────────────────────────────────────────────────────

function getLayer(id) {
  return state.layers.find(l => l.id === id);
}

function isLayerVisible(layerId) {
  const l = getLayer(layerId);
  return l ? l.visible : true;
}

function isLayerLocked(layerId) {
  const l = getLayer(layerId);
  return l ? l.locked : false;
}

function itemCountForLayer(layerId) {
  return state.nodes.filter(n => n.layer === layerId).length +
         state.paths.filter(p => p.layer === layerId).length;
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
  renderPaths();
  renderNodes();
  generateCode();
}

function renderNodes() {
  nodesLayer.innerHTML = '';
  for (const node of state.nodes) {
    if (!isLayerVisible(node.layer)) continue;

    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    const isSel = isSelected('node', node.id);
    const isSrc = state.pathBuilder.includes(node.id);
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
    shape.setAttribute('pointer-events', 'all');
    const strokeColor = isSel ? '#818cf8' : isSrc ? '#fbbf24' : (node.draw || 'var(--node-stroke)');
    shape.setAttribute('stroke', strokeColor);
    shape.setAttribute('stroke-width', isSel || isSrc ? 2 : 1);
    if (node.opacity != null) shape.setAttribute('opacity', node.opacity);
    g.appendChild(shape);

    if (node.label) {
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dominant-baseline', 'central');
      text.setAttribute('fill', node.textColor || 'var(--node-text)');
      text.textContent = node.label;
      g.appendChild(text);
    }

    attachNodeEvents(g, node);
    nodesLayer.appendChild(g);
  }
}

function renderPaths() {
  edgesLayer.innerHTML = '';

  // Draw in-progress path builder preview
  if (state.pathBuilder.length > 0) {
    const pts = state.pathBuilder.map(id => state.nodes.find(n => n.id === id)).filter(Boolean);
    if (pts.length >= 1) {
      let d = `M ${pts[0].x} ${pts[0].y}`;
      for (let i = 1; i < pts.length; i++) d += ` L ${pts[i].x} ${pts[i].y}`;
      const preview = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      preview.setAttribute('d', d);
      preview.setAttribute('stroke', '#818cf8');
      preview.setAttribute('stroke-width', 1.5);
      preview.setAttribute('stroke-dasharray', '6 3');
      preview.setAttribute('fill', 'none');
      preview.style.pointerEvents = 'none';
      edgesLayer.appendChild(preview);
    }
  }

  for (const p of state.paths) {
    if (!isLayerVisible(p.layer)) continue;

    const pts = p.nodeIds.map(id => state.nodes.find(n => n.id === id)).filter(Boolean);
    if (pts.length < 2) continue;

    const isSel = isSelected('path', p.id);
    const color = isSel ? '#818cf8' : p.color;

    let d = `M ${pts[0].x} ${pts[0].y}`;
    for (let i = 1; i < pts.length; i++) d += ` L ${pts[i].x} ${pts[i].y}`;
    if (p.cycle) d += ' Z';

    // Invisible hit area
    const hit = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    hit.setAttribute('d', d);
    hit.setAttribute('stroke', 'transparent');
    hit.setAttribute('stroke-width', Math.max(12 / state.zoom, p.lineWidth + 8));
    hit.setAttribute('fill', p.cycle ? 'transparent' : 'none');
    hit.style.cursor = 'pointer';
    hit.setAttribute('pointer-events', 'all');
    hit.addEventListener('click', (ev) => { ev.stopPropagation(); selectPath(p.id, ev.shiftKey); });
    hit.addEventListener('contextmenu', (ev) => { ev.preventDefault(); ev.stopPropagation(); selectPath(p.id); showContextMenu(ev, 'path', p); });
    edgesLayer.appendChild(hit);

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('class', 'tikz-edge' + (isSel ? ' selected' : ''));
    path.setAttribute('d', d);
    path.setAttribute('stroke', color);
    path.setAttribute('stroke-width', p.double ? p.lineWidth + 2 : p.lineWidth);
    path.setAttribute('fill', p.fill || 'none');
    if (p.fill && p.fillOpacity != null) path.setAttribute('fill-opacity', p.fillOpacity);
    if (p.opacity != null) path.setAttribute('opacity', p.opacity);
    if (p.drawOpacity != null) path.setAttribute('stroke-opacity', p.drawOpacity);
    if (p.dashPattern) {
      const dash = { 'dashed': '8 4', 'dotted': '2 3', 'densely dashed': '4 2', 'loosely dashed': '12 6', 'dash dot': '8 3 2 3' }[p.dashPattern] || p.dashPattern.replace(/on |off /g, '').replace(/pt/g, '');
      path.setAttribute('stroke-dasharray', dash);
    }
    if (p.lineCap) path.setAttribute('stroke-linecap', p.lineCap);
    if (p.lineJoin) path.setAttribute('stroke-linejoin', p.lineJoin);
    if (p.roundedCorners) path.setAttribute('stroke-linejoin', 'round');
    if (p.arrow !== 'none') {
      path.setAttribute('marker-end', isSel ? 'url(#arrowhead-sel)' : 'url(#arrowhead)');
    }
    edgesLayer.appendChild(path);

    if (p.double) {
      const inner = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      inner.setAttribute('d', d);
      inner.setAttribute('stroke', p.fill || 'var(--bg-canvas, #0c0e16)');
      inner.setAttribute('stroke-width', Math.max(1, p.lineWidth - 1));
      inner.setAttribute('fill', 'none');
      inner.style.pointerEvents = 'none';
      edgesLayer.appendChild(inner);
    }
  }
}

// ─── Node Events ───────────────────────────────────────────────────────────

function attachNodeEvents(g, node) {
  let dragging = false, didDrag = false, startX, startY, origPositions;

  g.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    if (state.mode === 'edge') { handlePathClick(node.id); e.stopPropagation(); return; }
    if (state.mode !== 'select') return;
    if (isLayerLocked(node.layer)) { setStatus(`Layer "${getLayer(node.layer)?.name}" is locked.`); e.stopPropagation(); return; }
    e.stopPropagation();

    // Selection logic
    if (e.shiftKey) {
      toggleInSelection('node', node.id);
    } else if (!isSelected('node', node.id)) {
      state.selected = [{ type: 'node', id: node.id }];
    }

    dragging = true; didDrag = false;
    startX = e.clientX; startY = e.clientY;

    // Store original positions of ALL selected nodes for batch move
    origPositions = {};
    state.selected.forEach(s => {
      if (s.type === 'node') {
        const n = state.nodes.find(nd => nd.id === s.id);
        if (n) origPositions[s.id] = { x: n.x, y: n.y };
      }
    });

    updatePropertiesPanel();
    renderAll();

    const onMove = (ev) => {
      if (!dragging) return;
      const dx = (ev.clientX - startX) / state.zoom;
      const dy = (ev.clientY - startY) / state.zoom;
      if (Math.abs(dx) > 2 || Math.abs(dy) > 2) didDrag = true;
      // Move all selected nodes
      for (const [id, orig] of Object.entries(origPositions)) {
        const n = state.nodes.find(nd => nd.id === id);
        if (n && !isLayerLocked(n.layer)) {
          n.x = snap(orig.x + dx);
          n.y = snap(orig.y + dy);
        }
      }
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
    if (!isSelected('node', node.id)) state.selected = [{ type: 'node', id: node.id }];
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
    background: 'var(--bg-input)', color: 'var(--text)',
    border: '1px solid var(--border-active)', borderRadius: '4px',
    outline: 'none', zIndex: '1000', padding: '0 4px',
    fontFamily: 'inherit',
  });

  const finish = () => {
    if (!input.parentNode) return;
    saveHistory();
    node.label = input.value || node.label;
    input.remove();
    renderAll();
    const prim = primarySelection();
    if (prim?.type === 'node') showNodeProperties(state.nodes.find(n => n.id === prim.id));
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

function selectNode(id, additive = false) {
  if (additive) {
    toggleInSelection('node', id);
  } else {
    state.selected = [{ type: 'node', id }];
  }
  updatePropertiesPanel();
  renderAll();
}

function selectPath(id, additive = false) {
  if (additive) {
    toggleInSelection('path', id);
  } else {
    state.selected = [{ type: 'path', id }];
  }
  updatePropertiesPanel();
  renderAll();
}

function clearSelection() {
  state.selected = [];
  propPanel.innerHTML = '<p class="hint">Select a node or edge to edit properties.</p>';
  renderAll();
}

function updatePropertiesPanel() {
  const prim = primarySelection();
  if (prim?.type === 'node') {
    showNodeProperties(state.nodes.find(n => n.id === prim.id));
  } else if (prim?.type === 'path') {
    showPathProperties(state.paths.find(p => p.id === prim.id));
  } else if (state.selected.length > 1) {
    showMultiSelectProperties();
  } else {
    propPanel.innerHTML = '<p class="hint">Select a node or edge to edit properties.</p>';
  }
}

function showMultiSelectProperties() {
  const nodeCount = state.selected.filter(s => s.type === 'node').length;
  const pathCount = state.selected.filter(s => s.type === 'path').length;
  const parts = [];
  if (nodeCount) parts.push(`${nodeCount} node${nodeCount > 1 ? 's' : ''}`);
  if (pathCount) parts.push(`${pathCount} path${pathCount > 1 ? 's' : ''}`);

  // Collect unique layers in selection
  const layerIds = new Set();
  state.selected.forEach(s => {
    const item = s.type === 'node'
      ? state.nodes.find(n => n.id === s.id)
      : state.paths.find(p => p.id === s.id);
    if (item) layerIds.add(item.layer);
  });

  const layerOpts = state.layers.map(l => `<option value="${l.id}">${l.name}</option>`).join('');

  propPanel.innerHTML = `
    <span class="multi-select-info">${parts.join(', ')} selected</span>
    <p class="hint" style="margin-bottom:0.6rem">Shift+click to add/remove items. Drag to batch-move nodes.</p>

    <details class="prop-group" open>
      <summary>Batch Actions</summary>
      <div class="prop-group-body">
        <button class="batch-btn" id="batch-move-layer">Move to layer: </button>
        <select id="batch-layer-target" style="font-size:0.68rem;padding:2px 4px;background:var(--bg-input);border:1px solid var(--border-input);color:var(--text);border-radius:3px;">
          ${layerOpts}
        </select>
        <div style="margin-top:0.4rem">
          <button class="batch-btn danger" id="batch-delete">Delete All Selected</button>
        </div>
      </div>
    </details>
  `;

  document.getElementById('batch-delete')?.addEventListener('click', deleteSelected);
  document.getElementById('batch-move-layer')?.addEventListener('click', () => {
    const targetLayer = parseInt(document.getElementById('batch-layer-target').value);
    saveHistory();
    state.selected.forEach(s => {
      const item = s.type === 'node'
        ? state.nodes.find(n => n.id === s.id)
        : state.paths.find(p => p.id === s.id);
      if (item) item.layer = targetLayer;
    });
    upd();
    renderLayersPanel();
    setStatus(`Moved ${state.selected.length} items to layer "${getLayer(targetLayer)?.name}".`);
  });
}

// ─── Path Creation ─────────────────────────────────────────────────────────

function handlePathClick(nodeId) {
  if (state.pathBuilder.length === 0) {
    state.pathBuilder = [nodeId];
    setStatus('Path: click more nodes. Enter to finish, click first node to cycle.');
    renderAll();
  } else if (nodeId === state.pathBuilder[0] && state.pathBuilder.length >= 2) {
    finishPath(true);
  } else if (nodeId === state.pathBuilder[state.pathBuilder.length - 1]) {
    finishPath(false);
  } else {
    state.pathBuilder.push(nodeId);
    setStatus(`Path: ${state.pathBuilder.length} nodes. Enter to finish, click first node to cycle.`);
    renderAll();
  }
}

function finishPath(cycle) {
  if (state.pathBuilder.length < 2) {
    state.pathBuilder = [];
    setStatus('Path cancelled (need at least 2 nodes).');
    renderAll();
    return;
  }
  saveHistory();
  const p = defaultPath([...state.pathBuilder]);
  p.cycle = cycle;
  state.paths.push(p);
  state.pathBuilder = [];
  setStatus(`Path created: ${p.nodeIds.length} nodes${cycle ? ' (cycled)' : ''}.`);
  selectPath(p.id);
}

function cancelPath() {
  if (state.pathBuilder.length > 0) {
    state.pathBuilder = [];
    setStatus('Path cancelled.');
    renderAll();
  }
}

// ─── Canvas Events (with Marquee Selection) ───────────────────────────────

let marquee = null;

canvasArea.addEventListener('mousedown', (e) => {
  if (e.button === 0 && state.mode === 'node' && !e.target.closest('.tikz-node')) {
    const pt = screenToWorld(e.clientX, e.clientY);
    if (isLayerLocked(state.activeLayer)) { setStatus(`Active layer is locked.`); return; }
    saveHistory();
    const node = defaultNode(snap(pt.x), snap(pt.y));
    state.nodes.push(node);
    selectNode(node.id);
    hideTemplateGallery();
    renderLayersPanel();
    setStatus(`Added "${node.id}" on layer "${getLayer(state.activeLayer)?.name}".`);
    return;
  }
  if (e.button === 0 && state.mode === 'select') {
    const t = e.target;
    if (t === svgCanvas || t === gridBg || (t.closest('#world') === worldGroup && !t.closest('.tikz-node') && !t.closest('.tikz-edge'))) {
      if (!e.shiftKey) clearSelection();
      // Start marquee selection
      const r = canvasArea.getBoundingClientRect();
      marquee = {
        startX: e.clientX - r.left,
        startY: e.clientY - r.top,
        x: e.clientX - r.left,
        y: e.clientY - r.top,
      };
    }
  }
});

canvasArea.addEventListener('mousemove', (e) => {
  if (!marquee) return;
  const r = canvasArea.getBoundingClientRect();
  marquee.x = e.clientX - r.left;
  marquee.y = e.clientY - r.top;
  const left = Math.min(marquee.startX, marquee.x);
  const top = Math.min(marquee.startY, marquee.y);
  const width = Math.abs(marquee.x - marquee.startX);
  const height = Math.abs(marquee.y - marquee.startY);
  if (width > 3 || height > 3) {
    marqueeEl.style.display = 'block';
    marqueeEl.style.left = `${left}px`;
    marqueeEl.style.top = `${top}px`;
    marqueeEl.style.width = `${width}px`;
    marqueeEl.style.height = `${height}px`;
  }
});

canvasArea.addEventListener('mouseup', (e) => {
  if (!marquee) return;
  const width = Math.abs(marquee.x - marquee.startX);
  const height = Math.abs(marquee.y - marquee.startY);
  if (width > 5 || height > 5) {
    // Convert marquee bounds to world coordinates
    const r = canvasArea.getBoundingClientRect();
    const wTL = screenToWorld(r.left + Math.min(marquee.startX, marquee.x), r.top + Math.min(marquee.startY, marquee.y));
    const wBR = screenToWorld(r.left + Math.max(marquee.startX, marquee.x), r.top + Math.max(marquee.startY, marquee.y));
    // Select nodes within bounds
    state.nodes.forEach(n => {
      if (isLayerVisible(n.layer) && n.x >= wTL.x && n.x <= wBR.x && n.y >= wTL.y && n.y <= wBR.y) {
        addToSelection('node', n.id);
      }
    });
    updatePropertiesPanel();
    renderAll();
  }
  marqueeEl.style.display = 'none';
  marquee = null;
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
    const count = state.selected.length;
    items = [
      { label: 'Edit Label', key: 'Dbl-click', action: () => startInlineEdit(item) },
      { label: 'Duplicate', key: 'Ctrl+D', action: () => duplicateSelected() },
      { sep: true },
      ...(count > 1 ? [{ label: `Delete ${count} items`, action: deleteSelected, cls: 'danger' }] : []),
      { label: 'Delete', key: 'Del', action: deleteSelected, cls: count > 1 ? undefined : 'danger' },
    ].filter((it, i, arr) => !(count > 1 && it.key === 'Del'));
    if (count > 1) {
      items = [
        { label: `${count} items selected`, action: () => {} },
        { sep: true },
        { label: 'Duplicate All', key: 'Ctrl+D', action: () => duplicateSelected() },
        { label: `Delete All (${count})`, action: deleteSelected, cls: 'danger' },
      ];
    }
  } else if (type === 'path') {
    items = [
      { label: item.cycle ? 'Remove Cycle' : 'Add Cycle', action: () => { item.cycle = !item.cycle; upd(); showPathProperties(item); } },
      { sep: true },
      { label: 'Delete', key: 'Del', action: deleteSelected, cls: 'danger' },
    ];
  } else {
    items = [
      { label: 'Add Node Here', action: () => {
        const pt = screenToWorld(e.clientX, e.clientY);
        if (isLayerLocked(state.activeLayer)) { setStatus('Active layer is locked.'); return; }
        saveHistory();
        const n = defaultNode(snap(pt.x), snap(pt.y));
        state.nodes.push(n);
        selectNode(n.id);
        renderLayersPanel();
      }},
      { sep: true },
      { label: `Select All`, key: 'Ctrl+A', action: selectAll },
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

// ─── Select All ───────────────────────────────────────────────────────────

function selectAll() {
  state.selected = [];
  state.nodes.forEach(n => { if (isLayerVisible(n.layer)) state.selected.push({ type: 'node', id: n.id }); });
  state.paths.forEach(p => { if (isLayerVisible(p.layer)) state.selected.push({ type: 'path', id: p.id }); });
  updatePropertiesPanel();
  renderAll();
  setStatus(`Selected ${state.selected.length} items.`);
}

// ─── Duplicate & Delete ────────────────────────────────────────────────────

function duplicateSelected() {
  const nodesSel = state.selected.filter(s => s.type === 'node');
  if (!nodesSel.length) {
    // If single path selected, nothing to duplicate
    return;
  }
  saveHistory();
  const newSelected = [];
  nodesSel.forEach(s => {
    const node = state.nodes.find(n => n.id === s.id);
    if (!node) return;
    const dup = JSON.parse(JSON.stringify(node));
    dup.id = `n${state.nextNodeId++}`;
    dup.label = node.label ? node.label + ' copy' : '';
    dup.x += 30; dup.y += 30;
    state.nodes.push(dup);
    newSelected.push({ type: 'node', id: dup.id });
  });
  state.selected = newSelected;
  updatePropertiesPanel();
  renderAll();
  renderLayersPanel();
  setStatus(`Duplicated ${nodesSel.length} node(s).`);
}

function deleteSelected() {
  if (!state.selected.length) return;
  saveHistory();
  const nodeIds = new Set(state.selected.filter(s => s.type === 'node').map(s => s.id));
  const pathIds = new Set(state.selected.filter(s => s.type === 'path').map(s => s.id));

  // Remove selected nodes
  state.nodes = state.nodes.filter(n => !nodeIds.has(n.id));
  // Remove selected paths AND paths that reference deleted nodes
  state.paths = state.paths
    .filter(p => !pathIds.has(p.id))
    .map(p => ({ ...p, nodeIds: p.nodeIds.filter(nid => !nodeIds.has(nid)) }))
    .filter(p => p.nodeIds.length >= 2);

  clearSelection();
  renderLayersPanel();
  setStatus('Deleted.');
}

// ─── Mode & Toolbar ────────────────────────────────────────────────────────

function setMode(mode) {
  if (state.mode === 'edge' && mode !== 'edge' && state.pathBuilder.length >= 2) finishPath(false);
  state.mode = mode;
  state.pathBuilder = [];
  document.getElementById('btn-select').classList.toggle('active', mode === 'select');
  document.getElementById('btn-add-node').classList.toggle('active', mode === 'node');
  document.getElementById('btn-add-edge').classList.toggle('active', mode === 'edge');
  canvasArea.className = `mode-${mode}`;
  const msgs = {
    select: 'Select mode: click to select, shift+click multi-select, drag marquee. Double-click to edit label.',
    node: 'Node mode: click canvas to place a node.',
    edge: 'Path mode: click nodes to build a path. Enter to finish, click first node to cycle.',
  };
  setStatus(msgs[mode]);
  renderNodes();
}

document.getElementById('btn-select').onclick = () => setMode('select');
document.getElementById('btn-add-node').onclick = () => setMode('node');
document.getElementById('btn-add-edge').onclick = () => setMode('edge');
document.getElementById('btn-undo').onclick = undo;
document.getElementById('btn-redo').onclick = redo;

// ─── Keyboard Shortcuts ────────────────────────────────────────────────────

document.addEventListener('keydown', (e) => {
  const tag = e.target.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

  if ((e.ctrlKey || e.metaKey) && !e.shiftKey) {
    if (e.key === 'z') { e.preventDefault(); undo(); return; }
    if (e.key === 'd') { e.preventDefault(); duplicateSelected(); return; }
    if (e.key === 'a') { e.preventDefault(); selectAll(); return; }
  }
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'z' || e.key === 'Z')) {
    e.preventDefault(); redo(); return;
  }

  if (e.key === 'Enter' && state.mode === 'edge' && state.pathBuilder.length >= 2) { finishPath(false); return; }
  if (e.key === 'Escape' && state.mode === 'edge' && state.pathBuilder.length > 0) { cancelPath(); return; }
  if (e.key === 'v' || e.key === 'V') setMode('select');
  if (e.key === 'n' || e.key === 'N') setMode('node');
  if (e.key === 'e' || e.key === 'E') setMode('edge');
  if (e.key === 'g' || e.key === 'G') toggleGrid();
  if (e.key === 'Delete' || e.key === 'Backspace') deleteSelected();
  if (e.key === 'Escape') { setMode('select'); clearSelection(); hideContextMenu(); }
});

// ─── Drawer Resize ─────────────────────────────────────────────────────────

canvasResizer.addEventListener('mousedown', (e) => {
  e.preventDefault();
  const startY = e.clientY;
  const drawer = document.getElementById('drawer');
  const startH = drawer.offsetHeight;
  const canvasCol = document.getElementById('canvas-column');

  const onMove = (ev) => {
    const delta = startY - ev.clientY;
    const newH = Math.max(80, Math.min(canvasCol.offsetHeight - 200, startH + delta));
    drawer.style.height = `${newH}px`;
  };
  const onUp = () => {
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onUp);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  };
  document.body.style.cursor = 'row-resize';
  document.body.style.userSelect = 'none';
  document.addEventListener('mousemove', onMove);
  document.addEventListener('mouseup', onUp);
});

rightResizer.addEventListener('mousedown', (e) => {
  e.preventDefault();
  const startX = e.clientX;
  const startW = rightPanel.offsetWidth;

  const onMove = (ev) => {
    const delta = startX - ev.clientX;
    const newW = Math.max(160, Math.min(500, startW + delta));
    rightPanel.style.width = `${newW}px`;
  };
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
function bindColor(clearId, colorId, obj, key, def = '#000000') {
  const clearEl = document.getElementById(clearId);
  const colorEl = document.getElementById(colorId);
  if (!colorEl) return;
  const wrap = colorEl.closest('.color-row-wrap');
  const setNone = (isNone) => {
    wrap?.classList.toggle('is-none', isNone);
    if (clearEl) clearEl.textContent = isNone ? '—' : '✕';
  };
  colorEl.addEventListener('input', () => { obj[key] = colorEl.value; setNone(false); upd(); });
  if (clearEl) clearEl.addEventListener('click', () => { obj[key] = null; setNone(true); upd(); });
}
function bindBool(id, obj, key) {
  const el = document.getElementById(id);
  if (el) el.addEventListener('change', () => { obj[key] = el.checked; upd(); });
}

function layerSelect(currentLayer) {
  return `<select id="p-layer">${state.layers.map(l => `<option value="${l.id}"${l.id === currentLayer ? ' selected' : ''}>${l.name}</option>`).join('')}</select>`;
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
        ${propRow('Layer', layerSelect(node.layer))}
        ${propRow('Comment', `<input type="text" id="p-comment" value="${(node.comment||'').replace(/"/g,'&quot;')}" placeholder="optional comment">`)}
      </div>
    </details>

    <details class="prop-group" open>
      <summary>Colors</summary>
      <div class="prop-group-body">
        ${propRow('Fill', `<div class="color-row-wrap${!node.fill?' is-none':''}"><input type="color" id="p-fill" value="${hexColor(node.fill)}"><button class="color-none-btn" id="p-fill-none">${!node.fill?'—':'✕'}</button></div>`)}
        ${propRow('Border', `<div class="color-row-wrap${!node.draw?' is-none':''}"><input type="color" id="p-draw" value="${hexColor(node.draw)}"><button class="color-none-btn" id="p-draw-none">${!node.draw?'—':'✕'}</button></div>`)}
        ${propRow('Text', `<div class="color-row-wrap${!node.textColor?' is-none':''}"><input type="color" id="p-text" value="${hexColor(node.textColor)}"><button class="color-none-btn" id="p-text-none">${!node.textColor?'—':'✕'}</button></div>`)}
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
  bindStr('p-comment', node, 'comment');

  const layerEl = document.getElementById('p-layer');
  if (layerEl) layerEl.addEventListener('change', () => {
    node.layer = parseInt(layerEl.value);
    renderLayersPanel();
    upd();
  });
}

// ─── Path Properties ───────────────────────────────────────────────────────

function showPathProperties(p) {
  if (!p) return;
  const nodeNames = p.nodeIds.map(id => {
    const n = state.nodes.find(nd => nd.id === id);
    return n?.label || id;
  }).join(' \u2192 ');

  const dashOpts = ['', 'dashed', 'dotted', 'densely dashed', 'loosely dashed', 'dash dot'];
  const capOpts = ['', 'butt', 'round', 'rect'];
  const joinOpts = ['', 'miter', 'round', 'bevel'];
  const decoOpts = ['', 'snake', 'zigzag', 'coil', 'bumps', 'saw'];

  propPanel.innerHTML = `
    <span class="prop-node-id">Path: ${p.id}</span>
    <p style="font-size:0.68rem;color:var(--text-muted);margin:0 0 0.4rem;word-break:break-all;">${nodeNames}${p.cycle ? ' \u2192 cycle' : ''}</p>

    <details class="prop-group" open>
      <summary>Path</summary>
      <div class="prop-group-body">
        ${propRow('Cycle', `<input type="checkbox" id="p-pcycle"${p.cycle?' checked':''}>`)}
        ${propRow('Arrow', `<select id="p-parrow">
          <option value="none"${p.arrow==='none'?' selected':''}>None</option>
          <option value="stealth"${p.arrow==='stealth'?' selected':''}>-Stealth</option>
          <option value="to"${p.arrow==='to'?' selected':''}>-></option>
          <option value="latex"${p.arrow==='latex'?' selected':''}>-latex</option>
          <option value="stealth-stealth"${p.arrow==='stealth-stealth'?' selected':''}>Stealth-Stealth</option>
        </select>`)}
        ${propRow('Layer', layerSelect(p.layer))}
        ${propRow('Comment', `<input type="text" id="p-comment" value="${(p.comment||'').replace(/"/g,'&quot;')}" placeholder="optional comment">`)}
      </div>
    </details>

    <details class="prop-group" open>
      <summary>Stroke</summary>
      <div class="prop-group-body">
        ${propRow('Color', `<input type="color" id="p-pcolor" value="${hexColor(p.color)}">`)}
        ${propRow('Line width', `<input type="number" id="p-plw" value="${p.lineWidth}" min="0.5" step="0.5">`)}
        ${propRow('Opacity', `<input type="number" id="p-popacity" value="${p.opacity??''}" min="0" max="1" step="0.05" placeholder="0\u20131">`)}
        ${propRow('Draw opacity', `<input type="number" id="p-pdrawopacity" value="${p.drawOpacity??''}" min="0" max="1" step="0.05" placeholder="0\u20131">`)}
      </div>
    </details>

    <details class="prop-group" open>
      <summary>Fill</summary>
      <div class="prop-group-body">
        ${propRow('Fill', `<div class="color-row-wrap${!p.fill?' is-none':''}"><input type="color" id="p-pfill" value="${hexColor(p.fill)}"><button class="color-none-btn" id="p-pfill-none">${!p.fill?'—':'✕'}</button></div>`)}
        ${propRow('Fill opacity', `<input type="number" id="p-pfillopacity" value="${p.fillOpacity??''}" min="0" max="1" step="0.05" placeholder="0\u20131">`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Line Style</summary>
      <div class="prop-group-body">
        ${propRow('Dash', `<select id="p-pdash">${dashOpts.map(d=>`<option value="${d}"${(p.dashPattern||'')===d?' selected':''}>${d||'solid'}</option>`).join('')}</select>`)}
        ${propRow('Dash phase', `<input type="text" id="p-pdashphase" value="${p.dashPhase??''}" placeholder="e.g. 2pt">`)}
        ${propRow('Line cap', `<select id="p-pcap">${capOpts.map(c=>`<option value="${c}"${(p.lineCap||'')===c?' selected':''}>${c||'---'}</option>`).join('')}</select>`)}
        ${propRow('Line join', `<select id="p-pjoin">${joinOpts.map(j=>`<option value="${j}"${(p.lineJoin||'')===j?' selected':''}>${j||'---'}</option>`).join('')}</select>`)}
        ${propRow('Rounded', `<input type="text" id="p-prounded" value="${p.roundedCorners??''}" placeholder="e.g. 5pt">`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Double Line</summary>
      <div class="prop-group-body">
        ${propRow('Double', `<input type="checkbox" id="p-pdouble"${p.double?' checked':''}>`)}
        ${propRow('Distance', `<input type="text" id="p-pdoubledist" value="${p.doubleDistance??''}" placeholder="e.g. 2pt">`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Bending</summary>
      <div class="prop-group-body">
        ${propRow('Bend left', `<input type="number" id="p-pbendleft" value="${p.bendLeft??''}" step="5" placeholder="degrees">`)}
        ${propRow('Bend right', `<input type="number" id="p-pbendright" value="${p.bendRight??''}" step="5" placeholder="degrees">`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Decoration</summary>
      <div class="prop-group-body">
        ${propRow('Type', `<select id="p-pdeco">${decoOpts.map(d=>`<option value="${d}"${(p.decoration||'')===d?' selected':''}>${d||'none'}</option>`).join('')}</select>`)}
      </div>
    </details>
  `;

  const bind = (id, key, parse = v => v) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', () => { p[key] = parse(el.value); upd(); });
  };
  bind('p-pcolor', 'color');
  bind('p-plw', 'lineWidth', Number);
  bind('p-parrow', 'arrow');
  bindNum('p-popacity', p, 'opacity');
  bindNum('p-pdrawopacity', p, 'drawOpacity');
  bindStr('p-pdash', p, 'dashPattern');
  bindStr('p-pdashphase', p, 'dashPhase');
  bindStr('p-pcap', p, 'lineCap');
  bindStr('p-pjoin', p, 'lineJoin');
  bindStr('p-prounded', p, 'roundedCorners');
  bindBool('p-pdouble', p, 'double');
  bindStr('p-pdoubledist', p, 'doubleDistance');
  bindNum('p-pbendleft', p, 'bendLeft');
  bindNum('p-pbendright', p, 'bendRight');
  bindStr('p-pdeco', p, 'decoration');
  bindStr('p-comment', p, 'comment');

  const cycleEl = document.getElementById('p-pcycle');
  if (cycleEl) cycleEl.addEventListener('change', () => { p.cycle = cycleEl.checked; upd(); showPathProperties(p); });

  bindColor('p-pfill-none', 'p-pfill', p, 'fill', '#4488cc');
  bindNum('p-pfillopacity', p, 'fillOpacity');

  const layerEl = document.getElementById('p-layer');
  if (layerEl) layerEl.addEventListener('change', () => {
    p.layer = parseInt(layerEl.value);
    renderLayersPanel();
    upd();
  });
}

// ─── Layers Panel ──────────────────────────────────────────────────────────

function renderLayersPanel() {
  if (!layersPanel) return;

  const rows = state.layers.map(l => {
    const count = itemCountForLayer(l.id);
    const isActive = l.id === state.activeLayer;
    return `
      <div class="layer-row${isActive ? ' active-layer' : ''}" data-layer-id="${l.id}">
        <button class="layer-vis-btn${l.visible ? '' : ' hidden-layer'}" data-vis="${l.id}" title="Toggle visibility">${l.visible ? '\u{1F441}' : '\u{1F441}\u200D\u{1F5E8}'}</button>
        <button class="layer-lock-btn${l.locked ? ' locked-layer' : ''}" data-lock="${l.id}" title="Toggle lock">${l.locked ? '\u{1F512}' : '\u{1F513}'}</button>
        <span class="layer-name">${l.name}</span>
        <span class="layer-count">${count}</span>
      </div>
    `;
  }).join('');

  layersPanel.innerHTML = `
    ${rows}
    <div class="layer-actions">
      <button class="layer-action-btn" id="layer-add">+ Add</button>
      <button class="layer-action-btn" id="layer-rename">Rename</button>
      <button class="layer-action-btn" id="layer-delete">Delete</button>
    </div>
  `;

  // Click row to set active layer
  layersPanel.querySelectorAll('.layer-row').forEach(row => {
    row.addEventListener('click', (e) => {
      if (e.target.closest('.layer-vis-btn') || e.target.closest('.layer-lock-btn')) return;
      state.activeLayer = parseInt(row.dataset.layerId);
      renderLayersPanel();
      setStatus(`Active layer: "${getLayer(state.activeLayer)?.name}".`);
    });
  });

  // Visibility toggles
  layersPanel.querySelectorAll('.layer-vis-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const l = getLayer(parseInt(btn.dataset.vis));
      if (l) { l.visible = !l.visible; renderLayersPanel(); renderAll(); }
    });
  });

  // Lock toggles
  layersPanel.querySelectorAll('.layer-lock-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const l = getLayer(parseInt(btn.dataset.lock));
      if (l) { l.locked = !l.locked; renderLayersPanel(); }
    });
  });

  // Add layer
  document.getElementById('layer-add')?.addEventListener('click', () => {
    saveHistory();
    const newLayer = { id: state.nextLayerId++, name: `Layer ${state.layers.length}`, visible: true, locked: false };
    state.layers.push(newLayer);
    state.activeLayer = newLayer.id;
    renderLayersPanel();
    setStatus(`Added layer "${newLayer.name}".`);
  });

  // Rename layer
  document.getElementById('layer-rename')?.addEventListener('click', () => {
    const l = getLayer(state.activeLayer);
    if (!l) return;
    const name = prompt('Layer name:', l.name);
    if (name && name.trim()) {
      saveHistory();
      l.name = name.trim();
      renderLayersPanel();
    }
  });

  // Delete layer
  document.getElementById('layer-delete')?.addEventListener('click', () => {
    if (state.layers.length <= 1) { setStatus('Cannot delete last layer.'); return; }
    const l = getLayer(state.activeLayer);
    if (!l) return;
    const count = itemCountForLayer(l.id);
    if (count > 0 && !confirm(`Delete layer "${l.name}" and its ${count} items?`)) return;
    saveHistory();
    // Remove items on this layer
    state.nodes = state.nodes.filter(n => n.layer !== l.id);
    state.paths = state.paths.filter(p => p.layer !== l.id);
    // Also clean up paths referencing deleted nodes
    const nodeIds = new Set(state.nodes.map(n => n.id));
    state.paths = state.paths
      .map(p => ({ ...p, nodeIds: p.nodeIds.filter(nid => nodeIds.has(nid)) }))
      .filter(p => p.nodeIds.length >= 2);
    state.layers = state.layers.filter(ly => ly.id !== l.id);
    state.activeLayer = state.layers[0].id;
    clearSelection();
    renderLayersPanel();
    setStatus(`Deleted layer "${l.name}".`);
  });
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
  return { stealth: '-Stealth', to: '->', latex: '-latex', 'stealth-stealth': 'Stealth-Stealth', none: '-' }[arrow] || '-';
}

function generateNodeCode(node) {
  const { cx, cy } = worldToTikz(node.x, node.y);
  const args = [`x=${cx}`, `y=${cy}`, `label="${node.id}"`];
  if (node.label) args.push(`content="${node.label}"`);
  if (node.fill && node.fill !== 'none') args.push(`fill="${node.id}_fill"`);
  if (node.draw && node.draw !== 'none') args.push(`draw="${node.id}_draw"`);
  if (node.shape !== 'rectangle') args.push(`shape="${node.shape}"`);
  if (node.textColor) args.push(`text="${cssColorToLatex(node.textColor)}"`);
  if (node.minWidth !== 40) args.push(`minimum_width="${(node.minWidth / PX_PER_UNIT).toFixed(1)}cm"`);
  if (node.minHeight !== 40) args.push(`minimum_height="${(node.minHeight / PX_PER_UNIT).toFixed(1)}cm"`);
  if (node.opacity != null) args.push(`opacity=${node.opacity}`);
  if (node.fillOpacity != null) args.push(`fill_opacity=${node.fillOpacity}`);
  if (node.drawOpacity != null) args.push(`draw_opacity=${node.drawOpacity}`);
  if (node.minimumSize) args.push(`minimum_size="${node.minimumSize}"`);
  if (node.innerSep) args.push(`inner_sep="${node.innerSep}"`);
  if (node.outerSep) args.push(`outer_sep="${node.outerSep}"`);
  if (node.nodeLineWidth) args.push(`line_width="${node.nodeLineWidth}"`);
  if (node.font) args.push(`font="${node.font}"`);
  if (node.textWidth) args.push(`text_width="${node.textWidth}"`);
  if (node.align) args.push(`align="${node.align}"`);
  if (node.anchor) args.push(`anchor="${node.anchor}"`);
  if (node.rotate != null) args.push(`rotate=${node.rotate}`);
  if (node.xshift) args.push(`xshift="${node.xshift}"`);
  if (node.yshift) args.push(`yshift="${node.yshift}"`);
  if (node.scale != null) args.push(`scale=${node.scale}`);
  if (node.roundedCorners) args.push(`rounded_corners="${node.roundedCorners}"`);
  if (node.doubleBorder) args.push(`double="none"`);
  if (node.dashPattern) args.push(`dash_pattern="${node.dashPattern}"`);
  if (node.pattern) args.push(`pattern="${node.pattern}"`);
  if (node.shading) args.push(`shading="${node.shading}"`);
  if (node.comment) args.push(`comment="${node.comment}"`);
  return `fig.add_node(${args.join(', ')})`;
}

function generatePathCode(p) {
  const nodeList = `[${p.nodeIds.map(id => `"${id}"`).join(', ')}]`;
  const args = [nodeList];

  // options (flag-style)
  const opts = [];
  if (p.arrow !== 'none') opts.push(`"${arrowToTikz(p.arrow)}"`);
  if (p.dashPattern) opts.push(`"${p.dashPattern}"`);
  if (p.decoration) opts.push(`"decorate"`, `"decoration=${p.decoration}"`);
  if (opts.length) args.push(`options=[${opts.join(', ')}]`);

  if (p.cycle) args.push(`cycle=True`);
  if (p.center) args.push(`center=True`);

  if (p.color && p.color !== '#666666') {
    const cl = cssColorToLatex(p.color);
    if (cl && cl.startsWith('{rgb')) args.push(`color="${p.id}_color"`);
    else if (cl) args.push(`color="${cl}"`);
  }

  const hasFill = p.fill && p.fill !== 'none';
  if (hasFill) {
    const fl = cssColorToLatex(p.fill);
    if (fl && fl.startsWith('{rgb')) args.push(`fill="${p.id}_fill"`);
    else if (fl) args.push(`fill="${fl}"`);
  }

  if (p.opacity != null) args.push(`opacity=${p.opacity}`);
  if (p.drawOpacity != null) args.push(`draw_opacity=${p.drawOpacity}`);
  if (p.fillOpacity != null && hasFill) args.push(`fill_opacity=${p.fillOpacity}`);
  if (p.lineWidth !== 1) args.push(`line_width=${p.lineWidth}`);
  if (p.dashPhase) args.push(`dash_phase="${p.dashPhase}"`);
  if (p.lineCap) args.push(`line_cap="${p.lineCap}"`);
  if (p.lineJoin) args.push(`line_join="${p.lineJoin}"`);
  if (p.roundedCorners) args.push(`rounded_corners="${p.roundedCorners}"`);
  if (p.double) args.push(`double="white"`);
  if (p.doubleDistance) args.push(`double_distance="${p.doubleDistance}"`);
  if (p.bendLeft != null) args.push(`bend_left=${p.bendLeft}`);
  if (p.bendRight != null) args.push(`bend_right=${p.bendRight}`);
  if (p.comment) args.push(`comment="${p.comment}"`);

  return `fig.draw(${args.join(', ')})`;
}

function generatePythonCode() {
  if (!state.nodes.length && !state.rawTikz) return '# Add nodes to the canvas to generate code';
  const lines = ['from tikzfigure import TikzFigure', '', 'fig = TikzFigure()'];

  // Color definitions
  const colorDefs = [];
  state.nodes.forEach(node => {
    const fl = cssColorToLatex(node.fill);
    const dl = cssColorToLatex(node.draw);
    if (fl && fl.startsWith('{rgb')) colorDefs.push(`fig.colorlet("${node.id}_fill", "${fl.slice(1,-1)}")`);
    if (dl && dl.startsWith('{rgb')) colorDefs.push(`fig.colorlet("${node.id}_draw", "${dl.slice(1,-1)}")`);
  });
  state.paths.forEach(p => {
    const fl = cssColorToLatex(p.fill);
    if (fl && fl.startsWith('{rgb')) colorDefs.push(`fig.colorlet("${p.id}_fill", "${fl.slice(1,-1)}")`);
    const cl = cssColorToLatex(p.color);
    if (cl && cl.startsWith('{rgb') && p.color !== '#666666') colorDefs.push(`fig.colorlet("${p.id}_color", "${cl.slice(1,-1)}")`);
  });
  if (colorDefs.length) { lines.push(''); lines.push('# Define colors'); colorDefs.forEach(l => lines.push(l)); }

  // Group items by layer
  const hasMultipleLayers = state.layers.length > 1;
  const usedLayers = new Set();
  state.nodes.forEach(n => usedLayers.add(n.layer));
  state.paths.forEach(p => usedLayers.add(p.layer));
  const multiLayer = usedLayers.size > 1;

  if (multiLayer) {
    // Render layer by layer
    state.layers.forEach(layer => {
      const layerNodes = state.nodes.filter(n => n.layer === layer.id);
      const layerPaths = state.paths.filter(p => p.layer === layer.id);
      if (!layerNodes.length && !layerPaths.length) return;

      lines.push('');
      lines.push(`# Layer: ${layer.name} (${layer.id})`);

      if (layerNodes.length) {
        layerNodes.forEach(node => {
          const code = generateNodeCode(node);
          // Add layer parameter
          const insertPos = code.lastIndexOf(')');
          lines.push(code.slice(0, insertPos) + `, layer=${layer.id}` + code.slice(insertPos));
        });
      }

      if (layerPaths.length) {
        layerPaths.forEach(p => {
          const code = generatePathCode(p);
          const insertPos = code.lastIndexOf(')');
          lines.push(code.slice(0, insertPos) + `, layer=${layer.id}` + code.slice(insertPos));
        });
      }
    });
  } else {
    // Single layer — no layer parameter needed
    if (state.nodes.length) {
      lines.push(''); lines.push('# Add nodes');
      state.nodes.forEach(node => lines.push(generateNodeCode(node)));
    }

    if (state.paths.length) {
      lines.push(''); lines.push('# Add paths');
      state.paths.forEach(p => lines.push(generatePathCode(p)));
    }
  }

  // Raw TikZ
  if (state.rawTikz.trim()) {
    lines.push('');
    lines.push('# Raw TikZ');
    // Split into individual add_raw calls per line group
    const rawLines = state.rawTikz.trim();
    lines.push(`fig.add_raw("""${rawLines}""")`);
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
  if (!state.pyodideReady || (!state.nodes.length && !state.rawTikz)) return;
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

// ─── Drawer Section Switcher ───────────────────────────────────────────────

const drawerState = { section: 'code' };

function switchDrawerSection(section) {
  drawerState.section = section;
  document.querySelectorAll('.drawer-tab').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.section === section);
  });
  document.querySelectorAll('.drawer-section').forEach(el => {
    el.style.display = el.id === `drawer-section-${section}` ? '' : 'none';
  });
}

document.getElementById('drawer-tabs').addEventListener('click', (e) => {
  const btn = e.target.closest('.drawer-tab');
  if (btn) switchDrawerSection(btn.dataset.section);
});

// ─── Compile ───────────────────────────────────────────────────────────────

function openCompileDialog() {
  if (!state.standaloneLaTeX) {
    setStatus('No LaTeX code ready — add nodes and wait for Pyodide.');
    return;
  }
  runCompile(new Set(state.layers.map(l => l.id)));
}

async function runCompile(includedLayerIds) {
  if (!state.standaloneLaTeX) { setStatus('No LaTeX to compile.'); return; }

  const allIncluded = state.layers.every(l => includedLayerIds.has(l.id));
  let latexToCompile = state.standaloneLaTeX;

  if (!allIncluded) {
    const excludedNames = state.layers
      .filter(l => !includedLayerIds.has(l.id))
      .map(l => l.name);
    excludedNames.forEach(name => {
      const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const re = new RegExp(
        `\\\\begin\\{pgfonlayer\\}\\{${escaped}\\}[\\s\\S]*?\\\\end\\{pgfonlayer\\}`,
        'g'
      );
      latexToCompile = latexToCompile.replace(re, '');
    });
  }

  compileBtn.disabled = true;
  compileBtn.textContent = 'Compiling\u2026';
  setStatus('Sending to latex.ytotech.com\u2026');
  showLog('', false);

  try {
    const resp = await fetch('https://latex.ytotech.com/builds/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        compiler: 'pdflatex',
        resources: [{ main: true, content: latexToCompile }],
      }),
    });

    if (resp.status === 201) {
      const buf = await resp.arrayBuffer();
      if (state._prevPdfUrl) URL.revokeObjectURL(state._prevPdfUrl);
      const blob = new Blob([buf], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      state._prevPdfUrl = url;
      pdfViewer.src = url;
      pdfViewer.style.display = 'block';
      pdfDl.href = url;
      pdfDl.style.display = 'inline-block';
      setStatus('PDF compiled successfully.');
      showLog('Compilation successful.', false);
      document.getElementById('card-preview').open = true;
    } else {
      const json = await resp.json().catch(() => ({}));
      const log = (json.log_files || {})['__main_document__.log'] || JSON.stringify(json);
      showLog(log, true);
      const errLine = log.split('\n').find(l => l.startsWith('!') || /TeX capacity exceeded/i.test(l)) || `HTTP ${resp.status}`;
      setStatus(`Compilation error: ${errLine.trim()}`);
      switchDrawerSection('log');
    }
  } catch (err) {
    setStatus(`Network error: ${err.message}`);
    showLog(err.message, true);
  } finally {
    compileBtn.disabled = false;
    compileBtn.textContent = 'Compile to PDF (latex-on-http)';
  }
}

document.getElementById('compile-btn').addEventListener('click', () => openCompileDialog());

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

// ─── Raw TikZ Input ───────────────────────────────────────────────────────

if (rawTikzInput) {
  rawTikzInput.addEventListener('input', () => {
    state.rawTikz = rawTikzInput.value;
    upd();
  });
}

// ─── Copy Helpers ──────────────────────────────────────────────────────────

function copyCode(type) {
  const text = type === 'python' ? pythonPre.textContent : tikzPre.textContent;
  navigator.clipboard.writeText(text).then(
    () => setStatus(`Copied ${type === 'python' ? 'Python' : 'TikZ'} code.`),
    () => setStatus('Copy failed.')
  );
}
window.copyCode = copyCode;

document.getElementById('btn-compile-toolbar').addEventListener('click', () => openCompileDialog());

// ─── Export .tex ──────────────────────────────────────────────────────────

document.getElementById('btn-export-tex')?.addEventListener('click', () => {
  if (!state.standaloneLaTeX) {
    setStatus('No LaTeX code ready. Add nodes and wait for Pyodide.');
    return;
  }
  const blob = new Blob([state.standaloneLaTeX], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'figure.tex';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  setStatus('Downloaded figure.tex');
});

// ─── PDF Compilation ───────────────────────────────────────────────────────

const compileLogDetails = document.getElementById('compile-log-details');
const compileLog        = document.getElementById('compile-log');

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

// ─── Theme Toggle ─────────────────────────────────────────────────────────

function toggleTheme() {
  const isLight = document.body.classList.toggle('light');
  document.getElementById('theme-icon-dark').style.display = isLight ? 'none' : '';
  document.getElementById('theme-icon-light').style.display = isLight ? '' : 'none';
  const dot = document.querySelector('#grid-dots circle');
  if (dot) dot.setAttribute('fill', isLight ? '#d0d1d9' : '#282d3e');
  localStorage.setItem('tikz-editor-theme', isLight ? 'light' : 'dark');
}

document.getElementById('btn-theme').onclick = toggleTheme;

if (localStorage.getItem('tikz-editor-theme') === 'light') toggleTheme();

// ─── Template Gallery ─────────────────────────────────────────────────────

const TEMPLATES = [
  {
    name: 'Simple Graph',
    desc: 'Nodes connected with arrows',
    preview: '<svg viewBox="0 0 120 50"><circle cx="20" cy="25" r="8" fill="none" stroke="#818cf8" stroke-width="1.5"/><circle cx="60" cy="25" r="8" fill="none" stroke="#818cf8" stroke-width="1.5"/><circle cx="100" cy="25" r="8" fill="none" stroke="#818cf8" stroke-width="1.5"/><line x1="28" y1="25" x2="50" y2="25" stroke="#666" stroke-width="1.2" marker-end="url(#tpl-arrow)"/><line x1="68" y1="25" x2="90" y2="25" stroke="#666" stroke-width="1.2" marker-end="url(#tpl-arrow)"/><text x="20" y="28" text-anchor="middle" fill="#818cf8" font-size="8">A</text><text x="60" y="28" text-anchor="middle" fill="#818cf8" font-size="8">B</text><text x="100" y="28" text-anchor="middle" fill="#818cf8" font-size="8">C</text></svg>',
    nodes: [
      { x: 200, y: 260, label: 'A' },
      { x: 400, y: 260, label: 'B' },
      { x: 600, y: 260, label: 'C' },
    ],
    paths: [
      { ni: [0, 1], arrow: 'stealth' },
      { ni: [1, 2], arrow: 'stealth' },
    ],
  },
  {
    name: 'Triangle',
    desc: 'Cycled path with fill',
    preview: '<svg viewBox="0 0 120 70"><polygon points="60,8 20,58 100,58" fill="rgba(129,140,248,0.15)" stroke="#818cf8" stroke-width="1.5"/><circle cx="60" cy="8" r="4" fill="#818cf8"/><circle cx="20" cy="58" r="4" fill="#818cf8"/><circle cx="100" cy="58" r="4" fill="#818cf8"/></svg>',
    nodes: [
      { x: 400, y: 160, label: 'A' },
      { x: 240, y: 400, label: 'B' },
      { x: 560, y: 400, label: 'C' },
    ],
    paths: [
      { ni: [0, 1, 2], cycle: true, fill: '#334488', center: true },
    ],
  },
  {
    name: 'Flowchart',
    desc: 'Decision flow with shapes',
    preview: '<svg viewBox="0 0 120 70"><rect x="42" y="2" width="36" height="16" rx="8" fill="none" stroke="#818cf8" stroke-width="1.2"/><rect x="42" y="26" width="36" height="16" fill="none" stroke="#818cf8" stroke-width="1.2"/><polygon points="60,48 78,58 60,68 42,58" fill="none" stroke="#818cf8" stroke-width="1.2"/><line x1="60" y1="18" x2="60" y2="26" stroke="#666" stroke-width="1" marker-end="url(#tpl-arrow)"/><line x1="60" y1="42" x2="60" y2="48" stroke="#666" stroke-width="1" marker-end="url(#tpl-arrow)"/></svg>',
    nodes: [
      { x: 400, y: 120, label: 'Start', shape: 'ellipse', fill: '#1a3a2a' },
      { x: 400, y: 260, label: 'Process', shape: 'rectangle', minWidth: 80, minHeight: 40 },
      { x: 400, y: 420, label: '?', shape: 'diamond', minWidth: 60, minHeight: 60 },
      { x: 600, y: 420, label: 'Yes' },
      { x: 200, y: 420, label: 'No' },
    ],
    paths: [
      { ni: [0, 1], arrow: 'stealth' },
      { ni: [1, 2], arrow: 'stealth' },
      { ni: [2, 3], arrow: 'stealth' },
      { ni: [2, 4], arrow: 'stealth' },
    ],
  },
  {
    name: 'Network',
    desc: 'Interconnected nodes',
    preview: '<svg viewBox="0 0 120 70"><circle cx="25" cy="18" r="6" fill="none" stroke="#818cf8" stroke-width="1.2"/><circle cx="95" cy="18" r="6" fill="none" stroke="#818cf8" stroke-width="1.2"/><circle cx="25" cy="52" r="6" fill="none" stroke="#818cf8" stroke-width="1.2"/><circle cx="95" cy="52" r="6" fill="none" stroke="#818cf8" stroke-width="1.2"/><line x1="31" y1="18" x2="89" y2="18" stroke="#666" stroke-width="1"/><line x1="25" y1="24" x2="25" y2="46" stroke="#666" stroke-width="1"/><line x1="95" y1="24" x2="95" y2="46" stroke="#666" stroke-width="1"/><line x1="31" y1="52" x2="89" y2="52" stroke="#666" stroke-width="1"/><line x1="31" y1="22" x2="89" y2="48" stroke="#666" stroke-width="1" stroke-dasharray="3 2"/></svg>',
    nodes: [
      { x: 220, y: 180, label: 'A' },
      { x: 540, y: 180, label: 'B' },
      { x: 220, y: 380, label: 'C' },
      { x: 540, y: 380, label: 'D' },
    ],
    paths: [
      { ni: [0, 1] },
      { ni: [0, 2] },
      { ni: [1, 3] },
      { ni: [2, 3] },
      { ni: [0, 3], dashPattern: 'dashed' },
    ],
  },
  {
    name: 'State Machine',
    desc: 'States with labeled transitions',
    preview: '<svg viewBox="0 0 120 60"><circle cx="30" cy="30" r="12" fill="none" stroke="#818cf8" stroke-width="1.5"/><circle cx="90" cy="30" r="12" fill="none" stroke="#818cf8" stroke-width="1.5"/><line x1="42" y1="26" x2="76" y2="26" stroke="#666" stroke-width="1.2" marker-end="url(#tpl-arrow)"/><line x1="78" y1="34" x2="42" y2="34" stroke="#666" stroke-width="1.2" marker-end="url(#tpl-arrow)"/><text x="30" y="33" text-anchor="middle" fill="#818cf8" font-size="7">S0</text><text x="90" y="33" text-anchor="middle" fill="#818cf8" font-size="7">S1</text></svg>',
    nodes: [
      { x: 200, y: 280, label: 'S0', fill: '#1a2e3a' },
      { x: 500, y: 280, label: 'S1', fill: '#1a2e3a' },
      { x: 500, y: 440, label: 'S2', fill: '#1a2e3a' },
    ],
    paths: [
      { ni: [0, 1], arrow: 'stealth' },
      { ni: [1, 2], arrow: 'stealth' },
      { ni: [2, 0], arrow: 'stealth', dashPattern: 'dashed' },
    ],
  },
  {
    name: 'Binary Tree',
    desc: 'Hierarchical tree structure',
    preview: '<svg viewBox="0 0 120 70"><circle cx="60" cy="10" r="6" fill="none" stroke="#818cf8" stroke-width="1.2"/><circle cx="30" cy="38" r="6" fill="none" stroke="#818cf8" stroke-width="1.2"/><circle cx="90" cy="38" r="6" fill="none" stroke="#818cf8" stroke-width="1.2"/><circle cx="15" cy="60" r="5" fill="none" stroke="#818cf8" stroke-width="1"/><circle cx="45" cy="60" r="5" fill="none" stroke="#818cf8" stroke-width="1"/><line x1="55" y1="15" x2="34" y2="33" stroke="#666" stroke-width="1"/><line x1="65" y1="15" x2="86" y2="33" stroke="#666" stroke-width="1"/><line x1="26" y1="43" x2="18" y2="55" stroke="#666" stroke-width="1"/><line x1="34" y1="43" x2="42" y2="55" stroke="#666" stroke-width="1"/></svg>',
    nodes: [
      { x: 400, y: 120, label: '1' },
      { x: 260, y: 260, label: '2' },
      { x: 540, y: 260, label: '3' },
      { x: 190, y: 400, label: '4' },
      { x: 330, y: 400, label: '5' },
      { x: 470, y: 400, label: '6' },
      { x: 610, y: 400, label: '7' },
    ],
    paths: [
      { ni: [0, 1] },
      { ni: [0, 2] },
      { ni: [1, 3] },
      { ni: [1, 4] },
      { ni: [2, 5] },
      { ni: [2, 6] },
    ],
  },
  {
    name: 'Neural Network',
    desc: 'Layered network diagram',
    preview: '<svg viewBox="0 0 120 70"><circle cx="20" cy="18" r="5" fill="none" stroke="#818cf8" stroke-width="1"/><circle cx="20" cy="35" r="5" fill="none" stroke="#818cf8" stroke-width="1"/><circle cx="20" cy="52" r="5" fill="none" stroke="#818cf8" stroke-width="1"/><circle cx="60" cy="24" r="5" fill="none" stroke="#f59e0b" stroke-width="1"/><circle cx="60" cy="46" r="5" fill="none" stroke="#f59e0b" stroke-width="1"/><circle cx="100" cy="35" r="5" fill="none" stroke="#6ee7b7" stroke-width="1"/><line x1="25" y1="18" x2="55" y2="24" stroke="#666" stroke-width="0.7"/><line x1="25" y1="18" x2="55" y2="46" stroke="#666" stroke-width="0.7"/><line x1="25" y1="35" x2="55" y2="24" stroke="#666" stroke-width="0.7"/><line x1="25" y1="35" x2="55" y2="46" stroke="#666" stroke-width="0.7"/><line x1="25" y1="52" x2="55" y2="24" stroke="#666" stroke-width="0.7"/><line x1="25" y1="52" x2="55" y2="46" stroke="#666" stroke-width="0.7"/><line x1="65" y1="24" x2="95" y2="35" stroke="#666" stroke-width="0.7"/><line x1="65" y1="46" x2="95" y2="35" stroke="#666" stroke-width="0.7"/></svg>',
    nodes: [
      { x: 160, y: 160, label: 'x1' },
      { x: 160, y: 280, label: 'x2' },
      { x: 160, y: 400, label: 'x3' },
      { x: 380, y: 200, label: 'h1', draw: '#f59e0b' },
      { x: 380, y: 340, label: 'h2', draw: '#f59e0b' },
      { x: 600, y: 280, label: 'y', draw: '#6ee7b7' },
    ],
    paths: [
      { ni: [0, 3] }, { ni: [0, 4] },
      { ni: [1, 3] }, { ni: [1, 4] },
      { ni: [2, 3] }, { ni: [2, 4] },
      { ni: [3, 5], arrow: 'stealth' },
      { ni: [4, 5], arrow: 'stealth' },
    ],
  },
  {
    name: 'Layered',
    desc: 'Multi-layer demo (bg + fg)',
    preview: '<svg viewBox="0 0 120 70"><rect x="10" y="10" width="100" height="50" rx="6" fill="rgba(129,140,248,0.1)" stroke="#818cf8" stroke-width="1" stroke-dasharray="3 2"/><circle cx="40" cy="35" r="10" fill="none" stroke="#f59e0b" stroke-width="1.5"/><circle cx="80" cy="35" r="10" fill="none" stroke="#6ee7b7" stroke-width="1.5"/><line x1="50" y1="35" x2="70" y2="35" stroke="#666" stroke-width="1.2" marker-end="url(#tpl-arrow)"/></svg>',
    nodes: [
      { x: 280, y: 260, label: 'A', draw: '#f59e0b', layer: 0 },
      { x: 500, y: 260, label: 'B', draw: '#6ee7b7', layer: 0 },
    ],
    paths: [
      { ni: [0, 1], arrow: 'stealth', layer: 0 },
    ],
    layers: [
      { name: 'Background', items: 'bg' },
      { name: 'Foreground', items: 'fg' },
    ],
    setup: (state) => {
      // Add a second layer to demonstrate
      if (state.layers.length === 1) {
        state.layers.push({ id: state.nextLayerId++, name: 'Background', visible: true, locked: false });
      }
    },
  },
];

function loadTemplate(tpl) {
  saveHistory();
  state.nodes = [];
  state.paths = [];
  state.nextNodeId = 1;
  state.nextPathId = 1;

  // Reset layers if template has custom setup
  if (tpl.setup) tpl.setup(state);

  tpl.nodes.forEach(n => {
    const node = defaultNode(n.x, n.y);
    if (n.label) node.label = n.label;
    if (n.shape) node.shape = n.shape;
    if (n.fill) node.fill = n.fill;
    if (n.draw) node.draw = n.draw;
    if (n.minWidth) node.minWidth = n.minWidth;
    if (n.minHeight) node.minHeight = n.minHeight;
    if (n.layer != null) node.layer = n.layer;
    state.nodes.push(node);
  });

  tpl.paths.forEach(p => {
    const nodeIds = p.ni.map(i => state.nodes[i].id);
    const path = defaultPath(nodeIds);
    if (p.arrow) path.arrow = p.arrow;
    if (p.cycle) path.cycle = true;
    if (p.center) path.center = true;
    if (p.fill) path.fill = p.fill;
    if (p.dashPattern) path.dashPattern = p.dashPattern;
    if (p.layer != null) path.layer = p.layer;
    state.paths.push(path);
  });

  clearSelection();
  hideTemplateGallery();
  renderLayersPanel();
  setStatus(`Loaded "${tpl.name}" template.`);
}

function showTemplateGallery() {
  const el = document.getElementById('template-gallery');
  el.classList.remove('hidden');
  el.innerHTML = `
    <div class="tpl-title">Start with a template</div>
    <div class="tpl-subtitle">Or press N to add nodes manually</div>
    <svg style="position:absolute;width:0;height:0">
      <defs><marker id="tpl-arrow" markerWidth="6" markerHeight="5" refX="5" refY="2.5" orient="auto"><polygon points="0 0,6 2.5,0 5" fill="#666"/></marker></defs>
    </svg>
    <div class="tpl-grid">
      ${TEMPLATES.map((t, i) => `
        <button class="tpl-card" data-tpl="${i}">
          ${t.preview}
          <span class="tpl-card-name">${t.name}</span>
          <span class="tpl-card-desc">${t.desc}</span>
        </button>
      `).join('')}
    </div>
  `;
  el.querySelectorAll('.tpl-card').forEach(btn => {
    btn.addEventListener('click', () => loadTemplate(TEMPLATES[parseInt(btn.dataset.tpl)]));
  });
}

function hideTemplateGallery() {
  document.getElementById('template-gallery').classList.add('hidden');
}

// ─── Init ──────────────────────────────────────────────────────────────────

updateWorldTransform();
renderLayersPanel();
if (!state.nodes.length) showTemplateGallery();
