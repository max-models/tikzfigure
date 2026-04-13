# TikZ Editor Redesign — Design Specification

**Date:** 2026-04-13
**Feature:** Redesign the browser editor into a more standard online drawing workspace
**Scope:** `astro_docs/public/tikz-editor.html`, `astro_docs/public/tikz-editor.css`, `astro_docs/public/tikz-editor.js`

---

## Context

The current TikZ editor already has the core interaction model needed for drawing:
- a top toolbar with zoom, grid, snap, theme, compile, and export controls
- a left tool rail for select / node / edge modes and editing actions
- a large SVG canvas
- a right-side panel with closable, draggable tabs for properties, code, PDF, and layers

The main UX problem is the right-side tab system. It adds custom interaction overhead, consumes horizontal space, and makes the editor feel less like a standard design tool. The redesign should keep the existing editor engine and capabilities, but reshape the UI into a more familiar canvas-first layout.

The user wants the redesign to optimize for visual drawing first, remove the closable-tab concept entirely, and move more global actions into the top bar.

---

## Requirements

### Functional Requirements

1. **Replace the closable right-side tab UI**
   - Remove draggable, hideable, restorable tabs from the right side
   - Eliminate the tab-management state and related controls in JavaScript
   - Do not preserve the current "close tab / restore tab" interaction model in a new form

2. **Adopt a standard drawing-app workspace**
   - Keep the canvas as the primary visual focus
   - Keep a left drawing toolbar for creation and mode switching
   - Keep a stable right inspector for editing the current selection
   - Introduce a bottom drawer for output-oriented tasks

3. **Move global actions to the top bar**
   - Top bar should host global or document-level controls such as compile/export, zoom/view, grid/snap, theme, and quick edit actions like undo/redo
   - Controls should be grouped and visually clearer than the current compact strip

4. **Preserve existing editor capabilities**
   - Selection, dragging, multi-select, node creation, edge creation, duplication, deletion, layers, raw TikZ input, code generation, PDF compilation, and status messaging must continue to work
   - Existing keyboard shortcuts should remain supported unless there is a clear collision created by the redesign

5. **Provide stable output and preview surfaces**
   - Python code, TikZ code, raw TikZ input, PDF preview, and compile log must still be available
   - These surfaces should live in a bottom utility drawer rather than in right-side tabs

### Non-Functional Requirements

- The editor should feel more like a standard online drawing platform than a custom demo UI
- The redesign should reduce horizontal competition with the canvas
- The implementation should simplify UI state rather than re-creating tab complexity elsewhere
- Existing rendering and generation logic should be reused instead of rewritten

---

## Recommended Approach

Use a **canvas-first studio layout**:

- **Top bar:** global actions and document controls
- **Left rail:** tool modes and core editing tools
- **Center workspace:** canvas
- **Right inspector:** always-visible contextual properties and layers
- **Bottom drawer:** code, raw TikZ, PDF preview, and compile log

This is the best fit because it mirrors common drawing and diagramming tools, gives the canvas more usable width, and removes the bespoke tab UX without sacrificing existing features.

Two alternatives were considered and rejected:

1. **Single inspector workspace** — stack everything in the right panel. Simpler, but code/PDF still compete directly with drawing width.
2. **Overlay utilities** — push outputs into modal or temporary overlays. Cleaner at rest, but weaker for edit-and-compare workflows.

---

## Design

### 1. Layout Architecture

The page should be reorganized into three major vertical bands:

1. **Top application bar**
2. **Main workspace**
3. **Status bar**

The main workspace should then be split into:

1. **Left tool rail**
2. **Canvas column**
3. **Right inspector**

The **canvas column** should contain:

1. the canvas itself
2. a resizable bottom drawer docked beneath it

This changes the information flow from "canvas + tabbed sidecar" to "canvas + inspector + utility drawer", which is a more standard mental model for drawing tools.

### 2. Top Bar Responsibilities

The top bar should become the home for global controls:

- brand/title
- primary document actions
  - compile to PDF
  - export `.tex`
- history and quick editing actions
  - undo
  - redo
  - duplicate
  - delete
- view controls
  - zoom out
  - zoom level
  - zoom in
  - fit/reset
- canvas toggles
  - grid
  - snap
- theme toggle
- Pyodide readiness indicator

These should be grouped visually so the bar reads as a professional application header rather than a row of unrelated buttons.

### 3. Left Tool Rail

The left rail should stay focused and narrow. It should contain only the actions that define or directly support the drawing mode:

- select / move
- add node
- draw path

