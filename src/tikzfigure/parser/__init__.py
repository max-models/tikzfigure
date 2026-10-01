"""Parse TikZ source into :class:`~tikzfigure.TikzFigure` objects.

Example:
    >>> from tikzfigure.parser import parse_tikz
    >>> result = parse_tikz(r'''
    ... \\begin{tikzpicture}
    ...     \\node[draw] (a) at (0, 0) {A};
    ...     \\draw (a) edge[bend left] (1, 1);
    ... \\end{tikzpicture}
    ... ''')
    >>> result.coverage
    0.5
    >>> print(result.raw[0])
    line 4: \\draw kept as raw TikZ: path operation 'edge'

See ``tikz_catalogue/`` in the repository and
``python -m tikzfigure.parser.catalogue`` for a coverage report across a
collection of TikZ examples.
"""

from __future__ import annotations

from typing import Any

from tikzfigure.parser.builder import Diagnostic, ParseResult, load_tikz
from tikzfigure.parser.lexer import Statement, TikzParseError, split_statements


def parse_tikz(source: str, strict: bool = False, **figure_kwargs: Any) -> ParseResult:
    """Parse *source* into a new figure and report how each statement mapped.

    Args:
        source: TikZ code containing a ``tikzpicture`` environment.
        strict: Raise :class:`TikzParseError` if any statement is kept raw.
        **figure_kwargs: Keyword arguments for :class:`~tikzfigure.TikzFigure`.

    Returns:
        A :class:`ParseResult` with the figure and its diagnostics.
    """
    from tikzfigure.core.figure import TikzFigure

    return load_tikz(TikzFigure(**figure_kwargs), source, strict=strict)


__all__ = [
    "Diagnostic",
    "ParseResult",
    "Statement",
    "TikzParseError",
    "load_tikz",
    "parse_tikz",
    "split_statements",
]
