from typing import Any


class RawTikz:
    """A verbatim TikZ code block inserted directly into the figure output.

    Use this to inject arbitrary TikZ commands that are not covered by the
    higher-level API.

    Attributes:
        tikz_code: The raw TikZ string that will be emitted verbatim.
    """

    def __init__(self, tikz_code: str) -> None:
        """Initialize a RawTikz block.

        Args:
            tikz_code: Verbatim TikZ code to include in the figure output.
        """
        self.tikz_code = tikz_code

    def to_tikz(self) -> str:
        """Return the raw TikZ code with a trailing newline.

        Returns:
            The verbatim TikZ code string followed by a newline character.
        """
        return self.tikz_code + "\n"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RawTikz):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def to_dict(self) -> dict[str, Any]:
        """Serialize this block to a plain dictionary.

        Returns:
            A dictionary with ``type`` and ``tikz_code`` keys.
        """
        return {"type": "RawTikz", "tikz_code": self.tikz_code}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RawTikz":
        """Reconstruct a RawTikz block from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`RawTikz` instance.
        """
        return cls(tikz_code=d["tikz_code"])
