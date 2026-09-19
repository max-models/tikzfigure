"""Module-level drawing API backed by an implicit "current figure".

This mirrors the way :mod:`matplotlib.pyplot` works: instead of creating a
:class:`~tikzfigure.core.figure.TikzFigure` yourself, you call the drawing
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
:func:`gcf`, so see :class:`~tikzfigure.core.figure.TikzFigure` for the
full argument documentation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tikzfigure.core.figure import TikzFigure

if TYPE_CHECKING:
    from tikzfigure.core.arc import Arc
    from tikzfigure.core.axis import Axis2D
    from tikzfigure.core.circle import Circle
    from tikzfigure.core.color import Color
    from tikzfigure.core.coordinate import Coordinate
    from tikzfigure.core.declared_function import DeclaredFunction
    from tikzfigure.core.ellipse import Ellipse
    from tikzfigure.core.fit import Fit
    from tikzfigure.core.gantt import GanttChart
    from tikzfigure.core.grid import Grid
    from tikzfigure.core.line import Line
    from tikzfigure.core.loop import Loop
    from tikzfigure.core.matrix import Matrix
    from tikzfigure.core.node import Node
    from tikzfigure.core.parabola import Parabola
    from tikzfigure.core.path import TikzPath
    from tikzfigure.core.plot import Plot3D, TikzPlot
    from tikzfigure.core.polygon import Polygon, Square, Triangle
    from tikzfigure.core.raw import RawTikz
    from tikzfigure.core.rectangle import Rectangle
    from tikzfigure.core.scope import Scope
    from tikzfigure.core.spy import Spy
    from tikzfigure.core.variable import Variable
    from tikzfigure.styles import TikzStyle

__all__ = [
    "add",
    "add_coordinate",
    "add_copy",
    "add_fit",
    "add_gantt",
    "add_gantt_chart",
    "add_loop",
    "add_matrix",
    "add_node",
    "add_package",
    "add_parametric_grid",
    "add_plot",
    "add_raw",
    "add_scope",
    "add_spy",
    "add_spy_scope",
    "add_style",
    "add_subfigure",
    "add_variable",
    "arc",
    "axis2d",
    "circle",
    "clf",
    "clip",
    "close",
    "colorlet",
    "compile_pdf",
    "coordinate",
    "declare_function",
    "draw",
    "ellipse",
    "figure",
    "fill",
    "filldraw",
    "function",
    "gantt",
    "gantt_chart",
    "gcf",
    "generate_standalone",
    "generate_tikz",
    "grid",
    "line",
    "loop",
    "midpoint",
    "node",
    "parabola",
    "parametric_grid",
    "path",
    "plot",
    "plot3d",
    "polygon",
    "raw",
    "rectangle",
    "savefig",
    "scf",
    "scope",
    "show",
    "spy",
    "spy_scope",
    "square",
    "subfigure",
    "subfigure_axis",
    "triangle",
    "usetikzlibrary",
    "variable",
]

_current_figure: TikzFigure | None = None


# ------------------------------------------------------------- #
# Current-figure management


def gcf() -> TikzFigure:
    """Return the current figure, creating an empty one if needed.

    Returns:
        The :class:`~tikzfigure.core.figure.TikzFigure` that the
        module-level drawing functions operate on.
    """
    global _current_figure
    if _current_figure is None:
        _current_figure = TikzFigure()
    return _current_figure


def scf(fig: TikzFigure) -> TikzFigure:
    """Make *fig* the current figure.

    Args:
        fig: The figure the module-level functions should draw on.

    Returns:
        The figure that was passed in.

    Raises:
        TypeError: If *fig* is not a :class:`TikzFigure`.
    """
    global _current_figure
    if not isinstance(fig, TikzFigure):
        raise TypeError(f"Expected a TikzFigure, got {type(fig).__name__}.")
    _current_figure = fig
    return fig


def figure(*args: Any, **kwargs: Any) -> TikzFigure:
    """Create a new figure, make it current, and return it.

    Accepts the same arguments as :class:`~tikzfigure.core.figure.TikzFigure`.
    """
    return scf(TikzFigure(*args, **kwargs))


def clf(*args: Any, **kwargs: Any) -> TikzFigure:
    """Replace the current figure with a fresh, empty one.

    Accepts the same arguments as :class:`~tikzfigure.core.figure.TikzFigure`.
    """
    return figure(*args, **kwargs)


def close() -> None:
    """Discard the current figure.

    The next call to :func:`gcf` (or to any drawing function) creates a
    new empty figure.
    """
    global _current_figure
    _current_figure = None


# ------------------------------------------------------------- #
# Paths


def draw(*args: Any, **kwargs: Any) -> TikzPath:
    """Draw a path on the current figure. See :meth:`TikzFigure.draw`."""
    return gcf().draw(*args, **kwargs)


def filldraw(*args: Any, **kwargs: Any) -> TikzPath:
    """Fill and draw a path on the current figure. See :meth:`TikzFigure.filldraw`."""
    return gcf().filldraw(*args, **kwargs)


def fill(*args: Any, **kwargs: Any) -> TikzPath:
    """Fill a path on the current figure. See :meth:`TikzFigure.fill`."""
    return gcf().fill(*args, **kwargs)


def clip(*args: Any, **kwargs: Any) -> TikzPath:
    """Clip against a path on the current figure. See :meth:`TikzFigure.clip`."""
    return gcf().clip(*args, **kwargs)


def path(*args: Any, **kwargs: Any) -> TikzPath:
    """Add a plain path to the current figure. See :meth:`TikzFigure.path`."""
    return gcf().path(*args, **kwargs)


# ------------------------------------------------------------- #
# Nodes, coordinates, and generic items


def add(*args: Any, **kwargs: Any) -> None:
    """Add existing items to the current figure. See :meth:`TikzFigure.add`."""
    return gcf().add(*args, **kwargs)


def add_copy(*args: Any, **kwargs: Any) -> Node:
    """Add a modified copy of a node. See :meth:`TikzFigure.add_copy`."""
    return gcf().add_copy(*args, **kwargs)


def add_node(*args: Any, **kwargs: Any) -> Node:
    """Add a node to the current figure. See :meth:`TikzFigure.add_node`."""
    return gcf().add_node(*args, **kwargs)


def add_coordinate(*args: Any, **kwargs: Any) -> Coordinate:
    """Add a coordinate to the current figure. See :meth:`TikzFigure.add_coordinate`."""
    return gcf().add_coordinate(*args, **kwargs)


def midpoint(*args: Any, **kwargs: Any) -> Node:
    """Add a midpoint node to the current figure. See :meth:`TikzFigure.midpoint`."""
    return gcf().midpoint(*args, **kwargs)


# ------------------------------------------------------------- #
# Shapes


def arc(*args: Any, **kwargs: Any) -> Arc:
    """Add an arc to the current figure. See :meth:`TikzFigure.arc`."""
    return gcf().arc(*args, **kwargs)


def circle(*args: Any, **kwargs: Any) -> Circle:
    """Add a circle to the current figure. See :meth:`TikzFigure.circle`."""
    return gcf().circle(*args, **kwargs)


def ellipse(*args: Any, **kwargs: Any) -> Ellipse:
    """Add an ellipse to the current figure. See :meth:`TikzFigure.ellipse`."""
    return gcf().ellipse(*args, **kwargs)


def grid(*args: Any, **kwargs: Any) -> Grid:
    """Add a grid to the current figure. See :meth:`TikzFigure.grid`."""
    return gcf().grid(*args, **kwargs)


def line(*args: Any, **kwargs: Any) -> Line:
    """Add a line to the current figure. See :meth:`TikzFigure.line`."""
    return gcf().line(*args, **kwargs)


def parabola(*args: Any, **kwargs: Any) -> Parabola:
    """Add a parabola to the current figure. See :meth:`TikzFigure.parabola`."""
    return gcf().parabola(*args, **kwargs)


def polygon(*args: Any, **kwargs: Any) -> Polygon:
    """Add a polygon to the current figure. See :meth:`TikzFigure.polygon`."""
    return gcf().polygon(*args, **kwargs)


def rectangle(*args: Any, **kwargs: Any) -> Rectangle:
    """Add a rectangle to the current figure. See :meth:`TikzFigure.rectangle`."""
    return gcf().rectangle(*args, **kwargs)


def square(*args: Any, **kwargs: Any) -> Square:
    """Add a square to the current figure. See :meth:`TikzFigure.square`."""
    return gcf().square(*args, **kwargs)


def triangle(*args: Any, **kwargs: Any) -> Triangle:
    """Add a triangle to the current figure. See :meth:`TikzFigure.triangle`."""
    return gcf().triangle(*args, **kwargs)


# ------------------------------------------------------------- #
# Plots


def add_plot(*args: Any, **kwargs: Any) -> TikzPlot:
    """Add a plot to the current figure. See :meth:`TikzFigure.add_plot`."""
    return gcf().add_plot(*args, **kwargs)


def add_parametric_grid(*args: Any, **kwargs: Any) -> tuple[Loop, Loop]:
    """Add a parametric grid. See :meth:`TikzFigure.add_parametric_grid`."""
    return gcf().add_parametric_grid(*args, **kwargs)


def axis2d(*args: Any, **kwargs: Any) -> Axis2D:
    """Add a pgfplots axis to the current figure. See :meth:`TikzFigure.axis2d`."""
    return gcf().axis2d(*args, **kwargs)


def plot3d(*args: Any, **kwargs: Any) -> Plot3D:
    """Add a 3-D plot to the current figure. See :meth:`TikzFigure.plot3d`."""
    return gcf().plot3d(*args, **kwargs)


def add_gantt_chart(*args: Any, **kwargs: Any) -> GanttChart:
    """Add a Gantt chart to the current figure. See :meth:`TikzFigure.add_gantt_chart`."""
    return gcf().add_gantt_chart(*args, **kwargs)


# ------------------------------------------------------------- #
# Containers and libraries


def add_loop(*args: Any, **kwargs: Any) -> Loop:
    """Add a ``\\foreach`` loop to the current figure. See :meth:`TikzFigure.add_loop`."""
    return gcf().add_loop(*args, **kwargs)


def add_scope(*args: Any, **kwargs: Any) -> Scope:
    """Add a scope to the current figure. See :meth:`TikzFigure.add_scope`."""
    return gcf().add_scope(*args, **kwargs)


def add_matrix(*args: Any, **kwargs: Any) -> Matrix:
    """Add a matrix to the current figure. See :meth:`TikzFigure.add_matrix`."""
    return gcf().add_matrix(*args, **kwargs)


def add_fit(*args: Any, **kwargs: Any) -> Fit:
    """Add a fit node to the current figure. See :meth:`TikzFigure.add_fit`."""
    return gcf().add_fit(*args, **kwargs)


def add_spy(*args: Any, **kwargs: Any) -> Spy:
    """Add a spy to the current figure. See :meth:`TikzFigure.add_spy`."""
    return gcf().add_spy(*args, **kwargs)


def add_spy_scope(*args: Any, **kwargs: Any) -> Scope:
    """Add a spy scope to the current figure. See :meth:`TikzFigure.add_spy_scope`."""
    return gcf().add_spy_scope(*args, **kwargs)


def add_raw(*args: Any, **kwargs: Any) -> RawTikz:
    """Add raw TikZ code to the current figure. See :meth:`TikzFigure.add_raw`."""
    return gcf().add_raw(*args, **kwargs)


def usetikzlibrary(*args: Any, **kwargs: Any) -> None:
    """Load TikZ libraries in the current figure. See :meth:`TikzFigure.usetikzlibrary`."""
    return gcf().usetikzlibrary(*args, **kwargs)


def add_package(*args: Any, **kwargs: Any) -> None:
    """Add a LaTeX package to the current figure. See :meth:`TikzFigure.add_package`."""
    return gcf().add_package(*args, **kwargs)


# ------------------------------------------------------------- #
# Styles, colors, variables, functions


def add_style(*args: Any, **kwargs: Any) -> TikzStyle:
    """Define a named style on the current figure. See :meth:`TikzFigure.add_style`."""
    return gcf().add_style(*args, **kwargs)


def colorlet(*args: Any, **kwargs: Any) -> Color:
    """Define a color on the current figure. See :meth:`TikzFigure.colorlet`."""
    return gcf().colorlet(*args, **kwargs)


def add_variable(*args: Any, **kwargs: Any) -> Variable:
    """Define a variable on the current figure. See :meth:`TikzFigure.add_variable`."""
    return gcf().add_variable(*args, **kwargs)


def declare_function(*args: Any, **kwargs: Any) -> DeclaredFunction:
    """Declare a function on the current figure. See :meth:`TikzFigure.declare_function`."""
    return gcf().declare_function(*args, **kwargs)


# ------------------------------------------------------------- #
# Output


def generate_tikz(*args: Any, **kwargs: Any) -> str:
    """Return the TikZ code of the current figure. See :meth:`TikzFigure.generate_tikz`."""
    return gcf().generate_tikz(*args, **kwargs)


def generate_standalone(*args: Any, **kwargs: Any) -> str:
    """Return a standalone document. See :meth:`TikzFigure.generate_standalone`."""
    return gcf().generate_standalone(*args, **kwargs)


def compile_pdf(*args: Any, **kwargs: Any) -> None:
    """Compile the current figure to PDF. See :meth:`TikzFigure.compile_pdf`."""
    return gcf().compile_pdf(*args, **kwargs)


def savefig(*args: Any, **kwargs: Any) -> None:
    """Save the current figure to a file. See :meth:`TikzFigure.savefig`."""
    return gcf().savefig(*args, **kwargs)


def show(*args: Any, **kwargs: Any) -> None:
    """Display the current figure. See :meth:`TikzFigure.show`."""
    return gcf().show(*args, **kwargs)


# ------------------------------------------------------------- #
# Subfigures


def add_subfigure(*args: Any, **kwargs: Any) -> TikzFigure:
    """Add a subfigure to the current figure. See :meth:`TikzFigure.add_subfigure`."""
    return gcf().add_subfigure(*args, **kwargs)


def subfigure_axis(*args: Any, **kwargs: Any) -> Axis2D:
    """Add a subfigure axis. See :meth:`TikzFigure.subfigure_axis`."""
    return gcf().subfigure_axis(*args, **kwargs)


# ------------------------------------------------------------- #
# Short public aliases, mirroring the ones on TikzFigure.
coordinate = add_coordinate
function = declare_function
gantt = add_gantt_chart
gantt_chart = add_gantt_chart
add_gantt = add_gantt_chart
loop = add_loop
node = add_node
parametric_grid = add_parametric_grid
plot = add_plot
raw = add_raw
scope = add_scope
spy = add_spy
spy_scope = add_spy_scope
subfigure = add_subfigure
variable = add_variable
