# TikZ Editor Redesign — Design Specification

**Date:** 2026-04-13
**Feature:** Redesign the browser editor into a Photoshop-style drawing workspace
**Scope:** `astro_docs/public/tikz-editor.html`, `astro_docs/public/tikz-editor.css`, `astro_docs/public/tikz-editor.js`

---

## Context

The current TikZ editor has the core interaction model needed for drawing but its right-side panel uses closable, draggable, restorable tabs. This makes the editor feel like a custom demo UI rather than a standard drawing tool. The user has requested a redesign that:

- removes the closable tab concept entirely
- restructures panels to feel like Photoshop (stacked, always-visible, collapsible sections)
- moves global actions into the top bar
- puts code and PDF output in a bottom drawer beneath the canvas
- adds a pre-flight layer selection dialog when compiling to PDF
- adds a Layer assignment dropdown in the Properties section

---

## Requirements

### Functional Requirements

1. **Remove closable tab UI** — No tabs, no close/restore tab controls, no drag-to-reorder tabs.

2. **Right inspector: stacked collapsible cards** — The right panel is a single scrollable column with two collapsible section cards (Photoshop-style):
   - **Properties** card — on top
   - **Layers** card — below Properties

3. **Layer assignment in Properties** — When a node or edge is selected, the Properties card shows a "Layer" dropdown at the top of the property fields. Changing the dropdown moves the object to that layer.

4. **Layers card shows object membership** — Each layer row in the Layers card shows a count badge (how many objects belong to that layer), plus the existing eye/lock toggle buttons. Add and Delete layer buttons appear at the bottom of the card.

5. **Compile dialog for layer selection** — Clicking Compile PDF opens a modal dialog instead of immediately compiling. The dialog title is "Select layers to include in PDF." The body is a checkbox list of all current layers, all checked by default. Buttons: Cancel and Compile. The Compile button passes only the checked layers to the compile function.

6. **Bottom drawer** — A docked, resizable drawer beneath the canvas. Three sections selectable via pill-style tabs at the drawer's top edge:
   - **Code** — Python output and TikZ output (existing collapsible folds)
   - **Raw TikZ** — verbatim textarea
   - **Preview** — Compile PDF button (triggers the dialog), PDF viewer iframe, PDF download link, compile log

7. **Top bar** — Houses all global/document-level controls. Left to right:
   - Brand label
   - Separator
   - Compile PDF button (triggers dialog)
   - Export TEX button
   - Separator
   - Undo, Redo
   - Separator
   - Zoom−, zoom level display, Zoom+, Fit
   - Separator
   - Grid toggle, Snap toggle
   - Separator
   - Theme toggle
   - Pyodide status indicator (right-aligned)

8. **Left rail** — Contains only the three drawing-mode buttons: Select, Add Node, Draw Path. Undo/Redo/Duplicate/Delete are removed from the rail (moved to top bar or accessible via keyboard/context menu).

9. **Preserve existing capabilities** — Selection, dragging, multi-select, node/edge creation, duplication, deletion, raw TikZ input, code generation, PDF compilation, keyboard shortcuts, and status bar messaging must all continue to work.

### Non-Functional Requirements

- The editor should feel like a professional drawing tool, not a demo
- The right panel should feel structurally similar to Photoshop's docked panel system: dark chrome, clear section headers with a collapse triangle, no tab strip
- The redesign should reduce UI state complexity (no tab state machine)
- Existing rendering and generation logic should be reused, not rewritten

---

## Layout Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  TOP BAR (brand · doc actions · edit · view · toggles)      │
├────┬──────────────────────────────────┬─────────────────────┤
│    │                                  │  RIGHT INSPECTOR    │
│    │           CANVAS                 │  ┌───────────────┐  │
│ L  │                                  │  │ ▾ Properties  │  │
│ E  │                                  │  │   (fields)    │  │
│ F  ├──────────────────────────────────┤  └───────────────┘  │
│ T  │  BOTTOM DRAWER                   │  ┌───────────────┐  │
│    │  [Code | Raw TikZ | Preview]     │  │ ▾ Layers      │  │
│    │                                  │  │   (list)      │  │
│    │                                  │  └───────────────┘  │
├────┴──────────────────────────────────┴─────────────────────┤
│  STATUS BAR                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Design

### Top Bar

Arranged left-to-right with visual separator elements between groups:

| Group | Controls |
|---|---|
| Brand | "TikZ Editor" label |
| Document | Compile PDF, Export TEX |
| Edit | Undo, Redo |
| View | Zoom−, zoom%, Zoom+, Fit |
| Canvas | Grid toggle, Snap toggle |
| System | Theme toggle, Pyodide status |

### Left Rail

Three buttons only:
- Select / Move (V)
- Add Node (N)
- Draw Path (E)

Duplicate, Delete, and Clear are removed from the left rail. They remain accessible via keyboard shortcuts (Ctrl+D, Del, etc.) and the right-click context menu. They are not added to the top bar.

### Right Inspector

A fixed-width (~280px) scrollable column. No tab bar. Two stacked section cards:

