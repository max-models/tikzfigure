from __future__ import annotations

from typing import TypeAlias


class TikzPattern:
    """A reusable TikZ fill-pattern specification."""

    def __init__(self, pattern_spec: str) -> None:
        if pattern_spec == "":
            raise ValueError("pattern_spec must not be empty")
        self.pattern_spec = pattern_spec

    def to_tikz(self) -> str:
        """Return the raw TikZ pattern specification."""
        return self.pattern_spec

    def __str__(self) -> str:
        return self.pattern_spec

    def __repr__(self) -> str:
        return f"TikzPattern({self.pattern_spec!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TikzPattern):
            return NotImplemented
        return self.pattern_spec == other.pattern_spec

    def __hash__(self) -> int:
        return hash(self.pattern_spec)


PatternInput: TypeAlias = str | TikzPattern


def pattern(pattern_spec: str) -> TikzPattern:
    """Create a custom raw TikZ pattern specification."""
    return TikzPattern(pattern_spec)


horizontal_lines: TikzPattern = TikzPattern("horizontal lines")
vertical_lines: TikzPattern = TikzPattern("vertical lines")
north_east_lines: TikzPattern = TikzPattern("north east lines")
north_west_lines: TikzPattern = TikzPattern("north west lines")
grid: TikzPattern = TikzPattern("grid")
crosshatch: TikzPattern = TikzPattern("crosshatch")
dots: TikzPattern = TikzPattern("dots")
crosshatch_dots: TikzPattern = TikzPattern("crosshatch dots")
fivepointed_stars: TikzPattern = TikzPattern("fivepointed stars")
sixpointed_stars: TikzPattern = TikzPattern("sixpointed stars")
bricks: TikzPattern = TikzPattern("bricks")
checkerboard: TikzPattern = TikzPattern("checkerboard")

__all__ = [
    "TikzPattern",
    "PatternInput",
    "pattern",
    "horizontal_lines",
    "vertical_lines",
    "north_east_lines",
    "north_west_lines",
    "grid",
    "crosshatch",
    "dots",
    "crosshatch_dots",
    "fivepointed_stars",
    "sixpointed_stars",
    "bricks",
    "checkerboard",
]
