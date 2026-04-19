from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, TypeAlias

from tikzfigure.core.base import TikzObject

if TYPE_CHECKING:
    from tikzfigure.core.node import Node
    from tikzfigure.core.path_builder import NodePathBuilder
    from tikzfigure.options import OptionInput
    from tikzfigure.units import TikzDimension

    CoordinateValue: TypeAlias = float | int | str | TikzDimension
else:
    CoordinateValue: TypeAlias = float | int | str
CoordinateTuple2D: TypeAlias = tuple[CoordinateValue, CoordinateValue]
CoordinateTuple3D: TypeAlias = tuple[CoordinateValue, CoordinateValue, CoordinateValue]


class Coordinate(TikzObject):
    """A named TikZ coordinate declared with ``\\coordinate``.

    Unlike a :class:`~tikzfigure.core.node.Node`, a coordinate has no
    visible output — it simply registers a named point in the figure that
    can be referenced in paths, calc expressions, or anywhere TikZ accepts a
    node label.

    Common uses:

    * Defining fixed reference points::

          fig.add_coordinate("origin", x=0, y=0)
          fig.draw(["origin", "A"])

    * Placing a point at the midpoint between two nodes (requires the
      ``calc`` TikZ library)::

          fig.add_coordinate("mid", at="$(A)!0.5!(B)$")
          fig.draw(["A", "mid", "B"])

    * Naming a point at a node anchor::

          fig.add_coordinate("atip", at="A.north")

    Attributes:
        label: The TikZ name for this coordinate.
        x: X value when using absolute positioning, or ``None``.
        y: Y value when using absolute positioning, or ``None``.
        at: Raw TikZ coordinate expression when using expression
            positioning, or ``None``.
    """

    def __init__(
        self,
        label: str,
        x: CoordinateValue
        | CoordinateTuple2D
        | CoordinateTuple3D
        | "TikzCoordinate"
        | None = None,
        y: CoordinateValue | None = None,
        z: CoordinateValue | None = None,
        at: str | None = None,
        layer: int = 0,
        comment: str | None = None,
    ) -> None:
        """Initialize a Coordinate.

        Provide either explicit coordinates, or a raw TikZ coordinate
        expression via ``at``.

        Args:
            label: TikZ name for this coordinate, used when referencing it
                in path lists and other commands.
            x: X-coordinate value, a ``(x, y)`` / ``(x, y, z)`` tuple, or a
                :class:`TikzCoordinate`. Must be provided together with ``y``
                when passed as a scalar. Mutually exclusive with ``at``.
            y: Y-coordinate value when passing explicit scalar coordinates.
                Mutually exclusive with ``at``.
            z: Z-coordinate value when passing explicit scalar coordinates.
                Mutually exclusive with ``at``.
            at: Raw TikZ coordinate expression. Examples:

                * ``"$(A)!0.5!(B)$"`` — midpoint via ``calc`` library
                * ``"A.north"`` — at a node anchor
                * ``"30:2cm"`` — polar coordinates

                If the string does not begin with ``(``, parentheses are
                added automatically. Mutually exclusive with ``x``/``y``.
            layer: Layer index this coordinate belongs to. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.

        Raises:
            ValueError: If both ``at`` and explicit coordinates are supplied,
                or if neither is supplied.
        """
        if at is not None and (x is not None or y is not None or z is not None):
            raise ValueError(
                "Provide either coordinates or an 'at' expression, not both."
            )

        super().__init__(label=label, layer=layer, comment=comment)
        self._at = at
        if at is not None:
            self._coordinate = None
        else:
            if x is None:
                raise ValueError(
                    "Provide both x and y coordinates, or pass a coordinate tuple/TikzCoordinate."
                )
            self._coordinate = TikzCoordinate(x=x, y=y, z=z, layer=layer)

    @property
    def x(self) -> CoordinateValue | None:
        """X-coordinate value, or ``None`` if using an ``at`` expression."""
        if self._coordinate is None:
            return None
        return self._coordinate.x

    @property
    def y(self) -> CoordinateValue | None:
        """Y-coordinate value, or ``None`` if using an ``at`` expression."""
        if self._coordinate is None:
            return None
        return self._coordinate.y

    @property
    def z(self) -> CoordinateValue | None:
        """Z-coordinate value, or ``None`` for 2-D / ``at`` coordinates."""
        if self._coordinate is None:
            return None
        return self._coordinate.z

    def to(
        self,
        target: "Node | Coordinate",
        options: "OptionInput | None" = None,
        **kwargs: Any,
    ) -> "NodePathBuilder":
        """Create a path builder for a segment from this coordinate to ``target``.

        The returned builder always starts with ``self`` and records the segment
        options for the edge from ``self`` to ``target``. Chain additional
        ``.to(...)`` or ``.arc(...)`` calls on the builder to add more path
        segments. Only :class:`~tikzfigure.core.node.Node` and
        :class:`Coordinate` targets are accepted by ``.to(...)``.
        """
        from tikzfigure.core.path_builder import NodePathBuilder

        return NodePathBuilder(self).to(target, options=options, **kwargs)

    @property
    def ndim(self) -> int:
        """Number of spatial dimensions (``2`` or ``3``)."""
        if self._coordinate is None:
            return 2
        return self._coordinate.ndim

    @property
    def at(self) -> str | None:
        """Raw TikZ coordinate expression, or ``None`` if using x/y."""
        return self._at

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the TikZ ``\\coordinate`` declaration.

        Returns:
            A ``\\coordinate (label) at (...);`` string ending with a
            newline, optionally preceded by a comment line.
        """
        if self._at is not None:
            at_str = self._at if self._at.startswith("(") else f"({self._at})"
            coord_str = f"\\coordinate ({self.label}) at {at_str};\n"
        else:
            assert self._coordinate is not None
            coord_str = f"\\coordinate ({self.label}) at {self._coordinate.to_tikz(output_unit)};\n"
        return self.add_comment(coord_str)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this coordinate to a plain dictionary.

        Returns:
            A dictionary with ``type``, ``label``, ``x``, ``y``, ``at``,
            ``layer``, and ``comment`` keys.
        """
        d = super().to_dict()
        d.update(
            {
                "type": "Coordinate",
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "at": self._at,
            }
        )
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Coordinate":
        """Reconstruct a Coordinate from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Coordinate` instance.
        """
        return cls(
            label=d.get("label", ""),
            x=d.get("x"),
            y=d.get("y"),
            z=d.get("z"),
            at=d.get("at"),
            layer=d.get("layer", 0),
            comment=d.get("comment"),
        )


