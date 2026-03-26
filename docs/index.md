# tikzpics

**tikzpics** is a Python library that provides a programmatic interface to generate readable [TikZ](https://tikz.dev/) (LaTeX) figures. Build figures through a clean Python API, then export to LaTeX, PDF, or PNG/JPG.

## Quick start

```python
from tikzpics import TikzFigure, Node

fig = TikzFigure()
a = fig.add_node(Node(0, 0, content="A"))
b = fig.add_node(Node(2, 0, content="B"))
fig.draw(a, b, arrow="->")
fig.show()
```

## Features

- Build TikZ figures via a Python API — no LaTeX knowledge required
- Export to LaTeX source, PDF, PNG, or JPG
- Layer support for z-ordering
- 3D figure support via `pgfplots`
- Jupyter/IPython magic commands (`%%tikz`)
- Readable, inspectable LaTeX output

## Links

- [Source code](https://github.com/max-models/tikzpics)
- [Installation](installation.md)
- [Tutorials](tutorials/tutorial_01_getting_started.ipynb)
- [API Reference](api.md)
