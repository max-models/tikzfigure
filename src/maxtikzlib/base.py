class TikzObject:
    def __init__(
        self,
        label: str | None = None,
        comment: str | None = None,
        layer: int = 0,
        **kwargs,
    ) -> None:

        self._label = label
        self._comment = comment
        self._layer = layer
        self._kwargs = kwargs

    @property
    def label(self) -> str | None:
        return self._label

    @property
    def comment(self) -> str | None:
        return self._comment

    @property
    def layer(self) -> int:
        return self._layer

    @property
    def kwargs(self) -> dict:
        return self._kwargs

    @property
    def options(self) -> str:
        options = ", ".join(
            f"{k.replace('_', ' ')}={v}" for k, v in self.kwargs.items()
        )
        return options
