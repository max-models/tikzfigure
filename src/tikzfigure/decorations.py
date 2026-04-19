from __future__ import annotations

from typing import TypeAlias


class TikzDecoration:
    """A reusable TikZ path-decoration specification."""

    def __init__(self, decoration_spec: str) -> None:
        if decoration_spec == "":
            raise ValueError("decoration_spec must not be empty")
        self.decoration_spec = decoration_spec

    def to_tikz(self) -> str:
        """Return the raw TikZ decoration specification."""
        return self.decoration_spec

    def __str__(self) -> str:
        return self.decoration_spec

    def __repr__(self) -> str:
        return f"TikzDecoration({self.decoration_spec!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TikzDecoration):
            return NotImplemented
        return self.decoration_spec == other.decoration_spec

    def __hash__(self) -> int:
        return hash(self.decoration_spec)


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
    "TikzDecoration",
    "DecorationInput",
    "decoration",
    "zigzag",
    "snake",
    "coil",
    "bumps",
    "bent",
    "random_steps",
    "saw",
    "brace",
    "ticks",
    "border",
    "markings",
    "expanding_waves",
    "footprints",
]
