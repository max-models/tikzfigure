---
title: API Reference
description: Generated reference for the current tikzfigure Python API.
editUrl: false
---

> This page is generated from the current Python docstrings by
> `astro_docs/scripts/generate_api_docs.py`. Edit the docstrings in
> `src/tikzfigure/`, not this file.

The sections below follow the current public API surface exported from
`tikzfigure`, plus the underlying modules that define the main public
classes.

## Figure API

```python
from tikzfigure import TikzFigure
```

<a id="tikzfigure.core.figure.TikzFigure"></a>

### TikzFigure

```python
class TikzFigure(FigureParsingMixin, FigurePathMixin, FigureLayoutMixin,
                 FigureRenderMixin, FigureExportMixin)
```

Main entry point for building TikZ figures programmatically.

Holds layers, variables, colors, and all TikZ primitives.  Call
`generate_tikz` to obtain the LaTeX source, `compile_pdf`
to compile it, and `savefig` / `show` to export or display
the result.

Compilation: `compile_pdf`, `savefig`, and `show`
compile with a local pdflatex. If pdflatex is missing or the document
fails to build, they raise a `RuntimeError` describing what went
wrong.

Without a local LaTeX installation, tikzfigure can compile through the
latex-on-http web API instead. That uploads the LaTeX source of the figure
to a third-party server, so it is opt-in and never happens on its own:
pass ``use_web_compilation=True`` to those methods, or set
``TIKZFIGURE_USE_WEB_COMPILATION=1`` to enable it process-wide. Either way
a `UserWarning` is emitted when a figure is uploaded. See
https://github.com/max-models/tikzfigure for more details.

**Attributes**:

- `layers` - The `LayerCollection` holding all drawing layers.
- `variables` - List of `Variable` objects defined in this figure.
- `colors` - List of ``(name, Color)`` pairs defined with
  `colorlet`.
- `ndim` - Number of spatial dimensions (``2`` or ``3``).
- `document_setup` - Custom LaTeX preamble inserted before
  ``\begin{document}``.
- `extra_packages` - Extra LaTeX packages to include in the preamble.

<a id="tikzfigure.core.figure.TikzFigure.__init__"></a>

##### TikzFigure.\_\_init\_\_

```python
def __init__(ndim: int = 2,
             label: str | None = None,
             grid: bool = False,
             tikz_code: str | None = None,
             extra_packages: list | None = None,
             document_setup: str | None = None,
             figure_setup: str | None = None,
             figsize: tuple[float, float] = (10, 6),
             description: str | None = None,
             show_axes: bool = False,
             rows: int | None = None,
             cols: int | None = None) -> None
```

Initialize a TikzFigure.

**Arguments**:

- `ndim` - Number of spatial dimensions. Use ``2`` for standard
  figures and ``3`` for pgfplots 3-D axis figures.
  Defaults to ``2``.
- `label` - LaTeX ``\label`` for the surrounding ``figure``
  environment. When set, the figure is wrapped in a
  ``figure`` environment.
- `grid` - If ``True``, draw a background grid. Defaults to
  ``False``.
- `tikz_code` - Existing TikZ code to parse and import. When
  provided, nodes and paths are reconstructed from the
  source. Defaults to ``None``.
- `extra_packages` - Additional LaTeX packages to include in the
  standalone preamble (e.g. ``["amsmath"]``).
- `document_setup` - Raw LaTeX to insert in the preamble after
  the standard packages.
- `figure_setup` - TikZ options string placed inside the opening
  ``\begin{tikzpicture}[…]`` bracket.
- `figsize` - ``(width, height)`` in centimetres used as a hint
  for display backends. Defaults to ``(10, 6)``.
- `description` - Long description stored for documentation
  purposes (not emitted in TikZ output).
- `show_axes` - For 3-D figures, if ``True`` render the pgfplots
  axis lines and labels. Defaults to ``False``.
- `rows` - Number of rows in subfigure grid. Must be specified with cols.
  Defaults to None (no grid).
- `cols` - Number of columns in subfigure grid. Must be specified with rows.
  Defaults to None (no grid).

<a id="tikzfigure.core.figure.TikzFigure.to_python"></a>

##### TikzFigure.to\_python

```python
def to_python(name: str = "fig",
              header: bool = True,
              verify: bool = True) -> str
```

Return Python code that rebuilds this figure.

Useful together with `from_tikz_code` to turn existing TikZ
source into a tikzfigure script.

**Examples**:

  >>> fig = TikzFigure()
  >>> _ = fig.add_node(0, 0, label="a", content="A")
  >>> print(fig.to_python(header=False), end="")
  fig = TikzFigure()
  fig.add_node(0, 0, label='a', content='A')


**Arguments**:

- `name` - Variable name for the figure in the generated code.
- `header` - Include the ``import`` lines.
- `verify` - Run the generated code and check it produces the same
  TikZ output as this figure.


**Returns**:

  Python source code.


**Raises**:

- `CodegenError` - If the figure uses features that cannot be
  expressed as Python calls yet (pgfplots axes or subfigures).

<a id="tikzfigure.core.figure.TikzFigure.to_dict"></a>

##### TikzFigure.to\_dict

```python
def to_dict() -> dict[str, Any]
```

Serialize this figure to a plain dictionary.

**Returns**:

  A dictionary capturing all figure settings, layers, variables,
  and colors, suitable for round-tripping via `from_dict`.

<a id="tikzfigure.core.figure.TikzFigure.from_dict"></a>

##### TikzFigure.from\_dict

```python
@classmethod
def from_dict(cls, d: dict[str, Any]) -> "TikzFigure"
```

Reconstruct a TikzFigure from a dictionary.

**Arguments**:

- `d` - Dictionary as produced by `to_dict`.


**Returns**:

  A fully restored `TikzFigure` instance.

<a id="tikzfigure.core.figure.TikzFigure.copy"></a>

##### TikzFigure.copy

```python
def copy(**overrides: Any) -> "TikzFigure"
```

Return a deep copy of this figure with optional figure-level overrides.

<a id="tikzfigure.core.figure.TikzFigure.configure_spy_scope"></a>

##### TikzFigure.configure\_spy\_scope

```python
def configure_spy_scope(*,
                        mode: SpyScopeMode = "scope",
                        options: OptionInput | None = None,
                        magnification: float | None = None,
                        lens: OptionInput | str | None = None,
                        lens_kwargs: dict[str, Any] | None = None,
                        size: str | object | None = None,
                        width: str | object | None = None,
                        height: str | object | None = None,
                        connect_spies: bool = False,
                        every_spy_in_node_options: OptionInput | None = None,
                        every_spy_in_node_style: dict[str, Any] | None = None,
                        every_spy_on_node_options: OptionInput | None = None,
                        every_spy_on_node_style: dict[str, Any] | None = None,
                        spy_connection_path: str | None = None,
                        **kwargs: Any) -> None
```

Append figure-wide defaults for subsequent spy commands.

This updates ``figure_setup`` with a top-level spy scope configuration,
which is useful when several ``fig.spy(...)`` calls should share the
same magnification, lens, node styling, or connection-path settings.

<a id="tikzfigure.core.figure.TikzFigure.add_spy"></a>

##### TikzFigure.add\_spy

```python
def add_spy(on: Any,
            *,
            layer: int = 0,
            comment: str | None = None,
            verbose: bool = False,
            options: OptionInput | None = None,
            magnification: float | None = None,
            lens: OptionInput | str | None = None,
            lens_kwargs: dict[str, Any] | None = None,
            size: str | object | None = None,
            width: str | object | None = None,
            height: str | object | None = None,
            connect_spies: bool = False,
            at: Any = None,
            node_label: str | None = None,
            node_options: OptionInput | None = None,
            node_style: dict[str, Any] | None = None,
            **kwargs: Any) -> Spy
```

Add a top-level ``\spy`` command to the figure.

If the figure does not yet have any spy-scope configuration, this
method enables a bare ``spy scope`` automatically so the generated
command works without extra setup.

<a id="tikzfigure.core.figure.TikzFigure.add_spy_scope"></a>

##### TikzFigure.add\_spy\_scope

```python
def add_spy_scope(layer: int = 0,
                  comment: str | None = None,
                  verbose: bool = False,
                  mode: SpyScopeMode = "scope",
                  options: OptionInput | None = None,
                  magnification: float | None = None,
                  lens: OptionInput | str | None = None,
                  lens_kwargs: dict[str, Any] | None = None,
                  size: str | object | None = None,
                  width: str | object | None = None,
                  height: str | object | None = None,
                  connect_spies: bool = False,
                  every_spy_in_node_options: OptionInput | None = None,
                  every_spy_in_node_style: dict[str, Any] | None = None,
                  every_spy_on_node_options: OptionInput | None = None,
                  every_spy_on_node_style: dict[str, Any] | None = None,
                  spy_connection_path: str | None = None,
                  **kwargs: Any) -> Scope
```

Create a nested scope with local spy defaults.

Use this when spy behavior should apply only to a region of the figure,
or when you want nested spy configurations such as an outer
``outlines`` scope with an inner ``overlays`` scope.

<a id="tikzfigure.core.figure.TikzFigure.add_copy"></a>

##### TikzFigure.add\_copy

```python
def add_copy(node: Node, verbose: bool = False, **overrides: Any) -> Node
```

Copy a node into this figure, applying optional constructor-style overrides.

If the source node has an explicit label and no ``label=...`` override is
provided, the copied node keeps that label and a warning is logged. Nodes
whose label was auto-generated by a figure are treated as unlabeled here
and receive a fresh ``node<N>`` label from this figure.

<a id="tikzfigure.core.figure.TikzFigure.add"></a>

##### TikzFigure.add

```python
def add(items: Any, layer: int = 0, verbose: bool = False) -> None
```

Add one or more pre-built items to the figure.

**Arguments**:

- `items` - A single TikZ object (`Node`, `TikzPath`,
  `tikzfigure.core.circle.Circle`, ...) or a
  list/tuple of them.
- `layer` - Target layer index. Defaults to ``0``.
- `verbose` - If ``True``, print a debug message for each insertion.

<a id="tikzfigure.core.figure.TikzFigure.colorlet"></a>

##### TikzFigure.colorlet

```python
def colorlet(name: str, color_spec: ColorInput, layer: int = 0) -> Color
```

Define a named color with ``\colorlet``.

**Arguments**:

- `name` - The name to assign to the color in LaTeX.
- `color_spec` - A TikZ color specification (e.g. ``"blue!20"``).
- `layer` - Layer index (currently unused). Defaults to ``0``.


**Returns**:

  The `Color` object that was registered.

<a id="tikzfigure.core.figure.TikzFigure.add_package"></a>

##### TikzFigure.add\_package

```python
def add_package(package: str) -> None
```

Add a LaTeX package to the standalone preamble.

**Examples**:

  >>> fig = TikzFigure()
  >>> fig.add_package("amsmath")

<a id="tikzfigure.core.figure.TikzFigure.add_style"></a>

##### TikzFigure.add\_style

```python
def add_style(name: str,
              options: OptionInput | None = None,
              **kwargs: Any) -> TikzStyle
```

Define or update a named TikZ style at figure scope.

**Examples**:

  >>> fig = TikzFigure()
  >>> axes = fig.add_style("axes")
  >>> fig.add_style("important line", options=["very thick"])
  >>> fig.add_style("information text", fill="red!10", inner_sep="1ex")
  >>> fig.draw([(0, 0), (1, 0)], options=[axes])

<a id="tikzfigure.core.figure.TikzFigure.usetikzlibrary"></a>

##### TikzFigure.usetikzlibrary

```python
def usetikzlibrary(
        *libraries: "str | TikzLibrary | type[TikzLibrary]") -> None
```

Register TikZ libraries for standalone output and compilation.

Accepts plain library name strings, or a `TikzLibrary`
subclass/instance for libraries with dedicated Python support (e.g.
`tikzfigure.core.matrix.MatrixLibrary`,
`tikzfigure.core.spy.SpyLibrary`).

