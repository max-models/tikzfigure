from __future__ import annotations

from typing import TypeAlias

from tikzfigure.units import TikzDimension


class TikzStyle:
    """A reusable TikZ style token or option fragment."""

    def __init__(self, style_spec: str) -> None:
        if style_spec == "":
            raise ValueError("style_spec must not be empty")
        self.style_spec = style_spec

    def to_tikz(self) -> str:
        """Return the raw TikZ style fragment."""
        return self.style_spec

    def __str__(self) -> str:
        return self.style_spec

    def __repr__(self) -> str:
        return f"TikzStyle({self.style_spec!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TikzStyle):
            return NotImplemented
        return self.style_spec == other.style_spec

    def __hash__(self) -> int:
        return hash(self.style_spec)


StyleInput: TypeAlias = str | TikzStyle


def _format_measure(value: str | int | float | TikzDimension) -> str:
    if isinstance(value, TikzDimension):
        return str(value)
    if isinstance(value, (int, float)):
        return f"{value}pt"
    return value


def style(style_spec: str) -> TikzStyle:
    """Create a custom raw TikZ style token."""
    return TikzStyle(style_spec)


def line_width(value: str | int | float | TikzDimension) -> TikzStyle:
    """Build a ``line width=...`` option fragment."""
    return TikzStyle(f"line width={_format_measure(value)}")


def rounded_corners(radius: str | int | float | TikzDimension) -> TikzStyle:
    """Build a ``rounded corners=...`` option fragment."""
    return TikzStyle(f"rounded corners={_format_measure(radius)}")


def dash_pattern(
    on: str | int | float | TikzDimension,
    off: str | int | float | TikzDimension,
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
    "TikzStyle",
    "StyleInput",
    "style",
    "line_width",
    "rounded_corners",
    "dash_pattern",
    "bend_left",
    "bend_right",
    "solid",
    "dashed",
    "dotted",
    "densely_dashed",
    "loosely_dashed",
    "densely_dotted",
    "loosely_dotted",
    "dash_dot",
    "densely_dash_dot",
    "loosely_dash_dot",
    "ultra_thin",
    "very_thin",
    "thin",
    "semithick",
    "thick",
    "very_thick",
    "ultra_thick",
    "draw",
    "fill",
    "clip",
    "decorate",
    "sharp_corners",
    "butt",
    "rect",
    "round",
    "miter",
    "bevel",
]
