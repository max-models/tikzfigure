from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import (
    PositionInput,
    TikzCoordinate,
    TikzVector,
    VectorInput,
)
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.core.types import _Option
from tikzfigure.options import OptionInput


class Line(TikzObject):
    """A TikZ line segment drawn with \\draw.

    Attributes:
        start: Starting point coordinate.
        end: Ending point coordinate.
    """

    def __init__(
        self,
        start: PositionInput,
        end: PositionInput,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Line.

        Args:
            start: Starting point as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            end: Ending point as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            label: Internal TikZ name for this line. Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to 0.
            options: Flag-style TikZ options (e.g. ["->", "thick"]).
            **kwargs: Keyword-style TikZ options (e.g. color="red").
        """
        if options is None:
            options = []

        self._start = TikzCoordinate(start, layer=layer)
        self._end = TikzCoordinate(end, layer=layer)

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

    @property
    def vector(self) -> TikzVector:
        """Vector from the start point to the end point."""
        return self.start.vector_to(self.end)

    @property
    def direction(self) -> TikzVector:
        """Alias for :attr:`vector`."""
        return self.vector

    @property
    def length(self) -> float:
        """Euclidean length of the line segment."""
        return self.vector.norm()

    def translate(self, vector: VectorInput) -> "Line":
        """Return a translated copy of this line."""
        offset = TikzVector(vector, layer=self.layer or 0)
        return Line(
            start=self.start + offset,
            end=self.end + offset,
            label=self.label or "",
            comment=self.comment,
            layer=self.layer or 0,
            options=[str(option) for option in self.options],
            **dict(self.kwargs),
        )

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ line command.

        Returns:
            A \\draw command string ending with a newline,
            optionally preceded by a comment line.
        """
        options = self.tikz_options(output_unit)

        if options:
            full_options = f"[{options}]"
        else:
            full_options = ""

        line_str = f"\\draw{full_options} {self.start.to_tikz(output_unit)} -- {self.end.to_tikz(output_unit)};\n"
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
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized line data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Line":
        """Reconstruct a Line from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Line instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized line data must deserialize to a dict.")
        start = TikzCoordinate.from_dict(restored["start"])
        end = TikzCoordinate.from_dict(restored["end"])
        return cls(
            start=start,
            end=end,
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options", []),
            **restored.get("kwargs", {}),
        )
