from typing import Any

from tikzfigure.core.base import TikzObject


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
        x: float | str | None = None,
        y: float | str | None = None,
        at: str | None = None,
        layer: int = 0,
        comment: str | None = None,
    ) -> None:
        """Initialize a Coordinate.

        Provide either numeric ``x`` and ``y`` coordinates, or a raw TikZ
        coordinate expression via ``at``.

        Args:
            label: TikZ name for this coordinate, used when referencing it
                in path lists and other commands.
            x: X-coordinate value (numeric or PGF expression string). Must
                be provided together with ``y``. Mutually exclusive with
                ``at``.
            y: Y-coordinate value (numeric or PGF expression string). Must
                be provided together with ``x``. Mutually exclusive with
                ``at``.
            at: Raw TikZ coordinate expression. Examples:

                * ``"$(A)!0.5!(B)$"`` — midpoint via ``calc`` library
                * ``"A.north"`` — at a node anchor
                * ``"30:2cm"`` — polar coordinates

                If the string does not begin with ``(``, parentheses are
                added automatically. Mutually exclusive with ``x``/``y``.
            layer: Layer index this coordinate belongs to. Defaults to ``0``.
            comment: Optional comment prepended in the TikZ output.

        Raises:
            ValueError: If both ``at`` and ``x``/``y`` are supplied, or if
                neither is supplied.
        """
        if at is not None and (x is not None or y is not None):
            raise ValueError(
                "Provide either x/y coordinates or an 'at' expression, not both."
            )
        if at is None and (x is None or y is None):
            raise ValueError("Provide both x and y coordinates, or an 'at' expression.")

        super().__init__(label=label, layer=layer, comment=comment)
        self._x = x
        self._y = y
        self._at = at

    @property
    def x(self) -> float | str | None:
        """X-coordinate value, or ``None`` if using an ``at`` expression."""
        return self._x

    @property
    def y(self) -> float | str | None:
        """Y-coordinate value, or ``None`` if using an ``at`` expression."""
        return self._y

    @property
    def at(self) -> str | None:
        """Raw TikZ coordinate expression, or ``None`` if using x/y."""
        return self._at

    def to_tikz(self) -> str:
        """Generate the TikZ ``\\coordinate`` declaration.

        Returns:
            A ``\\coordinate (label) at (...);`` string ending with a
            newline, optionally preceded by a comment line.
        """
        if self._at is not None:
            at_str = self._at if self._at.startswith("(") else f"({self._at})"
            coord_str = f"\\coordinate ({self.label}) at {at_str};\n"
        else:
            x_str = str(self._x)
            y_str = str(self._y)
            coord_str = f"\\coordinate ({self.label}) at ({{{x_str}}},{{{y_str}}});\n"
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
                "x": self._x,
                "y": self._y,
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
        x: float | str,
        y: float | str,
        z: float | str | None = None,
        layer: int = 0,
    ) -> None:
        """Initialize a TikzCoordinate.

        Args:
            x: X-coordinate value (numeric or PGF expression string).
            y: Y-coordinate value (numeric or PGF expression string).
            z: Z-coordinate value (numeric or PGF expression string).
                When provided, the coordinate is treated as 3-D.
                Defaults to ``None`` (2-D).
            layer: Layer index this coordinate belongs to. Defaults to ``0``.
        """
        super().__init__(layer=layer, comment=None)

        self._x = x
        self._y = y
        self._z = z
        if z is None:
            self._ndim = 2
        else:
            self._ndim = 3

    @property
    def x(self) -> float | str:
        """X-coordinate value (numeric or PGF expression string)."""
        return self._x

    @property
    def y(self) -> float | str:
        """Y-coordinate value (numeric or PGF expression string)."""
        return self._y

    @property
    def z(self) -> float | str | None:
        """Z-coordinate value (numeric or PGF expression string), or ``None`` for 2-D coordinates."""
        return self._z

    @property
    def coordinate(self) -> tuple[float | str, ...]:
        """Coordinate as a tuple, either ``(x, y)`` or ``(x, y, z)``."""
        if self.ndim == 2:
            return ((self.x), self.y)
        else:
            return (self.x, self.y, self.z)  # type: ignore[return-value]

    @property
    def ndim(self) -> int:
        """Number of spatial dimensions (``2`` or ``3``)."""
        return self._ndim

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
