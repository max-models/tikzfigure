from __future__ import annotations

from typing import TypeAlias

from tikzfigure.core.tikz_token import TikzToken


class TikzMark(TikzToken):
    """A reusable pgfplots plot-mark specification."""

    _attr = "mark_spec"
    mark_spec: str

    def __init__(self, mark_spec: str) -> None:
        super().__init__(mark_spec)


MarkInput: TypeAlias = str | TikzMark


def mark(mark_spec: str) -> TikzMark:
    """Create a custom raw pgfplots mark specification."""
    return TikzMark(mark_spec)


asterisk: TikzMark = TikzMark("*")
x: TikzMark = TikzMark("x")
circle: TikzMark = TikzMark("o")
plus: TikzMark = TikzMark("+")
bar: TikzMark = TikzMark("|")
dash: TikzMark = TikzMark("-")
square: TikzMark = TikzMark("square")
square_filled: TikzMark = TikzMark("square*")
triangle: TikzMark = TikzMark("triangle")
triangle_filled: TikzMark = TikzMark("triangle*")
diamond: TikzMark = TikzMark("diamond")
diamond_filled: TikzMark = TikzMark("diamond*")
pentagon: TikzMark = TikzMark("pentagon")
pentagon_filled: TikzMark = TikzMark("pentagon*")
oplus: TikzMark = TikzMark("oplus")
oplus_filled: TikzMark = TikzMark("oplus*")
otimes: TikzMark = TikzMark("otimes")
otimes_filled: TikzMark = TikzMark("otimes*")
spoked_asterisk: TikzMark = TikzMark("asterisk")
star: TikzMark = TikzMark("star")
ten_pointed_star: TikzMark = TikzMark("10-pointed star")
ball: TikzMark = TikzMark("ball")

__all__ = [
    "MarkInput",
    "TikzMark",
    "asterisk",
    "ball",
    "bar",
    "circle",
    "dash",
    "diamond",
    "diamond_filled",
    "mark",
    "oplus",
    "oplus_filled",
    "otimes",
    "otimes_filled",
    "pentagon",
    "pentagon_filled",
    "plus",
    "spoked_asterisk",
    "square",
    "square_filled",
    "star",
    "ten_pointed_star",
    "triangle",
    "triangle_filled",
    "x",
]