If undo/redo and destructive actions are moved into the top bar, the left rail can become cleaner and closer to the conventions of other drawing apps.

### 4. Right Inspector

The right panel should stop behaving like a tab host and become a stable inspector with stacked sections.

Recommended section order:

1. **Selection / Properties**
   - show the current empty state when nothing is selected
   - render the existing node/path property controls when there is a selection
2. **Layers**
   - show the layer list and layer actions beneath the selection editor

This makes the right side a predictable editing surface rather than a place where unrelated tasks compete for the same slot.

### 5. Bottom Drawer

The bottom drawer should become the utility workspace for non-drawing tasks.

Recommended sections inside the drawer:

1. **Code**
   - Python output
   - TikZ output
2. **Raw TikZ**
   - verbatim input area
3. **Preview**
   - compile button
   - PDF preview
   - PDF download
   - compile log

The drawer may switch between sections, but this should be a lightweight docked control rather than a hideable right-side tab strip. It should be resizable and optionally collapsible, but not closable in the old sense.

### 6. Empty States and Guidance

The redesign should improve the idle experience:

- Right inspector:
  - explain that selecting a node or edge reveals editable properties
- Bottom drawer:
  - explain when code is not yet generated
  - explain when PDF preview is unavailable because nothing has been compiled
- Status bar:
  - continue surfacing lightweight action feedback and shortcut hints

These empty states should feel intentional and instructional, not like missing content.

### 7. Visual Direction

The CSS refresh should support the new workspace structure with:

- stronger panel hierarchy
- clearer grouping in the top bar
- more deliberate spacing and section headers
- less dense right-panel chrome
- a more polished docked-drawer appearance

The theme can stay close to the current dark/light palette, but the layout should feel more mature and less experimental.

---

## JavaScript and Markup Changes

### HTML Changes

Update the document structure to:

- remove `#tab-bar` and all `tab-pane-*` wrappers
- convert `#right-panel` into a persistent inspector shell
- introduce a bottom drawer container in the canvas column
- keep existing content anchors for properties, layers, code, raw TikZ, PDF viewer, and compile log where practical so existing JS renderers can be reused

### JavaScript Changes

Remove the tab system entirely:

- delete `tabState`
- delete `switchTab()`, `renderTabs()`, and restore-menu logic
- remove tab-bar event handlers and drag/drop behavior

Replace it with simpler UI state:

- bottom drawer active section
- bottom drawer collapsed / expanded state
- bottom drawer height or resize state if resizing is implemented in JS

Existing business logic should remain intact:

- selection rendering still writes into the properties container
- layer rendering still writes into the layers container
- code generation still writes into the code containers
- compile/export logic still targets the same functional controls

The goal is to simplify layout coordination while preserving editor functionality.

### CSS Changes

The stylesheet should be reorganized around the new workspace primitives:

- app bar
- left rail
- canvas column
- right inspector
- bottom drawer

Tab-specific styles should be removed. New styles should support:

- grouped top-bar controls
- inspector section cards or panels
- drawer header and section switcher
- better responsive behavior on narrower screens

---

## Error Handling and Behavior Safety

- Do not silently drop existing functionality during the redesign
- If a control moves, preserve its behavior and keyboard shortcut
- If the bottom drawer section is unavailable because content is not ready yet, show a clear empty state instead of a broken control
- Keep the current compile readiness checks and status messages
- Preserve the existing canvas, generation, and compilation flows unless a layout change requires explicit event rewiring

---

## Testing and Verification Expectations

The implementation should verify:

1. the new layout loads without missing-element JS errors
2. selection still updates the inspector correctly
3. layers still render and remain editable
4. Python and TikZ output still appear in the drawer
5. raw TikZ input still updates generated output
6. compile/export actions still work from their new positions
7. the removed tab system leaves no dead event handlers or broken references

The emphasis is on preserving capabilities while simplifying the UI model.

---

## Implementation Notes

- Prefer structural refactoring over incremental patching of the old tab layout
- Reuse existing DOM IDs and renderer entry points when that reduces risk
- Avoid introducing a new custom workspace manager that recreates the complexity being removed
- Keep the redesign limited to the editor shell, styles, and UI wiring in the specified files

---

## Summary

This redesign should turn the TikZ editor into a more standard online drawing workspace by removing the closable right-side tabs, moving global actions into a stronger top bar, keeping a stable right-side inspector, and relocating code/PDF/output tasks into a bottom drawer beneath the canvas. The implementation should simplify the UI state machine while preserving the editor's existing capabilities.
