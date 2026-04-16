from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import PositionInput, TikzCoordinate


class Ellipse(TikzObject):
    """A TikZ ellipse drawn with \\draw ellipse or \\filldraw ellipse.

    Attributes:
        center: Center coordinate.
        x_radius: Horizontal radius.
        y_radius: Vertical radius.
        tikz_command: The TikZ drawing command ("draw" or "filldraw").
    """

    def __init__(
        self,
        center: PositionInput,
        x_radius: float | str,
        y_radius: float | str,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: list | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize an Ellipse.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            x_radius: Horizontal radius (numeric or PGF expression string).
            y_radius: Vertical radius (numeric or PGF expression string).
            label: Internal TikZ name for this ellipse. Defaults to "".
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

        self._x_radius = x_radius
        self._y_radius = y_radius
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
        """Center coordinate of the ellipse."""
        return self._center

    @property
    def x_radius(self) -> float | str:
        """Horizontal radius of the ellipse."""
        return self._x_radius

    @property
    def y_radius(self) -> float | str:
        """Vertical radius of the ellipse."""
        return self._y_radius

    @property
    def tikz_command(self) -> str:
        """The TikZ drawing command ("draw" or "filldraw")."""
        return self._tikz_command

    def to_tikz(self) -> str:
        """Generate the TikZ ellipse command for this ellipse.

        Returns:
            A \\draw or \\filldraw command string ending with a newline,
            optionally preceded by a comment line.
        """
        options = self.tikz_options

        if options:
            full_options = f"[{options}]"
        else:
            full_options = ""

        ellipse_str = f"\\{self.tikz_command}{full_options} {self.center.to_tikz()} ellipse ({self._x_radius} and {self._y_radius});\n"
        ellipse_str = self.add_comment(ellipse_str)

        return ellipse_str

    def to_dict(self) -> dict[str, Any]:
        """Serialize this ellipse to a plain dictionary.

        Returns:
            A dictionary with type, center, radii, tikz_command,
            and all base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Ellipse",
                "center": self._center.to_dict(),
                "x_radius": self._x_radius,
                "y_radius": self._y_radius,
                "tikz_command": self._tikz_command,
            }
        )
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Ellipse":
        """Reconstruct an Ellipse from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Ellipse instance.
        """
        center = TikzCoordinate.from_dict(d["center"])
        return cls(
            center=center,
            x_radius=d["x_radius"],
            y_radius=d["y_radius"],
            label=d.get("label", ""),
            comment=d.get("comment"),
            layer=d.get("layer", 0),
            options=d.get("options", []),
            tikz_command=d.get("tikz_command", "draw"),
            **{
                k: v
                for k, v in d.items()
                if k
                not in [
                    "type",
                    "center",
                    "x_radius",
                    "y_radius",
                    "label",
                    "comment",
                    "layer",
                    "options",
                    "tikz_command",
                    "kwargs",
                ]
            },
        )
