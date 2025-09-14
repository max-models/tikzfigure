from maxtikzlib.base import TikzObject


class Position(TikzObject):
    def __init__(
        self,
        label: str | None = None,
        comment: str | None = None,
        layer: int = 0,
        options: list | None = None,
        **kwargs,
    ) -> None:
        super().__init__(label, comment, layer, options, **kwargs)
