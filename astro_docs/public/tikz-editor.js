// ─── State ────────────────────────────────────────────────────────────────────

const state = {
  nodes: [],   // { id, x, y, label, shape, fill, draw, textColor, minWidth, minHeight, opacity, fillOpacity, drawOpacity, minimumSize, innerSep, outerSep, nodeLineWidth, font, textWidth, align, anchor, rotate, xshift, yshift, scale, roundedCorners, dashPattern, doubleBorder, pattern, shading }
  edges: [],   // { id, sourceId, targetId, color, lineWidth, arrow, bendLeft, bendRight }
  selected: null,        // { type: 'node'|'edge', id }
  mode: 'select',        // 'select' | 'node' | 'edge'
  edgeSource: null,      // node id while drawing an edge
  nextNodeId: 1,
  nextEdgeId: 1,
  pyodide: null,
  pyodideReady: false,
  standaloneLaTeX: '',
};

// ─── DOM References ────────────────────────────────────────────────────────────

const svgCanvas    = document.getElementById('svg-canvas');
const nodesLayer   = document.getElementById('nodes-layer');
const edgesLayer   = document.getElementById('edges-layer');
const canvasArea   = document.getElementById('canvas-area');
const statusBar    = document.getElementById('status-bar');
const propPanel    = document.getElementById('properties-panel');
const pythonPre    = document.getElementById('python-code');
const tikzPre      = document.getElementById('tikz-code');
const compileBtn   = document.getElementById('compile-btn');
const pdfCanvas    = document.getElementById('pdf-canvas');
const pyodideStatus = document.getElementById('pyodide-status');
const resizer      = document.getElementById('resizer');
const rightPanelEl = document.getElementById('right-panel');

// ─── Resizer drag ──────────────────────────────────────────────────────────────