**Examples**:

  >>> fig = TikzFigure()
  >>> fig.usetikzlibrary("calc", "intersections")
  >>> fig.usetikzlibrary("positioning,quotes")

<a id="tikzfigure.core.figure.TikzFigure.add_node"></a>

##### TikzFigure.add\_node

```python
def add_node(x: (float
                 | str
                 | tuple[float | int | str, float | int | str]
                 | tuple[float | int | str, float | int | str,
                         float | int | str]
                 | Node
                 | TikzCoordinate
                 | None) = None,
             y: float | str | None = None,
             z: float | str | None = None,
             label: str | None = None,
             content: str = "",
             layer: int = 0,
             comment: str | None = None,
             options: OptionInput | None = None,
             verbose: bool = False,
             shape: _Shape = None,
             color: ColorInput | None = None,
             fill: ColorInput | None = None,
             draw: ColorInput | None = None,
             text: ColorInput | None = None,
             opacity: float | None = None,
             fill_opacity: float | None = None,
             draw_opacity: float | None = None,
             text_opacity: float | None = None,
             minimum_width: str | TikzDimension | None = None,
             minimum_height: str | TikzDimension | None = None,
             minimum_size: str | TikzDimension | None = None,
             inner_sep: str | TikzDimension | None = None,
             inner_xsep: str | TikzDimension | None = None,
             inner_ysep: str | TikzDimension | None = None,
             outer_sep: str | TikzDimension | None = None,
             outer_xsep: str | TikzDimension | None = None,
             outer_ysep: str | TikzDimension | None = None,
             line_width: str | TikzDimension | None = None,
             font: str | None = None,
             text_width: str | TikzDimension | None = None,
             text_height: str | TikzDimension | None = None,
             text_depth: str | TikzDimension | None = None,
             align: _Align = None,
             anchor: _Anchor = None,
             above: str | None = None,
             below: str | None = None,
             left: str | None = None,
             right: str | None = None,
             above_left: str | None = None,
             above_right: str | None = None,
             below_left: str | None = None,
             below_right: str | None = None,
             above_of: str | None = None,
             below_of: str | None = None,
             left_of: str | None = None,
             right_of: str | None = None,
             node_distance: str | TikzDimension | None = None,
             rotate: float | None = None,
             xshift: str | TikzDimension | None = None,
             yshift: str | TikzDimension | None = None,
             scale: float | None = None,
             xscale: float | None = None,
             yscale: float | None = None,
             xslant: float | None = None,
             yslant: float | None = None,
             rounded_corners: str | TikzDimension | None = None,
             double: ColorInput | None = None,
             double_distance: str | TikzDimension | None = None,
             dash_pattern: str | None = None,
             dash_phase: str | None = None,
             pattern: _Pattern = None,
             pattern_color: ColorInput | None = None,
             shading: _Shading = None,
             shading_angle: float | None = None,
             left_color: ColorInput | None = None,
             right_color: ColorInput | None = None,
             top_color: ColorInput | None = None,
             bottom_color: ColorInput | None = None,
             inner_color: ColorInput | None = None,
             outer_color: ColorInput | None = None,
             ball_color: ColorInput | None = None,
             regular_polygon_sides: int | None = None,
             star_points: int | None = None,
             star_point_ratio: float | None = None,
             star_point_height: str | None = None,
             shadow_xshift: str | None = None,
             shadow_yshift: str | None = None,
             shadow_color: ColorInput | None = None,
             shadow_opacity: float | None = None,
             shadow_scale: float | None = None,
             pin: str | None = None,
             **kwargs: Any) -> Node
```

Add a node to the TikZ figure.

**Arguments**:

- `x` - X-coordinate, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
  `TikzCoordinate`. Use ``None`` for relatively
  positioned nodes.
- `y` - Y-coordinate. Use ``None`` when ``x`` already provides the
  full position.
- `z` - Z-coordinate for 3-D figures. Use ``None`` when ``x`` already
  provides the full position.
- `label` - Internal TikZ name. Auto-assigned when ``None``.
- `content` - Text or LaTeX content displayed inside the node.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `options` - Flag-style TikZ options
  (e.g. ``["draw", "thick"]``).
- `verbose` - If ``True``, print a debug message.
- `shape` - Node shape
  (e.g. ``"circle"``, ``"rectangle"``, ``"diamond"``).
- `color` - Text color (e.g. ``"red"``, ``"blue!50"``).
- `fill` - Fill color.
- `draw` - Border/stroke color. Use ``"none"`` to hide the border.
- `text` - Alias for text color.
- `opacity` - Overall opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `draw_opacity` - Border opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `minimum_width` - Minimum node width (e.g. ``"2cm"``).
- `minimum_height` - Minimum node height.
- `minimum_size` - Minimum size in both dimensions.
- `inner_sep` - Inner separation between content and border.
- `inner_xsep` - Horizontal inner separation.
- `inner_ysep` - Vertical inner separation.
- `outer_sep` - Outer separation between border and anchors.
- `outer_xsep` - Horizontal outer separation.
- `outer_ysep` - Vertical outer separation.
- `line_width` - Border line width (e.g. ``"1pt"``).
- `font` - Font specification (e.g. ``"\\tiny"``).
- `text_width` - Text width for automatic line wrapping.
- `text_height` - Explicit text height.
- `text_depth` - Explicit text depth.
- `align` - Text alignment (``"left"``, ``"center"``, ``"right"``).
- `anchor` - Anchor point
  (e.g. ``"center"``, ``"north"``, ``"south west"``).
