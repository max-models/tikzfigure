from maxtikzlib.base import TikzObject


class Path(TikzObject):
    def __init__(
        self,
        nodes,
        path_actions=[],
        cycle: bool = False,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        **kwargs,
    ):
        """
        Represents a path (line) connecting multiple nodes.

        Parameters:
        - nodes (list of str): List of node names to connect.
        - **kwargs: Additional TikZ path options (e.g., style, color).
        """
        self.nodes = nodes
        self._path_actions = path_actions
        self._cycle = cycle

        super().__init__(label=label, comment=comment, layer=layer, **kwargs)

    @property
    def path_actions(self):
        return self._path_actions

    @property
    def cycle(self) -> bool:
        return self._cycle

    def to_tikz(self):
        """
        Generate the TikZ code for this path.

        Returns:
        - tikz_str (str): TikZ code string for the path.
        """
        # options = ", ".join(
        #     f"{k.replace('_', ' ')}={v}" for k, v in self.options.items()
        # )

        options = self.options
        if len(self.path_actions) > 0:
            options = ", ".join(self.path_actions) + ", " + options
        if options:
            options = f"[{options}]"
        path_str = " to ".join(f"({node.label})" for node in self.nodes)
        if self.cycle:
            path_str += " -- cycle"

        path_str = f"\\draw{options} {path_str};\n"

        path_str = self.add_comment(path_str)

        return path_str