resizer.addEventListener('mousedown', (e) => {
  e.preventDefault();
  const startX = e.clientX;
  const startWidth = rightPanelEl.offsetWidth;
  const onMove = (ev) => {
    const newWidth = startWidth + (startX - ev.clientX);
    rightPanelEl.style.width = `${Math.max(20, newWidth)}px`;
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

// ─── Node defaults ─────────────────────────────────────────────────────────────

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
    // Optional extended properties (null = use tikzfigure default)
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
    color: '#94a3b8',
    lineWidth: 1.5,
    arrow: 'stealth',
    bendLeft: 0,
    bendRight: 0,
  };
}

// ─── SVG Utilities ─────────────────────────────────────────────────────────────

function svgPoint(evt) {
  const rect = svgCanvas.getBoundingClientRect();
  return { x: evt.clientX - rect.left, y: evt.clientY - rect.top };
}

function snapToGrid(v, grid = 15) {
  return Math.round(v / grid) * grid;
}

// ─── Render ────────────────────────────────────────────────────────────────────

function renderAll() {
  renderEdges();
  renderNodes();
  generateCode();
}

function renderNodes() {
  nodesLayer.innerHTML = '';
  for (const node of state.nodes) {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', 'tikz-node' + (state.selected?.type === 'node' && state.selected.id === node.id ? ' selected' : '') + (state.edgeSource === node.id ? ' edge-source' : ''));
    g.setAttribute('data-id', node.id);
    g.setAttribute('transform', `translate(${node.x}, ${node.y})`);

    const hw = node.minWidth / 2, hh = node.minHeight / 2;

    let shape;
    if (node.shape === 'circle') {
      shape = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      const r = Math.max(hw, hh);
      shape.setAttribute('r', r);
      shape.setAttribute('cx', 0);
      shape.setAttribute('cy', 0);
    } else if (node.shape === 'ellipse') {
      shape = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
      shape.setAttribute('rx', hw);
      shape.setAttribute('ry', hh);
      shape.setAttribute('cx', 0);
      shape.setAttribute('cy', 0);
    } else {
      shape = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      shape.setAttribute('x', -hw);
      shape.setAttribute('y', -hh);
      shape.setAttribute('width', node.minWidth);
      shape.setAttribute('height', node.minHeight);
      shape.setAttribute('rx', 4);
    }
    shape.setAttribute('fill', node.fill || '#e2e8f0');
    shape.setAttribute('stroke', node.draw || '#475569');
    g.appendChild(shape);

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('dominant-baseline', 'central');
    text.setAttribute('fill', node.textColor || '#1e293b');
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

    const isSelected = state.selected?.type === 'edge' && state.selected.id === edge.id;

    let d;
    if (edge.bendLeft !== 0 || edge.bendRight !== 0) {
      const bend = (edge.bendLeft - edge.bendRight) * 0.5;
      const mx = (src.x + tgt.x) / 2;
      const my = (src.y + tgt.y) / 2;
      const dx = tgt.x - src.x, dy = tgt.y - src.y;
      const len = Math.sqrt(dx * dx + dy * dy) || 1;
      const cpx = mx + (-dy / len) * bend * 1.5;
      const cpy = my + (dx / len) * bend * 1.5;
      d = `M ${src.x} ${src.y} Q ${cpx} ${cpy} ${tgt.x} ${tgt.y}`;
    } else {
      d = `M ${src.x} ${src.y} L ${tgt.x} ${tgt.y}`;
    }

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('class', 'tikz-edge' + (isSelected ? ' selected' : ''));
    path.setAttribute('d', d);
    path.setAttribute('stroke', isSelected ? '#a78bfa' : edge.color);
    path.setAttribute('stroke-width', edge.lineWidth);
    if (edge.arrow !== 'none') {
      path.setAttribute('marker-end', isSelected ? 'url(#arrowhead-selected)' : 'url(#arrowhead)');
    }
    path.setAttribute('data-id', edge.id);
    path.addEventListener('click', () => selectEdge(edge.id));
    edgesLayer.appendChild(path);
  }
}

// ─── Node drag events ──────────────────────────────────────────────────────────

function attachNodeEvents(g, node) {
  let dragging = false, startX, startY, origX, origY;

  g.addEventListener('mousedown', (e) => {
    if (state.mode === 'edge') {
      handleEdgeClick(node.id);
      e.stopPropagation();
      return;
    }
    if (state.mode !== 'select') return;
    e.stopPropagation();
    dragging = true;
    startX = e.clientX; startY = e.clientY;
    origX = node.x; origY = node.y;
    selectNode(node.id);
    g.style.cursor = 'grabbing';

    const onMove = (ev) => {
      if (!dragging) return;
      node.x = snapToGrid(origX + (ev.clientX - startX));
      node.y = snapToGrid(origY + (ev.clientY - startY));
      renderAll();
    };
    const onUp = () => {
      dragging = false;
      g.style.cursor = 'grab';
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  });
}

// ─── Selection ─────────────────────────────────────────────────────────────────

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
  propPanel.innerHTML = '<p style="font-size:0.78rem;color:#64748b;">Select a node or edge to edit its properties.</p>';
  renderAll();
}

// ─── Edge creation ─────────────────────────────────────────────────────────────

function handleEdgeClick(nodeId) {
  if (!state.edgeSource) {
    state.edgeSource = nodeId;
    setStatus('Edge mode: click a target node to connect.');
    renderNodes();
  } else if (state.edgeSource === nodeId) {
    state.edgeSource = null;
    setStatus('Edge mode: click a source node.');
    renderNodes();
  } else {
    const edge = defaultEdge(state.edgeSource, nodeId);
    state.edges.push(edge);
    state.edgeSource = null;
    setStatus(`Edge added: ${edge.sourceId} → ${edge.targetId}`);
    renderAll();
  }
}

// ─── Canvas click (add node in node mode) ─────────────────────────────────────

canvasArea.addEventListener('click', (e) => {
  if (state.mode !== 'node') return;
  if (e.target !== svgCanvas && !e.target.closest('#svg-canvas')) return;
  const pt = svgPoint(e);
  const node = defaultNode(snapToGrid(pt.x), snapToGrid(pt.y));
  state.nodes.push(node);
  selectNode(node.id);
  setStatus(`Node "${node.label}" added at (${node.x}, ${node.y})`);
});

svgCanvas.addEventListener('click', (e) => {
  if (state.mode === 'select' && e.target === svgCanvas) {
    clearSelection();
  }
});

// ─── Tool buttons ──────────────────────────────────────────────────────────────

function setMode(mode) {
  state.mode = mode;
  state.edgeSource = null;
  document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
  canvasArea.className = '';
  if (mode === 'select') {
    document.getElementById('btn-select').classList.add('active');
    canvasArea.classList.add('mode-select');
    setStatus('Select mode: click nodes or edges to select, drag to move.');
  } else if (mode === 'node') {
    document.getElementById('btn-add-node').classList.add('active');
    canvasArea.classList.add('mode-node');
    setStatus('Node mode: click on the canvas to add a node.');
  } else if (mode === 'edge') {
    document.getElementById('btn-add-edge').classList.add('active');
    canvasArea.classList.add('mode-edge');
    setStatus('Edge mode: click a source node, then a target node.');
  }
  renderNodes();
}

document.getElementById('btn-select').onclick = () => setMode('select');
document.getElementById('btn-add-node').onclick = () => setMode('node');
document.getElementById('btn-add-edge').onclick = () => setMode('edge');

document.getElementById('btn-delete').onclick = () => {
  if (!state.selected) return;
  if (state.selected.type === 'node') {
    const id = state.selected.id;
    state.nodes = state.nodes.filter(n => n.id !== id);
    state.edges = state.edges.filter(e => e.sourceId !== id && e.targetId !== id);
  } else {
    state.edges = state.edges.filter(e => e.id !== state.selected.id);
  }
  clearSelection();
  setStatus('Deleted.');
};

document.getElementById('btn-clear').onclick = () => {
  if (!confirm('Clear all nodes and edges?')) return;
  state.nodes = []; state.edges = []; state.nextNodeId = 1; state.nextEdgeId = 1;
  clearSelection();
  setStatus('Cleared.');
};

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT') return;
  if (e.key === 'v' || e.key === 'V') setMode('select');
  if (e.key === 'n' || e.key === 'N') setMode('node');
  if (e.key === 'e' || e.key === 'E') setMode('edge');
  if (e.key === 'Delete' || e.key === 'Backspace') document.getElementById('btn-delete').click();
  if (e.key === 'Escape') { setMode('select'); clearSelection(); }
});

