"""Data structures and rendering support for two-dimensional quadtrees."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.options import OptionInput

_QUADRANTS = ("sw", "se", "nw", "ne")


class QuadtreeNode:
    """A quadtree node whose children are ordered SW, SE, NW, NE.

    A leaf is represented by ``children=None``.  For convenience, children
    may also be supplied as a mapping with those four keys or as a four-item
    sequence.  A child may be another :class:`QuadtreeNode`, ``None`` (a
    leaf), or a nested mapping/sequence in the same format.
    """

    def __init__(
        self,
        children: Mapping[str, Any] | Sequence[Any] | None = None,
        *,
        value: Any = None,
    ) -> None:
        self.value = value
        self.children = self._normalize_children(children)

    @staticmethod
    def _normalize_children(
        children: Mapping[str, Any] | Sequence[Any] | None,
    ) -> tuple[QuadtreeNode | None, ...] | None:
        if children is None:
            return None
        if isinstance(children, Mapping):
            missing = [quadrant for quadrant in _QUADRANTS if quadrant not in children]
            if missing:
                raise ValueError(
                    "Quadtree child mappings must contain sw, se, nw, and ne "
                    f"(missing: {', '.join(missing)})."
                )
            raw_children = [children[quadrant] for quadrant in _QUADRANTS]
        else:
            if isinstance(children, (str, bytes)) or len(children) != 4:
                raise ValueError("Quadtree children must be a four-item sequence.")
            raw_children = list(children)
        return tuple(QuadtreeNode._coerce_child(child) for child in raw_children)

    @staticmethod
    def _coerce_child(child: Any) -> QuadtreeNode | None:
        if child is None:
            return None
        if isinstance(child, QuadtreeNode):
            return child
        if isinstance(child, Mapping):
            # A mapping with a ``children`` key is an explicit serialized node;
            # otherwise it is shorthand for a quadrant mapping.
            if "children" in child:
                return QuadtreeNode(child["children"], value=child.get("value"))
            return QuadtreeNode(child)
        if isinstance(child, Sequence) and not isinstance(child, (str, bytes)):
            return QuadtreeNode(child)
        raise TypeError(
            "Quadtree children must be nodes, mappings, sequences, or None."
        )

    @property
    def is_leaf(self) -> bool:
        return self.children is None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "QuadtreeNode",
            "children": (
                None
                if self.children is None
                else [
                    child.to_dict() if child is not None else None
                    for child in self.children
                ]
            ),
            "value": serialize_tikz_value(self.value),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "QuadtreeNode":
        children = data.get("children")
        value = deserialize_tikz_value(data.get("value"))
        if children is None:
            return cls(value=value)
        return cls(
            [cls.from_dict(child) if child is not None else None for child in children],
            value=value,
        )


class QuadtreePlot(TikzObject):
    """Render a quadtree as nested, depth-colored TikZ rectangles.

    ``tree`` accepts a :class:`QuadtreeNode`, a four-item nested sequence, or
    a mapping with ``sw``, ``se``, ``nw``, and ``ne`` keys.  ``level_colors[0]``
    colors the root cell; deeper levels use subsequent entries, with the last
    color reused when the tree is deeper than the color list.
    """

    def __init__(
        self,
        tree: QuadtreeNode | Mapping[str, Any] | Sequence[Any] | None,
        bounds: tuple[float, float, float, float] = (0, 0, 1, 1),
        level_colors: Sequence[Any] | None = None,
        *,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> None:
        if len(bounds) != 4 or bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
            raise ValueError(
                "bounds must be (xmin, ymin, xmax, ymax) with positive area."
            )
        if level_colors is not None and len(level_colors) == 0:
            raise ValueError("level_colors must contain at least one color.")
        self._tree = QuadtreeNode._coerce_child(tree) or QuadtreeNode()
        self._bounds = tuple(bounds)
        self._level_colors = list(level_colors or ["black"])
        super().__init__(
            label=label, comment=comment, layer=layer, options=options, **kwargs
        )

    @property
    def tree(self) -> QuadtreeNode:
        return self._tree

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return self._bounds

    @property
    def level_colors(self) -> list[Any]:
        return self._level_colors

    def _rectangles(self) -> list[tuple[int, tuple[float, float, float, float]]]:
        xmin, ymin, xmax, ymax = self.bounds
        rectangles: list[tuple[int, tuple[float, float, float, float]]] = []

        def visit(
            node: QuadtreeNode, box: tuple[float, float, float, float], level: int
        ) -> None:
            rectangles.append((level, box))
            if node.children is None:
                return
            left, bottom, right, top = box
            mid_x, mid_y = (left + right) / 2, (bottom + top) / 2
            boxes = (
                (left, bottom, mid_x, mid_y),
                (mid_x, bottom, right, mid_y),
                (left, mid_y, mid_x, top),
                (mid_x, mid_y, right, top),
            )
            for child, child_box in zip(node.children, boxes):
                if child is not None:
                    visit(child, child_box, level + 1)

        visit(self.tree, (xmin, ymin, xmax, ymax), 0)
        return rectangles

    def to_tikz(self, output_unit: str | None = None) -> str:
        lines: list[str] = []
        for level, (xmin, ymin, xmax, ymax) in self._rectangles():
            color = self.level_colors[min(level, len(self.level_colors) - 1)]
            options = self.tikz_options(output_unit)
            color_option = f"draw={color}"
            option_text = ", ".join(part for part in (options, color_option) if part)
            lines.append(
                f"\\draw[{option_text}] ({xmin},{ymin}) rectangle ({xmax},{ymax});"
            )
        return self.add_comment("\n".join(lines) + "\n")

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "type": "QuadtreePlot",
                "tree": self.tree.to_dict(),
                "bounds": self.bounds,
                "level_colors": self.level_colors,
            }
        )
        return serialize_tikz_value(data)  # type: ignore[return-value]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuadtreePlot":
        restored = deserialize_tikz_value(data)
        if not isinstance(restored, dict):
            raise TypeError("Serialized quadtree data must deserialize to a dict.")
        return cls(
            tree=QuadtreeNode.from_dict(restored["tree"]),
            bounds=tuple(restored["bounds"]),
            level_colors=restored.get("level_colors"),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options", []),
            **restored.get("kwargs", {}),
        )


QuadtreePlotter = QuadtreePlot
