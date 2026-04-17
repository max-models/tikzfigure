from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias

from tikzfigure.arrows import TikzArrow
from tikzfigure.styles import TikzStyle

OptionValue: TypeAlias = str | TikzArrow | TikzStyle
OptionInput: TypeAlias = OptionValue | Sequence[OptionValue]


def normalize_options(options: OptionInput | None) -> list[OptionValue]:
    """Normalize one-or-many option inputs to a plain list."""
    if options is None:
        return []
    if isinstance(options, (str, TikzArrow, TikzStyle)):
        return [options]
    return list(options)


__all__ = ["OptionValue", "OptionInput", "normalize_options"]
