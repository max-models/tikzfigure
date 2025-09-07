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
        path = Path(nodes, comment=comment, **kwargs)
        self._items.append(path)
        return path

    def add_raw(self, raw_tikz):
        wrapper = TikzWrapper(raw_tikz)
        self._items.append(wrapper)
        return wrapper

    def to_tikz(self):
        values_str = ",".join(str(v) for v in self.values)
        tikz_body = "".join([item.to_tikz() for item in self.items])
        return f"\\foreach \\{self.variable} in {{{values_str}}}{{% start \\foreach\n{tikz_body}}}% end \\foreach\n"


class TikzLoopContext:
    def __init__(self, figure, variable, values, layer=0):
        self._figure = figure
        self._loop = Loop(variable, values, layer=layer)

    @property
    def figure(self):
        return self._figure

    @property
    def loop(self):
        return self._loop

    def __enter__(self):
        return self.loop

    def __exit__(self, exc_type, exc_value, traceback):
        self.figure.add_item(self.loop, self.loop.layer)