class TikzCoordinate(TikzObject):
    """A bare coordinate point (no drawn node) in a TikZ figure.

    Used to define path waypoints without producing visible nodes.

    Attributes:
        x: X-coordinate value (numeric or PGF expression string).
        y: Y-coordinate value (numeric or PGF expression string).
        z: Z-coordinate value, or ``None`` for 2-D figures.
        ndim: Number of dimensions (``2`` or ``3``).
        coordinate: Coordinate as a tuple ready for TikZ output.
    """

    def __init__(
        self,
        x: CoordinateValue | CoordinateTuple2D | CoordinateTuple3D | "TikzCoordinate",
        y: CoordinateValue | None = None,
        z: CoordinateValue | None = None,
        layer: int = 0,
    ) -> None:
        """Initialize a TikzCoordinate.

        Args:
            x: X-coordinate value, a ``(x, y)`` / ``(x, y, z)`` tuple, or an
                existing :class:`TikzCoordinate`.
            y: Y-coordinate value when passing explicit scalar coordinates.
            z: Z-coordinate value when passing explicit scalar coordinates.
                When provided, the coordinate is treated as 3-D. Defaults to
                ``None`` (2-D).
            layer: Layer index this coordinate belongs to. Defaults to ``0``.
        """
        super().__init__(layer=layer)
        self._x, self._y, self._z = self._normalize_coordinate_values(x=x, y=y, z=z)
        self._ndim = 2 if self._z is None else 3

    @staticmethod
    def _normalize_coordinate_values(
        x: CoordinateValue | CoordinateTuple2D | CoordinateTuple3D | "TikzCoordinate",
        y: CoordinateValue | None = None,
        z: CoordinateValue | None = None,
    ) -> tuple[CoordinateValue, CoordinateValue, CoordinateValue | None]:
        """Normalize scalar, tuple, and TikzCoordinate inputs."""
        if isinstance(x, TikzCoordinate):
            if y is not None or z is not None:
                raise ValueError("When x is a TikzCoordinate, do not also pass y or z.")
            return x.x, x.y, x.z

        if isinstance(x, tuple):
            if y is not None or z is not None:
                raise ValueError(
                    "When x is a coordinate tuple, do not also pass y or z."
                )
            if len(x) == 2:
                return x[0], x[1], None
            if len(x) == 3:
                return x[0], x[1], x[2]
            raise ValueError(
                "Coordinate tuples passed to TikzCoordinate must have length 2 or 3."
            )

        if y is None:
            raise ValueError(
                "Provide both x and y coordinates, or pass a coordinate tuple/TikzCoordinate."
            )
        return x, y, z

    @property
    def x(self) -> CoordinateValue:
        """X-coordinate value (numeric or PGF expression string)."""
        return self._x

    @property
    def y(self) -> CoordinateValue:
        """Y-coordinate value (numeric or PGF expression string)."""
        return self._y

    @property
    def z(self) -> CoordinateValue | None:
        """Z-coordinate value (numeric or PGF expression string), or ``None`` for 2-D coordinates."""
        return self._z

    @property
    def coordinate(self) -> tuple[CoordinateValue, ...]:
        """Coordinate as a tuple, either ``(x, y)`` or ``(x, y, z)``."""
        if self.ndim == 2:
            return ((self.x), self.y)
        else:
            return (self.x, self.y, self.z)  # type: ignore[return-value]

    @property
    def ndim(self) -> int:
        """Number of spatial dimensions (``2`` or ``3``)."""
        return self._ndim

    @staticmethod
    def _format_component(
        value: CoordinateValue, output_unit: str | None = None
    ) -> str:
        """Format one coordinate component for TikZ output."""
        from tikzfigure.units import TikzDimension

        if isinstance(value, TikzDimension):
            return str(value.to(output_unit)) if output_unit is not None else str(value)
        value_str = str(value)
        if (
            value_str.startswith("(")
            and value_str.endswith(")")
            and not value_str.startswith("((")
        ):
            value_str = value_str[1:-1]
        return value_str

    def _numeric_components(self, operation: str) -> tuple[float, ...]:
        """Return numeric components for linear algebra operations."""
        numeric_components: list[float] = []
        for value in self.coordinate:
            try:
                numeric_components.append(float(value))
            except (TypeError, ValueError) as exc:
                raise TypeError(
                    f"{self.__class__.__name__} {operation} requires numeric coordinates, got {value!r}."
                ) from exc
        return tuple(numeric_components)

    def _validate_same_dimension(
        self, other: TikzCoordinate | TikzVector, operation: str
    ) -> None:
        """Ensure both operands share the same dimension."""
        if self.ndim != other.ndim:
            raise ValueError(
                f"Cannot {operation} operands with different dimensions: {self.ndim}D and {other.ndim}D."
            )

    def _coordinate_from_numeric_components(
        self, components: tuple[float, ...]
    ) -> TikzCoordinate:
        """Build a point from numeric components while preserving dimension."""
        if len(components) == 2:
            return TikzCoordinate(components[0], components[1], layer=self.layer or 0)
        if len(components) == 3:
            return TikzCoordinate(
                components[0],
                components[1],
                components[2],
                layer=self.layer or 0,
            )
        raise ValueError("Coordinates must be 2-D or 3-D.")

    def _vector_from_numeric_components(
        self, components: tuple[float, ...]
    ) -> TikzVector:
        """Build a vector from numeric components while preserving dimension."""
        if len(components) == 2:
            return TikzVector(components[0], components[1], layer=self.layer or 0)
        if len(components) == 3:
            return TikzVector(
                components[0],
                components[1],
                components[2],
                layer=self.layer or 0,
            )
        raise ValueError("Vectors must be 2-D or 3-D.")

    def to_vector(self) -> TikzVector:
        """Interpret this point as a vector from the origin."""
        return TikzVector(self, layer=self.layer or 0)

    def vector_to(self, other: TikzCoordinate) -> TikzVector:
        """Return the vector from this point to another point."""
        self._validate_same_dimension(other, "subtract")
        point_a = self._numeric_components("subtraction")
        point_b = other._numeric_components("subtraction")
        return self._vector_from_numeric_components(
            tuple(b - a for a, b in zip(point_a, point_b, strict=True))
        )

    def distance_to(self, other: TikzCoordinate) -> float:
        """Return the Euclidean distance to another point."""
        return self.vector_to(other).norm()

    def translate(self, vector: TikzVector) -> TikzCoordinate:
        """Return the translated point."""
        return self + vector

    def __add__(self, other: TikzVector) -> TikzCoordinate:
        if not isinstance(other, TikzVector):
            return NotImplemented
        self._validate_same_dimension(other, "add")
        point = self._numeric_components("addition")
        vector = other._numeric_components("addition")
        return self._coordinate_from_numeric_components(
            tuple(a + b for a, b in zip(point, vector, strict=True))
        )

    def __sub__(
        self, other: TikzCoordinate | TikzVector
    ) -> TikzCoordinate | TikzVector:
        if isinstance(other, TikzVector):
            self._validate_same_dimension(other, "subtract")
            point = self._numeric_components("subtraction")
            vector = other._numeric_components("subtraction")
            return self._coordinate_from_numeric_components(
                tuple(a - b for a, b in zip(point, vector, strict=True))
            )
        if isinstance(other, TikzCoordinate):
            self._validate_same_dimension(other, "subtract")
            point_a = self._numeric_components("subtraction")
            point_b = other._numeric_components("subtraction")
            return self._vector_from_numeric_components(
                tuple(a - b for a, b in zip(point_a, point_b, strict=True))
            )
        return NotImplemented

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Render this coordinate as a TikZ position expression."""
        # 2-D coordinate: render as (x, y)
        x_str = self._format_component(self.x, output_unit)
        y_str = self._format_component(self.y, output_unit)
        if self.ndim == 2:
            return f"({{{x_str}}}, {{{y_str}}})"

        # 3-D coordinate: use axis cs for proper layering in 3D plots
        assert self.z is not None
        z_str = self._format_component(self.z, output_unit)
        return f"(axis cs:{{{x_str}}}, {{{y_str}}}, {{{z_str}}})"

    def to_dict(self) -> dict[str, Any]:
        """Serialize this coordinate to a plain dictionary.

        Returns:
            A dictionary with ``type``, ``x``, ``y``, ``z``, and ``layer``
            keys.
        """
        return {
            "type": "TikzCoordinate",
            "x": self._x,
            "y": self._y,
            "z": self._z,
            "layer": self._layer,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TikzCoordinate":
        """Reconstruct a TikzCoordinate from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`TikzCoordinate` instance.
        """
        return cls(x=d["x"], y=d["y"], z=d.get("z"), layer=d.get("layer", 0))


class TikzVector(TikzCoordinate):
    """A geometric vector used for linear algebra operations."""

    def dot(self, other: TikzVector) -> float:
        """Return the dot product with another vector."""
        if not isinstance(other, TikzVector):
            raise TypeError(
                "Dot product is only defined between two TikzVector objects."
            )
        self._validate_same_dimension(other, "compute a dot product for")
        return sum(
            a * b
            for a, b in zip(
                self._numeric_components("dot product"),
                other._numeric_components("dot product"),
                strict=True,
            )
        )

    def cross(self, other: TikzVector) -> TikzVector:
        """Return the cross product with another vector."""
        if not isinstance(other, TikzVector):
            raise TypeError(
                "Cross product is only defined between two TikzVector objects."
            )
        if self.ndim != 3 or other.ndim != 3:
            raise ValueError("Cross product is only defined for 3-D vectors.")

        ax, ay, az = self._numeric_components("cross product")
        bx, by, bz = other._numeric_components("cross product")
        return TikzVector(
            (
                ay * bz - az * by,
                az * bx - ax * bz,
                ax * by - ay * bx,
            ),
            layer=self.layer or 0,
        )

    def norm(self) -> float:
        """Return the Euclidean norm."""
        return math.sqrt(self.dot(self))

    def magnitude(self) -> float:
        """Return the Euclidean norm."""
        return self.norm()

    def __add__(self, other: TikzVector) -> TikzVector:
        if not isinstance(other, TikzVector):
            return NotImplemented
        self._validate_same_dimension(other, "add")
        return self._vector_from_numeric_components(
            tuple(
                a + b
                for a, b in zip(
                    self._numeric_components("addition"),
                    other._numeric_components("addition"),
                    strict=True,
                )
            )
        )

    def __radd__(self, other: TikzCoordinate) -> TikzCoordinate | TikzVector:
        if isinstance(other, TikzCoordinate) and not isinstance(other, TikzVector):
            other._validate_same_dimension(self, "add")
            point = other._numeric_components("addition")
            vector = self._numeric_components("addition")
            return other._coordinate_from_numeric_components(
                tuple(a + b for a, b in zip(point, vector, strict=True))
            )
        return self.__add__(other)

    def __sub__(
        self, other: TikzCoordinate | TikzVector
    ) -> TikzVector | TikzCoordinate:
        if not isinstance(other, TikzVector):
            return NotImplemented
        self._validate_same_dimension(other, "subtract")
        return self._vector_from_numeric_components(
            tuple(
                a - b
                for a, b in zip(
                    self._numeric_components("subtraction"),
                    other._numeric_components("subtraction"),
                    strict=True,
                )
            )
        )

    def __mul__(self, scalar: float | int) -> TikzVector:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return self._vector_from_numeric_components(
            tuple(
                component * scalar for component in self._numeric_components("scaling")
            )
        )

    def __rmul__(self, scalar: float | int) -> TikzVector:
        return self * scalar

    def __matmul__(self, other: TikzVector) -> float:
        return self.dot(other)

    def __neg__(self) -> TikzVector:
        return -1 * self

    def to_dict(self) -> dict[str, Any]:
        """Serialize this vector to a plain dictionary."""
        d = super().to_dict()
        d["type"] = "TikzVector"
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TikzVector":
        """Reconstruct a TikzVector from a dictionary."""
        return cls(x=d["x"], y=d["y"], z=d.get("z"), layer=d.get("layer", 0))


PositionInput: TypeAlias = CoordinateTuple2D | CoordinateTuple3D | TikzCoordinate
VectorInput: TypeAlias = CoordinateTuple2D | CoordinateTuple3D | TikzVector
