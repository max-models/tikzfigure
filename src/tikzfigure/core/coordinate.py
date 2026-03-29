from typing import Any

from tikzfigure.core.base import TikzObject


class TikzCoordinate(TikzObject):
    def __init__(
        self,
        x: float,
        y: float,
        z: float | None = None,
        layer: int = 0,
    ) -> None:
        super().__init__(layer=layer, comment=None)

        self._x = x
        self._y = y
        self._z = z
        if z is None:
            self._ndim = 2
        else:
            self._ndim = 3

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def coordinate(self):
        if self.ndim == 2:
            return ((self.x), self.y)
        else:
            return (self.x, self.y, self.z)

    @property
    def ndim(self):
        return self._ndim

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "TikzCoordinate",
            "x": self._x,
            "y": self._y,
            "z": self._z,
            "layer": self._layer,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TikzCoordinate":
        return cls(x=d["x"], y=d["y"], z=d.get("z"), layer=d.get("layer", 0))
