from __future__ import annotations

import types
from collections.abc import Callable
from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import Coordinate, TikzCoordinate
from tikzfigure.core.figure_paths import FigurePathMixin
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.core.path_builder import NodePathBuilder, SegmentOption
from tikzfigure.core.raw import RawTikz
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.options import OptionInput


class Scope(FigurePathMixin, TikzObject):
    """A TikZ ``scope`` block with local options and nested content."""

    def __init__(
        self,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        node_resolver: Callable[[str], Node | Coordinate] | None = None,
        **kwargs: Any,
    ) -> None:
        self._items: list[Any] = []
        self._node_resolver = node_resolver
        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def items(self) -> list[Any]:
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
                    "segment_options cannot be passed to draw()/filldraw() "
                    "when using a NodePathBuilder."
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
        raise ValueError(f"Node with label {node_label} not found in this scope!")

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
        if not isinstance(nodes, list):
            raise ValueError("nodes parameter must be a list of node names.")

        resolved_layer = self._container_layer()
        nodes_cleaned: list[Node | Coordinate | TikzCoordinate] = []
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
                coords = tuple(node)
                nodes_cleaned.append(TikzCoordinate(*coords, layer=resolved_layer))  # type: ignore[misc]
                node_anchors.append(None)
            elif isinstance(node, TikzCoordinate):
                nodes_cleaned.append(node)
                node_anchors.append(None)
            else:
                raise NotImplementedError(
                    f"Node type {type(node)} not implemented for Scope._add_path"
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
            print(f"Added {path} to scope")
        return path

    def add_node(self, *args: Any, **kwargs: Any) -> Node:
        kwargs.setdefault("layer", self._container_layer())
        node = Node(*args, **kwargs)
        self._items.append(node)
        return node

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

    def add_raw(self, tikz_code: str) -> RawTikz:
        raw = RawTikz(tikz_code)
        self._items.append(raw)
        return raw

    def add_loop(
        self,
        variable: str,
        values: list[Any] | tuple[Any, ...] | range,
        comment: str | None = None,
    ) -> Any:
        from tikzfigure.core.loop import Loop

        loop = Loop(
            variable=variable,
            values=values,
            layer=self._container_layer(),
            comment=comment,
        )
        self._items.append(loop)
        return loop

    def add_scope(
        self,
        comment: str | None = None,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> "Scope":
        scope = Scope(
            comment=comment,
            layer=self._container_layer(),
            options=options,
            node_resolver=self.get_node,
            **kwargs,
        )
        self._items.append(scope)
        return scope

    node = add_node
    coordinate = add_coordinate
    raw = add_raw
    loop = add_loop
    scope = add_scope

    def to_tikz(self, output_unit: str | None = None) -> str:
        options = self.tikz_options(output_unit)
        begin = f"\\begin{{scope}}[{options}]\n" if options else "\\begin{scope}\n"
        body = "".join(item.to_tikz(output_unit) for item in self._items)
        scope_str = begin + body + "\\end{scope}\n"
        return self.add_comment(scope_str)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "type": "Scope",
                "items": [item.to_dict() for item in self._items],
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized scope data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(
        cls,
        d: dict[str, Any],
        node_lookup: dict[str, Node | Coordinate] | None = None,
    ) -> "Scope":
        from tikzfigure.core.loop import Loop

        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized scope data must deserialize to a dict.")
        scope = cls(
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options"),
            **restored.get("kwargs", {}),
        )
        local_lookup: dict[str, Node | Coordinate] = dict(node_lookup or {})
        for item_data in restored.get("items", []):
            item_type = item_data.get("type")
            if item_type == "Node":
                node = Node.from_dict(item_data)
                scope._items.append(node)
                if node.label is not None:
                    local_lookup[node.label] = node
            elif item_type == "Coordinate":
                coord = Coordinate.from_dict(item_data)
                scope._items.append(coord)
                if coord.label:
                    local_lookup[coord.label] = coord
            elif item_type == "Path":
                scope._items.append(
                    TikzPath.from_dict(item_data, node_lookup=local_lookup)
                )
            elif item_type == "Loop":
                scope._items.append(Loop.from_dict(item_data, node_lookup=local_lookup))
            elif item_type == "Scope":
                scope._items.append(
                    Scope.from_dict(item_data, node_lookup=local_lookup)
                )
            elif item_type == "RawTikz":
                scope._items.append(RawTikz.from_dict(item_data))
        return scope

    def copy(self, **overrides: Any) -> "Scope":
        clone = type(self).from_dict(self.to_dict())
        clone._node_resolver = self._node_resolver
        return self._apply_base_copy_overrides(clone, overrides)  # type: ignore[return-value]

    def __enter__(self) -> "Scope":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        pass
