from typing import Any

from tikzpics.core.coordinate import TikzCoordinate
from tikzpics.core.path import TikzPath


class Plot3D(TikzPath):
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

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["type"] = "Plot3D"
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Plot3D":
        nodes_data = d.get("nodes", [])
        x = [n["x"] for n in nodes_data]
        y = [n["y"] for n in nodes_data]
        z = [n["z"] for n in nodes_data]
        kwargs = d.get("kwargs", {})
        return cls(
            x=x,
            y=y,
            z=z,
            cycle=d.get("cycle", False),
            label=d.get("label", ""),
            comment=d.get("comment"),
            layer=d.get("layer", 0),
            center=d.get("center", False),
            options=d.get("options"),
            **kwargs,
        )
