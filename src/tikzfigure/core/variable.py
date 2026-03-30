from typing import Any

from tikzfigure.core.base import TikzObject


class Variable(TikzObject):
    """A named pgfmath variable (``\\pgfmathsetmacro``) in a TikZ figure.

    Variables are emitted at the top of the ``tikzpicture`` environment so
    they can be referenced throughout the figure.

    Attributes:
        value: The numeric value assigned to this variable.
    """

    def __init__(
        self,
        label: str,
        value: int | float,
        layer: int | None = 0,
        comment: str | None = None,
    ) -> None:
        """Initialize a Variable.

        Args:
            label: Name of the pgfmath variable (without the leading
                backslash), e.g. ``"radius"``.
            value: Numeric value to assign to the variable.
            layer: Layer index this variable belongs to. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.
        """
        super().__init__(label=label, layer=layer, comment=comment)
        self._value = value

    def to_tikz(self) -> str:
        """Return the TikZ representation of this variable.

        Returns:
            A TikZ comment placeholder (variable emission is handled by
            :meth:`TikzFigure.generate_tikz`).
        """
        return "% Hi\n"

    @property
    def value(self) -> int | float:
        """The numeric value assigned to this variable."""
        return self._value

    def to_dict(self) -> dict[str, Any]:
        """Serialize this variable to a plain dictionary.

        Returns:
            A dictionary with ``type``, ``value``, and all base-class keys.
        """
        d = super().to_dict()
        d.update({"type": "Variable", "value": self._value})
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Variable":
        """Reconstruct a Variable from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Variable` instance.
        """
        return cls(
            label=d["label"],
            value=d["value"],
            layer=d.get("layer", 0),
            comment=d.get("comment"),
        )
