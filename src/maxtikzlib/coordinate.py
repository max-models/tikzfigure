from maxtikzlib.base import TikzObject


class TikzCoordinate(TikzObject):
    def __init__(self, x, y, layer: int = 0) -> None:
        super().__init__(layer=layer, comment=None)

        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y
