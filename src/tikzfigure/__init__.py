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
    pyplot,
    shapes,
    styles,
    units,
)
from .pyplot import *  # noqa: F403
from .pyplot import __all__ as _pyplot_all

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
    "pyplot",
    "shapes",
    "styles",
    "units",
    *_pyplot_all,
]


def load_ipython_extension(ipython):
    """Load the IPython magic extension."""
    from tikzfigure.core.ipython import load_ipython_extension as _load

    _load(ipython)


def unload_ipython_extension(ipython):
    """Unload the IPython magic extension."""
    from tikzfigure.core.ipython import unload_ipython_extension as _unload

    _unload(ipython)
