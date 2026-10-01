from __future__ import annotations

from typing import TypeAlias

from tikzfigure.core.tikz_token import TikzToken


class TikzArrow(TikzToken):
    """A reusable TikZ arrow-tip specification."""

    _attr = "arrow_spec"
    arrow_spec: str

    def __init__(self, arrow_spec: str) -> None:
        super().__init__(arrow_spec)


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
    "ArrowInput",
    "TikzArrow",
    "backward",
    "bar_backward",
    "bar_both",
    "bar_forward",
    "both",
    "forward",
    "latex",
    "latex_both",
    "latex_reversed",
    "stealth",
    "stealth_both",
    "stealth_reversed",
    "tip",
]
