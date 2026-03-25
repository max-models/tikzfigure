from typing import Any

from tikzpics.core.base import TikzObject


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

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({"type": "Variable", "value": self._value})
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Variable":
        return cls(
            label=d["label"],
            value=d["value"],
            layer=d.get("layer", 0),
            comment=d.get("comment"),
        )
