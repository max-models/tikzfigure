from tikzpics.figure import TikzFigure
from tikzpics.node import Node

__all__ = ["TikzFigure", "Node"]


def load_ipython_extension(ipython):
    """Load the IPython magic extension."""
    from tikzpics.ipython import load_ipython_extension as _load

    _load(ipython)


def unload_ipython_extension(ipython):
    """Unload the IPython magic extension."""
    from tikzpics.ipython import unload_ipython_extension as _unload

    _unload(ipython)