**Properties card:**
- Header: "Properties" with a collapse triangle (▾/▸). Starts expanded.
- When nothing is selected: muted hint text "Select a node or edge to edit properties."
- When an object is selected:
  - Layer dropdown at the top: label "Layer", value = current layer name, options = all layer names
  - Existing property fields (position, fill, stroke, shape, label, etc.) below the dropdown
  - For multi-select: existing batch controls

**Layers card:**
- Header: "Layers" with a collapse triangle. Starts expanded.
- Each layer row:
  - Eye toggle button (visibility)
  - Lock toggle button
  - Layer name (editable on double-click)
  - Object count badge (e.g., "3 objects")
- Active layer highlighted
- Bottom of card: "Add Layer" and "Delete Layer" buttons

### Bottom Drawer

Docked beneath the canvas. Resizable by dragging its top edge. Initial height: ~180px.

Section switcher: three pill-style tabs at the top of the drawer — **Code**, **Raw TikZ**, **Preview**.

- **Code section:** Python output fold + TikZ output fold (existing collapsible `<details>` blocks with Copy buttons)
- **Raw TikZ section:** verbatim textarea input
- **Preview section:** Compile PDF button (triggers dialog), PDF viewer iframe, PDF download link, compile log details

The drawer is not closable.

### Compile Dialog

A modal overlay, triggered by any Compile PDF button (top bar or Preview section).

- **Title:** "Select layers to include in PDF"
- **Body:** Checkbox list. One row per layer. All checked by default. Each row: `[✓] Layer name`.
- **Footer buttons:** Cancel (dismisses dialog, no compile) | Compile (passes checked layers to compile function)
- The compile function filters the TikZ output to only include `\pgfonlayer{name}` blocks for the checked layers before sending to the compile service.

---

## JavaScript Changes

### Remove
- `tabState` object
- `switchTab()`, `renderTabs()`, restore-menu logic
- Tab drag/drop event handlers
- All tab-hide and tab-restore button creation

### Add
- `drawerState`: `{ section: 'code'|'rawtikz'|'preview' }`
- `drawerSectionSwitch(section)`: updates active pill and shows correct content
- Drawer resize handler (drag the drawer's top edge)
- `openCompileDialog()`: creates and shows the modal, populates with current layer names
- `executeCompile(checkedLayers)`: filters TikZ output per selected layers, then calls existing compile logic
- Layer assignment: `setObjectLayer(id, layerName)` — updates the object's layer, re-renders layer counts, regenerates code

### Update
- `renderProperties()`: add Layer dropdown at top of selection form; wire `change` event to `setObjectLayer`
- `renderLayers()`: add object count badges per layer row
- Existing compile/export entry points: route through `openCompileDialog()` instead of directly compiling

### Preserve
- All selection, drag, multi-select, canvas interaction logic
- Code generation (`generateCode()`, `generate_tikz()`)
- Export TEX logic
- Keyboard shortcuts
- Context menu
- Status bar updates

---

## CSS Changes

Remove tab-specific styles. Add:

- **`.inspector-card`** — card wrapper for each right-panel section
- **`.inspector-card-header`** — Photoshop-style section header: dark background, uppercase label, collapse triangle, full-width clickable
- **`.inspector-card-body`** — content area, hidden when collapsed
- **`.drawer`** — bottom drawer container
- **`.drawer-tabs`** — pill tab switcher at drawer top
- **`.drawer-section`** — each section's content container
- **`.compile-dialog-overlay`** — full-screen modal backdrop
- **`.compile-dialog`** — dialog card
- **`.layer-count-badge`** — small count indicator on layer rows

Retain the existing dark/light color token system (`--bg-*`, `--text-*`, `--accent`, etc.).

---

## Error Handling

- If no layers exist when Compile dialog opens, show a single unchecked row "Default" as a fallback.
- If all layers are unchecked in the dialog, disable the Compile button with a tooltip: "Select at least one layer."
- If drawer resize would reduce canvas height below a usable minimum (~200px), clamp it.
- Preserve existing compile error display (log + error highlighting) in the Preview section.

---

## Testing Checklist

1. New layout loads without JS errors
2. Properties card renders correctly for: nothing selected, node selected, edge selected, multi-select
3. Layer dropdown in Properties correctly reassigns object to new layer
4. Layers card shows correct object counts; counts update when objects move layers
5. Compile dialog opens when Compile PDF is clicked; unchecking layers filters TikZ output correctly
6. Bottom drawer section switching works; resize handle works; content persists across section switches
7. Undo/Redo in top bar operates correctly
8. All keyboard shortcuts still work
9. No dead event handlers for removed tab system
10. Light/dark theme toggle applies correctly to all new components

---

## Summary

The redesign restructures the TikZ editor as a Photoshop-style drawing workspace: a global top bar, a narrow left tool rail, a large canvas, a persistent right inspector with stacked collapsible Property and Layer cards, and a bottom utility drawer for code and PDF output. The closable-tab UX is removed entirely. PDF compilation gains a pre-flight layer selection dialog. Objects can be assigned to layers via a dropdown in the Properties card.
