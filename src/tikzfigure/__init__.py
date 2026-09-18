from tikzfigure.core.coordinate import TikzCoordinate, TikzVector
from tikzfigure.core.figure import TikzFigure
from tikzfigure.core.gantt import GanttChart
from tikzfigure.core.node import Node

from . import (
    arrows,
    colors,
    decorations,
    marks,
    options,
    patterns,
    shapes,
    styles,
    units,
)

__all__ = [
    "GanttChart",
    "Node",
    "TikzCoordinate",
    "TikzFigure",
    "TikzVector",
    "arrows",
    "colors",
    "decorations",
    "marks",
    "options",
    "patterns",
    "shapes",
    "styles",
    "units",
]


def load_ipython_extension(ipython):
    """Load the IPython magic extension."""
    from tikzfigure.core.ipython import load_ipython_extension as _load

    _load(ipython)


def unload_ipython_extension(ipython):
    """Unload the IPython magic extension."""
    from tikzfigure.core.ipython import unload_ipython_extension as _unload

    _unload(ipython)
