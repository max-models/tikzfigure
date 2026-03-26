from typing import Any


class Color:
    def __init__(self, color_spec):
        """
        Initialize the Color object by parsing the color specification.

        Parameters:
        - color_spec: Can be a TikZ color string (e.g., 'blue!20'), a standard color name,
                      an RGB tuple, a hex code, etc.
        """
        self._color_spec = color_spec

    @property
    def color_spec(self):
        return self._color_spec

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def to_dict(self) -> dict[str, Any]:
        return {"type": "Color", "color_spec": self._color_spec}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Color":
        return cls(color_spec=d["color_spec"])
