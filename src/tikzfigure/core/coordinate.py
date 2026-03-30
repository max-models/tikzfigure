from typing import Any

from tikzfigure.core.base import TikzObject


class TikzCoordinate(TikzObject):
    """A bare coordinate point (no drawn node) in a TikZ figure.

    Used to define path waypoints without producing visible nodes.

    Attributes:
        x: X-coordinate value.
        y: Y-coordinate value.
        z: Z-coordinate value, or ``None`` for 2-D figures.
        ndim: Number of dimensions (``2`` or ``3``).
        coordinate: Coordinate as a tuple ready for TikZ output.
    """

    def __init__(
        self,
        x: float,
        y: float,
        z: float | None = None,
        layer: int = 0,
    ) -> None:
        """Initialize a TikzCoordinate.

        Args:
            x: X-coordinate value.
            y: Y-coordinate value.
            z: Z-coordinate value. When provided, the coordinate is treated
                as 3-D. Defaults to ``None`` (2-D).
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
    def x(self) -> float:
        """X-coordinate value."""
        return self._x

    @property
    def y(self) -> float:
        """Y-coordinate value."""
        return self._y

    @property
    def z(self) -> float | None:
        """Z-coordinate value, or ``None`` for 2-D coordinates."""
        return self._z

    @property
    def coordinate(self) -> tuple[float, ...]:
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
