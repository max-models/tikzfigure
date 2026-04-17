from typing import Any

from tikzfigure.colors import ColorInput


class Color:
    """Represents a TikZ color definition used with ``\\colorlet``.

    Attributes:
        color_spec: The raw TikZ color specification string.
    """

    def __init__(self, color_spec: ColorInput) -> None:
        """Initialize a Color.

        Args:
            color_spec: A TikZ color specification, such as a named color
                (``"blue"``), a mixed color (``"blue!20"``), or any other
                string accepted by ``\\colorlet`` in LaTeX.
        """
        self._color_spec = color_spec

    @property
    def color_spec(self) -> str:
        """The raw TikZ color specification string."""
        return str(self._color_spec)

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Return the raw color specification."""
        return self.color_spec

    def to_dict(self) -> dict[str, Any]:
        """Serialize this color to a plain dictionary.

        Returns:
            A dictionary with ``type`` and ``color_spec`` keys.
        """
        return {"type": "Color", "color_spec": self.color_spec}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Color":
        """Reconstruct a Color from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Color` instance.
        """
        return cls(color_spec=d["color_spec"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return self.to_dict() == other.to_dict()
