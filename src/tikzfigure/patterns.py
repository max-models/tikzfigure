from __future__ import annotations

from typing import TypeAlias

from tikzfigure.core.tikz_token import TikzToken


class TikzPattern(TikzToken):
    """A reusable TikZ fill-pattern specification."""

    _attr = "pattern_spec"
    pattern_spec: str

    def __init__(self, pattern_spec: str) -> None:
        super().__init__(pattern_spec)


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
    "PatternInput",
    "TikzPattern",
    "bricks",
    "checkerboard",
    "crosshatch",
    "crosshatch_dots",
    "dots",
    "fivepointed_stars",
    "grid",
    "horizontal_lines",
    "north_east_lines",
    "north_west_lines",
    "pattern",
    "sixpointed_stars",
    "vertical_lines",
]
