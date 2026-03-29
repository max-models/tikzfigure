---
title: Installation
---

## Requirements

- Python >= 3.8
- A working `pdflatex` installation (e.g. [TeX Live](https://tug.org/texlive/) or [MiKTeX](https://miktex.org/))

## Install from PyPI

```bash
pip install tikzpics
```

## Install for development

```bash
git clone https://github.com/max-models/tikzpics.git
cd tikzpics
python -m venv env
source env/bin/activate
pip install -e ".[dev]"
```

## Optional extras

| Extra | Contents |
|-------|----------|
| `tikzpics[vis]` | `matplotlib`, `jupyterlab` |
| `tikzpics[docs]` | Documentation build dependencies |
| `tikzpics[test]` | `pytest`, `coverage` |
| `tikzpics[dev]` | All of the above plus linting tools |

```bash
pip install "tikzpics[vis]"
```

## Jupyter magic

To enable the `%%tikz` magic in Jupyter:

```python
%load_ext tikzpics.ipython
```
