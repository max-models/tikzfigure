from typing import Any

from tikzfigure.core.coordinate import TikzCoordinate
from tikzfigure.core.path import TikzPath


class Plot3D(TikzPath):
    """A 3-D data plot rendered with ``\\addplot3`` inside a pgfplots axis.

    Converts parallel x/y/z lists into a sequence of
    :class:`TikzCoordinate` waypoints and delegates rendering to
    :meth:`to_tikz`.
    """

    def __init__(
        self,
        x: list[float],
        y: list[float],
        z: list[float],
        cycle: bool = False,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        center: bool = False,
        options: list | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Plot3D.

        Args:
            x: List of x-coordinate values.
            y: List of y-coordinate values.
            z: List of z-coordinate values.
            cycle: If ``True``, close the plot path with ``-- cycle``.
                Defaults to ``False``.
            label: Internal TikZ name for this plot. Defaults to ``""``.
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index. Defaults to ``0``.
            center: If ``True``, connect through ``.center`` anchors.
                Defaults to ``False``.
            options: Flag-style TikZ/pgfplots options.
            **kwargs: Keyword-style TikZ/pgfplots options.
        """
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

    def to_tikz(self) -> str:
        """Generate the ``\\addplot3`` command for this 3-D plot.

        Returns:
            A ``\\addplot3[...]  coordinates {...};`` command string ending
            with a newline, optionally preceded by a comment line.
        """
        plot_str = f"\\addplot3[{self.tikz_options}]"
        plot_str += " coordinates "
        plot_str += "{" + " ".join(self.label_list) + "};\n"
        plot_str = self.add_comment(plot_str)

        return plot_str

    def to_dict(self) -> dict[str, Any]:
        """Serialize this plot to a plain dictionary.

        Returns:
            A dictionary identical to the base :class:`TikzPath`
            representation except that ``type`` is set to ``"Plot3D"``.
        """
        d = super().to_dict()
        d["type"] = "Plot3D"
        return d

    @classmethod
    def from_dict(
        cls, d: dict[str, Any], node_lookup: dict[str, Any] | None = None
    ) -> "Plot3D":  # noqa: ARG003
        """Reconstruct a Plot3D from a dictionary.

        Args:
            d: Dictionary as produced by :meth:`to_dict`.
            node_lookup: Unused; accepted for compatibility with the
                :class:`TikzPath` interface.

        Returns:
            A new :class:`Plot3D` instance.
        """
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
