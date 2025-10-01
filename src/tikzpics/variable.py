from tikzpics.base import TikzObject


class Variable(TikzObject):
    def __init__(
        self,
        label: str,
        value: int | float,
        layer: int | None = 0,
        comment: str | None = None,
    ) -> None:

        super().__init__(label=label, layer=layer, comment=comment)
        self._value = value

    def to_tikz(self):
        return "% Hi\n"

    @property
    def value(self):
        return self._value
