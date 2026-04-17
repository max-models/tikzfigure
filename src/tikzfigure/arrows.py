from __future__ import annotations

from typing import TypeAlias


class TikzArrow:
    """A reusable TikZ arrow-tip specification."""

    def __init__(self, arrow_spec: str) -> None:
        if arrow_spec == "":
            raise ValueError("arrow_spec must not be empty")
        self.arrow_spec = arrow_spec

    def to_tikz(self) -> str:
        """Return the raw TikZ arrow specification."""
        return self.arrow_spec

    def __str__(self) -> str:
        return self.arrow_spec

    def __repr__(self) -> str:
        return f"TikzArrow({self.arrow_spec!r})"

    def __hash__(self) -> int:
        return hash(self.arrow_spec)


ArrowInput: TypeAlias = str | TikzArrow


def tip(arrow_spec: str) -> TikzArrow:
    """Create a custom raw TikZ arrow specification."""
    return TikzArrow(arrow_spec)


forward: TikzArrow = TikzArrow("->")
backward: TikzArrow = TikzArrow("<-")
both: TikzArrow = TikzArrow("<->")
bar_forward: TikzArrow = TikzArrow("|->")
bar_backward: TikzArrow = TikzArrow("<-|")
bar_both: TikzArrow = TikzArrow("|-|")
stealth: TikzArrow = TikzArrow("-stealth")
stealth_reversed: TikzArrow = TikzArrow("stealth-")
stealth_both: TikzArrow = TikzArrow("stealth-stealth")
latex: TikzArrow = TikzArrow("-latex")
latex_reversed: TikzArrow = TikzArrow("latex-")
latex_both: TikzArrow = TikzArrow("latex-latex")

__all__ = [
    "TikzArrow",
    "ArrowInput",
    "tip",
    "forward",
    "backward",
    "both",
    "bar_forward",
    "bar_backward",
    "bar_both",
    "stealth",
    "stealth_reversed",
    "stealth_both",
    "latex",
    "latex_reversed",
    "latex_both",
]
