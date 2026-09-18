from __future__ import annotations

from typing import TypeAlias

from tikzfigure.core.tikz_token import TikzToken


class TikzDecoration(TikzToken):
    """A reusable TikZ path-decoration specification."""

    _attr = "decoration_spec"
    decoration_spec: str

    def __init__(self, decoration_spec: str) -> None:
        super().__init__(decoration_spec)


DecorationInput: TypeAlias = str | TikzDecoration


def decoration(decoration_spec: str) -> TikzDecoration:
    """Create a custom raw TikZ decoration specification."""
    return TikzDecoration(decoration_spec)


zigzag: TikzDecoration = TikzDecoration("zigzag")
snake: TikzDecoration = TikzDecoration("snake")
coil: TikzDecoration = TikzDecoration("coil")
bumps: TikzDecoration = TikzDecoration("bumps")
bent: TikzDecoration = TikzDecoration("bent")
random_steps: TikzDecoration = TikzDecoration("random steps")
saw: TikzDecoration = TikzDecoration("saw")
brace: TikzDecoration = TikzDecoration("brace")
ticks: TikzDecoration = TikzDecoration("ticks")
border: TikzDecoration = TikzDecoration("border")
markings: TikzDecoration = TikzDecoration("markings")
expanding_waves: TikzDecoration = TikzDecoration("expanding waves")
footprints: TikzDecoration = TikzDecoration("footprints")

__all__ = [
    "DecorationInput",
    "TikzDecoration",
    "bent",
    "border",
    "brace",
    "bumps",
    "coil",
    "decoration",
    "expanding_waves",
    "footprints",
    "markings",
    "random_steps",
    "saw",
    "snake",
    "ticks",
    "zigzag",
]
