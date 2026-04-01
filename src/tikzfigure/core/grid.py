from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import TikzCoordinate


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
        corner1: tuple[float | str, float | str] | TikzCoordinate,
        corner2: tuple[float | str, float | str] | TikzCoordinate,
        step: str | None = None,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: list | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize a Grid.

        Args:
            corner1: First corner as (x, y) tuple or TikzCoordinate.
            corner2: Opposite corner as (x, y) tuple or TikzCoordinate.
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

        if isinstance(corner1, tuple):
            self._corner1 = TikzCoordinate(corner1[0], corner1[1], layer=layer)
        else:
            self._corner1 = corner1

        if isinstance(corner2, tuple):
            self._corner2 = TikzCoordinate(corner2[0], corner2[1], layer=layer)
        else:
            self._corner2 = corner2

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

    def to_tikz(self) -> str:
        """Generate the TikZ grid command for this grid.

        Returns:
            A \\draw command string ending with a newline,
            optionally preceded by a comment line.
        """
        c1_parts = ", ".join(str(x) for x in self._corner1.coordinate)
        c2_parts = ", ".join(str(x) for x in self._corner2.coordinate)
        options = self.tikz_options

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

        grid_str = (
            f"\\{self.tikz_command}{full_options} ({c1_parts}) grid ({c2_parts});\n"
        )
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
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Grid":
        """Reconstruct a Grid from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Grid instance.
        """
        corner1 = TikzCoordinate.from_dict(d["corner1"])
        corner2 = TikzCoordinate.from_dict(d["corner2"])
        return cls(
            corner1=corner1,
            corner2=corner2,
            step=d.get("step"),
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
                    "corner1",
                    "corner2",
                    "step",
                    "label",
                    "comment",
                    "layer",
                    "options",
                    "tikz_command",
                    "kwargs",
                ]
            },
        )
