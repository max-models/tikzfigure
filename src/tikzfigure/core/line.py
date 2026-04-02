from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import TikzCoordinate


class Line(TikzObject):
    """A TikZ line segment drawn with \\draw.

    Attributes:
        start: Starting point coordinate.
        end: Ending point coordinate.
    """

    def __init__(
        self,
        start: tuple[float | str, float | str] | TikzCoordinate,
        end: tuple[float | str, float | str] | TikzCoordinate,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: list | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Line.

        Args:
            start: Starting point as (x, y) tuple or TikzCoordinate.
            end: Ending point as (x, y) tuple or TikzCoordinate.
            label: Internal TikZ name for this line. Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to 0.
            options: Flag-style TikZ options (e.g. ["->", "thick"]).
            **kwargs: Keyword-style TikZ options (e.g. color="red").
        """
        if options is None:
            options = []

        if isinstance(start, tuple):
            self._start = TikzCoordinate(start[0], start[1], layer=layer)
        else:
            self._start = start

        if isinstance(end, tuple):
            self._end = TikzCoordinate(end[0], end[1], layer=layer)
        else:
            self._end = end

        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def start(self) -> TikzCoordinate:
        """Starting point of the line."""
        return self._start

    @property
    def end(self) -> TikzCoordinate:
        """Ending point of the line."""
        return self._end

    def to_tikz(self) -> str:
        """Generate the TikZ line command.

        Returns:
            A \\draw command string ending with a newline,
            optionally preceded by a comment line.
        """
        start_parts = ", ".join(str(x) for x in self._start.coordinate)
        end_parts = ", ".join(str(x) for x in self._end.coordinate)
        options = self.tikz_options

        if options:
            full_options = f"[{options}]"
        else:
            full_options = ""

        line_str = f"\\draw{full_options} ({start_parts}) -- ({end_parts});\n"
        line_str = self.add_comment(line_str)

        return line_str

    def intersection(self, other: "Line") -> tuple[float, float] | None:
        """Find the intersection point of two lines.

        Uses parametric line equations to find where two lines intersect.
        Returns None if lines are parallel or coincident.

        Args:
            other: Another Line object.

        Returns:
            The (x, y) intersection point, or None if no intersection exists.
        """
        # Extract numeric coordinates
        x1, y1 = float(self._start.x), float(self._start.y)
        x2, y2 = float(self._end.x), float(self._end.y)
        x3, y3 = float(other._start.x), float(other._start.y)
        x4, y4 = float(other._end.x), float(other._end.y)

        # Direction vectors
        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = x4 - x3
        dy2 = y4 - y3

        # Cross product (determinant)
        denom = dx1 * dy2 - dy1 * dx2

        # Lines are parallel (or coincident) if determinant is ~0
        if abs(denom) < 1e-10:
            return None

        # Solve for intersection using parametric equations
        # Line 1: (x1, y1) + t * (dx1, dy1)
        # Line 2: (x3, y3) + s * (dx2, dy2)
        dx3 = x3 - x1
        dy3 = y3 - y1

        t = (dx3 * dy2 - dy3 * dx2) / denom

        # Calculate intersection point
        ix = x1 + t * dx1
        iy = y1 + t * dy1

        return (ix, iy)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this line to a plain dictionary.

        Returns:
            A dictionary with type, start, end, and all base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Line",
                "start": self._start.to_dict(),
                "end": self._end.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Line":
        """Reconstruct a Line from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Line instance.
        """
        start = TikzCoordinate.from_dict(d["start"])
        end = TikzCoordinate.from_dict(d["end"])
        return cls(
            start=start,
            end=end,
            label=d.get("label", ""),
            comment=d.get("comment"),
            layer=d.get("layer", 0),
            options=d.get("options", []),
            **{
                k: v
                for k, v in d.items()
                if k
                not in [
                    "type",
                    "start",
                    "end",
                    "label",
                    "comment",
                    "layer",
                    "options",
                    "kwargs",
                ]
            },
        )
