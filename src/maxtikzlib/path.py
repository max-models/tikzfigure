from maxtikzlib.base import TikzObject
from maxtikzlib.coordinate import TikzCoordinate
from maxtikzlib.node import Node


class Path(TikzObject):
    def __init__(
        self,
        nodes: list,
        path_actions=[],
        cycle: bool = False,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        center=False,
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
        self._center = center

        super().__init__(label=label, comment=comment, layer=layer, **kwargs)

    @property
    def path_actions(self):
        return self._path_actions

    @property
    def cycle(self) -> bool:
        return self._cycle

    @property
    def center(self) -> bool:
        return self._center

    def to_tikz(self):
        """
        Generate the TikZ code for this path.

        Returns:
        - tikz_str (str): TikZ code string for the path.
        """

        options = self.options
        if len(self.path_actions) > 0:
            options = ", ".join(self.path_actions) + ", " + options
        if options:
            options = f"[{options}]"

        label_list = []
        for node in self.nodes:
            if isinstance(node, Node):
                if self.center:
                    label_list.append(f"({node.label}.center)")
                else:
                    label_list.append(f"({node.label})")
            elif isinstance(node, TikzCoordinate):
                label_list.append(f"({node.x},{node.y})")

        path_str = " to ".join(label_list)
        # if self.center:
        #     path_str = " to ".join(f"({node.label}.center)" for node in self.nodes)
        # else:
        #     path_str = " to ".join(f"({node.label})" for node in self.nodes)

        if self.cycle:
            path_str += " -- cycle"

        path_str = f"\\draw{options} {path_str};\n"

        path_str = self.add_comment(path_str)

        return path_str
