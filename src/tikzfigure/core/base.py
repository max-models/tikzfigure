from typing import Any

from tikzfigure.options import OptionInput, OptionValue, normalize_options


class TikzObject:
    """Base class for all TikZ elements.

    Provides shared logic for labels, comments, options, and
    conversion of Python keyword arguments to TikZ option strings.

    Attributes:
        label: Unique identifier for this object within the figure.
        comment: Optional comment prepended to the generated TikZ code.
        layer: Layer index this object belongs to.
        options: Flag-style TikZ options (e.g. ``["thick", "->"]``).
        kwargs: Keyword-style TikZ options (e.g. ``{"color": "red"}``).
    """

    def __init__(
        self,
        label: str | None = None,
        comment: str | None = None,
        layer: int | None = 0,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a TikzObject.

        Args:
            label: Unique identifier for this object within the figure.
            comment: Comment prepended to the generated TikZ code.
            layer: Layer index this object belongs to. Defaults to ``0``.
            options: Flag-style TikZ options without values
                (e.g. ``["thick", "->"]``).
            **kwargs: Keyword-style TikZ options. Underscores in keys are
                converted to spaces in the output
                (e.g. ``line_width="1pt"`` → ``line width=1pt``).
        """
        self._label = label
        self._comment = comment
        self._layer = layer
        self._options = normalize_options(options)
        self._kwargs = kwargs

    @property
    def label(self) -> str | None:
        """Unique identifier for this object within the figure."""
        return self._label

    @property
    def comment(self) -> str | None:
        """Comment prepended to the generated TikZ code, or ``None``."""
        return self._comment

    @property
    def layer(self) -> int | None:
        """Layer index this object belongs to."""
        return self._layer

    @property
    def options(self) -> list[OptionValue]:
        """Flag-style TikZ options without values."""
        return self._options

    @property
    def kwargs(self) -> dict:
        """Keyword-style TikZ options as a plain dict."""
        return self._kwargs

    def tikz_options(self, output_unit: str | None = None) -> str:
        """Render all options as a single TikZ option string.

        Combines flag-style options and keyword options into the format
        expected inside TikZ square brackets, e.g.
        ``"thick, color=red, line width=1pt"``.

        Args:
            output_unit: If provided, any :class:`~tikzfigure.units.TikzDimension`
                values are converted to this unit before rendering.

        Returns:
            A comma-separated string of TikZ options.
        """
        from tikzfigure.arrows import TikzArrow
        from tikzfigure.colors import TikzColor
        from tikzfigure.styles import TikzStyle
        from tikzfigure.units import TikzDimension

        def _fmt(v: object) -> str:
            if isinstance(v, TikzDimension):
                return str(v.to(output_unit)) if output_unit is not None else str(v)
            if isinstance(v, (TikzArrow, TikzColor, TikzStyle)):
                return str(v)
            return str(v)

        if len(self.options) == 0:
            options = ""
        else:
            options = ", ".join(str(option) for option in self.options) + ", "

        options += ", ".join(
            f"{k.replace('_', ' ')}={_fmt(v)}" for k, v in self.kwargs.items()
        )
        return options

    def add_comment(self, string_in: str) -> str:
        """Prepend a TikZ comment line to a string if a comment is set.

        Args:
            string_in: The TikZ code string to annotate.

        Returns:
            The original string prefixed with ``% <comment>\\n`` when a
            comment is set, otherwise the string unchanged.
        """
        if self.comment is not None:
            return f"% {self.comment}\n{string_in}"
        return string_in

    def to_dict(self) -> dict[str, Any]:
        """Serialize this object to a plain dictionary.

        Returns:
            A dictionary containing ``label``, ``comment``, ``layer``,
            ``options``, and ``kwargs`` keys.
        """
        from tikzfigure.arrows import TikzArrow
        from tikzfigure.colors import TikzColor
        from tikzfigure.styles import TikzStyle
        from tikzfigure.units import TikzDimension

        def _serialize(v: object) -> object:
            if isinstance(v, (TikzArrow, TikzColor, TikzDimension, TikzStyle)):
                return str(v)
            return v

        return {
            "label": self._label,
            "comment": self._comment,
            "layer": self._layer,
            "options": list(self._options),
            "kwargs": {k: _serialize(v) for k, v in self._kwargs.items()},
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TikzObject":
        """Reconstruct a TikzObject from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new instance of the calling class populated from *d*.
        """
        kwargs = d.get("kwargs", {})
        return cls(
            label=d.get("label"),
            comment=d.get("comment"),
            layer=d.get("layer"),
            options=d.get("options"),
            **kwargs,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TikzObject):
            return NotImplemented
        return self.to_dict() == other.to_dict()
