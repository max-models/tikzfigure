from tikzfigure.core.coordinate import TikzCoordinate, TikzVector
from tikzfigure.core.figure import TikzFigure
from tikzfigure.core.node import Node

__all__ = ["TikzFigure", "Node", "TikzCoordinate", "TikzVector"]


def load_ipython_extension(ipython):
    """Load the IPython magic extension."""
    from tikzfigure.core.ipython import load_ipython_extension as _load

    _load(ipython)


def unload_ipython_extension(ipython):
    """Unload the IPython magic extension."""
    from tikzfigure.core.ipython import unload_ipython_extension as _unload

    _unload(ipython)
