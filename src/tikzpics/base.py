class TikzObject:
    def __init__(
        self,
        label: str | None = None,
        comment: str | None = None,
        layer: int | None = 0,
        options: list | None = None,
        **kwargs,
    ) -> None:

        if options is None:
            options = []

        self._label = label
        self._comment = comment
        self._layer = layer
        self._options = options
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
    def options(self) -> list:
        return self._options

    @property
    def kwargs(self) -> dict:
        return self._kwargs

    @property
    def tikz_options(self) -> str:
        if len(self.options) == 0:
            options = ""
        else:
            options = ", ".join(self.options) + ", "

        options += ", ".join(
            f"{k.replace('_', ' ')}={v}" for k, v in self.kwargs.items()
        )
        return options

    def add_comment(self, string_in) -> str:
        if self.comment is not None:
            return f"\n% {self.comment}\n{string_in}"
        return string_in
