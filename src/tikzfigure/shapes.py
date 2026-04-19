from __future__ import annotations

from typing import TypeAlias


class TikzShape:
    """A reusable TikZ node-shape specification."""

    def __init__(self, shape_spec: str) -> None:
        if shape_spec == "":
            raise ValueError("shape_spec must not be empty")
        self.shape_spec = shape_spec

    def to_tikz(self) -> str:
        """Return the raw TikZ shape specification."""
        return self.shape_spec

    def __str__(self) -> str:
        return self.shape_spec

    def __repr__(self) -> str:
        return f"TikzShape({self.shape_spec!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TikzShape):
            return NotImplemented
        return self.shape_spec == other.shape_spec

    def __hash__(self) -> int:
        return hash(self.shape_spec)


ShapeInput: TypeAlias = str | TikzShape


def shape(shape_spec: str) -> TikzShape:
    """Create a custom raw TikZ shape specification."""
    return TikzShape(shape_spec)


circle: TikzShape = TikzShape("circle")
rectangle: TikzShape = TikzShape("rectangle")
diamond: TikzShape = TikzShape("diamond")
ellipse: TikzShape = TikzShape("ellipse")
star: TikzShape = TikzShape("star")
regular_polygon: TikzShape = TikzShape("regular polygon")
trapezium: TikzShape = TikzShape("trapezium")
semicircle: TikzShape = TikzShape("semicircle")
cylinder: TikzShape = TikzShape("cylinder")
dart: TikzShape = TikzShape("dart")
kite: TikzShape = TikzShape("kite")
isosceles_triangle: TikzShape = TikzShape("isosceles triangle")
signal: TikzShape = TikzShape("signal")
cloud: TikzShape = TikzShape("cloud")
forbidden_sign: TikzShape = TikzShape("forbidden sign")
cross_out: TikzShape = TikzShape("cross out")
strike_out: TikzShape = TikzShape("strike out")

__all__ = [
    "TikzShape",
    "ShapeInput",
    "shape",
    "circle",
    "rectangle",
    "diamond",
    "ellipse",
    "star",
    "regular_polygon",
    "trapezium",
    "semicircle",
    "cylinder",
    "dart",
    "kite",
    "isosceles_triangle",
    "signal",
    "cloud",
    "forbidden_sign",
    "cross_out",
    "strike_out",
]
