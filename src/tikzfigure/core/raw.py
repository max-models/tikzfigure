from typing import Any


class RawTikz:
    def __init__(self, tikz_code: str):
        self.tikz_code = tikz_code

    def to_tikz(self) -> str:
        return self.tikz_code + "\n"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RawTikz):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def to_dict(self) -> dict[str, Any]:
        return {"type": "RawTikz", "tikz_code": self.tikz_code}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RawTikz":
        return cls(tikz_code=d["tikz_code"])
