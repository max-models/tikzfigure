from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import PositionInput, TikzCoordinate


class Parabola(TikzObject):
    """A TikZ parabola drawn with \\draw parabola or \\filldraw parabola.

    Attributes:
        start: Starting coordinate.
        end: Ending coordinate.
        bend: Bend point (control point), or None for default bend.
        tikz_command: The TikZ drawing command ("draw" or "filldraw").
    """

    def __init__(
        self,
        start: PositionInput,
        end: PositionInput,
        bend: PositionInput | None = None,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: list | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize a Parabola.

        Args:
            start: Starting coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            end: Ending coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            bend: Bend point as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
                If None, uses default TikZ behavior. Defaults to None.
            label: Internal TikZ name for this parabola. Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to 0.
            options: Flag-style TikZ options (e.g. ["thick"]).
            tikz_command: The TikZ drawing command, either "draw" or
                "filldraw". Defaults to "draw".
            **kwargs: Keyword-style TikZ options (e.g. color="red").
        """
        if options is None:
            options = []

        self._start = TikzCoordinate(start, layer=layer)
        self._end = TikzCoordinate(end, layer=layer)
        self._bend = TikzCoordinate(bend, layer=layer) if bend is not None else None

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
        """Starting coordinate of the parabola."""
        return self._start

    @property
    def end(self) -> TikzCoordinate:
        """Ending coordinate of the parabola."""
        return self._end

    @property
    def bend(self) -> TikzCoordinate | None:
        """Bend (control) point of the parabola, or None."""
        return self._bend

    @property
    def tikz_command(self) -> str:
        """The TikZ drawing command ("draw" or "filldraw")."""
        return self._tikz_command

    def to_tikz(self) -> str:
        """Generate the TikZ parabola command for this parabola.

        Returns:
            A \\draw or \\filldraw command string ending with a newline,
            optionally preceded by a comment line.
        """
        options = self.tikz_options

        if options:
            full_options = f"[{options}]"
        else:
            full_options = ""

        if self._bend is not None:
            parabola_str = f"\\{self.tikz_command}{full_options} {self.start.to_tikz()} parabola bend {self._bend.to_tikz()} {self.end.to_tikz()};\n"
        else:
            parabola_str = f"\\{self.tikz_command}{full_options} {self.start.to_tikz()} parabola {self.end.to_tikz()};\n"

        parabola_str = self.add_comment(parabola_str)

        return parabola_str

    def to_dict(self) -> dict[str, Any]:
        """Serialize this parabola to a plain dictionary.

        Returns:
            A dictionary with type, coordinates, tikz_command,
            and all base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Parabola",
                "start": self._start.to_dict(),
                "end": self._end.to_dict(),
                "bend": self._bend.to_dict() if self._bend is not None else None,
                "tikz_command": self._tikz_command,
            }
        )
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Parabola":
        """Reconstruct a Parabola from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Parabola instance.
        """
        start = TikzCoordinate.from_dict(d["start"])
        end = TikzCoordinate.from_dict(d["end"])
        bend = TikzCoordinate.from_dict(d["bend"]) if d.get("bend") else None
        return cls(
            start=start,
            end=end,
            bend=bend,
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
                    "end",
                    "bend",
                    "label",
                    "comment",
                    "layer",
                    "options",
                    "tikz_command",
                    "kwargs",
                ]
            },
        )
