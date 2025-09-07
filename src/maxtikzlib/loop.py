from maxtikzlib.base import TikzObject
from maxtikzlib.node import Node
from maxtikzlib.path import Path
from maxtikzlib.wrapper import TikzWrapper


class Loop(TikzObject):
    def __init__(self, variable, values, layer=0):

        self._variable = variable
        self._values = list(values)
        self._items = []

        super().__init__(layer=layer)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Nothing to do; the parent loop already contains this loop
        pass

    @property
    def variable(self):
        return self._variable

    @property
    def values(self):
        return self._values

    @property
    def items(self):
        return self._items

    def add_node(self, *args, **kwargs):
        node = Node(*args, **kwargs)
        self._items.append(node)
        return node

    def add_path(self, nodes, comment: str | None = None, **kwargs):

        path = Path(nodes, comment=comment, layer=self.layer, **kwargs)
        self._items.append(path)
        return path

    def add_raw(self, raw_tikz):
        wrapper = TikzWrapper(raw_tikz)
        self._items.append(wrapper)
        return wrapper

    def add_loop(self, variable, values):
        """
        Add a nested loop inside this loop.
        Returns the Loop object itself, now a context manager.
        """
        loop = Loop(variable, values, layer=self.layer)
        self._items.append(loop)
        return loop

    def to_tikz(self):
        values_str = ",".join(str(v) for v in self.values)
        tikz_body = "".join([item.to_tikz() for item in self.items])
        return f"\\foreach \\{self.variable} in {{{values_str}}}{{% start \\foreach\n{tikz_body}}}% end \\foreach\n"
