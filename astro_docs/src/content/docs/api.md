---
title: API Reference
---

## TikzFigure

The main entry point. Holds all nodes, paths, layers, and variables. Use this to
build and render figures.

```python
from tikzfigure import TikzFigure

fig = TikzFigure(
    ndim=2,  # 2 or 3 dimensions
    label=None,  # figure label (str)
    grid=False,  # show background grid
    figsize=(10, 6),  # figure size in cm (width, height)
    caption=None,  # LaTeX figure caption
    description=None,  # accessibility description
    show_axes=False,  # draw coordinate axes
    extra_packages=None,  # list of extra LaTeX packages
    document_setup=None,  # extra LaTeX document preamble
    figure_setup=None,  # extra TikZ picture options
    tikz_code=None,  # parse existing TikZ code
)
```

### Methods

#### `add_node(node) → Node`

Add a `Node` to the figure. Returns the node (for use in subsequent `draw()`
calls).

#### `draw(*nodes_or_coords, **options)`

Draw a path between nodes or coordinates.

Common options: `arrow` (`"->"`, `"<-"`, `"<->"`, etc.), `color`, `line_width`,
`dashed`, `dotted`, `bend_left`, `bend_right`.

#### `filldraw(*nodes_or_coords, **options)`

Draw and fill a closed path.

#### `add_loop(loop)`

Add a `Loop` object to the figure.

#### `add_raw(tikz_str, layer=0)`

Insert a raw TikZ string directly.

#### `add_variable(name, value)`

Define a TikZ `\def` variable.

#### `colorlet(name, color)`

Define a named color via `\colorlet`.

#### `generate_tikz() → str`

Return the full TikZ/LaTeX source string.

#### `compile_pdf(output_path)`

Compile the figure to a PDF file using `pdflatex`.

#### `savefig(path, dpi=150)`

Save the figure as PNG or JPG (compiles to PDF first, then converts via
`pymupdf`).

#### `show(dpi=150)`

Display the figure inline (Jupyter) or open it (terminal).

#### `plot3d(x, y, z, **options)`

Add a 3D surface or line plot via `pgfplots`.

#### `from_tikz_code(tikz_code) → TikzFigure` *(class method)*

Parse an existing TikZ code string and return a `TikzFigure`.

---

## Node

Represents a TikZ node with a position, optional content, and styling options.

```python
from tikzfigure import Node

node = Node(
    x=0,
    y=0,  # coordinates (float or int)
    z=None,  # z coordinate for 3D
    label="",  # TikZ node name (\node[...] (label) ...)
    content="",  # text content inside the node
    layer=0,  # layer (z-order)
    # Shape
    shape=None,  # e.g. "circle", "rectangle", "ellipse"
    # Color
    color=None,  # shorthand for draw + text color
    fill=None,  # fill color
    draw=None,  # border color
    text=None,  # text color
    # Opacity
    opacity=None,
    fill_opacity=None,
    draw_opacity=None,
    text_opacity=None,
    # Size
    minimum_width=None,  # e.g. "2cm"
    minimum_height=None,
    minimum_size=None,
    # Separation
    inner_sep=None,
    outer_sep=None,
    # Line
    line_width=None,  # e.g. "1pt"
    # Text
    font=None,  # e.g. r"\small"
    text_width=None,
    align=None,  # "left", "center", "right"
    # Anchor
    anchor=None,  # e.g. "north", "south east"
    # Relative positioning
    above=None,
    below=None,
    left=None,
    right=None,
    above_of=None,
    below_of=None,
    left_of=None,
    right_of=None,
    # Raw options
    options=None,  # list of raw TikZ option strings
)
```

### `to_tikz() → str`

Return the TikZ `\node` string for this node.
