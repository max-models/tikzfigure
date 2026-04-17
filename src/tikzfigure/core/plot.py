from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import TikzCoordinate
from tikzfigure.core.path import TikzPath


class Plot2D(TikzObject):
    """A 2-D data plot for use within a pgfplots axis.

    Lightweight data holder for x/y coordinates (or a function expression)
    and pgfplots options. Rendering is delegated to the parent Axis2D.
    """

    def __init__(
        self,
        x: list[float] | None = None,
        y: list[float] | None = None,
        func: str | None = None,
        label: str = "",
        comment: str | None = None,
        options: list | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Plot2D.

        Args:
            x: List of x-coordinate values. Mutually exclusive with func.
            y: List of y-coordinate values. Mutually exclusive with func.
            func: PGF function string (e.g., "sin(x)", "x^2"). Mutually exclusive with x/y.
            label: Plot label (used in legend and serialization). Defaults to "".
            comment: Optional comment prepended in the TikZ output.
            options: Flag-style pgfplots options (e.g., ["thick"]).
            **kwargs: Keyword-style pgfplots options (e.g., color="red").

        Raises:
            ValueError: If neither (x, y) nor func is provided, or both are provided.
        """
        if options is None:
            options = []

        # Validate that either (x, y) or func is provided, but not both
        if func is not None and (x is not None or y is not None):
            raise ValueError("Cannot specify both func and (x, y) data")
        if func is None and (x is None or y is None):
            raise ValueError("Must specify either func or both (x, y) data")

        # Extract layer if provided in kwargs to avoid conflict
        # (layer is a property of the parent Axis2D, not the plot itself)
        kwargs_filtered = {k: v for k, v in kwargs.items() if k != "layer"}

        super().__init__(
            label=label,
            comment=comment,
            layer=0,
            options=options,
            **kwargs_filtered,
        )
        self._x = x if x is not None else []
        self._y = y if y is not None else []
        self._func = func

    @property
    def x(self) -> list[float]:
        """X-coordinate values (empty list if using func)."""
        return self._x

    @property
    def y(self) -> list[float]:
        """Y-coordinate values (empty list if using func)."""
        return self._y

    @property
    def func(self) -> str | None:
        """PGF function string, or None if using explicit data."""
        return self._func

    @property
    def is_function(self) -> bool:
        """True if this plot uses a function expression, False if explicit data."""
        return self._func is not None

    def to_dict(self) -> dict[str, Any]:
        """Serialize this plot to a plain dictionary.

        Returns:
            A dictionary with type, x, y, func, label, comment, options, and kwargs.
        """
        return {
            "type": "Plot2D",
            "x": self.x if not self.is_function else None,
            "y": self.y if not self.is_function else None,
            "func": self.func,
            "label": self.label,
            "comment": self.comment,
            "options": self.options,
            "kwargs": self.kwargs,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Plot2D":
        """Reconstruct a Plot2D from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Plot2D instance.
        """
        func = d.get("func")
        if func is not None:
            return cls(
                func=func,
                label=d.get("label", ""),
                comment=d.get("comment"),
                options=d.get("options"),
                **d.get("kwargs", {}),
            )
        else:
            return cls(
                x=d.get("x", []),
                y=d.get("y", []),
                label=d.get("label", ""),
                comment=d.get("comment"),
                options=d.get("options"),
                **d.get("kwargs", {}),
            )


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

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the ``\\addplot3`` command for this 3-D plot.

        Returns:
            A ``\\addplot3[...]  coordinates {...};`` command string ending
            with a newline, optionally preceded by a comment line.
        """
        plot_str = f"\\addplot3[{self.tikz_options(output_unit)}]"
        plot_str += " coordinates "
        plot_str += "{" + " ".join(self._render_label_list(output_unit)) + "};\n"
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
