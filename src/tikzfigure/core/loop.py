import types
from collections.abc import Sequence
from typing import Any, Callable

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import Coordinate
from tikzfigure.core.figure_paths import FigurePathMixin
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.core.path_builder import NodePathBuilder, SegmentOption
from tikzfigure.core.plot import TikzPlot
from tikzfigure.core.raw import RawTikz
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.math import Expr
from tikzfigure.options import OptionInput


class LoopVariable(Expr):
    """Expression-like handle returned by :class:`Loop` context managers.

    The handle behaves like the loop variable itself in PGF math expressions
    while still delegating ``node()``, ``plot()``, ``loop()``, and similar body
    builder methods to the underlying :class:`Loop`.
    """

    def __init__(self, loop: "Loop") -> None:
        self._loop = loop
        super().__init__(f"\\{loop.variable}")

    @property
    def var(self) -> "LoopVariable":
        """Return the loop variable expression itself."""
        return self

    def __getattr__(self, name: str) -> Any:
        return getattr(self._loop, name)


class Loop(FigurePathMixin, TikzObject):
    """A TikZ ``\\foreach`` loop that repeats items over a sequence of values.

    Loops can be nested and may contain nodes, paths, and other loops.
    They act as context managers so nested content can be added inside a
    ``with`` block. Inside that block, the bound value can be used directly as
    the iteration variable in expressions while still exposing ``node()``,
    ``plot()``, ``loop()``, and related methods.

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
        node_resolver: Callable[[str], Node | Coordinate] | None = None,
        library_loader: Callable[[str], None] | None = None,
        enter_callback: Callable[[Any], None] | None = None,
        exit_callback: Callable[[Any], None] | None = None,
    ) -> None:
        """Initialize a Loop.

        Args:
            variable: Loop variable name (without the leading backslash),
                e.g. ``"i"`` produces ``\\foreach \\i in {...}``.
            values: Sequence of values to iterate over. Python ``range`` inputs
                are rendered using TikZ's compact ``start,next,...,last``
                syntax when possible.
            layer: Layer index this loop belongs to. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
        """
        self._variable: str = variable
        self._var = LoopVariable(self)
        self._range_spec = self._extract_range_spec(values)
        self._values: list[Any] = list(values)
        self._items: list[Any] = []
        self._node_resolver = node_resolver
        self._library_loader = library_loader
        self._enter_callback = enter_callback
        self._exit_callback = exit_callback

        super().__init__(layer=layer, comment=comment)

    @staticmethod
    def _extract_range_spec(
        values: Sequence[Any],
    ) -> dict[str, int] | None:
        if not isinstance(values, range):
            return None
        return {
            "start": values.start,
            "stop": values.stop,
            "step": values.step,
        }

    def _set_values(self, values: Sequence[Any]) -> None:
        self._range_spec = self._extract_range_spec(values)
        self._values = list(values)

    def _render_values(self) -> str:
        if self._range_spec is not None and len(self._values) >= 3:
            return f"{self._values[0]},{self._values[1]},...,{self._values[-1]}"
        return ",".join(str(v) for v in self.values)

    @property
    def variable(self) -> str:
        """Loop variable name (without the leading backslash)."""
        return self._variable

    @property
    def var(self) -> LoopVariable:
        """Expression handle for the loop variable (for example ``\\i``)."""
        return self._var

    @property
    def values(self) -> list[Any]:
        """Sequence of values the loop iterates over."""
        return self._values

    @property
    def items(self) -> list[Any]:
        """TikZ objects contained in this loop body."""
        return self._items

    def _container_layer(self) -> int:
        return self.layer if self.layer is not None else 0

    @staticmethod
    def _coerce_path_input(
        nodes: list[Any] | NodePathBuilder,
        segment_options: list[SegmentOption] | None = None,
    ) -> tuple[list[Any], list[SegmentOption] | None]:
        if isinstance(nodes, NodePathBuilder):
            if segment_options is not None:
                raise ValueError(
                    "segment_options cannot be passed to draw()/filldraw() when using a NodePathBuilder."
                )
            return nodes.nodes, nodes.segment_options
        return nodes, segment_options

    def get_node(self, node_label: str) -> Node | Coordinate:
        def _search(items: list[Any]) -> Node | Coordinate | None:
            for item in items:
                if isinstance(item, (Node, Coordinate)) and item.label == node_label:
                    return item
                nested_items = getattr(item, "items", None)
                if nested_items is not None:
                    found = _search(nested_items)
                    if found is not None:
                        return found
            return None

        found = _search(self._items)
        if found is not None:
            return found
        if self._node_resolver is not None:
            return self._node_resolver(node_label)
        raise ValueError(f"Node with label {node_label} not found in this loop!")

    def _add_path(
        self,
        nodes: list[Any],
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        tikz_command: str = "draw",
        verbose: bool = False,
        options: OptionInput | None = None,
        cycle: bool = False,
        segment_options: list[SegmentOption] | None = None,
        **kwargs: Any,
    ) -> TikzPath:
        del layer
        if not isinstance(nodes, list):
            raise ValueError("nodes parameter must be a list of node names.")

        resolved_layer = self._container_layer()
        nodes_cleaned: list[Node | Coordinate | Any] = []
        node_anchors: list[str | None] = []

        for node in nodes:
            if isinstance(node, (Node, Coordinate)):
                nodes_cleaned.append(node)
                node_anchors.append(None)
            elif isinstance(node, str):
                try:
                    nodes_cleaned.append(self.get_node(node))
                    node_anchors.append(None)
                except ValueError:
                    if "." in node:
                        label_part, anchor_part = node.rsplit(".", 1)
                        nodes_cleaned.append(self.get_node(label_part))
                        node_anchors.append(anchor_part)
                    else:
                        raise
            elif isinstance(node, (tuple, list)):
                from tikzfigure.core.coordinate import TikzCoordinate

                coords = tuple(node)
                nodes_cleaned.append(TikzCoordinate(*coords, layer=resolved_layer))  # type: ignore[misc]
                node_anchors.append(None)
            else:
                from tikzfigure.core.coordinate import TikzCoordinate

                if isinstance(node, TikzCoordinate):
                    nodes_cleaned.append(node)
                    node_anchors.append(None)
                else:
                    raise NotImplementedError(
                        f"Node type {type(node)} not implemented for Loop._add_path"
                    )

        resolved_anchors = (
            node_anchors if any(anchor is not None for anchor in node_anchors) else None
        )
        path = TikzPath(
            nodes=nodes_cleaned,
            comment=comment,
            center=center,
            node_anchors=resolved_anchors,
            segment_options=segment_options,
            tikz_command=tikz_command,
            options=options,
            cycle=cycle,
            layer=resolved_layer,
            **kwargs,
        )
        self._items.append(path)
        if verbose:
            print(f"Added {path} to loop")
        return path

    def add_node(self, *args: Any, **kwargs: Any) -> Node:
        """Add a node inside this loop body.

        Args:
            *args: Positional arguments forwarded to :class:`Node`.
            **kwargs: Keyword arguments forwarded to :class:`Node`.

        Returns:
            The newly created :class:`Node`.
        """
        if len(args) == 1 and isinstance(args[0], Node):
            if kwargs:
                raise ValueError(
                    "When passing an existing Node to add_node(), do not also provide node-construction arguments."
                )
            node = args[0]
            self._items.append(node)
            return node
        node = Node(*args, **kwargs)
        self._items.append(node)
        return node

    def add_path(
        self,
        nodes: list[Any] | NodePathBuilder,
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        tikz_command: str = "draw",
        verbose: bool = False,
        options: OptionInput | None = None,
        cycle: bool = False,
        segment_options: list[SegmentOption] | None = None,
        **kwargs: Any,
    ) -> TikzPath:
        """Add a path inside this loop body.

        Args:
            nodes: List of nodes or coordinates to connect.
            comment: Optional comment prepended to the path in TikZ output.
            **kwargs: Additional TikZ path options.

        Returns:
            The newly created :class:`TikzPath`.
        """
        nodes, segment_options = self._coerce_path_input(nodes, segment_options)
        return self._add_path(
            nodes=nodes,
            layer=layer,
            comment=comment,
            center=center,
            tikz_command=tikz_command,
            verbose=verbose,
            options=options,
            cycle=cycle,
            segment_options=segment_options,
            **kwargs,
        )

    def add_coordinate(
        self,
        label: str,
        x: Any = None,
        y: Any = None,
        z: Any = None,
        at: str | None = None,
        comment: str | None = None,
    ) -> Coordinate:
        coord = Coordinate(
            label=label,
            x=x,
            y=y,
            z=z,
            at=at,
            layer=self._container_layer(),
            comment=comment,
        )
        self._items.append(coord)
        return coord

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
        loop = Loop(
            variable,
            values,
            layer=self.layer or 0,
            comment=comment,
            node_resolver=self.get_node,
            library_loader=self._library_loader,
            enter_callback=self._enter_callback,
            exit_callback=self._exit_callback,
        )
        self._items.append(loop)
        return loop

    def add_raw(self, tikz_code: str) -> RawTikz:
        raw = RawTikz(tikz_code)
        self._items.append(raw)
        return raw

    def add_plot(
        self,
        x: Any,
        y: Any | None = None,
        *,
        variable: str = "x",
        domain: tuple[Any, Any] | str | None = None,
        samples: int | None = None,
        smooth: bool = False,
        comment: str | None = None,
        options: Any = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> TikzPlot:
        """Add a plain TikZ expression plot inside this loop body."""
        plot = TikzPlot(
            x=x,
            y=y,
            variable=variable,
            domain=domain,
            samples=samples,
            smooth=smooth,
            comment=comment,
            options=options,
            tikz_command=tikz_command,
            layer=self.layer or 0,
            **kwargs,
        )
        self._items.append(plot)
        return plot

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
            node_resolver=self.get_node,
            library_loader=self._library_loader,
            **kwargs,
        )
        scope._enter_callback = self._enter_callback
        scope._exit_callback = self._exit_callback
        self._items.append(scope)
        return scope

    def path(
        self,
        nodes: list[Any],
        layer: int = 0,
        comment: str | None = None,
        center: bool = False,
        verbose: bool = False,
        options: OptionInput | None = None,
        cycle: bool = False,
        segment_options: list[SegmentOption] | None = None,
        name_path: str | None = None,
        pos: float | None = None,
        rotate: float | None = None,
        xshift: str | None = None,
        yshift: str | None = None,
        scale: float | None = None,
        **kwargs: Any,
    ) -> TikzPath:
        return self.add_path(
            nodes=nodes,
            layer=layer,
            comment=comment,
            center=center,
            verbose=verbose,
            options=options,
            cycle=cycle,
            segment_options=segment_options,
            name_path=name_path,
            pos=pos,
            rotate=rotate,
            xshift=xshift,
            yshift=yshift,
            scale=scale,
            **kwargs,
        )

    node = add_node
    coordinate = add_coordinate
    loop = add_loop
    raw = add_raw
    plot = add_plot
    scope = add_scope

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ ``\\foreach`` code for this loop.

        Returns:
            A string containing the complete ``\\foreach`` block, including
            all nested items.
        """
        values_str = self._render_values()
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
                "range_spec": dict(self._range_spec)
                if self._range_spec is not None
                else None,
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
        range_spec = restored.get("range_spec")
        if isinstance(range_spec, dict):
            values: Sequence[Any] = range(
                int(range_spec["start"]),
                int(range_spec["stop"]),
                int(range_spec["step"]),
            )
        else:
            values = restored["values"]
        loop = cls(
            variable=restored["variable"],
            values=values,
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
            elif item_type == "TikzPlot":
                loop._items.append(TikzPlot.from_dict(item_data))
            elif item_type == "RawTikz":
                loop._items.append(RawTikz.from_dict(item_data))
        return loop

    def copy(self, **overrides: Any) -> "Loop":
        clone = type(self).from_dict(self.to_dict())
        clone._node_resolver = self._node_resolver
        clone._library_loader = self._library_loader
        remaining = {key: self._copy_value(value) for key, value in overrides.items()}

        if "variable" in remaining:
            clone._variable = remaining.pop("variable")
            clone._var = LoopVariable(clone)
        if "values" in remaining:
            clone._set_values(remaining.pop("values"))

        return self._apply_base_copy_overrides(clone, remaining, allow_kwargs=False)  # type: ignore[return-value]

    def __enter__(self) -> LoopVariable:
        """Enter the context manager, returning the loop variable handle."""
        if self._enter_callback is not None:
            self._enter_callback(self)
        return self.var

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Exit the context manager (no-op; content is already collected)."""
        if self._exit_callback is not None:
            self._exit_callback(self)
