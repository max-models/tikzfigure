from typing import Any


class TikzWrapper:
    """A lightweight wrapper around a raw TikZ string with node-like metadata.

    Unlike :class:`RawTikz`, ``TikzWrapper`` carries label, content, and
    layer metadata so it can participate in layer-aware rendering without
    inheriting the full :class:`TikzObject` machinery.

    Attributes:
        raw_tikz: The verbatim TikZ string returned by :meth:`to_tikz`.
        label: Identifier string for this wrapper element.
        content: Text content associated with this wrapper.
        layer: Layer index this wrapper belongs to.
        options: Additional TikZ options passed as keyword arguments.
    """

    def __init__(
        self,
        raw_tikz: str,
        label: str = "",
        content: str = "",
        layer: int = 0,
        **kwargs: Any,
    ) -> None:
        """Initialize a TikzWrapper.

        Args:
            raw_tikz: Verbatim TikZ code to be returned by :meth:`to_tikz`.
            label: Identifier string for this element. Defaults to ``""``.
            content: Text content associated with this element.
                Defaults to ``""``.
            layer: Layer index. Defaults to ``0``.
            **kwargs: Additional TikZ options stored in :attr:`options`.
        """
        self.raw_tikz: str = raw_tikz
        self.label: str = label
        self.content: str = content
        self.layer: int = layer
        self.options: dict[str, Any] = kwargs

    def to_tikz(self) -> str:
        """Return the raw TikZ string for this wrapper.

        Returns:
            The verbatim TikZ code passed at construction time.
        """
        return self.raw_tikz