// ─── Status bar ────────────────────────────────────────────────────────────────

function setStatus(msg) { statusBar.textContent = msg; }

// ─── Properties Panel ──────────────────────────────────────────────────────────

function propRow(labelText, inputHtml) {
  return `<div class="prop-row"><label>${labelText}</label>${inputHtml}</div>`;
}

function showNodeProperties(node) {
  if (!node) return;
  const shapeOptions = ['rectangle','circle','ellipse','diamond','star','regular polygon','trapezium','cloud','cylinder','kite'];
  const anchorOptions = ['center','north','south','east','west','north east','north west','south east','south west'];
  const alignOptions = ['left','center','right','justify'];
  const patternOptions = ['horizontal lines','vertical lines','north east lines','north west lines','grid','crosshatch','dots','crosshatch dots','bricks','checkerboard'];

  propPanel.innerHTML = `
    <strong style="font-size:0.8rem;color:#a78bfa;display:block;margin-bottom:0.5rem;">Node: ${node.id}</strong>

    <details class="prop-group" open>
      <summary>Basic</summary>
      <div class="prop-group-body">
        ${propRow('Content', `<input type="text" id="p-label" value="${node.label.replace(/"/g,'&quot;')}">`)}
        ${propRow('Shape', `<select id="p-shape">${shapeOptions.map(s=>`<option value="${s}"${node.shape===s?' selected':''}>${s}</option>`).join('')}</select>`)}
        ${propRow('X (px)', `<input type="number" id="p-x" value="${node.x}" step="15">`)}
        ${propRow('Y (px)', `<input type="number" id="p-y" value="${node.y}" step="15">`)}
      </div>
    </details>

    <details class="prop-group" open>
      <summary>Colors</summary>
      <div class="prop-group-body">
        ${propRow('Fill', `<label class="color-none-wrap"><input type="checkbox" id="p-fill-none"${!node.fill?' checked':''}>none</label><input type="color" id="p-fill" value="${hexColor(node.fill)}"${!node.fill?' disabled':''}>`)}
        ${propRow('Border', `<label class="color-none-wrap"><input type="checkbox" id="p-draw-none"${!node.draw?' checked':''}>none</label><input type="color" id="p-draw" value="${hexColor(node.draw)}"${!node.draw?' disabled':''}>`)}
        ${propRow('Text', `<label class="color-none-wrap"><input type="checkbox" id="p-text-none"${!node.textColor?' checked':''}>none</label><input type="color" id="p-text" value="${hexColor(node.textColor)}"${!node.textColor?' disabled':''}>`)}
        ${propRow('Opacity', `<input type="number" id="p-opacity" value="${node.opacity??''}" min="0" max="1" step="0.05" placeholder="0–1">`)}
        ${propRow('Fill opacity', `<input type="number" id="p-fillopacity" value="${node.fillOpacity??''}" min="0" max="1" step="0.05" placeholder="0–1">`)}
        ${propRow('Draw opacity', `<input type="number" id="p-drawopacity" value="${node.drawOpacity??''}" min="0" max="1" step="0.05" placeholder="0–1">`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Size &amp; Spacing</summary>
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
        ${propRow('Align', `<select id="p-align"><option value=""${!node.align?' selected':''}>—</option>${alignOptions.map(a=>`<option value="${a}"${node.align===a?' selected':''}>${a}</option>`).join('')}</select>`)}
        ${propRow('Anchor', `<select id="p-anchor"><option value=""${!node.anchor?' selected':''}>—</option>${anchorOptions.map(a=>`<option value="${a}"${node.anchor===a?' selected':''}>${a}</option>`).join('')}</select>`)}
      </div>
    </details>

    <details class="prop-group">
      <summary>Transform</summary>
      <div class="prop-group-body">
        ${propRow('Rotate °', `<input type="number" id="p-rotate" value="${node.rotate??''}" step="5" placeholder="degrees">`)}
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
        ${propRow('Pattern', `<select id="p-pattern"><option value=""${!node.pattern?' selected':''}>— none —</option>${patternOptions.map(p=>`<option value="${p}"${node.pattern===p?' selected':''}>${p}</option>`).join('')}</select>`)}
        ${propRow('Shading', `<select id="p-shading"><option value=""${!node.shading?' selected':''}>— none —</option>${['axis','radial','ball'].map(s=>`<option value="${s}"${node.shading===s?' selected':''}>${s}</option>`).join('')}</select>`)}
      </div>
    </details>
  `;

  function upd() { renderAll(); if (state.pyodideReady) scheduleCodeGen(); }
  function bindStr(id, key) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('input', () => { node[key] = el.value || null; upd(); });
  }
  function bindNum(id, key) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('input', () => { node[key] = el.value === '' ? null : Number(el.value); upd(); });
  }
  function bindNumReq(id, key) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('input', () => { const v = parseFloat(el.value); if (!isNaN(v)) { node[key] = v; upd(); } });
  }
  function bindColor(noneId, colorId, key, defaultColor = '#000000') {
    const noneEl  = document.getElementById(noneId);
    const colorEl = document.getElementById(colorId);
    if (!noneEl || !colorEl) return;
    noneEl.addEventListener('change', () => {
      if (noneEl.checked) { node[key] = null; colorEl.disabled = true; }
      else { node[key] = colorEl.value || defaultColor; colorEl.disabled = false; }
      upd();
    });
    colorEl.addEventListener('input', () => { node[key] = colorEl.value; upd(); });
  }
  function bindBool(id, key) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('change', () => { node[key] = el.checked; upd(); });
  }

  // Basic
  const labelEl = document.getElementById('p-label');
  if (labelEl) labelEl.addEventListener('input', () => { node.label = labelEl.value; upd(); });
  const shapeEl = document.getElementById('p-shape');
  if (shapeEl) shapeEl.addEventListener('input', () => { node.shape = shapeEl.value; upd(); });
  bindNumReq('p-x', 'x');
  bindNumReq('p-y', 'y');
  // Colors
  bindColor('p-fill-none', 'p-fill', 'fill', '#e2e8f0');
  bindColor('p-draw-none', 'p-draw', 'draw', '#475569');
  bindColor('p-text-none', 'p-text', 'textColor', '#1e293b');
  bindNum('p-opacity', 'opacity');
  bindNum('p-fillopacity', 'fillOpacity');
  bindNum('p-drawopacity', 'drawOpacity');
  // Size & Spacing
  bindNumReq('p-mw', 'minWidth');
  bindNumReq('p-mh', 'minHeight');
  bindStr('p-minsize', 'minimumSize');
  bindStr('p-innersep', 'innerSep');
  bindStr('p-outersep', 'outerSep');
  bindStr('p-nlw', 'nodeLineWidth');
  // Text
  bindStr('p-font', 'font');
  bindStr('p-textwidth', 'textWidth');
  bindStr('p-align', 'align');
  bindStr('p-anchor', 'anchor');
  // Transform
  bindNum('p-rotate', 'rotate');
  bindStr('p-xshift', 'xshift');
  bindStr('p-yshift', 'yshift');
  bindNum('p-scale', 'scale');
  // Border
  bindStr('p-rounded', 'roundedCorners');
  bindBool('p-double', 'doubleBorder');
  bindStr('p-dash', 'dashPattern');
  // Pattern / Shading
  bindStr('p-pattern', 'pattern');
  bindStr('p-shading', 'shading');
}

function showEdgeProperties(edge) {
  if (!edge) return;
  const src = state.nodes.find(n => n.id === edge.sourceId);
  const tgt = state.nodes.find(n => n.id === edge.targetId);
  propPanel.innerHTML = `
    <strong style="font-size:0.8rem;color:#a78bfa;">Edge: ${edge.id}</strong>
    <p style="font-size:0.72rem;color:#64748b;margin:0.3rem 0 0.5rem;">${src?.label || edge.sourceId} → ${tgt?.label || edge.targetId}</p>
    ${propRow('Color', `<input type="color" id="p-ecolor" value="${hexColor(edge.color)}">`)}
    ${propRow('Line width', `<input type="number" id="p-elw" value="${edge.lineWidth}" min="0.5" step="0.5">`)}
    ${propRow('Arrow', `<select id="p-earrow">
      <option value="stealth" ${edge.arrow==='stealth'?'selected':''}>Stealth →</option>
      <option value="to" ${edge.arrow==='to'?'selected':''}>To →</option>
      <option value="latex" ${edge.arrow==='latex'?'selected':''}>LaTeX →</option>
      <option value="none" ${edge.arrow==='none'?'selected':''}>None</option>
    </select>`)}
    ${propRow('Bend left', `<input type="number" id="p-ebl" value="${edge.bendLeft}" min="-90" max="90" step="5">`)}
    ${propRow('Bend right', `<input type="number" id="p-ebr" value="${edge.bendRight}" min="-90" max="90" step="5">`)}
  `;

  const bind = (id, key, parse = v => v) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('input', () => {
      edge[key] = parse(el.value);
      renderAll();
      if (state.pyodideReady) scheduleCodeGen();
    });
  };

  bind('p-ecolor',  'color');
  bind('p-elw',     'lineWidth', Number);
  bind('p-earrow',  'arrow');
  bind('p-ebl',     'bendLeft',  Number);
  bind('p-ebr',     'bendRight', Number);
}

function hexColor(c) {
  if (!c || c === 'none') return '#888888';
  if (/^#[0-9a-fA-F]{6}$/.test(c)) return c;
  try {
    const ctx = document.createElement('canvas').getContext('2d');
    ctx.fillStyle = c;
    const style = ctx.fillStyle;
    if (/^#/.test(style)) return style;
    const m = style.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (m) return '#' + [m[1],m[2],m[3]].map(x => parseInt(x).toString(16).padStart(2,'0')).join('');
  } catch {}
  return '#888888';
}

// ─── Python Code Generation ────────────────────────────────────────────────────

const PX_PER_UNIT = 30;

function svgToTikz(px, py) {
  const cx = +(px / PX_PER_UNIT).toFixed(2);
  const cy = +((300 - py) / PX_PER_UNIT).toFixed(2);
  return { cx, cy };
}

function cssColorToLatex(hex) {
  if (!hex || hex === 'none') return null;
  if (/^#[0-9a-fA-F]{6}$/.test(hex)) {
    const r = parseInt(hex.slice(1,3), 16);
    const g = parseInt(hex.slice(3,5), 16);
    const b = parseInt(hex.slice(5,7), 16);
    return `{rgb,255:red,${r};green,${g};blue,${b}}`;
  }
  return hex;
}

function arrowToTikz(arrow) {
  const map = { stealth: '-Stealth', to: '->', latex: '-latex', none: '-' };
  return map[arrow] || '-Stealth';
}

function generatePythonCode() {
  if (state.nodes.length === 0) return '# Add nodes to the canvas to generate code';

  const lines = ['from tikzfigure import TikzFigure', '', 'fig = TikzFigure()'];

  const colorDefs = [];
  state.nodes.forEach(node => {
    const fillLatex = cssColorToLatex(node.fill);
    const drawLatex = cssColorToLatex(node.draw);
    // Strip outer braces — fig.colorlet wraps in {} itself, so passing {rgb,...} → double braces
    if (fillLatex && fillLatex.startsWith('{rgb')) {
      colorDefs.push(`fig.colorlet("${node.id}_fill", "${fillLatex.slice(1, -1)}")`);
    }
    if (drawLatex && drawLatex.startsWith('{rgb')) {
      colorDefs.push(`fig.colorlet("${node.id}_draw", "${drawLatex.slice(1, -1)}")`);
    }
  });
  if (colorDefs.length > 0) {
    lines.push('');
    lines.push('# Define colors');
    colorDefs.forEach(l => lines.push(l));
  }

  lines.push('');
  lines.push('# Add nodes');
  state.nodes.forEach(node => {
    const { cx, cy } = svgToTikz(node.x, node.y);
    const mw = (node.minWidth / PX_PER_UNIT).toFixed(1) + 'cm';
    const mh = (node.minHeight / PX_PER_UNIT).toFixed(1) + 'cm';
    const fillArg = node.fill && node.fill !== 'none' ? `, fill="${node.id}_fill"` : '';
    const drawArg = node.draw && node.draw !== 'none' ? `, draw="${node.id}_draw"` : '';
    const shapeArg = node.shape !== 'rectangle' ? `, shape="${node.shape}"` : '';
    const textArg = node.textColor ? `, text="${cssColorToLatex(node.textColor)}"` : '';
    const extraArgs = [];
    if (node.opacity     != null) extraArgs.push(`opacity=${node.opacity}`);
    if (node.fillOpacity != null) extraArgs.push(`fill_opacity=${node.fillOpacity}`);
    if (node.drawOpacity != null) extraArgs.push(`draw_opacity=${node.drawOpacity}`);
    if (node.minimumSize)  extraArgs.push(`minimum_size="${node.minimumSize}"`);
    if (node.innerSep)     extraArgs.push(`inner_sep="${node.innerSep}"`);
    if (node.outerSep)     extraArgs.push(`outer_sep="${node.outerSep}"`);
    if (node.nodeLineWidth) extraArgs.push(`line_width="${node.nodeLineWidth}"`);
    if (node.font)         extraArgs.push(`font="${node.font}"`);
    if (node.textWidth)    extraArgs.push(`text_width="${node.textWidth}"`);
    if (node.align)        extraArgs.push(`align="${node.align}"`);
    if (node.anchor)       extraArgs.push(`anchor="${node.anchor}"`);
    if (node.rotate   != null) extraArgs.push(`rotate=${node.rotate}`);
    if (node.xshift)       extraArgs.push(`xshift="${node.xshift}"`);
    if (node.yshift)       extraArgs.push(`yshift="${node.yshift}"`);
    if (node.scale    != null) extraArgs.push(`scale=${node.scale}`);
    if (node.roundedCorners) extraArgs.push(`rounded_corners="${node.roundedCorners}"`);
    if (node.doubleBorder)   extraArgs.push(`double="none"`);
    if (node.dashPattern)    extraArgs.push(`dash_pattern="${node.dashPattern}"`);
    if (node.pattern)        extraArgs.push(`pattern="${node.pattern}"`);
    if (node.shading)        extraArgs.push(`shading="${node.shading}"`);
    const extraStr = extraArgs.length > 0 ? ', ' + extraArgs.join(', ') : '';
    lines.push(`fig.add_node(x=${cx}, y=${cy}, label="${node.id}", content="${node.label}"${fillArg}${drawArg}${shapeArg}${textArg}, minimum_width="${mw}", minimum_height="${mh}"${extraStr})`);
  });

  if (state.edges.length > 0) {
    lines.push('');
    lines.push('# Add edges');
    state.edges.forEach(edge => {
      const arrowOpt = arrowToTikz(edge.arrow);
      const colorArg = edge.color ? `, color="${cssColorToLatex(edge.color)}"` : '';
      const lwArg = `, line_width="${edge.lineWidth}pt"`;
      const blArg = edge.bendLeft  !== 0 ? `, bend_left=${edge.bendLeft}` : '';
      const brArg = edge.bendRight !== 0 ? `, bend_right=${edge.bendRight}` : '';
      lines.push(`fig.draw(["${edge.sourceId}", "${edge.targetId}"]${colorArg}${lwArg}${blArg}${brArg}, options=["${arrowOpt}"])`);
    });
  }

  lines.push('');
  lines.push('tikz_code = fig.generate_tikz()');
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
  else tikzPre.textContent = '% Pyodide loading — TikZ will appear when ready';
}

async function runCodeGen() {
  if (!state.pyodideReady || state.nodes.length === 0) return;
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
    tikzPre.textContent = state.pyodide.globals.get('tikz_result') || '% (empty output)';
    state.standaloneLaTeX = state.pyodide.globals.get('standalone_result') || '';
    compileBtn.disabled = false;
  } catch (err) {
    tikzPre.textContent = `% Error: ${err}`;
    state.standaloneLaTeX = '';
    compileBtn.disabled = true;
  }
}

// ─── Tab System ────────────────────────────────────────────────────────────────

const tabState = {
  tabs: [
    { id: 'props', label: '⚙ Props' },
    { id: 'code',  label: '＜/＞ Code' },
    { id: 'pdf',   label: '⚡ PDF' },
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
      ${t.label}<span class="tab-hide-btn" data-hide="${t.id}">×</span>
    </button>
  `).join('') + (hidden.length ? '<button id="tab-restore-btn" title="Restore hidden tabs">+</button>' : '');

  // Show / hide panes
  tabState.tabs.forEach(t => {
    const pane = document.getElementById(`tab-pane-${t.id}`);
    if (!pane) return;
    const show = t.id === tabState.active;
    pane.style.display = show ? 'flex' : 'none';
    pane.classList.toggle('active-pane', show);
  });

  // Drag-to-reorder
  tabBar.querySelectorAll('.tab-btn[draggable]').forEach(btn => {
    const id = btn.dataset.tab;
    btn.addEventListener('dragstart', e => {
      e.dataTransfer.setData('text/plain', id);
      btn.classList.add('dragging');
    });
    btn.addEventListener('dragend', () => btn.classList.remove('dragging'));
    btn.addEventListener('dragover', e => { e.preventDefault(); btn.classList.add('drag-over'); });
    btn.addEventListener('dragleave', () => btn.classList.remove('drag-over'));
    btn.addEventListener('drop', e => {
      e.preventDefault();
      btn.classList.remove('drag-over');
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

// Single delegated click handler on the persistent tab bar element
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
    b.onclick = ev => {
      ev.stopPropagation();
      tabState.visible.add(tab.id);
      tabState.active = tab.id;
      renderTabs();
      menu.remove();
    };
    menu.appendChild(b);
  });
  document.getElementById('tab-bar').appendChild(menu);
  setTimeout(() => document.addEventListener('click', () => menu.remove(), { once: true }), 0);
}

renderTabs();

// ─── Pyodide Initialization ────────────────────────────────────────────────────

async function initPyodide() {
  pyodideStatus.textContent = 'Loading Pyodide…';
  try {
    state.pyodide = await loadPyodide();
    pyodideStatus.textContent = 'Installing tikzfigure…';
    await state.pyodide.loadPackage('micropip');
    await state.pyodide.runPythonAsync(`
import micropip
await micropip.install("tikzfigure")
`);
    state.pyodideReady = true;
    pyodideStatus.style.color = '#6ee7b7';
    pyodideStatus.textContent = '✓ Pyodide ready';
    setStatus('Pyodide ready. Add nodes and edges to generate TikZ code.');
    if (state.nodes.length > 0) runCodeGen();
  } catch (err) {
    pyodideStatus.style.color = '#f87171';
    pyodideStatus.textContent = `✗ Pyodide error: ${err.message}`;
  }
}

initPyodide();

// ─── Copy helpers ──────────────────────────────────────────────────────────────

function copyCode(type) {
  const text = type === 'python' ? pythonPre.textContent : tikzPre.textContent;
  navigator.clipboard.writeText(text).then(() => {
    setStatus(`Copied ${type === 'python' ? 'Python' : 'TikZ'} code to clipboard.`);
  }).catch(() => setStatus('Copy failed — use manual selection.'));
}

window.copyCode = copyCode;

document.getElementById('btn-compile-toolbar').addEventListener('click', () => {
  if (!compileBtn.disabled) compileBtn.click();
  else setStatus('No TikZ code ready yet — add nodes first.');
});

// ─── PDF Compilation via latex-on-http ─────────────────────────────────────────

const compileLogDetails = document.getElementById('compile-log-details');
const compileLog        = document.getElementById('compile-log');

// Configure PDF.js worker
if (typeof pdfjsLib !== 'undefined') {
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
}

function showLog(text, hasError) {
  if (!text) { compileLogDetails.style.display = 'none'; return; }
  const html = text.split('\n').map(line => {
    if (/^!/.test(line) || /error/i.test(line) && !/File:/.test(line))
      return `<span class="log-error">${escapeHtml(line)}</span>`;
    return escapeHtml(line);
  }).join('\n');
  compileLog.innerHTML = html;
  compileLog.className = hasError ? 'has-error' : '';
  compileLogDetails.style.display = '';
  compileLogDetails.open = hasError;
}

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

async function renderPdfToCanvas(arrayBuffer) {
  if (typeof pdfjsLib === 'undefined') return false;
  try {
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const page = await pdf.getPage(1);
    const containerWidth = pdfCanvas.parentElement?.clientWidth || 400;
    const viewport = page.getViewport({ scale: 1 });
    // Scale so the page fills the container width
    const scale = (containerWidth - 2) / viewport.width;
    const scaled = page.getViewport({ scale });
    pdfCanvas.width  = scaled.width;
    pdfCanvas.height = scaled.height;
    pdfCanvas.style.display = 'block';
    const ctx = pdfCanvas.getContext('2d');
    await page.render({ canvasContext: ctx, viewport: scaled }).promise;
    return true;
  } catch (err) {
    console.error('PDF.js render error:', err);
    return false;
  }
}

compileBtn.addEventListener('click', async () => {
  if (!state.standaloneLaTeX) {
    setStatus('No LaTeX to compile. Add nodes first.');
    return;
  }

  compileBtn.disabled = true;
  compileBtn.textContent = 'Compiling…';
  setStatus('Sending to latex.ytotech.com for compilation…');
  showLog('', false);

  const pdfDownload = document.getElementById('pdf-download');

  try {
    const resp = await fetch('https://latex.ytotech.com/builds/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        compiler: 'pdflatex',
        resources: [{ main: true, content: state.standaloneLaTeX }],
      }),
    });

    if (resp.status === 201) {
      const arrayBuffer = await resp.arrayBuffer();
      // Render to canvas via PDF.js (no browser PDF controls)
      await renderPdfToCanvas(arrayBuffer);
      // Also make the PDF available as a download
      if (state._prevPdfUrl) URL.revokeObjectURL(state._prevPdfUrl);
      const blob = new Blob([arrayBuffer], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      state._prevPdfUrl = url;
      pdfDownload.href = url;
      pdfDownload.style.display = 'inline-block';
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
    compileBtn.textContent = '⚡ Compile to PDF (latex-on-http)';
  }
});
