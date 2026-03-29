from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath


class Loop(TikzObject):
    def __init__(self, variable, values, layer=0, comment: str | None = None):
        self._variable = variable
        self._values = list(values)
        self._items = []

        super().__init__(layer=layer, comment=comment)

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
        path = TikzPath(nodes, comment=comment, layer=self.layer, **kwargs)
        self._items.append(path)
        return path

    def add_loop(self, variable, values, comment: str | None = None):
        """
        Add a nested loop inside this loop.
        """
        loop = Loop(variable, values, layer=self.layer, comment=comment)
        self._items.append(loop)
        return loop

    def to_tikz(self):
        values_str = ",".join(str(v) for v in self.values)
        tikz_body = "".join([item.to_tikz() for item in self.items])
        loop_str = f"\\foreach \\{self.variable} in {{{values_str}}}{{\n{tikz_body}}}\n"

        loop_str = self.add_comment(loop_str)

        return loop_str

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "type": "Loop",
                "variable": self._variable,
                "values": list(self._values),
                "items": [item.to_dict() for item in self._items],
            }
        )
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Loop":
        loop = cls(
            variable=d["variable"],
            values=d["values"],
            layer=d.get("layer", 0),
            comment=d.get("comment"),
        )
        node_lookup: dict[str, Node] = {}
        for item_data in d.get("items", []):
            item_type = item_data.get("type")
            if item_type == "Node":
                node = Node.from_dict(item_data)
                loop._items.append(node)
                node_lookup[node.label] = node
            elif item_type == "Path":
                loop._items.append(
                    TikzPath.from_dict(item_data, node_lookup=node_lookup)
                )
            elif item_type == "Loop":
                loop._items.append(Loop.from_dict(item_data))
        return loop
