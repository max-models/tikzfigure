from __future__ import annotations

from typing import TypeAlias


class TikzMark:
    """A reusable pgfplots plot-mark specification."""

    def __init__(self, mark_spec: str) -> None:
        if mark_spec == "":
            raise ValueError("mark_spec must not be empty")
        self.mark_spec = mark_spec

    def to_tikz(self) -> str:
        """Return the raw pgfplots mark specification."""
        return self.mark_spec

    def __str__(self) -> str:
        return self.mark_spec

    def __repr__(self) -> str:
        return f"TikzMark({self.mark_spec!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TikzMark):
            return NotImplemented
        return self.mark_spec == other.mark_spec

    def __hash__(self) -> int:
        return hash(self.mark_spec)


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
    "TikzMark",
    "MarkInput",
    "mark",
    "asterisk",
    "x",
    "circle",
    "plus",
    "bar",
    "dash",
    "square",
    "square_filled",
    "triangle",
    "triangle_filled",
    "diamond",
    "diamond_filled",
    "pentagon",
    "pentagon_filled",
    "oplus",
    "oplus_filled",
    "otimes",
    "otimes_filled",
    "spoked_asterisk",
    "star",
    "ten_pointed_star",
    "ball",
]
