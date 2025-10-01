from tikzpics.coordinate import TikzCoordinate
from tikzpics.path import Path


class Plot3D(Path):
    def __init__(
        self,
        x: list,
        y: list,
        z: list,
        cycle: bool = False,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        center=False,
        options: list | None = None,
        **kwargs,
    ):

        if options is None:
            options = []

        nodes = [TikzCoordinate(_x, _y, _z, layer=layer) for _x, _y, _z in zip(x, y, z)]

        super().__init__(
            nodes=nodes,
            cycle=cycle,
            label=label,
            comment=comment,
            layer=layer,
            center=center,
            options=options,
            **kwargs,
        )

    def to_tikz(self):
        """
        Generate the TikZ code for this path.

        Returns:
        - tikz_str (str): TikZ code string for the path.
        """

        plot_str = f"\\addplot3[{self.tikz_options}]"
        plot_str += " coordinates "
        plot_str += "{" + " ".join(self.label_list) + "};\n"
        plot_str = self.add_comment(plot_str)

        return plot_str
