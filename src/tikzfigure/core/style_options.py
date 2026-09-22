"""The style options shared by the shape helpers on :class:`TikzFigure`.

Every ``fig.circle(...)`` / ``fig.rectangle(...)`` / ... helper accepts the same
family of TikZ styling options (colors, opacities, line styles, transforms).
Each helper spells those parameters out in its own signature -- that is what
gives editors and type checkers something to complete and check against -- but
the *body* of each helper used to repeat the same forty lines of
``if color is not None: kwargs["color"] = color``.

:class:`StyleOptions` is the canonical list of those parameters, and
:func:`collect_style` harvests whichever of them a helper declares, dropping the
ones the caller left unset.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import Any

from tikzfigure.colors import ColorInput
from tikzfigure.core.types import _LineCap, _LineJoin

__all__ = ["STYLE_FIELDS", "StyleOptions", "collect_style"]


@dataclass(frozen=True)
class StyleOptions:
    """The TikZ styling options shared by the shape helpers.

    This dataclass is not part of the call signatures -- the helpers keep their
    explicit keyword parameters so that editors can complete them. It exists to
    define, in one place, *which* parameters count as style options and in what
    order they are emitted, which is what :func:`collect_style` reads.

    Attributes:
        color: Line color (e.g. ``"red"``, ``"blue!50"``).
        fill: Fill color for the enclosed area.
        draw: Stroke color when different from *color*.
        text: Text color.
        opacity: Overall opacity (0-1).
        draw_opacity: Stroke opacity (0-1).
        fill_opacity: Fill opacity (0-1).
        text_opacity: Text opacity (0-1).
        line_width: Line width (e.g. ``"1pt"``).
        line_cap: Line cap style: ``"butt"``, ``"rect"``, or ``"round"``.
        line_join: Line join style: ``"miter"``, ``"bevel"``, or ``"round"``.
        miter_limit: Miter limit factor for miter joins.
        dash_pattern: Custom dash pattern (e.g. ``"on 2pt off 3pt"``).
        dash_phase: Dash pattern starting offset (e.g. ``"2pt"``).
        rounded_corners: Corner rounding radius (e.g. ``"3pt"``).
        rotate: Rotation angle in degrees.
        xshift: Horizontal shift (e.g. ``"1cm"``).
        yshift: Vertical shift (e.g. ``"1cm"``).
        scale: Uniform scaling factor.
        xscale: Horizontal scaling factor.
        yscale: Vertical scaling factor.
    """

    # Color
    color: ColorInput | None = None
    fill: ColorInput | None = None
    draw: ColorInput | None = None
    text: ColorInput | None = None
    # Opacity
    opacity: float | None = None
    draw_opacity: float | None = None
    fill_opacity: float | None = None
    text_opacity: float | None = None
    # Line width
    line_width: str | None = None
    # Line style
    line_cap: _LineCap = None
    line_join: _LineJoin = None
    miter_limit: float | None = None
    # Dash
    dash_pattern: str | None = None
    dash_phase: str | None = None
    # Corners
    rounded_corners: str | float | None = None
    # Transformations
    rotate: float | None = None
    xshift: str | None = None
    yshift: str | None = None
    scale: float | None = None
    xscale: float | None = None
    yscale: float | None = None

    def as_kwargs(self) -> dict[str, Any]:
        """Return the options that were set, in canonical order."""
        return collect_style(vars(self))


#: The style parameter names, in the order they are emitted into the TikZ
#: option list. Derived from :class:`StyleOptions` so the two cannot drift.
STYLE_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(StyleOptions))


def collect_style(
    scope: Mapping[str, Any],
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Collect the style options present in *scope*, dropping unset ones.

    *scope* is normally the ``locals()`` of a shape helper, so only the style
    parameters that helper actually declares are picked up -- ``fig.grid()``
    has no ``fill``, and simply contributes none. Names outside
    :data:`STYLE_FIELDS` are ignored, so nothing else in *scope* can leak into
    the TikZ options.

    Because it reads ``locals()``, call it before rebinding any parameter.

    Args:
        scope: Mapping of names to values, typically ``locals()``.
        extra: Extra options merged in last, typically a helper's ``**kwargs``
            catch-all. These win over *scope* and are kept even when ``None``.

    Returns:
        The style options to pass on to a :class:`~tikzfigure.core.base.TikzObject`.
    """
    style = {
        name: scope[name]
        for name in STYLE_FIELDS
        if scope.get(name) is not None  # noqa: SIM118 -- Mapping, not a dict
    }
    if extra:
        style.update(extra)
    return style
