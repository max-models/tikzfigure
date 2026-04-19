import math
from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import PositionInput, TikzCoordinate
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.options import OptionInput


class Polygon(TikzObject):
    """A TikZ polygon (regular n-sided shape) drawn with \\draw or \\filldraw.

    Attributes:
        center: Center coordinate of the polygon.
        radius: Distance from center to vertices.
        sides: Number of sides (n >= 3).
        rotation: Rotation angle in degrees from default orientation.
        tikz_command: The TikZ drawing command ("draw" or "filldraw").
    """

    def __init__(
        self,
        center: PositionInput,
        radius: float | str,
        sides: int,
        rotation: float = 0,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize a Polygon.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            radius: Distance from center to vertices (numeric or PGF expression string).
            sides: Number of sides (must be >= 3).
            rotation: Rotation angle in degrees. Defaults to 0.
            label: Internal TikZ name for this polygon. Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to 0.
            options: Flag-style TikZ options (e.g. ["thick"]).
            tikz_command: The TikZ drawing command, either "draw" or
                "filldraw". Defaults to "draw".
            **kwargs: Keyword-style TikZ options (e.g. color="red").
        """
        if options is None:
            options = []

        if sides < 3:
            raise ValueError("Polygon must have at least 3 sides")

        self._center = TikzCoordinate(center, layer=layer)

        self._radius = radius
        self._sides = sides
        self._rotation = rotation
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
        """Center coordinate of the polygon."""
        return self._center

    @property
    def radius(self) -> float | str:
        """Distance from center to vertices."""
        return self._radius

    @property
    def sides(self) -> int:
        """Number of sides."""
        return self._sides

    @property
    def rotation(self) -> float:
        """Rotation angle in degrees."""
        return self._rotation

    @property
    def tikz_command(self) -> str:
        """The TikZ drawing command ("draw" or "filldraw")."""
        return self._tikz_command

    def _get_vertices(self) -> list[tuple[str, str]]:
        """Calculate vertex coordinates for the polygon.

        Returns:
            List of (x, y) coordinate strings for each vertex.

        Raises:
            ValueError: If radius or center coordinates cannot be converted to float.
        """
        try:
            cx = float(self._center.x)
        except (ValueError, TypeError):
            raise ValueError(
                f"Center x-coordinate must be numeric, got: {self._center.x}"
            )
        try:
            cy = float(self._center.y)
        except (ValueError, TypeError):
            raise ValueError(
                f"Center y-coordinate must be numeric, got: {self._center.y}"
            )
        try:
            r = float(self._radius)
        except (ValueError, TypeError):
            raise ValueError(
                f"Radius must be numeric (not '{self._radius}'). "
                "Polygon vertices are calculated in Python, so expressions like '1cm' are not supported. "
                "Use numeric values instead (e.g., 1.0 for approximately 1cm at 72dpi)."
            )
        rot_rad = math.radians(self._rotation)

        vertices = []
        for i in range(self._sides):
            angle = 2 * math.pi * i / self._sides + rot_rad
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            vertices.append((str(x), str(y)))

        return vertices

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ polygon command.

        Returns:
            A \\draw or \\filldraw command string ending with a newline,
            optionally preceded by a comment line.
        """
        vertices = self._get_vertices()
        options = self.tikz_options(output_unit)

        # Build path from vertices
        path_parts = [f"({x}, {y})" for x, y in vertices]
        path_str = " -- ".join(path_parts) + " -- cycle"

        if options:
            full_options = f"[{options}]"
        else:
            full_options = ""

        polygon_str = f"\\{self.tikz_command}{full_options} {path_str};\n"
        polygon_str = self.add_comment(polygon_str)

        return polygon_str

    def to_dict(self) -> dict[str, Any]:
        """Serialize this polygon to a plain dictionary.

        Returns:
            A dictionary with type, center, radius, sides, rotation,
            tikz_command, and all base-class keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Polygon",
                "center": self._center.to_dict(),
                "radius": self._radius,
                "sides": self._sides,
                "rotation": self._rotation,
                "tikz_command": self._tikz_command,
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized polygon data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Polygon":
        """Reconstruct a Polygon from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Polygon instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized polygon data must deserialize to a dict.")
        center = TikzCoordinate.from_dict(restored["center"])
        return cls(
            center=center,
            radius=restored["radius"],
            sides=restored["sides"],
            rotation=restored.get("rotation", 0),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options", []),
            tikz_command=restored.get("tikz_command", "draw"),
            **restored.get("kwargs", {}),
        )


class Triangle(Polygon):
    """A regular triangle (equilateral).

    Convenience subclass of Polygon with sides=3.
    """

    def __init__(
        self,
        center: PositionInput,
        radius: float | str,
        rotation: float = 0,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize a Triangle.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            radius: Distance from center to vertices.
            rotation: Rotation angle in degrees. Defaults to 0.
            label: Internal TikZ name. Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to 0.
            options: Flag-style TikZ options.
            tikz_command: The TikZ drawing command, either "draw" or "filldraw".
            **kwargs: Keyword-style TikZ options.
        """
        super().__init__(
            center=center,
            radius=radius,
            sides=3,
            rotation=rotation,
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            tikz_command=tikz_command,
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize this triangle to a plain dictionary.

        Returns:
            A dictionary with type="Triangle" and all base-class keys.
        """
        d = super().to_dict()
        d["type"] = "Triangle"
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized triangle data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Triangle":
        """Reconstruct a Triangle from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Triangle instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized triangle data must deserialize to a dict.")
        center = TikzCoordinate.from_dict(restored["center"])
        return cls(
            center=center,
            radius=restored["radius"],
            rotation=restored.get("rotation", 0),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options", []),
            tikz_command=restored.get("tikz_command", "draw"),
            **restored.get("kwargs", {}),
        )


class Square(Polygon):
    """A square (4-sided regular polygon).

    Convenience subclass of Polygon with sides=4.
    """

    def __init__(
        self,
        center: PositionInput,
        radius: float | str,
        rotation: float = 45,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        tikz_command: str = "draw",
        **kwargs: Any,
    ) -> None:
        """Initialize a Square.

        Args:
            center: Center coordinate as an ``(x, y)`` / ``(x, y, z)`` tuple or
                :class:`TikzCoordinate`.
            radius: Distance from center to vertices (corner-to-center distance).
            rotation: Rotation angle in degrees. Defaults to 45 (axis-aligned).
            label: Internal TikZ name. Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to 0.
            options: Flag-style TikZ options.
            tikz_command: The TikZ drawing command, either "draw" or "filldraw".
            **kwargs: Keyword-style TikZ options.
        """
        super().__init__(
            center=center,
            radius=radius,
            sides=4,
            rotation=rotation,
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            tikz_command=tikz_command,
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize this square to a plain dictionary.

        Returns:
            A dictionary with type="Square" and all base-class keys.
        """
        d = super().to_dict()
        d["type"] = "Square"
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized square data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Square":
        """Reconstruct a Square from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Square instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized square data must deserialize to a dict.")
        center = TikzCoordinate.from_dict(restored["center"])
        return cls(
            center=center,
            radius=restored["radius"],
            rotation=restored.get("rotation", 45),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options", []),
            tikz_command=restored.get("tikz_command", "draw"),
            **restored.get("kwargs", {}),
        )
