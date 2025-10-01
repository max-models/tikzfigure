from tikzpics.base import TikzObject


class Node(TikzObject):
    def __init__(
        self,
        x: float | int | None = None,
        y: float | int | None = None,
        z: float | int | None = None,
        label: str = "",
        content: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: list | None = None,
        **kwargs,
    ):
        """
        Represents a TikZ node.

        Parameters:
        - x (float): X-coordinate of the node.
        - y (float): Y-coordinate of the node.
        - name (str, optional): Name of the node. If None, a default name will be assigned.
        - **kwargs: Additional TikZ node options (e.g., shape, color).
        """
        if options is None:
            options = []

        self._x = x
        self._y = y
        self._z = z
        if z is None:
            self._ndim = 2
        else:
            self._ndim = 3

        self._content = content
        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def ndim(self):
        return self._ndim

    @property
    def content(self):
        return self._content

    def to_tikz(self):
        """
        Generate the TikZ code for this node.

        Returns:
        - tikz_str (str): TikZ code string for the node.
        """

        # options = ", ".join(
        #     f"{k.replace('_', ' ')}={v}" for k, v in self.options.items()
        # )
        options = self.tikz_options
        if options:
            options = f"[{options}]"
        if self.x is None and self.y is None:
            node_string = f"\\node{options} ({self.label}) {{{self.content}}};\n"
        elif self.ndim == 2:
            node_string = f"\\node{options} ({self.label}) at ({self.x}, {self.y}) {{{self.content}}};\n"
        else:
            node_string = f"\\node{options} ({self.label}) at (axis cs:{self.x}, {self.y}, {self.z}) {{{self.content}}};\n"

        node_string = self.add_comment(node_string)
        return node_string