- `above` - Place above, with optional offset (e.g. ``"5pt"``).
- `below` - Place below.
- `left` - Place left.
- `right` - Place right.
- `above_left` - Place above-left.
- `above_right` - Place above-right.
- `below_left` - Place below-left.
- `below_right` - Place below-right.
- `above_of` - Place above a named node.
- `below_of` - Place below a named node.
- `left_of` - Place left of a named node.
- `right_of` - Place right of a named node.
- `node_distance` - Distance for relative positioning
  (e.g. ``"1cm"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift.
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `xslant` - Horizontal slant factor.
- `yslant` - Vertical slant factor.
- `rounded_corners` - Corner rounding radius (e.g. ``"3pt"``).
- `double` - Inner color for double borders.
- `double_distance` - Distance between double borders.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
- `dash_phase` - Dash pattern starting offset.
- `pattern` - Fill pattern (e.g. ``"north east lines"``).
- `pattern_color` - Color for the fill pattern.
- `shading` - Shading type
  (``"axis"``, ``"radial"``, or ``"ball"``).
- `shading_angle` - Angle for axis shading.
- `left_color` - Left color for axis shading.
- `right_color` - Right color for axis shading.
- `top_color` - Top color for axis shading.
- `bottom_color` - Bottom color for axis shading.
- `inner_color` - Inner color for radial shading.
- `outer_color` - Outer color for radial shading.
- `ball_color` - Ball color for ball shading.
- `regular_polygon_sides` - Number of sides for
  ``shape="regular polygon"``.
- `star_points` - Number of points for ``shape="star"``.
- `star_point_ratio` - Inner-to-outer radius ratio for stars.
- `star_point_height` - Height of star points.
- `shadow_xshift` - Horizontal shadow shift.
- `shadow_yshift` - Vertical shadow shift.
- `shadow_color` - Shadow color.
- `shadow_opacity` - Shadow opacity (0–1).
- `shadow_scale` - Shadow scale factor.
- `pin` - Pin label specification (e.g. ``"above:text"``).
- `**kwargs` - Additional TikZ options. Underscores in keys become
  spaces (e.g. ``signal_from`` → ``signal from``).


**Returns**:

  The `Node` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.midpoint"></a>

##### TikzFigure.midpoint

```python
def midpoint(node1: "Node | str",
             node2: "Node | str",
             label: str | None = None,
             layer: int = 0,
             content: str = "",
             **kwargs: Any) -> Node
```

Add a node at the midpoint between two existing nodes.

**Arguments**:

- `node1` - First node object or its label string.
- `node2` - Second node object or its label string.
- `label` - Label for the new midpoint node. Auto-assigned when
  ``None``.
- `layer` - Target layer index. Defaults to ``0``.
- `content` - Text content for the midpoint node.
- `**kwargs` - Additional options forwarded to `add_node`.


**Returns**:

  The new `Node` placed at the computed midpoint.


**Raises**:

- `ValueError` - If either node lacks explicit numeric coordinates.

<a id="tikzfigure.core.figure.TikzFigure.add_coordinate"></a>

##### TikzFigure.add\_coordinate

```python
def add_coordinate(label: str,
                   x: (float
                       | str
                       | tuple[float | int | str, float | int | str]
                       | tuple[float | int | str, float | int | str,
                               float | int | str]
                       | TikzCoordinate
                       | None) = None,
                   y: float | str | None = None,
                   z: float | str | None = None,
                   at: str | None = None,
                   layer: int = 0,
                   comment: str | None = None,
                   verbose: bool = False) -> Coordinate
```

Add a named coordinate point using ``\coordinate``.

A coordinate is an invisible named point — lighter than a
`tikzfigure.core.node.Node` because it has no box, content,
or visible styling.  Use it to define reusable anchor points,
midpoints, or expression-based positions that you can reference in
paths and other commands.

Either provide explicit coordinates, or a raw TikZ coordinate
expression via ``at``.

Examples::

## Fixed point
fig.add_coordinate("origin", (0, 0))
fig.draw(["origin", "A"])

## Midpoint using calc (add "calc" to extra_packages)
fig.add_coordinate("mid", at="$(A)!0.5!(B)$")
fig.draw(["A", "mid", "B"])

## At a node anchor
fig.add_coordinate("atip", at="A.north")

**Arguments**:

- `label` - TikZ name for this coordinate.  Used when referencing
  it in path lists (e.g. ``["A", "mid", "B"]``).
- `x` - X-coordinate value, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
  `TikzCoordinate`. Must be provided together with ``y``
  when passed as a scalar. Mutually exclusive with ``at``.
- `y` - Y-coordinate value when passing explicit scalar coordinates.
  Mutually exclusive with ``at``.
- `z` - Z-coordinate value when passing explicit scalar coordinates.
  Mutually exclusive with ``at``.
- `at` - Raw TikZ coordinate expression.  Examples:

  * ``"$(A)!0.5!(B)$"`` — midpoint via ``calc`` library
  * ``"A.north"`` — at a node anchor
  * ``"30:2cm"`` — polar coordinates

  Parentheses are added automatically if absent.
  Mutually exclusive with ``x``/``y``.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message after insertion.


**Returns**:

  The newly created `Coordinate` object.

<a id="tikzfigure.core.figure.TikzFigure.add_variable"></a>

##### TikzFigure.add\_variable

```python
def add_variable(label: str,
                 value: float | str,
                 layer: int | None = 0,
                 comment: str | None = None,
                 verbose: bool = False) -> Variable
```

Add a pgfmath variable (``\pgfmathsetmacro``) to the figure.

Variables are emitted at the top of the ``tikzpicture`` environment
so they can be referenced anywhere in the figure.

**Arguments**:

- `label` - Variable name (without the leading backslash).
- `value` - Numeric value or PGF math expression string to assign
  (e.g. ``5``, ``"sqrt(2)"``, ``"sin(60)"``).
- `layer` - Layer index (currently unused). Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - Unused; reserved for future debug output.


**Returns**:

  The `Variable` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.declare_function"></a>

##### TikzFigure.declare\_function

```python
def declare_function(name: str,
                     args: str | list[str] | tuple[str, ...],
                     body: Any,
                     comment: str | None = None,
                     verbose: bool = False) -> DeclaredFunction
```

Declare a reusable PGF math function for this figure.

The returned `DeclaredFunction` is callable, so you can keep a
Python reference and later build expressions with ``f(x)`` instead of
spelling the function name again as a string.

<a id="tikzfigure.core.figure.TikzFigure.add_plot"></a>

##### TikzFigure.add\_plot

```python
def add_plot(x: Any,
             y: Any | None = None,
             *,
             variable: str = "x",
             domain: tuple[Any, Any] | str | None = None,
             samples: int | None = None,
             smooth: bool = False,
             layer: int = 0,
             comment: str | None = None,
             verbose: bool = False,
             options: OptionInput | None = None,
             tikz_command: str = "draw",
             **kwargs: Any) -> TikzPlot
```

Add a plain TikZ expression plot outside a pgfplots axis.

<a id="tikzfigure.core.figure.TikzFigure.add_parametric_grid"></a>

##### TikzFigure.add\_parametric\_grid

```python
def add_parametric_grid(x: Any,
                        y: Any,
                        *,
                        u_variable: str,
                        v_variable: str,
                        u_values: list[Any] | tuple[Any, ...] | range,
                        v_values: list[Any] | tuple[Any, ...] | range,
                        u_domain: tuple[Any, Any] | str = (0, 1),
                        v_domain: tuple[Any, Any] | str = (0, 1),
                        samples: int | None = None,
                        smooth: bool = False,
                        layer: int = 0,
                        comment: str | None = None,
                        verbose: bool = False,
                        options: OptionInput | None = None,
                        **kwargs: Any) -> tuple[Loop, Loop]
```

Draw both coordinate families of a parametric quadrilateral grid.

``x`` and ``y`` are expressions in ``u_variable`` and
``v_variable``.  The first family fixes each value in ``u_values``
and samples ``v_variable``; the second fixes each value in
``v_values`` and samples ``u_variable``.  This is useful for mapped
meshes, finite-element patches, and other curvilinear grids.

The variables should normally be created with `Var`, for
example ``x = map_x(Var("u"), Var("v"))``.  The returned loops allow
callers to inspect or further customize the generated TikZ.

<a id="tikzfigure.core.figure.TikzFigure.add_raw"></a>

##### TikzFigure.add\_raw

```python
def add_raw(tikz_code: str, layer: int = 0, verbose: bool = False) -> RawTikz
```

Insert a verbatim TikZ code block into the figure.

**Arguments**:

- `tikz_code` - Raw TikZ source to include verbatim.
- `layer` - Target layer index. Defaults to ``0``.
- `verbose` - If ``True``, print a debug message after insertion.


**Returns**:

  The `RawTikz` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.add_gantt_chart"></a>

##### TikzFigure.add\_gantt\_chart

```python
def add_gantt_chart(start: int | str,
                    end: int | str,
                    rows: list[dict[str, Any]]
                    | tuple[dict[str, Any], ...] = (),
                    layer: int = 0,
                    comment: str | None = None,
                    options: OptionInput | None = None,
                    verbose: bool = False,
                    **kwargs: Any) -> GanttChart
```

Add a chart rendered by LaTeX's ``pgfgantt`` package.

Each row is a dictionary with ``type`` set to ``title``,
``titlelist``, ``group``, ``bar``, ``milestone``, ``link``, or
``raw``. For example: ``{"type": "bar", "content": "Build",
"start": 1, "end": 3}``.

<a id="tikzfigure.core.figure.TikzFigure.arc"></a>

##### TikzFigure.arc

```python
def arc(start: PositionInput,
        start_angle: float,
        end_angle: float,
        radius: float | str,
        layer: int = 0,
        comment: str | None = None,
        verbose: bool = False,
        color: ColorInput | None = None,
        fill: ColorInput | None = None,
        draw: ColorInput | None = None,
        text: ColorInput | None = None,
        opacity: float | None = None,
        draw_opacity: float | None = None,
        fill_opacity: float | None = None,
        text_opacity: float | None = None,
        line_width: str | None = None,
        line_cap: _LineCap = None,
        line_join: _LineJoin = None,
        miter_limit: float | None = None,
        dash_pattern: str | None = None,
        dash_phase: str | None = None,
        arrows: ArrowInput | None = None,
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        xscale: float | None = None,
        yscale: float | None = None,
        **kwargs: Any) -> Arc
```

Add an arc to the figure.

**Arguments**:

- `start` - Starting coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `start_angle` - Start angle in degrees.
- `end_angle` - End angle in degrees.
- `radius` - Radius of the arc (e.g. ``"3mm"``, ``0.5``).
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `color` - Line color (e.g. ``"red"``, ``"blue!50"``).
- `fill` - Fill color for the enclosed area.
- `draw` - Stroke color when different from *color*.
- `text` - Text color.
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `line_width` - Line width (e.g. ``"1pt"``).
- `line_cap` - Line cap style: ``"butt"``, ``"rect"``, or
  ``"round"``.
- `line_join` - Line join style: ``"miter"``, ``"bevel"``, or
  ``"round"``.
- `miter_limit` - Miter limit factor for miter joins.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
- `dash_phase` - Dash pattern starting offset (e.g. ``"2pt"``).
- `arrows` - Arrow specification (e.g. ``"->"``, ``"<->"``, ``"*-*"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift (e.g. ``"1cm"``).
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Arc` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.circle"></a>

##### TikzFigure.circle

```python
def circle(center: PositionInput,
           radius: float | str,
           layer: int = 0,
           comment: str | None = None,
           verbose: bool = False,
           color: ColorInput | None = None,
           fill: ColorInput | None = None,
           draw: ColorInput | None = None,
           text: ColorInput | None = None,
           opacity: float | None = None,
           draw_opacity: float | None = None,
           fill_opacity: float | None = None,
           text_opacity: float | None = None,
           line_width: str | None = None,
           line_cap: _LineCap = None,
           line_join: _LineJoin = None,
           miter_limit: float | None = None,
           dash_pattern: str | None = None,
           dash_phase: str | None = None,
           rotate: float | None = None,
           xshift: str | None = None,
           yshift: str | None = None,
           scale: float | None = None,
           xscale: float | None = None,
           yscale: float | None = None,
           **kwargs: Any) -> Circle
```

Add a circle to the figure.

**Arguments**:

- `center` - Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `radius` - Radius of the circle (e.g. ``"5mm"``, ``1.0``).
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `color` - Line color (e.g. ``"red"``, ``"blue!50"``).
- `fill` - Fill color for the circle.
- `draw` - Stroke color when different from *color*.
- `text` - Text color.
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `line_width` - Line width (e.g. ``"1pt"``).
- `line_cap` - Line cap style: ``"butt"``, ``"rect"``, or
  ``"round"``.
- `line_join` - Line join style: ``"miter"``, ``"bevel"``, or
  ``"round"``.
- `miter_limit` - Miter limit factor for miter joins.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
- `dash_phase` - Dash pattern starting offset (e.g. ``"2pt"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift (e.g. ``"1cm"``).
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Circle` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.rectangle"></a>

##### TikzFigure.rectangle

```python
def rectangle(corner1: PositionInput,
              corner2: PositionInput,
              layer: int = 0,
              comment: str | None = None,
              verbose: bool = False,
              color: ColorInput | None = None,
              fill: ColorInput | None = None,
              draw: ColorInput | None = None,
              text: ColorInput | None = None,
              opacity: float | None = None,
              draw_opacity: float | None = None,
              fill_opacity: float | None = None,
              text_opacity: float | None = None,
              line_width: str | None = None,
              line_cap: _LineCap = None,
              line_join: _LineJoin = None,
              miter_limit: float | None = None,
              dash_pattern: str | None = None,
              dash_phase: str | None = None,
              rounded_corners: str | None = None,
              rotate: float | None = None,
              xshift: str | None = None,
              yshift: str | None = None,
              scale: float | None = None,
              xscale: float | None = None,
              yscale: float | None = None,
              **kwargs: Any) -> Rectangle
```

Add a rectangle to the figure.

**Arguments**:

- `corner1` - First corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `corner2` - Opposite corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `color` - Line color (e.g. ``"red"``, ``"blue!50"``).
- `fill` - Fill color for the rectangle.
- `draw` - Stroke color when different from *color*.
- `text` - Text color.
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `line_width` - Line width (e.g. ``"1pt"``).
- `line_cap` - Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
- `line_join` - Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
- `miter_limit` - Miter limit factor for miter joins.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
- `dash_phase` - Dash pattern starting offset (e.g. ``"2pt"``).
- `rounded_corners` - Corner rounding radius (e.g. ``"5pt"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift (e.g. ``"1cm"``).
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Rectangle` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.add_matrix"></a>

##### TikzFigure.add\_matrix

```python
def add_matrix(rows: list[list[Any]],
               x: (float
                   | str
                   | tuple[float | int | str, float | int | str]
                   | tuple[float | int | str, float | int | str,
                           float | int | str]
                   | TikzCoordinate
                   | None) = None,
               y: float | str | None = None,
               z: float | str | None = None,
               label: str | None = None,
               layer: int = 0,
               comment: str | None = None,
               options: OptionInput | None = None,
               row_sep: str | None = None,
               column_sep: str | None = None,
               cell_style: str | list[str] | None = None,
               anchor: _Anchor = None,
               verbose: bool = False,
               **kwargs: Any) -> Matrix
```

Add a matrix of nodes (``\matrix``) to the TikZ figure.

A first-class alternative to hand-writing raw ``\matrix`` TikZ,
with row/column separation, per-cell styling, and easy cell
addressing via `Matrix.cell`.

Examples::

m = fig.add_matrix(
[["A", "B"], ["C", "D"]],
label="m",
row_sep="5pt",
column_sep="1cm",
cell_style="draw, minimum size=8mm, anchor=center",
)
fig.add_coordinate("c11", at=m.cell(1, 1))
fig.add_coordinate("c22", at=m.cell(2, 2))
fig.draw(["c11", "c22"])

**Arguments**:

- `rows` - Grid of cells, given row by row. Each cell is either a
  plain string (node content), a dict of
- ```{"content"` - str, "options": ..., **node_kwargs}`` for
  per-cell styling, or ``None`` for an empty cell.
- `x` - X-coordinate, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
  `TikzCoordinate` giving the matrix's anchor
  position. Use ``None`` to let TikZ place it at the origin.
- `y` - Y-coordinate. Use ``None`` when ``x`` already provides the
  full position.
- `z` - Z-coordinate for 3-D figures.
- `label` - Internal TikZ name. Auto-assigned when ``None``.
  Required (explicitly or via auto-assignment) to address
  individual cells with `Matrix.cell`.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `options` - Flag-style TikZ options for the matrix node itself.
- `row_sep` - Row separation (e.g. ``"5pt"``).
- `column_sep` - Column separation (e.g. ``"1cm"``).
- `cell_style` - Shared TikZ style(s) applied to every cell node,
  rendered as ``nodes={<cell_style>}``.
- `anchor` - Anchor point for the whole matrix node.
- `verbose` - If ``True``, print a debug message.
- `**kwargs` - Additional matrix-level TikZ options.


**Returns**:

  The `Matrix` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.add_fit"></a>

##### TikzFigure.add\_fit

```python
def add_fit(targets: list[Any],
            content: str = "",
            label: str | None = None,
            layer: int = 0,
            comment: str | None = None,
            options: OptionInput | None = None,
            verbose: bool = False,
            **kwargs: Any) -> Fit
```

Wrap existing nodes/coordinates in a bounding node (``fit`` library).

A first-class alternative to hand-writing raw ``fit=(...)...`` node
options.

Examples::

a = fig.add_node((0, 0), content="A")
b = fig.add_node((2, 1), content="B")
fig.add_fit([a, b], options=["draw", "dashed", "rounded corners"])

**Arguments**:

- `targets` - Nodes/coordinates to fit around, as a list of
  `Node`/`Coordinate` objects or label strings
  (optionally with a ``.anchor`` suffix, e.g. ``"a.north"``).
  At least one is required.
- `content` - Text or LaTeX content displayed inside the fit node.
  Usually left empty.
- `label` - Internal TikZ name. Auto-assigned when ``None``.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `options` - Flag-style TikZ options (e.g. ``["draw", "dashed"]``).
- `verbose` - If ``True``, print a debug message.
- `**kwargs` - Additional TikZ options for the fit node (e.g.
  ``inner_sep="5pt"``).


**Returns**:

  The `Fit` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.ellipse"></a>

##### TikzFigure.ellipse

```python
def ellipse(center: PositionInput,
            x_radius: float | str,
            y_radius: float | str,
            layer: int = 0,
            comment: str | None = None,
            verbose: bool = False,
            color: ColorInput | None = None,
            fill: ColorInput | None = None,
            draw: ColorInput | None = None,
            text: ColorInput | None = None,
            opacity: float | None = None,
            draw_opacity: float | None = None,
            fill_opacity: float | None = None,
            text_opacity: float | None = None,
            line_width: str | None = None,
            line_cap: _LineCap = None,
            line_join: _LineJoin = None,
            miter_limit: float | None = None,
            dash_pattern: str | None = None,
            dash_phase: str | None = None,
            rotate: float | None = None,
            xshift: str | None = None,
            yshift: str | None = None,
            scale: float | None = None,
            xscale: float | None = None,
            yscale: float | None = None,
            **kwargs: Any) -> Ellipse
```

Add an ellipse to the figure.

**Arguments**:

- `center` - Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `x_radius` - Horizontal radius (e.g. ``"2cm"``, ``1.5``).
- `y_radius` - Vertical radius (e.g. ``"1cm"``, ``0.75``).
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `color` - Line color (e.g. ``"red"``, ``"blue!50"``).
- `fill` - Fill color for the ellipse.
- `draw` - Stroke color when different from *color*.
- `text` - Text color.
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `line_width` - Line width (e.g. ``"1pt"``).
- `line_cap` - Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
- `line_join` - Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
- `miter_limit` - Miter limit factor for miter joins.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
- `dash_phase` - Dash pattern starting offset (e.g. ``"2pt"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift (e.g. ``"1cm"``).
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Ellipse` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.grid"></a>

##### TikzFigure.grid

```python
def grid(corner1: PositionInput,
         corner2: PositionInput,
         step: str | None = None,
         layer: int = 0,
         comment: str | None = None,
         verbose: bool = False,
         color: ColorInput | None = None,
         opacity: float | None = None,
         draw_opacity: float | None = None,
         line_width: str | None = None,
         line_cap: _LineCap = None,
         line_join: _LineJoin = None,
         dash_pattern: str | None = None,
         dash_phase: str | None = None,
         rotate: float | None = None,
         xshift: str | None = None,
         yshift: str | None = None,
         scale: float | None = None,
         xscale: float | None = None,
         yscale: float | None = None,
         **kwargs: Any) -> Grid
```

Add a grid to the figure.

**Arguments**:

- `corner1` - First corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `corner2` - Opposite corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `step` - Grid step size (e.g. ``"1cm"`` for uniform, or
  ``"0.5cm,1cm"`` for different x/y steps). Defaults to ``None``
  (TikZ default of 1cm).
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `color` - Line color (e.g. ``"red"``, ``"gray!30"``).
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `line_width` - Line width (e.g. ``"0.5pt"``).
- `line_cap` - Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
- `line_join` - Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 1pt off 1pt"``).
- `dash_phase` - Dash pattern starting offset (e.g. ``"1pt"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift (e.g. ``"1cm"``).
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Grid` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.parabola"></a>

##### TikzFigure.parabola

```python
def parabola(start: PositionInput,
             end: PositionInput,
             bend: PositionInput | None = None,
             layer: int = 0,
             comment: str | None = None,
             verbose: bool = False,
             color: ColorInput | None = None,
             fill: ColorInput | None = None,
             draw: ColorInput | None = None,
             text: ColorInput | None = None,
             opacity: float | None = None,
             draw_opacity: float | None = None,
             fill_opacity: float | None = None,
             text_opacity: float | None = None,
             line_width: str | None = None,
             line_cap: _LineCap = None,
             line_join: _LineJoin = None,
             miter_limit: float | None = None,
             dash_pattern: str | None = None,
             dash_phase: str | None = None,
             arrows: ArrowInput | None = None,
             rotate: float | None = None,
             xshift: str | None = None,
             yshift: str | None = None,
             scale: float | None = None,
             xscale: float | None = None,
             yscale: float | None = None,
             **kwargs: Any) -> Parabola
```

Add a parabola to the figure.

**Arguments**:

- `start` - Starting coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `end` - Ending coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `bend` - Bend point as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`. If None, uses TikZ default.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `color` - Line color (e.g. ``"red"``, ``"blue!50"``).
- `fill` - Fill color for the parabola.
- `draw` - Stroke color when different from *color*.
- `text` - Text color.
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `line_width` - Line width (e.g. ``"1pt"``).
- `line_cap` - Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
- `line_join` - Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
- `miter_limit` - Miter limit factor for miter joins.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
- `dash_phase` - Dash pattern starting offset (e.g. ``"2pt"``).
- `arrows` - Arrow specification (e.g. ``"->"``, ``"<->"``, ``"*-*"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift (e.g. ``"1cm"``).
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Parabola` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.line"></a>

##### TikzFigure.line

```python
def line(start: PositionInput,
         end: PositionInput,
         layer: int = 0,
         comment: str | None = None,
         verbose: bool = False,
         options: OptionInput | None = None,
         color: ColorInput | None = None,
         text: ColorInput | None = None,
         opacity: float | None = None,
         draw_opacity: float | None = None,
         line_width: str | None = None,
         line_cap: _LineCap = None,
         line_join: _LineJoin = None,
         miter_limit: float | None = None,
         dash_pattern: str | None = None,
         dash_phase: str | None = None,
         arrows: ArrowInput | None = None,
         rotate: float | None = None,
         xshift: str | None = None,
         yshift: str | None = None,
         scale: float | None = None,
         xscale: float | None = None,
         yscale: float | None = None,
         **kwargs: Any) -> Line
```

Add a line segment to the figure.

**Arguments**:

- `start` - Starting point as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `end` - Ending point as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `options` - Flag-style TikZ options without values
  (e.g. ``["dashed", "thick"]``).
- `color` - Line color (e.g. ``"red"``, ``"blue!50"``).
- `text` - Text color.
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `line_width` - Line width (e.g. ``"1pt"``).
- `line_cap` - Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
- `line_join` - Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
- `miter_limit` - Miter limit factor for miter joins.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
- `dash_phase` - Dash pattern starting offset (e.g. ``"2pt"``).
- `arrows` - Arrow specification (e.g. ``"->"``, ``"<->"``, ``"*-*"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift (e.g. ``"1cm"``).
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Line` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.polygon"></a>

##### TikzFigure.polygon

```python
def polygon(center: PositionInput,
            radius: float | str,
            sides: int,
            rotation: float = 0,
            layer: int = 0,
            comment: str | None = None,
            verbose: bool = False,
            color: ColorInput | None = None,
            fill: ColorInput | None = None,
            draw: ColorInput | None = None,
            text: ColorInput | None = None,
            opacity: float | None = None,
            draw_opacity: float | None = None,
            fill_opacity: float | None = None,
            text_opacity: float | None = None,
            line_width: str | None = None,
            line_cap: _LineCap = None,
            line_join: _LineJoin = None,
            miter_limit: float | None = None,
            dash_pattern: str | None = None,
            dash_phase: str | None = None,
            rotate: float | None = None,
            xshift: str | None = None,
            yshift: str | None = None,
            scale: float | None = None,
            xscale: float | None = None,
            yscale: float | None = None,
            **kwargs: Any) -> Polygon
```

Add a regular polygon to the figure.

**Arguments**:

- `center` - Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `radius` - Distance from center to vertices.
- `sides` - Number of sides (must be >= 3).
- `rotation` - Rotation angle in degrees. Defaults to ``0``.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `color` - Line color (e.g. ``"red"``, ``"blue!50"``).
- `fill` - Fill color for the polygon.
- `draw` - Stroke color when different from *color*.
- `text` - Text color.
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `line_width` - Line width (e.g. ``"1pt"``).
- `line_cap` - Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
- `line_join` - Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
- `miter_limit` - Miter limit factor for miter joins.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
- `dash_phase` - Dash pattern starting offset (e.g. ``"2pt"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift (e.g. ``"1cm"``).
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Polygon` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.triangle"></a>

##### TikzFigure.triangle

```python
def triangle(center: PositionInput,
             radius: float | str,
             rotation: float = 0,
             layer: int = 0,
             comment: str | None = None,
             verbose: bool = False,
             color: ColorInput | None = None,
             fill: ColorInput | None = None,
             draw: ColorInput | None = None,
             text: ColorInput | None = None,
             opacity: float | None = None,
             draw_opacity: float | None = None,
             fill_opacity: float | None = None,
             text_opacity: float | None = None,
             line_width: str | None = None,
             **kwargs: Any) -> Triangle
```

Add an equilateral triangle to the figure.

**Arguments**:

- `center` - Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `radius` - Distance from center to vertices.
- `rotation` - Rotation angle in degrees. Defaults to ``0``.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `color` - Line color (e.g. ``"red"``, ``"blue!50"``).
- `fill` - Fill color for the triangle.
- `draw` - Stroke color when different from *color*.
- `text` - Text color.
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `line_width` - Line width (e.g. ``"1pt"``).
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Triangle` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.square"></a>

##### TikzFigure.square

```python
def square(center: PositionInput,
           radius: float | str,
           rotation: float = 45,
           layer: int = 0,
           comment: str | None = None,
           verbose: bool = False,
           color: ColorInput | None = None,
           fill: ColorInput | None = None,
           draw: ColorInput | None = None,
           text: ColorInput | None = None,
           opacity: float | None = None,
           draw_opacity: float | None = None,
           fill_opacity: float | None = None,
           text_opacity: float | None = None,
           line_width: str | None = None,
           **kwargs: Any) -> Square
```

Add a square to the figure.

**Arguments**:

- `center` - Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
  `TikzCoordinate`.
- `radius` - Distance from center to vertices (corner-to-center distance).
- `rotation` - Rotation angle in degrees. Defaults to ``45`` (axis-aligned).
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.
- `color` - Line color (e.g. ``"red"``, ``"blue!50"``).
- `fill` - Fill color for the square.
- `draw` - Stroke color when different from *color*.
- `text` - Text color.
- `opacity` - Overall opacity (0–1).
- `draw_opacity` - Stroke opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `line_width` - Line width (e.g. ``"1pt"``).
- `**kwargs` - Catch-all for unlisted TikZ options.


**Returns**:

  The `Square` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.plot3d"></a>

##### TikzFigure.plot3d

```python
def plot3d(x: list[float],
           y: list[float],
           z: list[float],
           layer: int = 0,
           comment: str | None = None,
           center: bool = False,
           verbose: bool = False,
           **kwargs: Any) -> Plot3D
```

Add a 3-D data plot with ``\addplot3``.

**Arguments**:

- `x` - List of x-coordinate values.
- `y` - List of y-coordinate values.
- `z` - List of z-coordinate values.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `center` - If ``True``, connect through ``.center`` anchors.
- `verbose` - If ``True``, print a debug message.
- `**kwargs` - Additional pgfplots options (e.g. ``mark="*"``).


**Returns**:

  The `Plot3D` object that was added.

<a id="tikzfigure.core.figure.TikzFigure.axis2d"></a>

##### TikzFigure.axis2d

```python
def axis2d(xlabel: str = "",
           ylabel: str = "",
           xlim: tuple[float, float] | None = None,
           ylim: tuple[float, float] | None = None,
           xlog: bool = False,
           ylog: bool = False,
           grid: bool | str = True,
           width: str | float | None = None,
           height: str | float | None = None,
           layer: int = 0,
           comment: str | None = None,
           **kwargs: Any) -> Axis2D
```

Create and register a 2D axis.

**Arguments**:

- `xlabel` - Label for x-axis. Defaults to "".
- `ylabel` - Label for y-axis. Defaults to "".
- `xlim` - (min, max) tuple for x-axis limits, or None for auto.
- `ylim` - (min, max) tuple for y-axis limits, or None for auto.
- `xlog` - Whether to use logarithmic scaling on the x-axis.
- `ylog` - Whether to use logarithmic scaling on the y-axis.
- `grid` - Enable grid lines. Pass ``True`` / ``False`` for the usual
  pgfplots values or a string such as ``"major"``.
- `width` - Width of the axis as a string (e.g., "8cm"), number in cm,
  or None for auto. Defaults to None.
- `height` - Height of the axis as a string (e.g., "6cm"), number in cm,
  or None for auto. Defaults to None.
- `layer` - Layer index (for metadata; axes render after all layers).
- `comment` - Optional comment prepended in TikZ output.
- `**kwargs` - Additional pgfplots axis options.


**Returns**:

  The newly created Axis2D object.

<a id="tikzfigure.core.figure.TikzFigure.add_loop"></a>

##### TikzFigure.add\_loop

```python
def add_loop(variable: str,
             values: list[Any] | tuple[Any, ...] | range,
             layer: int = 0,
             comment: str | None = None,
             verbose: bool = False) -> Loop
```

Add a ``\foreach`` loop to the figure.

**Arguments**:

- `variable` - Loop variable name (without the leading backslash),
  e.g. ``"i"`` produces ``\foreach \i in {...}``.
- `values` - Sequence of values to iterate over.
- `layer` - Target layer index. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.
- `verbose` - If ``True``, print a debug message.


**Returns**:

  The `Loop` context manager. Add nodes and paths inside a
  ``with`` block or by calling methods on the returned object.

<a id="tikzfigure.core.figure.TikzFigure.add_scope"></a>

##### TikzFigure.add\_scope

```python
def add_scope(layer: int = 0,
              comment: str | None = None,
              options: OptionInput | None = None,
              verbose: bool = False,
              **kwargs: Any) -> Scope
```

Add a TikZ ``scope`` block with local options to the figure.

<a id="tikzfigure.core.figure.TikzFigure.document_setup"></a>

##### TikzFigure.document\_setup

```python
@property
def document_setup() -> str | None
```

Raw LaTeX inserted in the preamble before ``\begin{document}``.

<a id="tikzfigure.core.figure.TikzFigure.extra_packages"></a>

##### TikzFigure.extra\_packages

```python
@property
def extra_packages() -> list[str] | None
```

Extra LaTeX packages included in the standalone preamble.

<a id="tikzfigure.core.figure.TikzFigure.named_styles"></a>

##### TikzFigure.named\_styles

```python
@property
def named_styles() -> list[dict[str, Any]]
```

Named TikZ styles defined at figure scope.

<a id="tikzfigure.core.figure.TikzFigure.tikz_libraries"></a>

##### TikzFigure.tikz\_libraries

```python
@property
def tikz_libraries() -> list[str]
```

TikZ libraries loaded in standalone output via ``\usetikzlibrary``.

<a id="tikzfigure.core.figure.TikzFigure.ndim"></a>

##### TikzFigure.ndim

```python
@property
def ndim() -> int
```

Number of spatial dimensions (``2`` or ``3``).

<a id="tikzfigure.core.figure.TikzFigure.layers"></a>

##### TikzFigure.layers

```python
@property
def layers() -> LayerCollection
```

The `LayerCollection` holding all drawing layers.

<a id="tikzfigure.core.figure.TikzFigure.colors"></a>

##### TikzFigure.colors

```python
@property
def colors() -> list[tuple[str, Color]]
```

List of ``(name, Color)`` pairs defined with `colorlet`.

<a id="tikzfigure.core.figure.TikzFigure.variables"></a>

##### TikzFigure.variables

```python
@property
def variables() -> list
```

List of `Variable` objects defined in this figure.

<a id="tikzfigure.core.figure.TikzFigure.declared_functions"></a>

##### TikzFigure.declared\_functions

```python
@property
def declared_functions() -> list[DeclaredFunction]
```

List of declared PGF functions available in this figure.

<a id="tikzfigure.core.figure.TikzFigure.axes"></a>

##### TikzFigure.axes

```python
@property
def axes() -> list[Axis2D]
```

List of `Axis2D` objects created in this figure.

<a id="tikzfigure.core.figure.TikzFigure.subfigure_axes"></a>

##### TikzFigure.subfigure\_axes

```python
@property
def subfigure_axes() -> list[tuple[Axis2D, float]]
```

List of subfigure axes with widths.

<a id="tikzfigure.core.figure.TikzFigure.__repr__"></a>

##### TikzFigure.\_\_repr\_\_

```python
def __repr__() -> str
```

Return the generated TikZ source as the object representation.

<a id="tikzfigure.core.figure.TikzFigure.__str__"></a>

##### TikzFigure.\_\_str\_\_

```python
def __str__() -> str
```

Return the generated TikZ source as a string.

## Node API

```python
from tikzfigure import Node
```

<a id="tikzfigure.core.node.Node"></a>

### Node

```python
class Node(TikzObject)
```

A TikZ node with an optional position, content, and styling options.

Accepts the same TikZ options as `TikzFigure.add_node`. Refer to
that method for the full parameter reference.

**Attributes**:

- `x` - X-coordinate of the node, or ``None`` for relatively positioned
  nodes.
- `y` - Y-coordinate of the node, or ``None`` for relatively positioned
  nodes.
- `z` - Z-coordinate for 3-D figures, or ``None`` for 2-D figures.
- `ndim` - Number of spatial dimensions (``2`` or ``3``).
- `content` - Text or LaTeX content displayed inside the node.

<a id="tikzfigure.core.node.Node.__init__"></a>

##### Node.\_\_init\_\_

```python
def __init__(x: (CoordinateValue
                 | CoordinateTuple2D
                 | CoordinateTuple3D
                 | TikzCoordinate
                 | None) = None,
             y: CoordinateValue | None = None,
             z: CoordinateValue | None = None,
             label: str = "",
             content: str = "",
             comment: str | None = None,
             layer: int = 0,
             options: OptionInput | None = None,
             shape: _Shape = None,
             color: ColorInput | None = None,
             fill: ColorInput | None = None,
             draw: ColorInput | None = None,
             text: ColorInput | None = None,
             opacity: float | None = None,
             fill_opacity: float | None = None,
             draw_opacity: float | None = None,
             text_opacity: float | None = None,
             minimum_width: str | None = None,
             minimum_height: str | None = None,
             minimum_size: str | None = None,
             inner_sep: str | None = None,
             inner_xsep: str | None = None,
             inner_ysep: str | None = None,
             outer_sep: str | None = None,
             outer_xsep: str | None = None,
             outer_ysep: str | None = None,
             line_width: str | None = None,
             font: str | None = None,
             text_width: str | None = None,
             text_height: str | None = None,
             text_depth: str | None = None,
             align: _Align = None,
             anchor: _Anchor = None,
             above: str | None = None,
             below: str | None = None,
             left: str | None = None,
             right: str | None = None,
             above_left: str | None = None,
             above_right: str | None = None,
             below_left: str | None = None,
             below_right: str | None = None,
             above_of: str | None = None,
             below_of: str | None = None,
             left_of: str | None = None,
             right_of: str | None = None,
             node_distance: str | None = None,
             rotate: float | None = None,
             xshift: str | None = None,
             yshift: str | None = None,
             scale: float | None = None,
             xscale: float | None = None,
             yscale: float | None = None,
             xslant: float | None = None,
             yslant: float | None = None,
             rounded_corners: str | None = None,
             double: ColorInput | None = None,
             double_distance: str | None = None,
             dash_pattern: str | None = None,
             dash_phase: str | None = None,
             pattern: _Pattern = None,
             pattern_color: ColorInput | None = None,
             shading: _Shading = None,
             shading_angle: float | None = None,
             left_color: ColorInput | None = None,
             right_color: ColorInput | None = None,
             top_color: ColorInput | None = None,
             bottom_color: ColorInput | None = None,
             inner_color: ColorInput | None = None,
             outer_color: ColorInput | None = None,
             ball_color: ColorInput | None = None,
             regular_polygon_sides: int | None = None,
             star_points: int | None = None,
             star_point_ratio: float | None = None,
             star_point_height: str | None = None,
             shadow_xshift: str | None = None,
             shadow_yshift: str | None = None,
             shadow_color: ColorInput | None = None,
             shadow_opacity: float | None = None,
             shadow_scale: float | None = None,
             pin: str | None = None,
             **kwargs: Any) -> None
```

Initialize a Node.

Accepts the same TikZ options as `TikzFigure.add_node`.
Refer to that method for the full parameter reference.

**Arguments**:

- `x` - X-coordinate, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
  `TikzCoordinate`. Use ``None`` for relatively
  positioned nodes.
- `y` - Y-coordinate. Use ``None`` when ``x`` already provides the
  full position.
- `z` - Z-coordinate for 3-D figures. Use ``None`` when ``x`` already
  provides the full position.
- `label` - Internal TikZ name for this node. Defaults to ``""``.
- `content` - Text or LaTeX content displayed inside the node.
- `comment` - Optional comment prepended in the TikZ output.
- `layer` - Layer index. Defaults to ``0``.
- `options` - Flag-style TikZ options (e.g. ``["draw", "thick"]``).
- `shape` - Node shape (e.g. ``"circle"``, ``"rectangle"``).
- `color` - Text color.
- `fill` - Fill color.
- `draw` - Border/stroke color.
- `text` - Alias for text color.
- `opacity` - Overall opacity (0–1).
- `fill_opacity` - Fill opacity (0–1).
- `draw_opacity` - Border opacity (0–1).
- `text_opacity` - Text opacity (0–1).
- `minimum_width` - Minimum node width (e.g. ``"2cm"``).
- `minimum_height` - Minimum node height.
- `minimum_size` - Minimum size in both dimensions.
- `inner_sep` - Inner separation between content and border.
- `inner_xsep` - Horizontal inner separation.
- `inner_ysep` - Vertical inner separation.
- `outer_sep` - Outer separation between border and anchors.
- `outer_xsep` - Horizontal outer separation.
- `outer_ysep` - Vertical outer separation.
- `line_width` - Border line width (e.g. ``"1pt"``).
- `font` - Font specification (e.g. ``"\\tiny"``).
- `text_width` - Text width for automatic line wrapping.
- `text_height` - Explicit text height.
- `text_depth` - Explicit text depth.
- `align` - Text alignment (``"left"``, ``"center"``, ``"right"``).
- `anchor` - Anchor point (e.g. ``"center"``, ``"north"``).
- `above` - Place above, with optional offset (e.g. ``"5pt"``).
- `below` - Place below.
- `left` - Place left.
- `right` - Place right.
- `above_left` - Place above-left.
- `above_right` - Place above-right.
- `below_left` - Place below-left.
- `below_right` - Place below-right.
- `above_of` - Place above a named node.
- `below_of` - Place below a named node.
- `left_of` - Place left of a named node.
- `right_of` - Place right of a named node.
- `node_distance` - Distance for relative positioning (e.g. ``"1cm"``).
- `rotate` - Rotation angle in degrees.
- `xshift` - Horizontal shift (e.g. ``"1cm"``).
- `yshift` - Vertical shift.
- `scale` - Uniform scaling factor.
- `xscale` - Horizontal scaling factor.
- `yscale` - Vertical scaling factor.
- `xslant` - Horizontal slant factor.
- `yslant` - Vertical slant factor.
- `rounded_corners` - Corner rounding radius (e.g. ``"3pt"``).
- `double` - Inner color for double borders.
- `double_distance` - Distance between double borders.
- `dash_pattern` - Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
- `dash_phase` - Dash pattern starting offset.
- `pattern` - Fill pattern (e.g. ``"north east lines"``).
- `pattern_color` - Color for the fill pattern.
- `shading` - Shading type (``"axis"``, ``"radial"``, ``"ball"``).
- `shading_angle` - Angle for axis shading.
- `left_color` - Left color for axis shading.
- `right_color` - Right color for axis shading.
- `top_color` - Top color for axis shading.
- `bottom_color` - Bottom color for axis shading.
- `inner_color` - Inner color for radial shading.
- `outer_color` - Outer color for radial shading.
- `ball_color` - Ball color for ball shading.
- `regular_polygon_sides` - Number of sides for ``shape="regular polygon"``.
- `star_points` - Number of points for ``shape="star"``.
- `star_point_ratio` - Inner-to-outer radius ratio for stars.
- `star_point_height` - Height of star points.
- `shadow_xshift` - Horizontal shadow shift.
- `shadow_yshift` - Vertical shadow shift.
- `shadow_color` - Shadow color.
- `shadow_opacity` - Shadow opacity (0–1).
- `shadow_scale` - Shadow scale factor.
- `pin` - Pin label specification (e.g. ``"above:text"``).
- `**kwargs` - Additional TikZ options not listed above. Underscores
  in keys become spaces in the output.

<a id="tikzfigure.core.node.Node.x"></a>

##### Node.x

```python
@property
def x() -> CoordinateValue | None
```

X-coordinate, or ``None`` for relatively positioned nodes.

<a id="tikzfigure.core.node.Node.y"></a>

##### Node.y

```python
@property
def y() -> CoordinateValue | None
```

Y-coordinate, or ``None`` for relatively positioned nodes.

<a id="tikzfigure.core.node.Node.z"></a>

##### Node.z

```python
@property
def z() -> CoordinateValue | None
```

Z-coordinate for 3-D figures, or ``None`` for 2-D figures.

<a id="tikzfigure.core.node.Node.coordinate"></a>

##### Node.coordinate

```python
@property
def coordinate() -> TikzCoordinate | None
```

TikzCoordinate for this node, or ``None`` for relatively positioned nodes.

<a id="tikzfigure.core.node.Node.position"></a>

##### Node.position

```python
@property
def position() -> TikzCoordinate | None
```

Alias for `coordinate` for geometric operations.

<a id="tikzfigure.core.node.Node.ndim"></a>

##### Node.ndim

```python
@property
def ndim() -> int
```

Number of spatial dimensions (``2`` or ``3``).

<a id="tikzfigure.core.node.Node.center"></a>

##### Node.center

```python
@property
def center() -> str
```

Anchor point for the center of the node.

<a id="tikzfigure.core.node.Node.content"></a>

##### Node.content

```python
@property
def content() -> str
```

Text or LaTeX content displayed inside this node.

<a id="tikzfigure.core.node.Node.copy"></a>

##### Node.copy

```python
def copy(**overrides: Any) -> "Node"
```

Return a copy of this node with optional constructor-style overrides.

<a id="tikzfigure.core.node.Node.to_vector"></a>

##### Node.to\_vector

```python
def to_vector() -> TikzVector
```

Interpret this node position as a vector from the origin.

<a id="tikzfigure.core.node.Node.vector_to"></a>

##### Node.vector\_to

```python
def vector_to(other: "Node | TikzCoordinate") -> TikzVector
```

Return the vector from this node to another node or point.

<a id="tikzfigure.core.node.Node.distance_to"></a>

##### Node.distance\_to

```python
def distance_to(other: "Node | TikzCoordinate") -> float
```

Return the Euclidean distance to another node or point.

<a id="tikzfigure.core.node.Node.translate"></a>

##### Node.translate

```python
def translate(vector: VectorInput) -> TikzCoordinate
```

Return the translated point for this node.

<a id="tikzfigure.core.node.Node.to"></a>

##### Node.to

```python
def to(target: "Node | Coordinate",
       options: OptionInput | None = None,
       **kwargs: Any) -> "NodePathBuilder"
```

Create a path builder for a segment from this node to ``target``.

The returned builder always starts with ``self`` and records the segment
options for the edge from ``self`` to ``target``. Chain additional
``.to(...)`` or ``.arc(...)`` calls on the builder to add more path
segments. Only `Node` and `Coordinate` targets are
accepted by ``.to(...)``.

<a id="tikzfigure.core.node.Node.to_tikz"></a>

##### Node.to\_tikz

```python
def to_tikz(output_unit: str | None = None) -> str
```

Generate the TikZ ``\node`` command for this node.

**Returns**:

  A TikZ ``\node`` command string ending with a newline, optionally
  preceded by a comment line.

<a id="tikzfigure.core.node.Node.to_dict"></a>

##### Node.to\_dict

```python
def to_dict() -> dict[str, Any]
```

Serialize this node to a plain dictionary.

**Returns**:

  A dictionary with ``type``, ``x``, ``y``, ``z``, ``content``,
  and all base-class keys.

<a id="tikzfigure.core.node.Node.from_dict"></a>

##### Node.from\_dict

```python
@classmethod
def from_dict(cls, d: dict[str, Any]) -> "Node"
```

Reconstruct a Node from a dictionary.

**Arguments**:

- `d` - Dictionary as produced by `to_dict`.


**Returns**:

  A new `Node` instance.

## Implicit figure API

```python
import tikzfigure as tf
```

Module-level drawing API backed by an implicit "current figure".

This mirrors the way `matplotlib.pyplot` works: instead of creating a
`tikzfigure.core.figure.TikzFigure` yourself, you call the drawing
functions directly on the module and they are forwarded to the current
figure, which is created on demand::

    import tikzfigure as tf

    tf.draw([(0, 0), (1, 1)])
    tf.show()

This is a convenience layer for quick scripts and notebooks.  For anything
larger, prefer the explicit object-oriented API::

    fig = tf.TikzFigure()
    fig.draw([(0, 0), (1, 1)])
    fig.show()

Every function here simply calls the identically named method on
`gcf`, so see `tikzfigure.core.figure.TikzFigure` for the
full argument documentation.

<a id="tikzfigure.pyplot.gcf"></a>

##### gcf

```python
def gcf() -> TikzFigure
```

Return the current figure, creating an empty one if needed.

**Returns**:

  The `tikzfigure.core.figure.TikzFigure` that the
  module-level drawing functions operate on.

<a id="tikzfigure.pyplot.scf"></a>

##### scf

```python
def scf(fig: TikzFigure) -> TikzFigure
```

Make *fig* the current figure.

**Arguments**:

- `fig` - The figure the module-level functions should draw on.


**Returns**:

  The figure that was passed in.


**Raises**:

- `TypeError` - If *fig* is not a `TikzFigure`.

<a id="tikzfigure.pyplot.figure"></a>

##### figure

```python
def figure(*args: Any, **kwargs: Any) -> TikzFigure
```

Create a new figure, make it current, and return it.

Accepts the same arguments as `tikzfigure.core.figure.TikzFigure`.

<a id="tikzfigure.pyplot.clf"></a>

##### clf

```python
def clf(*args: Any, **kwargs: Any) -> TikzFigure
```

Replace the current figure with a fresh, empty one.

Accepts the same arguments as `tikzfigure.core.figure.TikzFigure`.

<a id="tikzfigure.pyplot.close"></a>

##### close

```python
def close() -> None
```

Discard the current figure.

The next call to `gcf` (or to any drawing function) creates a
new empty figure.

<a id="tikzfigure.pyplot.from_tikz_code"></a>

##### from\_tikz\_code

```python
def from_tikz_code(*args: Any, **kwargs: Any) -> TikzFigure
```

Parse TikZ source into a new current figure.

See `TikzFigure.from_tikz_code`. The parsed figure becomes the
current one, so subsequent module-level calls draw on top of it.

<a id="tikzfigure.pyplot.from_dict"></a>

##### from\_dict

```python
def from_dict(*args: Any, **kwargs: Any) -> TikzFigure
```

Rebuild a figure from a dict and make it current.

See `TikzFigure.from_dict`.

<a id="tikzfigure.pyplot.copy"></a>

##### copy

```python
def copy(*args: Any, **kwargs: Any) -> TikzFigure
```

Copy the current figure. See `TikzFigure.copy`.

The copy is *not* made current; pass it to `scf` if you want that.

<a id="tikzfigure.pyplot.to_dict"></a>

##### to\_dict

```python
def to_dict(*args: Any, **kwargs: Any) -> dict[str, Any]
```

Serialize the current figure to a dict. See `TikzFigure.to_dict`.

<a id="tikzfigure.pyplot.to_python"></a>

##### to\_python

```python
def to_python(*args: Any, **kwargs: Any) -> str
```

Emit Python that rebuilds the current figure. See `TikzFigure.to_python`.

<a id="tikzfigure.pyplot.generate_subfigures"></a>

##### generate\_subfigures

Combine several figures side by side. See `TikzFigure.generate_subfigures`.
This one is a static helper: it takes the figures explicitly rather than
operating on the current figure.

<a id="tikzfigure.pyplot.draw"></a>

##### draw

```python
def draw(*args: Any, **kwargs: Any) -> TikzPath
```

Draw a path on the current figure. See `TikzFigure.draw`.

<a id="tikzfigure.pyplot.filldraw"></a>

##### filldraw

```python
def filldraw(*args: Any, **kwargs: Any) -> TikzPath
```

Fill and draw a path on the current figure. See `TikzFigure.filldraw`.

<a id="tikzfigure.pyplot.fill"></a>

##### fill

```python
def fill(*args: Any, **kwargs: Any) -> TikzPath
```

Fill a path on the current figure. See `TikzFigure.fill`.

<a id="tikzfigure.pyplot.clip"></a>

##### clip

```python
def clip(*args: Any, **kwargs: Any) -> TikzPath
```

Clip against a path on the current figure. See `TikzFigure.clip`.

<a id="tikzfigure.pyplot.path"></a>

##### path

```python
def path(*args: Any, **kwargs: Any) -> TikzPath
```

Add a plain path to the current figure. See `TikzFigure.path`.

<a id="tikzfigure.pyplot.add"></a>

##### add

```python
def add(*args: Any, **kwargs: Any) -> None
```

Add existing items to the current figure. See `TikzFigure.add`.

<a id="tikzfigure.pyplot.add_copy"></a>

##### add\_copy

```python
def add_copy(*args: Any, **kwargs: Any) -> Node
```

Add a modified copy of a node. See `TikzFigure.add_copy`.

<a id="tikzfigure.pyplot.add_node"></a>

##### add\_node

```python
def add_node(*args: Any, **kwargs: Any) -> Node
```

Add a node to the current figure. See `TikzFigure.add_node`.

<a id="tikzfigure.pyplot.add_coordinate"></a>

##### add\_coordinate

```python
def add_coordinate(*args: Any, **kwargs: Any) -> Coordinate
```

Add a coordinate to the current figure. See `TikzFigure.add_coordinate`.

<a id="tikzfigure.pyplot.midpoint"></a>

##### midpoint

```python
def midpoint(*args: Any, **kwargs: Any) -> Node
```

Add a midpoint node to the current figure. See `TikzFigure.midpoint`.

<a id="tikzfigure.pyplot.arc"></a>

##### arc

```python
def arc(*args: Any, **kwargs: Any) -> Arc
```

Add an arc to the current figure. See `TikzFigure.arc`.

<a id="tikzfigure.pyplot.circle"></a>

##### circle

```python
def circle(*args: Any, **kwargs: Any) -> Circle
```

Add a circle to the current figure. See `TikzFigure.circle`.

<a id="tikzfigure.pyplot.ellipse"></a>

##### ellipse

```python
def ellipse(*args: Any, **kwargs: Any) -> Ellipse
```

Add an ellipse to the current figure. See `TikzFigure.ellipse`.

<a id="tikzfigure.pyplot.grid"></a>

##### grid

```python
def grid(*args: Any, **kwargs: Any) -> Grid
```

Add a grid to the current figure. See `TikzFigure.grid`.

<a id="tikzfigure.pyplot.line"></a>

##### line

```python
def line(*args: Any, **kwargs: Any) -> Line
```

Add a line to the current figure. See `TikzFigure.line`.

<a id="tikzfigure.pyplot.parabola"></a>

##### parabola

```python
def parabola(*args: Any, **kwargs: Any) -> Parabola
```

Add a parabola to the current figure. See `TikzFigure.parabola`.

<a id="tikzfigure.pyplot.polygon"></a>

##### polygon

```python
def polygon(*args: Any, **kwargs: Any) -> Polygon
```

Add a polygon to the current figure. See `TikzFigure.polygon`.

<a id="tikzfigure.pyplot.rectangle"></a>

##### rectangle

```python
def rectangle(*args: Any, **kwargs: Any) -> Rectangle
```

Add a rectangle to the current figure. See `TikzFigure.rectangle`.

<a id="tikzfigure.pyplot.square"></a>

##### square

```python
def square(*args: Any, **kwargs: Any) -> Square
```

Add a square to the current figure. See `TikzFigure.square`.

<a id="tikzfigure.pyplot.triangle"></a>

##### triangle

```python
def triangle(*args: Any, **kwargs: Any) -> Triangle
```

Add a triangle to the current figure. See `TikzFigure.triangle`.

<a id="tikzfigure.pyplot.add_plot"></a>

##### add\_plot

```python
def add_plot(*args: Any, **kwargs: Any) -> TikzPlot
```

Add a plot to the current figure. See `TikzFigure.add_plot`.

<a id="tikzfigure.pyplot.add_parametric_grid"></a>

##### add\_parametric\_grid

```python
def add_parametric_grid(*args: Any, **kwargs: Any) -> tuple[Loop, Loop]
```

Add a parametric grid. See `TikzFigure.add_parametric_grid`.

<a id="tikzfigure.pyplot.axis2d"></a>

##### axis2d

```python
def axis2d(*args: Any, **kwargs: Any) -> Axis2D
```

Add a pgfplots axis to the current figure. See `TikzFigure.axis2d`.

<a id="tikzfigure.pyplot.plot3d"></a>

##### plot3d

```python
def plot3d(*args: Any, **kwargs: Any) -> Plot3D
```

Add a 3-D plot to the current figure. See `TikzFigure.plot3d`.

<a id="tikzfigure.pyplot.add_gantt_chart"></a>

##### add\_gantt\_chart

```python
def add_gantt_chart(*args: Any, **kwargs: Any) -> GanttChart
```

Add a Gantt chart to the current figure. See `TikzFigure.add_gantt_chart`.

<a id="tikzfigure.pyplot.add_loop"></a>

##### add\_loop

```python
def add_loop(*args: Any, **kwargs: Any) -> Loop
```

Add a ``\foreach`` loop to the current figure. See `TikzFigure.add_loop`.

<a id="tikzfigure.pyplot.add_scope"></a>

##### add\_scope

```python
def add_scope(*args: Any, **kwargs: Any) -> Scope
```

Add a scope to the current figure. See `TikzFigure.add_scope`.

<a id="tikzfigure.pyplot.add_matrix"></a>

##### add\_matrix

```python
def add_matrix(*args: Any, **kwargs: Any) -> Matrix
```

Add a matrix to the current figure. See `TikzFigure.add_matrix`.

<a id="tikzfigure.pyplot.add_fit"></a>

##### add\_fit

```python
def add_fit(*args: Any, **kwargs: Any) -> Fit
```

Add a fit node to the current figure. See `TikzFigure.add_fit`.

<a id="tikzfigure.pyplot.add_spy"></a>

##### add\_spy

```python
def add_spy(*args: Any, **kwargs: Any) -> Spy
```

Add a spy to the current figure. See `TikzFigure.add_spy`.

<a id="tikzfigure.pyplot.add_spy_scope"></a>

##### add\_spy\_scope

```python
def add_spy_scope(*args: Any, **kwargs: Any) -> Scope
```

Add a spy scope to the current figure. See `TikzFigure.add_spy_scope`.

<a id="tikzfigure.pyplot.configure_spy_scope"></a>

##### configure\_spy\_scope

```python
def configure_spy_scope(*args: Any, **kwargs: Any) -> None
```

Configure the figure-level spy scope. See `TikzFigure.configure_spy_scope`.

<a id="tikzfigure.pyplot.add_raw"></a>

##### add\_raw

```python
def add_raw(*args: Any, **kwargs: Any) -> RawTikz
```

Add raw TikZ code to the current figure. See `TikzFigure.add_raw`.

<a id="tikzfigure.pyplot.usetikzlibrary"></a>

##### usetikzlibrary

```python
def usetikzlibrary(*args: Any, **kwargs: Any) -> None
```

Load TikZ libraries in the current figure. See `TikzFigure.usetikzlibrary`.

<a id="tikzfigure.pyplot.add_package"></a>

##### add\_package

```python
def add_package(*args: Any, **kwargs: Any) -> None
```

Add a LaTeX package to the current figure. See `TikzFigure.add_package`.

<a id="tikzfigure.pyplot.add_style"></a>

##### add\_style

```python
def add_style(*args: Any, **kwargs: Any) -> TikzStyle
```

Define a named style on the current figure. See `TikzFigure.add_style`.

<a id="tikzfigure.pyplot.colorlet"></a>

##### colorlet

```python
def colorlet(*args: Any, **kwargs: Any) -> Color
```

Define a color on the current figure. See `TikzFigure.colorlet`.

<a id="tikzfigure.pyplot.add_variable"></a>

##### add\_variable

```python
def add_variable(*args: Any, **kwargs: Any) -> Variable
```

Define a variable on the current figure. See `TikzFigure.add_variable`.

<a id="tikzfigure.pyplot.declare_function"></a>

##### declare\_function

```python
def declare_function(*args: Any, **kwargs: Any) -> DeclaredFunction
```

Declare a function on the current figure. See `TikzFigure.declare_function`.

<a id="tikzfigure.pyplot.generate_tikz"></a>

##### generate\_tikz

```python
def generate_tikz(*args: Any, **kwargs: Any) -> str
```

Return the TikZ code of the current figure. See `TikzFigure.generate_tikz`.

<a id="tikzfigure.pyplot.generate_standalone"></a>

##### generate\_standalone

```python
def generate_standalone(*args: Any, **kwargs: Any) -> str
```

Return a standalone document. See `TikzFigure.generate_standalone`.

<a id="tikzfigure.pyplot.files"></a>

##### files

```python
def files() -> dict[str, bytes]
```

The image files of the current figure. See `TikzFigure.files`.

<a id="tikzfigure.pyplot.compile_pdf"></a>

##### compile\_pdf

```python
def compile_pdf(*args: Any, **kwargs: Any) -> None
```

Compile the current figure to PDF. See `TikzFigure.compile_pdf`.

<a id="tikzfigure.pyplot.savefig"></a>

##### savefig

```python
def savefig(*args: Any, **kwargs: Any) -> None
```

Save the current figure to a file. See `TikzFigure.savefig`.

<a id="tikzfigure.pyplot.show"></a>

##### show

```python
def show(*args: Any, **kwargs: Any) -> None
```

Display the current figure. See `TikzFigure.show`.

<a id="tikzfigure.pyplot.add_subfigure"></a>

##### add\_subfigure

```python
def add_subfigure(*args: Any, **kwargs: Any) -> TikzFigure
```

Add a subfigure to the current figure. See `TikzFigure.add_subfigure`.

<a id="tikzfigure.pyplot.subfigure_axis"></a>

##### subfigure\_axis

```python
def subfigure_axis(*args: Any, **kwargs: Any) -> Axis2D
```

Add a subfigure axis. See `TikzFigure.subfigure_axis`.

## Coordinates and vectors

```python
from tikzfigure import TikzCoordinate, TikzVector
```

<a id="tikzfigure.core.coordinate.Coordinate"></a>

### Coordinate

```python
class Coordinate(TikzObject)
```

A named TikZ coordinate declared with ``\coordinate``.

Unlike a `tikzfigure.core.node.Node`, a coordinate has no
visible output — it simply registers a named point in the figure that
can be referenced in paths, calc expressions, or anywhere TikZ accepts a
node label.

Common uses:

* Defining fixed reference points::

fig.add_coordinate("origin", x=0, y=0)
fig.draw(["origin", "A"])

* Placing a point at the midpoint between two nodes (requires the
``calc`` TikZ library)::

fig.add_coordinate("mid", at="$(A)!0.5!(B)$")
fig.draw(["A", "mid", "B"])

* Naming a point at a node anchor::

fig.add_coordinate("atip", at="A.north")

**Attributes**:

- `label` - The TikZ name for this coordinate.
- `x` - X value when using absolute positioning, or ``None``.
- `y` - Y value when using absolute positioning, or ``None``.
- `at` - Raw TikZ coordinate expression when using expression
  positioning, or ``None``.

<a id="tikzfigure.core.coordinate.Coordinate.__init__"></a>

##### Coordinate.\_\_init\_\_

```python
def __init__(label: str,
             x: (CoordinateValue
                 | CoordinateTuple2D
                 | CoordinateTuple3D
                 | TikzCoordinate
                 | None) = None,
             y: CoordinateValue | None = None,
             z: CoordinateValue | None = None,
             at: str | None = None,
             layer: int = 0,
             comment: str | None = None) -> None
```

Initialize a Coordinate.

Provide either explicit coordinates, or a raw TikZ coordinate
expression via ``at``.

**Arguments**:

- `label` - TikZ name for this coordinate, used when referencing it
  in path lists and other commands.
- `x` - X-coordinate value, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
  `TikzCoordinate`. Must be provided together with ``y``
  when passed as a scalar. Mutually exclusive with ``at``.
- `y` - Y-coordinate value when passing explicit scalar coordinates.
  Mutually exclusive with ``at``.
- `z` - Z-coordinate value when passing explicit scalar coordinates.
  Mutually exclusive with ``at``.
- `at` - Raw TikZ coordinate expression. Examples:

  * ``"$(A)!0.5!(B)$"`` — midpoint via ``calc`` library
  * ``"A.north"`` — at a node anchor
  * ``"30:2cm"`` — polar coordinates

  If the string does not begin with ``(``, parentheses are
  added automatically. Mutually exclusive with ``x``/``y``.
- `layer` - Layer index this coordinate belongs to. Defaults to ``0``.
- `comment` - Optional comment prepended in the TikZ output.


**Raises**:

- `ValueError` - If both ``at`` and explicit coordinates are supplied,
  or if neither is supplied.

<a id="tikzfigure.core.coordinate.Coordinate.x"></a>

##### Coordinate.x

```python
@property
def x() -> CoordinateValue | None
```

X-coordinate value, or ``None`` if using an ``at`` expression.

<a id="tikzfigure.core.coordinate.Coordinate.y"></a>

##### Coordinate.y

```python
@property
def y() -> CoordinateValue | None
```

Y-coordinate value, or ``None`` if using an ``at`` expression.

<a id="tikzfigure.core.coordinate.Coordinate.z"></a>

##### Coordinate.z

```python
@property
def z() -> CoordinateValue | None
```

Z-coordinate value, or ``None`` for 2-D / ``at`` coordinates.

<a id="tikzfigure.core.coordinate.Coordinate.to"></a>

##### Coordinate.to

```python
def to(target: Node | Coordinate,
       options: OptionInput | None = None,
       **kwargs: Any) -> NodePathBuilder
```

Create a path builder for a segment from this coordinate to ``target``.

The returned builder always starts with ``self`` and records the segment
options for the edge from ``self`` to ``target``. Chain additional
``.to(...)`` or ``.arc(...)`` calls on the builder to add more path
segments. Only `tikzfigure.core.node.Node` and
`Coordinate` targets are accepted by ``.to(...)``.

<a id="tikzfigure.core.coordinate.Coordinate.ndim"></a>

##### Coordinate.ndim

```python
@property
def ndim() -> int
```

Number of spatial dimensions (``2`` or ``3``).

<a id="tikzfigure.core.coordinate.Coordinate.at"></a>

##### Coordinate.at

```python
@property
def at() -> str | None
```

Raw TikZ coordinate expression, or ``None`` if using x/y.

<a id="tikzfigure.core.coordinate.Coordinate.to_tikz"></a>

##### Coordinate.to\_tikz

```python
def to_tikz(output_unit: str | None = None) -> str
```

Generate the TikZ ``\coordinate`` declaration.

**Returns**:

  A ``\coordinate (label) at (...);`` string ending with a
  newline, optionally preceded by a comment line.

<a id="tikzfigure.core.coordinate.Coordinate.to_dict"></a>

##### Coordinate.to\_dict

```python
def to_dict() -> dict[str, Any]
```

Serialize this coordinate to a plain dictionary.

**Returns**:

  A dictionary with ``type``, ``label``, ``x``, ``y``, ``at``,
  ``layer``, and ``comment`` keys.

<a id="tikzfigure.core.coordinate.Coordinate.from_dict"></a>

##### Coordinate.from\_dict

```python
@classmethod
def from_dict(cls, d: dict[str, Any]) -> Coordinate
```

Reconstruct a Coordinate from a dictionary.

**Arguments**:

- `d` - Dictionary as produced by `to_dict`.


**Returns**:

  A new `Coordinate` instance.

<a id="tikzfigure.core.coordinate.TikzCoordinate"></a>

### TikzCoordinate

```python
class TikzCoordinate(TikzObject)
```

A bare coordinate point (no drawn node) in a TikZ figure.

Used to define path waypoints without producing visible nodes.

**Attributes**:

- `x` - X-coordinate value (numeric or PGF expression string).
- `y` - Y-coordinate value (numeric or PGF expression string).
- `z` - Z-coordinate value, or ``None`` for 2-D figures.
- `ndim` - Number of dimensions (``2`` or ``3``).
- `coordinate` - Coordinate as a tuple ready for TikZ output.

<a id="tikzfigure.core.coordinate.TikzCoordinate.__init__"></a>

##### TikzCoordinate.\_\_init\_\_

```python
def __init__(x: CoordinateValue | CoordinateTuple2D | CoordinateTuple3D
             | TikzCoordinate,
             y: CoordinateValue | None = None,
             z: CoordinateValue | None = None,
             layer: int = 0) -> None
```

Initialize a TikzCoordinate.

**Arguments**:

- `x` - X-coordinate value, a ``(x, y)`` / ``(x, y, z)`` tuple, or an
  existing `TikzCoordinate`.
- `y` - Y-coordinate value when passing explicit scalar coordinates.
- `z` - Z-coordinate value when passing explicit scalar coordinates.
  When provided, the coordinate is treated as 3-D. Defaults to
  ``None`` (2-D).
- `layer` - Layer index this coordinate belongs to. Defaults to ``0``.

<a id="tikzfigure.core.coordinate.TikzCoordinate.x"></a>

##### TikzCoordinate.x

```python
@property
def x() -> CoordinateValue
```

X-coordinate value (numeric or PGF expression string).

<a id="tikzfigure.core.coordinate.TikzCoordinate.y"></a>

##### TikzCoordinate.y

```python
@property
def y() -> CoordinateValue
```

Y-coordinate value (numeric or PGF expression string).

<a id="tikzfigure.core.coordinate.TikzCoordinate.z"></a>

##### TikzCoordinate.z

```python
@property
def z() -> CoordinateValue | None
```

Z-coordinate value (numeric or PGF expression string), or ``None`` for 2-D coordinates.

<a id="tikzfigure.core.coordinate.TikzCoordinate.coordinate"></a>

##### TikzCoordinate.coordinate

```python
@property
def coordinate() -> tuple[CoordinateValue, ...]
```

Coordinate as a tuple, either ``(x, y)`` or ``(x, y, z)``.

<a id="tikzfigure.core.coordinate.TikzCoordinate.ndim"></a>

##### TikzCoordinate.ndim

```python
@property
def ndim() -> int
```

Number of spatial dimensions (``2`` or ``3``).

<a id="tikzfigure.core.coordinate.TikzCoordinate.to_vector"></a>

##### TikzCoordinate.to\_vector

```python
def to_vector() -> TikzVector
```

Interpret this point as a vector from the origin.

<a id="tikzfigure.core.coordinate.TikzCoordinate.vector_to"></a>

##### TikzCoordinate.vector\_to

```python
def vector_to(other: TikzCoordinate) -> TikzVector
```

Return the vector from this point to another point.

<a id="tikzfigure.core.coordinate.TikzCoordinate.distance_to"></a>

##### TikzCoordinate.distance\_to

```python
def distance_to(other: TikzCoordinate) -> float
```

Return the Euclidean distance to another point.

<a id="tikzfigure.core.coordinate.TikzCoordinate.translate"></a>

##### TikzCoordinate.translate

```python
def translate(vector: TikzVector) -> TikzCoordinate
```

Return the translated point.

<a id="tikzfigure.core.coordinate.TikzCoordinate.to_tikz"></a>

##### TikzCoordinate.to\_tikz

```python
def to_tikz(output_unit: str | None = None) -> str
```

Render this coordinate as a TikZ position expression.

<a id="tikzfigure.core.coordinate.TikzCoordinate.to_dict"></a>

##### TikzCoordinate.to\_dict

```python
def to_dict() -> dict[str, Any]
```

Serialize this coordinate to a plain dictionary.

**Returns**:

  A dictionary with ``type``, ``x``, ``y``, ``z``, and ``layer``
  keys.

<a id="tikzfigure.core.coordinate.TikzCoordinate.from_dict"></a>

##### TikzCoordinate.from\_dict

```python
@classmethod
def from_dict(cls, d: dict[str, Any]) -> TikzCoordinate
```

Reconstruct a TikzCoordinate from a dictionary.

**Arguments**:

- `d` - Dictionary as produced by `to_dict`.


**Returns**:

  A new `TikzCoordinate` instance.

<a id="tikzfigure.core.coordinate.TikzVector"></a>

### TikzVector

```python
class TikzVector(TikzCoordinate)
```

A geometric vector used for linear algebra operations.

<a id="tikzfigure.core.coordinate.TikzVector.dot"></a>

##### TikzVector.dot

```python
def dot(other: TikzVector) -> float
```

Return the dot product with another vector.

<a id="tikzfigure.core.coordinate.TikzVector.cross"></a>

##### TikzVector.cross

```python
def cross(other: TikzVector) -> TikzVector
```

Return the cross product with another vector.

<a id="tikzfigure.core.coordinate.TikzVector.norm"></a>

##### TikzVector.norm

```python
def norm() -> float
```

Return the Euclidean norm.

<a id="tikzfigure.core.coordinate.TikzVector.magnitude"></a>

##### TikzVector.magnitude

```python
def magnitude() -> float
```

Return the Euclidean norm.

<a id="tikzfigure.core.coordinate.TikzVector.to_dict"></a>

##### TikzVector.to\_dict

```python
def to_dict() -> dict[str, Any]
```

Serialize this vector to a plain dictionary.

<a id="tikzfigure.core.coordinate.TikzVector.from_dict"></a>

##### TikzVector.from\_dict

```python
@classmethod
def from_dict(cls, d: dict[str, Any]) -> TikzVector
```

Reconstruct a TikzVector from a dictionary.

## Colors

```python
from tikzfigure import colors
```

Generated by scripts/generate_colors.py. Do not edit by hand.

<a id="tikzfigure.colors.TikzColor"></a>

### TikzColor

```python
class TikzColor()
```

An xcolor-compatible TikZ color expression.

<a id="tikzfigure.colors.TikzColor.mix"></a>

##### TikzColor.mix

```python
def mix(other: str | TikzColor | None = None,
        percent: float = 0.5) -> TikzColor
```

Build an xcolor mix like ``red!50`` or ``red!50!blue``.

<a id="tikzfigure.colors.TikzColor.complement"></a>

##### TikzColor.complement

```python
def complement() -> TikzColor
```

Return the xcolor complementary-expression form.

<a id="tikzfigure.colors.TikzColor.to_tikz"></a>

##### TikzColor.to\_tikz

```python
def to_tikz() -> str
```

Return the raw xcolor expression.

## Units

```python
from tikzfigure import units
```

<a id="tikzfigure.units.TikzDimension"></a>

### TikzDimension

```python
class TikzDimension()
```

A TikZ dimension value with a unit, e.g. 2.5cm or 10pt.

<a id="tikzfigure.units.TikzDimension.to"></a>

##### TikzDimension.to

```python
def to(target_unit: str) -> TikzDimension
```

Convert to another TikZ unit.

## Shapes

```python
from tikzfigure import shapes
```

<a id="tikzfigure.shapes.TikzShape"></a>

### TikzShape

```python
class TikzShape(TikzToken)
```

A reusable TikZ node-shape specification.

<a id="tikzfigure.shapes.shape"></a>

##### shape

```python
def shape(shape_spec: str) -> TikzShape
```

Create a custom raw TikZ shape specification.

## Styles

```python
from tikzfigure import styles
```

<a id="tikzfigure.styles.TikzStyle"></a>

### TikzStyle

```python
class TikzStyle(TikzToken)
```

A reusable TikZ style token or option fragment.

<a id="tikzfigure.styles.style"></a>

##### style

```python
def style(style_spec: str) -> TikzStyle
```

Create a custom raw TikZ style token.

<a id="tikzfigure.styles.line_width"></a>

##### line\_width

```python
def line_width(value: str | float | TikzDimension) -> TikzStyle
```

Build a ``line width=...`` option fragment.

<a id="tikzfigure.styles.rounded_corners"></a>

##### rounded\_corners

```python
def rounded_corners(radius: str | float | TikzDimension) -> TikzStyle
```

Build a ``rounded corners=...`` option fragment.

<a id="tikzfigure.styles.dash_pattern"></a>

##### dash\_pattern

```python
def dash_pattern(on: str | float | TikzDimension,
                 off: str | float | TikzDimension) -> TikzStyle
```

Build a simple ``dash pattern=on ... off ...`` option fragment.

<a id="tikzfigure.styles.bend_left"></a>

##### bend\_left

```python
def bend_left(angle: float | None = None) -> TikzStyle
```

Build a ``bend left`` option fragment.

<a id="tikzfigure.styles.bend_right"></a>

##### bend\_right

```python
def bend_right(angle: float | None = None) -> TikzStyle
```

Build a ``bend right`` option fragment.

## Arrows

```python
from tikzfigure import arrows
```

<a id="tikzfigure.arrows.TikzArrow"></a>

### TikzArrow

```python
class TikzArrow(TikzToken)
```

A reusable TikZ arrow-tip specification.

<a id="tikzfigure.arrows.tip"></a>

##### tip

```python
def tip(arrow_spec: str) -> TikzArrow
```

Create a custom raw TikZ arrow specification.

## Patterns

```python
from tikzfigure import patterns
```

<a id="tikzfigure.patterns.TikzPattern"></a>

### TikzPattern

```python
class TikzPattern(TikzToken)
```

A reusable TikZ fill-pattern specification.

<a id="tikzfigure.patterns.pattern"></a>

##### pattern

```python
def pattern(pattern_spec: str) -> TikzPattern
```

Create a custom raw TikZ pattern specification.

## Decorations

```python
from tikzfigure import decorations
```

<a id="tikzfigure.decorations.TikzDecoration"></a>

### TikzDecoration

```python
class TikzDecoration(TikzToken)
```

A reusable TikZ path-decoration specification.

<a id="tikzfigure.decorations.decoration"></a>

##### decoration

```python
def decoration(decoration_spec: str) -> TikzDecoration
```

Create a custom raw TikZ decoration specification.

## Marks

```python
from tikzfigure import marks
```

<a id="tikzfigure.marks.TikzMark"></a>

### TikzMark

```python
class TikzMark(TikzToken)
```

A reusable pgfplots plot-mark specification.

<a id="tikzfigure.marks.mark"></a>

##### mark

```python
def mark(mark_spec: str) -> TikzMark
```

Create a custom raw pgfplots mark specification.

## Options

```python
from tikzfigure import options
```

<a id="tikzfigure.options.normalize_options"></a>

##### normalize\_options

```python
def normalize_options(options: OptionInput | None) -> list[OptionValue]
```

Normalize one-or-many option inputs to a plain list.
