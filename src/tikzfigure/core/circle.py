from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import PositionInput, TikzCoordinate
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.options import OptionInput


class Circle(TikzObject):
    """A TikZ circle drawn with \\draw circle or \\filldraw circle.

    Attributes:
        center: Center coordinate as a TikzCoordinate or (x, y) tuple.
        radius: Radius of the circle.
        tikz_command: The TikZ drawing command ("draw" or "filldraw").
    """

    def __init__(
        self,
        center: PositionInput,
        radius: float | str,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize a Circle.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            radius: Radius of the circle (numeric or PGF expression string).
            label: Internal TikZ name for this circle. Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to 0.
            options: Flag-style TikZ options (e.g. ["thick"]).
            tikz_command: The TikZ drawing command, either "draw" or
                "filldraw". Defaults to "draw".
            **kwargs: Keyword-style TikZ options (e.g. color="red").
        """
        if options is None:
            options = []

        self._center = TikzCoordinate(center, layer=layer)

        self._radius = radius
        self._tikz_command = tikz_command

        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def center(self) -> TikzCoordinate:
        """Center coordinate of the circle."""
        return self._center

    @property
    def radius(self) -> float | str:
        """Radius of the circle."""
        return self._radius

    @property
    def tikz_command(self) -> str:
        """The TikZ drawing command ("draw" or "filldraw")."""
        return self._tikz_command

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ circle command for this circle.

        Returns:
            A \\draw or \\filldraw command string ending with a newline,
            optionally preceded by a comment line.
        """
        options = self.tikz_options(output_unit)

        if options:
            full_options = f"[{options}]"
        else:
            full_options = ""

        circle_str = f"\\{self.tikz_command}{full_options} {self.center.to_tikz(output_unit)} circle ({self._radius});\n"
        circle_str = self.add_comment(circle_str)

        return circle_str

    def to_dict(self) -> dict[str, Any]:
        """Serialize this circle to a plain dictionary.

        Returns:
            A dictionary with type, center, radius, tikz_command,
            and all base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Circle",
                "center": self._center.to_dict(),
                "radius": self._radius,
                "tikz_command": self._tikz_command,
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized circle data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Circle":
        """Reconstruct a Circle from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Circle instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized circle data must deserialize to a dict.")
        center = TikzCoordinate.from_dict(restored["center"])
        return cls(
            center=center,
            radius=restored["radius"],
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options", []),
            tikz_command=restored.get("tikz_command", "draw"),
            **restored.get("kwargs", {}),
        )
