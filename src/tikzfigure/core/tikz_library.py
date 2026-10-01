"""Base class and registry for TikZ libraries (``\\usetikzlibrary{...}``).

Most TikZ library names are just passed through :meth:`TikzFigure.usetikzlibrary`
as plain strings (see ``_TikzLibraryLiteral`` in :mod:`tikzfigure.core.types`
for the full catalogue). A handful of libraries have first-class Python
support beyond that -- a dedicated object model, option-formatting helpers,
naming conventions, and so on. :class:`TikzLibrary` gives that support a
single, explicit home per library instead of scattering it across
:class:`~tikzfigure.core.figure.TikzFigure` and unrelated helper modules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from tikzfigure.core.figure import TikzFigure


class TikzLibrary:
    """Base class for a TikZ library with first-class Python support.

    Subclasses set a class-level :attr:`name` equal to the TikZ library
    name (as passed to ``\\usetikzlibrary{...}``). Subclassing automatically
    registers the library in :attr:`registry`, so
    ``TikzLibrary.registry`` is always the authoritative, explicit list of
    every TikZ library tikzfigure has dedicated support for.

    Use :meth:`ensure` to register a library on a figure -- it is
    idempotent and is the preferred way for feature code (e.g.
    :class:`~tikzfigure.core.matrix.Matrix`, :class:`~tikzfigure.core.spy.Spy`)
    to declare the library it depends on, instead of calling
    ``figure.usetikzlibrary("...")`` with a bare string.
    """

    name: ClassVar[str]

    registry: ClassVar[dict[str, type[TikzLibrary]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        name = getattr(cls, "name", None)
        if not name:
            raise TypeError(f"{cls.__name__} must define a non-empty 'name'.")
        TikzLibrary.registry[name] = cls

    @classmethod
    def ensure(cls, figure: TikzFigure) -> None:
        """Register this library on *figure*. Safe to call more than once."""
        figure.usetikzlibrary(cls.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TikzLibrary):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)


class ArrowsMetaLibrary(TikzLibrary):
    """The ``arrows.meta`` library, always loaded for standalone compilation."""

    name = "arrows.meta"


class AnimationsLibrary(TikzLibrary):
    """The ``animations`` library, for attribute/motion-path PDF animations.

    TikZ's ``animations`` library drives per-attribute animations (e.g.
    ``\\tikzset{<node>/.animate = {fill=red}}``) that get embedded as PDF
    animations. tikzfigure has no dedicated object model for it yet -- call
    ``AnimationsLibrary.ensure(fig)`` and use :meth:`TikzFigure.add_raw` for
    the animation directives in the meantime.
    """

    name = "animations"
