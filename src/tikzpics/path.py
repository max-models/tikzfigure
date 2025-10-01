from tikzpics.base import TikzObject
from tikzpics.coordinate import TikzCoordinate
from tikzpics.node import Node


class Path(TikzObject):
    def __init__(
        self,
        nodes: list,
        cycle: bool = False,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        center: bool = False,
        options: list | None = None,
        tikz_command: str = "draw",
        **kwargs,
    ):
        """
        Represents a path (line) connecting multiple nodes.

        Parameters:
        - nodes (list of str): List of node names to connect.
        - **kwargs: Additional TikZ path options (e.g., style, color).
        """

        if options is None:
            options = []

        self._nodes = nodes
        self._cycle = cycle
        self._center = center
        self._tikz_command = tikz_command

        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

    @property
    def nodes(self):
        return self._nodes

    @property
    def cycle(self) -> bool:
        return self._cycle

    @property
    def center(self) -> bool:
        return self._center

    @property
    def tikz_options(self) -> str:
        # options = super().tikz_options
        options = ", ".join(
            f"{k.replace('_', ' ')}={v}" for k, v in self.kwargs.items()
        )
        if len(self.options) > 0:
            options = ", ".join(self.options) + ", " + options

        return options

    @property
    def label_list(self) -> list:
        label_list = []
        for node in self.nodes:
            if isinstance(node, Node):
                assert (
                    node.label != ""
                ), "Trying to draw a path using a node without a label!"
                if self.center:
                    label_list.append(f"({node.label}.center)")
                else:
                    print()
                    label_list.append(f"({node.label})")
            elif isinstance(node, TikzCoordinate):
                label_list.append(f"{tuple(float(x) for x in node.coordinate)}")
        return label_list

    @property
    def tikz_command(self) -> str:
        return self._tikz_command

    def to_tikz(self):
        """
        Generate the TikZ code for this path.

        Returns:
        - tikz_str (str): TikZ code string for the path.
        """

        options = self.tikz_options
        label_list = self.label_list

        path_str = " to ".join(label_list)
        if self.cycle:
            path_str += " -- cycle"

        path_str = f"\\{self.tikz_command}[{options}] {path_str};\n"

        path_str = self.add_comment(path_str)

        return path_str
