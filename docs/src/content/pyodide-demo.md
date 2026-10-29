---
title: Tikzfigure in the Browser (Pyodide Demo)
description: Try Tikzfigure interactively in your browser using Pyodide and WebAssembly.
---

# Tikzfigure in the Browser (Pyodide Demo)

This page lets you generate TikZ code using the
[tikzfigure](https://github.com/max-models/tikzfigure) Python library, running
entirely in your browser via [Pyodide](https://pyodide.org/).

- Write Python code using the TikzFigure API in the left box.
- Click **Generate** to see the resulting TikZ code on the right.
- No server or LaTeX installation required!

<div style="margin: 2em 0;">
  <iframe src="/pyodide-demo.html" width="100%" height="600" style="border: none; border-radius: 12px; box-shadow: 0 2px 16px rgba(0,0,0,0.07);"></iframe>
</div>

## How does it work?

- The code runs in your browser using Pyodide (Python compiled to WebAssembly).
- The [tikzfigure](https://pypi.org/project/tikzfigure/) package is installed
  dynamically from PyPI.
- No code or data is sent to any server.

---

**Tip:** You can copy the generated TikZ code and use it in your LaTeX
documents!
