---
title: Interactive TikZ Editor
description: Build TikZ figures visually in your browser — add nodes, edges, and export to LaTeX or PDF.
---

# Interactive TikZ Editor

Build TikZ figures visually in your browser. Add nodes, connect them with edges, edit properties, then export the generated TikZ code or compile to PDF — all without installing anything.

<div style="margin: 2em 0;">
  <a href="/tikzfigure/tikz-editor.html" target="_blank" rel="noopener noreferrer" style="display:inline-block; padding: 0.6em 1.4em; background: #6e3ff3; color: white; border-radius: 8px; text-decoration: none; font-weight: bold;">Open Editor ↗</a>
</div>

## How it works

- **Add nodes** by clicking the canvas. Set label, fill color, shape, and size in the properties panel.
- **Add edges** by switching to edge mode, then clicking a source node and a target node.
- **Export** generates tikzfigure Python code and the resulting TikZ LaTeX code (via Pyodide running in-browser).
- **Compile to PDF** sends the TikZ code to [latex-on-http](https://github.com/YtoTech/latex-on-http) and displays the result.

> **Note:** PDF compilation requires an internet connection to `latex.ytotech.com`.
