from tikzpics.core.figure import TikzFigure
from tikzpics.core.node import Node

__all__ = ["TikzFigure", "Node"]


def load_ipython_extension(ipython):
    """Load the IPython magic extension."""
    from tikzpics.core.ipython import load_ipython_extension as _load

    _load(ipython)


def unload_ipython_extension(ipython):
    """Unload the IPython magic extension."""
    from tikzpics.core.ipython import unload_ipython_extension as _unload

    _unload(ipython)
