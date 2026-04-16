from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import PositionInput, TikzCoordinate


class Arc(TikzObject):
    """A TikZ arc drawn with \\draw arc or \\filldraw arc.

    Attributes:
        start: Starting coordinate as a TikzCoordinate or (x, y) tuple.
        start_angle: Start angle in degrees.
        end_angle: End angle in degrees.
        radius: Radius of the arc.
        tikz_command: The TikZ drawing command ("draw" or "filldraw").
    """

    def __init__(
        self,
        start: PositionInput,
        start_angle: float,
        end_angle: float,
        radius: float | str,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: list | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize an Arc.

        Args:
            start: Starting coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            start_angle: Start angle in degrees.
            end_angle: End angle in degrees.
            radius: Radius of the arc (numeric or PGF expression string).
            label: Internal TikZ name for this arc. Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to 0.
            options: Flag-style TikZ options (e.g. ["->", "thick"]).
            tikz_command: The TikZ drawing command, either "draw" or
                "filldraw". Defaults to "draw".
            **kwargs: Keyword-style TikZ options (e.g. color="red").
        """
        if options is None:
            options = []

        self._start = TikzCoordinate(start, layer=layer)

        self._start_angle = start_angle
        self._end_angle = end_angle
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
    def start(self) -> TikzCoordinate:
        """Starting coordinate of the arc."""
        return self._start

    @property
    def start_angle(self) -> float:
        """Start angle in degrees."""
        return self._start_angle

    @property
    def end_angle(self) -> float:
        """End angle in degrees."""
        return self._end_angle

    @property
    def radius(self) -> float | str:
        """Radius of the arc."""
        return self._radius

    @property
    def tikz_command(self) -> str:
        """The TikZ drawing command ("draw" or "filldraw")."""
        return self._tikz_command

    def to_tikz(self) -> str:
        """Generate the TikZ arc command for this arc.

        Returns:
            A \\draw or \\filldraw command string ending with a newline,
            optionally preceded by a comment line.
        """
        options = self.tikz_options

        arc_options = f"start angle={self._start_angle}, end angle={self._end_angle}, radius={self._radius}"

        if options:
            full_options = f"{options}, {arc_options}"
        else:
            full_options = arc_options

        arc_str = f"\\{self.tikz_command}[{full_options}] {self.start.to_tikz()} arc;\n"
        arc_str = self.add_comment(arc_str)

        return arc_str

    def to_dict(self) -> dict[str, Any]:
        """Serialize this arc to a plain dictionary.

        Returns:
            A dictionary with type, start, angles, radius, tikz_command,
            and all base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Arc",
                "start": self._start.to_dict(),
                "start_angle": self._start_angle,
                "end_angle": self._end_angle,
                "radius": self._radius,
                "tikz_command": self._tikz_command,
            }
        )
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Arc":
        """Reconstruct an Arc from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Arc instance.
        """
        start = TikzCoordinate.from_dict(d["start"])
        return cls(
            start=start,
            start_angle=d["start_angle"],
            end_angle=d["end_angle"],
            radius=d["radius"],
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
                    "start",
                    "start_angle",
                    "end_angle",
                    "radius",
                    "label",
                    "comment",
                    "layer",
                    "options",
                    "tikz_command",
                    "kwargs",
                ]
            },
        )
