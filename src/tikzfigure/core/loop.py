import types
from collections.abc import Sequence
from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import Coordinate
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.core.raw import RawTikz
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value


class Loop(TikzObject):
    """A TikZ ``\\foreach`` loop that repeats items over a sequence of values.

    Loops can be nested and may contain nodes, paths, and other loops.
    They act as context managers so nested content can be added inside a
    ``with`` block.

    Attributes:
        variable: The loop variable name (without the leading backslash).
        values: The sequence of values the loop iterates over.
        items: TikZ objects added inside this loop body.
    """

    def __init__(
        self,
        variable: str,
        values: Sequence[Any],
        layer: int = 0,
        comment: str | None = None,
    ) -> None:
        """Initialize a Loop.

        Args:
            variable: Loop variable name (without the leading backslash),
                e.g. ``"i"`` produces ``\\foreach \\i in {...}``.
            values: Sequence of values to iterate over.
            layer: Layer index this loop belongs to. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
        """
        self._variable: str = variable
        self._values: list[Any] = list(values)
        self._items: list[Any] = []

        super().__init__(layer=layer, comment=comment)

    @property
    def variable(self) -> str:
        """Loop variable name (without the leading backslash)."""
        return self._variable

    @property
    def values(self) -> list[Any]:
        """Sequence of values the loop iterates over."""
        return self._values

    @property
    def items(self) -> list[Any]:
        """TikZ objects contained in this loop body."""
        return self._items

    def add_node(self, *args: Any, **kwargs: Any) -> Node:
        """Add a node inside this loop body.

        Args:
            *args: Positional arguments forwarded to :class:`Node`.
            **kwargs: Keyword arguments forwarded to :class:`Node`.

        Returns:
            The newly created :class:`Node`.
        """
        node = Node(*args, **kwargs)
        self._items.append(node)
        return node

    def add_path(
        self, nodes: list[Any], comment: str | None = None, **kwargs: Any
    ) -> TikzPath:
        """Add a path inside this loop body.

        Args:
            nodes: List of nodes or coordinates to connect.
            comment: Optional comment prepended to the path in TikZ output.
            **kwargs: Additional TikZ path options.

        Returns:
            The newly created :class:`TikzPath`.
        """
        path = TikzPath(nodes, comment=comment, layer=self.layer or 0, **kwargs)
        self._items.append(path)
        return path

    def add_loop(
        self, variable: str, values: Sequence[Any], comment: str | None = None
    ) -> "Loop":
        """Add a nested loop inside this loop body.

        Args:
            variable: Loop variable name for the nested loop.
            values: Sequence of values for the nested loop to iterate over.
            comment: Optional comment prepended to the nested loop.

        Returns:
            The newly created nested :class:`Loop`.
        """
        loop = Loop(variable, values, layer=self.layer or 0, comment=comment)
        self._items.append(loop)
        return loop

    def add_raw(self, tikz_code: str) -> RawTikz:
        raw = RawTikz(tikz_code)
        self._items.append(raw)
        return raw

    def add_scope(
        self,
        comment: str | None = None,
        options: Any = None,
        **kwargs: Any,
    ) -> Any:
        from tikzfigure.core.scope import Scope

        scope = Scope(
            layer=self.layer or 0,
            comment=comment,
            options=options,
            **kwargs,
        )
        self._items.append(scope)
        return scope

    node = add_node
    path = add_path
    loop = add_loop
    raw = add_raw
    scope = add_scope

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ ``\\foreach`` code for this loop.

        Returns:
            A string containing the complete ``\\foreach`` block, including
            all nested items.
        """
        values_str = ",".join(str(v) for v in self.values)
        tikz_body = "".join([item.to_tikz(output_unit) for item in self.items])
        loop_str = f"\\foreach \\{self.variable} in {{{values_str}}}{{\n{tikz_body}}}% {{\\end foreach}}\n"

        loop_str = self.add_comment(loop_str)

        return loop_str

    def to_dict(self) -> dict[str, Any]:
        """Serialize this loop to a plain dictionary.

        Returns:
            A dictionary with ``type``, ``variable``, ``values``, ``items``,
            and all base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Loop",
                "variable": self._variable,
                "values": list(self._values),
                "items": [item.to_dict() for item in self._items],
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized loop data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(
        cls,
        d: dict[str, Any],
        node_lookup: dict[str, Node | Coordinate] | None = None,
    ) -> "Loop":
        """Reconstruct a Loop from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Loop` instance with all nested items restored.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized loop data must deserialize to a dict.")
        loop = cls(
            variable=restored["variable"],
            values=restored["values"],
            layer=restored.get("layer", 0),
            comment=restored.get("comment"),
        )
        local_lookup: dict[str, Node | Coordinate] = dict(node_lookup or {})
        for item_data in restored.get("items", []):
            item_type = item_data.get("type")
            if item_type == "Node":
                node = Node.from_dict(item_data)
                loop._items.append(node)
                if node.label is not None:
                    local_lookup[node.label] = node
            elif item_type == "Coordinate":
                coord = Coordinate.from_dict(item_data)
                loop._items.append(coord)
                if coord.label:
                    local_lookup[coord.label] = coord
            elif item_type == "Path":
                loop._items.append(
                    TikzPath.from_dict(item_data, node_lookup=local_lookup)
                )
            elif item_type == "Loop":
                loop._items.append(Loop.from_dict(item_data, node_lookup=local_lookup))
            elif item_type == "Scope":
                from tikzfigure.core.scope import Scope

                loop._items.append(Scope.from_dict(item_data, node_lookup=local_lookup))
            elif item_type == "RawTikz":
                loop._items.append(RawTikz.from_dict(item_data))
        return loop

    def copy(self, **overrides: Any) -> "Loop":
        clone = type(self).from_dict(self.to_dict())
        remaining = {key: self._copy_value(value) for key, value in overrides.items()}

        if "variable" in remaining:
            clone._variable = remaining.pop("variable")
        if "values" in remaining:
            clone._values = list(remaining.pop("values"))

        return self._apply_base_copy_overrides(clone, remaining, allow_kwargs=False)  # type: ignore[return-value]

    def __enter__(self) -> "Loop":
        """Enter the context manager, returning this loop."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Exit the context manager (no-op; content is already collected)."""
        pass
