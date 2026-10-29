---
title: Installation
---

## Requirements

- Python >= 3.8
- A working `pdflatex` installation (e.g. [TeX Live](https://tug.org/texlive/)
  or [MiKTeX](https://miktex.org/))

## Install from PyPI

```bash
pip install tikzfigure
```

## Install for development

```bash
git clone https://github.com/max-models/tikzfigure.git
cd tikzfigure
python -m venv env
source env/bin/activate
pip install -e ".[dev]"
```

## Optional extras

| Extra              | Contents                            |
| ------------------ | ----------------------------------- |
| `tikzfigure[vis]`  | `matplotlib`, `jupyterlab`          |
| `tikzfigure[docs]` | Documentation build dependencies    |
| `tikzfigure[test]` | `pytest`, `coverage`                |
| `tikzfigure[dev]`  | All of the above plus linting tools |

```bash
pip install "tikzfigure[vis]"
```

## Jupyter magic

To enable the `%%tikz` magic in Jupyter:

```python
%load_ext tikzfigure.ipython
```
