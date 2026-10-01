"""Base class for the small "raw TikZ spec string" wrapper types.

:class:`~tikzfigure.arrows.TikzArrow`, :class:`~tikzfigure.decorations.TikzDecoration`,
:class:`~tikzfigure.marks.TikzMark`, :class:`~tikzfigure.patterns.TikzPattern`,
:class:`~tikzfigure.shapes.TikzShape`, and :class:`~tikzfigure.styles.TikzStyle`
each wrap a single raw TikZ fragment -- an arrow tip, a fill pattern, a style
name, and so on -- so it can be typed, compared, and interpolated into TikZ
option strings while still allowing arbitrary raw TikZ via a plain string.
:class:`TikzToken` factors out the identical construction, formatting, and
equality logic they all shared.
"""

from __future__ import annotations

from typing import ClassVar, cast


class TikzToken:
    """Base class for a reusable, raw TikZ specification-string wrapper.

    Subclasses set the class attribute ``_attr`` to the public attribute
    name the raw spec is stored under (e.g. ``"arrow_spec"``). That name is
    kept distinct per subclass -- rather than a single shared attribute
    name here -- for backward-compatible serialization; see
    :mod:`tikzfigure.core.serialization`, which reads/writes it by name.
    """

    _attr: ClassVar[str] = "_spec_value"

    def __init__(self, spec: str) -> None:
        if spec == "":
            raise ValueError(f"{self._attr} must not be empty")
        setattr(self, self._attr, spec)

    @property
    def spec(self) -> str:
        """The raw TikZ specification string."""
        return cast(str, getattr(self, self._attr))

    def to_tikz(self) -> str:
        """Return the raw TikZ specification string."""
        return self.spec

    def __str__(self) -> str:
        return self.spec

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.spec!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.spec == other.spec

    def __hash__(self) -> int:
        return hash(self.spec)
