from __future__ import annotations

from typing import TypeAlias

from tikzfigure.core.tikz_token import TikzToken
from tikzfigure.units import TikzDimension


class TikzStyle(TikzToken):
    """A reusable TikZ style token or option fragment."""

    _attr = "style_spec"
    style_spec: str

    def __init__(self, style_spec: str) -> None:
        super().__init__(style_spec)


StyleInput: TypeAlias = str | TikzStyle


def _format_measure(value: str | float | TikzDimension) -> str:
    if isinstance(value, TikzDimension):
        return str(value)
    if isinstance(value, (int, float)):
        return f"{value}pt"
    return value


def style(style_spec: str) -> TikzStyle:
    """Create a custom raw TikZ style token."""
    return TikzStyle(style_spec)


def line_width(value: str | float | TikzDimension) -> TikzStyle:
    """Build a ``line width=...`` option fragment."""
    return TikzStyle(f"line width={_format_measure(value)}")


def rounded_corners(radius: str | float | TikzDimension) -> TikzStyle:
    """Build a ``rounded corners=...`` option fragment."""
    return TikzStyle(f"rounded corners={_format_measure(radius)}")


def dash_pattern(
    on: str | float | TikzDimension,
    off: str | float | TikzDimension,
) -> TikzStyle:
    """Build a simple ``dash pattern=on ... off ...`` option fragment."""
    return TikzStyle(
        f"dash pattern=on {_format_measure(on)} off {_format_measure(off)}"
    )


def bend_left(angle: float | None = None) -> TikzStyle:
    """Build a ``bend left`` option fragment."""
    if angle is None:
        return TikzStyle("bend left")
    return TikzStyle(f"bend left={angle}")


def bend_right(angle: float | None = None) -> TikzStyle:
    """Build a ``bend right`` option fragment."""
    if angle is None:
        return TikzStyle("bend right")
    return TikzStyle(f"bend right={angle}")


solid: TikzStyle = TikzStyle("solid")
dashed: TikzStyle = TikzStyle("dashed")
dotted: TikzStyle = TikzStyle("dotted")
densely_dashed: TikzStyle = TikzStyle("densely dashed")
loosely_dashed: TikzStyle = TikzStyle("loosely dashed")
densely_dotted: TikzStyle = TikzStyle("densely dotted")
loosely_dotted: TikzStyle = TikzStyle("loosely dotted")
dash_dot: TikzStyle = TikzStyle("dash dot")
densely_dash_dot: TikzStyle = TikzStyle("densely dash dot")
loosely_dash_dot: TikzStyle = TikzStyle("loosely dash dot")
ultra_thin: TikzStyle = TikzStyle("ultra thin")
very_thin: TikzStyle = TikzStyle("very thin")
thin: TikzStyle = TikzStyle("thin")
semithick: TikzStyle = TikzStyle("semithick")
thick: TikzStyle = TikzStyle("thick")
very_thick: TikzStyle = TikzStyle("very thick")
ultra_thick: TikzStyle = TikzStyle("ultra thick")
draw: TikzStyle = TikzStyle("draw")
fill: TikzStyle = TikzStyle("fill")
clip: TikzStyle = TikzStyle("clip")
decorate: TikzStyle = TikzStyle("decorate")
sharp_corners: TikzStyle = TikzStyle("sharp corners")
butt: TikzStyle = TikzStyle("butt")
rect: TikzStyle = TikzStyle("rect")
round: TikzStyle = TikzStyle("round")
miter: TikzStyle = TikzStyle("miter")
bevel: TikzStyle = TikzStyle("bevel")

__all__ = [
    "StyleInput",
    "TikzStyle",
    "bend_left",
    "bend_right",
    "bevel",
    "butt",
    "clip",
    "dash_dot",
    "dash_pattern",
    "dashed",
    "decorate",
    "densely_dash_dot",
    "densely_dashed",
    "densely_dotted",
    "dotted",
    "draw",
    "fill",
    "line_width",
    "loosely_dash_dot",
    "loosely_dashed",
    "loosely_dotted",
    "miter",
    "rect",
    "round",
    "rounded_corners",
    "semithick",
    "sharp_corners",
    "solid",
    "style",
    "thick",
    "thin",
    "ultra_thick",
    "ultra_thin",
    "very_thick",
    "very_thin",
]
