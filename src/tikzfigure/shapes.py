from __future__ import annotations

from typing import TypeAlias

from tikzfigure.core.tikz_token import TikzToken


class TikzShape(TikzToken):
    """A reusable TikZ node-shape specification."""

    _attr = "shape_spec"
    shape_spec: str

    def __init__(self, shape_spec: str) -> None:
        super().__init__(shape_spec)


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
    "ShapeInput",
    "TikzShape",
    "circle",
    "cloud",
    "cross_out",
    "cylinder",
    "dart",
    "diamond",
    "ellipse",
    "forbidden_sign",
    "isosceles_triangle",
    "kite",
    "rectangle",
    "regular_polygon",
    "semicircle",
    "shape",
    "signal",
    "star",
    "strike_out",
    "trapezium",
]
