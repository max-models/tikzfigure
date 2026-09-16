from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

if TYPE_CHECKING:
    from tikzfigure.parser import ParseResult


class FigureParsingMixin:
    def _load_tikz_code(self, tikz_code: str, strict: bool = False) -> ParseResult:
        from tikzfigure.parser import load_tikz

        return load_tikz(self, tikz_code, strict=strict)  # type: ignore[arg-type]

    @classmethod
    def from_tikz_code(
        cls, tikz_code: str, strict: bool = False, **kwargs: Any
    ) -> Self:
        """Create a TikzFigure by parsing existing TikZ source code.

        Statements that map onto tikzfigure objects (nodes, paths, circles,
        rectangles, coordinates, scopes, ``\\foreach`` loops, layers,
        variables, colors, styles, ...) are reconstructed as such; anything
        else is kept verbatim as raw TikZ so the figure renders the same.
        Use :func:`tikzfigure.parser.parse_tikz` to also get per-statement
        diagnostics.

        Args:
            tikz_code: A string containing a ``tikzpicture`` environment,
                optionally inside a ``figure`` environment or a complete
                LaTeX document.
            strict: If ``True``, raise
                :class:`~tikzfigure.parser.TikzParseError` when any statement
                had to be kept as raw TikZ.
            **kwargs: Additional keyword arguments forwarded to
                :meth:`__init__`.

        Returns:
            A new :class:`TikzFigure` reconstructed from *tikz_code*.

        Raises:
            TikzParseError: If *tikz_code* is malformed (for example
                unbalanced braces or no ``tikzpicture``), or in strict mode
                if some statements could not be mapped.
        """
        figure = cls(**kwargs)
        figure._load_tikz_code(tikz_code, strict=strict)
        return figure
