from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import PositionInput, TikzCoordinate
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.options import OptionInput


class Grid(TikzObject):
    """A TikZ grid drawn with \\draw grid.

    Attributes:
        corner1: First corner coordinate.
        corner2: Second corner coordinate (opposite corner).
        step: Grid step size (single value for uniform grid, or "x_step,y_step").
        tikz_command: The TikZ drawing command ("draw" or "filldraw").
    """

    def __init__(
        self,
        corner1: PositionInput,
        corner2: PositionInput,
        step: str | None = None,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize a Grid.

        Args:
            corner1: First corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            corner2: Opposite corner as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            step: Grid step size (e.g. "1cm" or "0.5cm,1cm"). If None, defaults
                to TikZ default (1cm).
            label: Internal TikZ name for this grid. Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to 0.
            options: Flag-style TikZ options (e.g. ["thick"]).
            tikz_command: The TikZ drawing command, either "draw" or
                "filldraw". Defaults to "draw".
            **kwargs: Keyword-style TikZ options (e.g. color="red").
        """
        if options is None:
            options = []

        self._corner1 = TikzCoordinate(corner1, layer=layer)
        self._corner2 = TikzCoordinate(corner2, layer=layer)

        self._step = step
        self._tikz_command = tikz_command

        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def corner1(self) -> TikzCoordinate:
        """First corner coordinate of the grid."""
        return self._corner1

    @property
    def corner2(self) -> TikzCoordinate:
        """Second (opposite) corner coordinate of the grid."""
        return self._corner2

    @property
    def step(self) -> str | None:
        """Grid step size."""
        return self._step

    @property
    def tikz_command(self) -> str:
        """The TikZ drawing command ("draw" or "filldraw")."""
        return self._tikz_command

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ grid command for this grid.

        Returns:
            A \\draw command string ending with a newline,
            optionally preceded by a comment line.
        """
        options = self.tikz_options(output_unit)

        # Add step to options if specified
        if self._step is not None:
            if options:
                options = f"{options}, step={self._step}"
            else:
                options = f"step={self._step}"

        if options:
            full_options = f"[{options}]"
        else:
            full_options = ""

        grid_str = f"\\{self.tikz_command}{full_options} {self.corner1.to_tikz(output_unit)} grid {self.corner2.to_tikz(output_unit)};\n"
        grid_str = self.add_comment(grid_str)

        return grid_str

    def to_dict(self) -> dict[str, Any]:
        """Serialize this grid to a plain dictionary.

        Returns:
            A dictionary with type, corners, step, tikz_command,
            and all base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Grid",
                "corner1": self._corner1.to_dict(),
                "corner2": self._corner2.to_dict(),
                "step": self._step,
                "tikz_command": self._tikz_command,
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized grid data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Grid":
        """Reconstruct a Grid from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Grid instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized grid data must deserialize to a dict.")
        corner1 = TikzCoordinate.from_dict(restored["corner1"])
        corner2 = TikzCoordinate.from_dict(restored["corner2"])
        return cls(
            corner1=corner1,
            corner2=corner2,
            step=restored.get("step"),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options", []),
            tikz_command=restored.get("tikz_command", "draw"),
            **restored.get("kwargs", {}),
        )
