from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import TikzCoordinate
from tikzfigure.core.path import TikzPath
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.options import OptionInput, normalize_options


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
        options: OptionInput | None = None,
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
        serialized = serialize_tikz_value(
            {
                "type": "Plot2D",
                "x": self.x if not self.is_function else None,
                "y": self.y if not self.is_function else None,
                "func": self.func,
                "label": self.label,
                "comment": self.comment,
                "options": self.options,
                "kwargs": self.kwargs,
            }
        )
        if not isinstance(serialized, dict):
            raise TypeError("Serialized Plot2D data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Plot2D":
        """Reconstruct a Plot2D from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Plot2D instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized Plot2D data must deserialize to a dict.")
        kwargs = restored.get("kwargs", {})
        if not isinstance(kwargs, dict):
            raise TypeError("Serialized Plot2D kwargs must deserialize to a dict.")
        func = restored.get("func")
        if func is not None:
            return cls(
                func=func,
                label=restored.get("label", ""),
                comment=restored.get("comment"),
                options=restored.get("options"),
                **kwargs,
            )
        else:
            return cls(
                x=restored.get("x", []),
                y=restored.get("y", []),
                label=restored.get("label", ""),
                comment=restored.get("comment"),
                options=restored.get("options"),
                **kwargs,
            )


class TikzPlot(TikzObject):
    """A plain TikZ ``\\draw ... plot (...)`` command outside pgfplots axes.

    Use this for function-style or parametric plots directly in a TikZ picture.
    Unlike :class:`Plot2D`, this renders standard TikZ path plots rather than
    ``\\addplot`` commands inside an ``axis`` environment.
    """

    def __init__(
        self,
        x: Any,
        y: Any | None = None,
        *,
        variable: str = "x",
        domain: tuple[Any, Any] | str | None = None,
        samples: int | None = None,
        smooth: bool = False,
        tikz_command: str = "draw",
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a plain TikZ expression plot.

        Args:
            x: X expression for a parametric plot, or the Y expression for a
                regular function plot.
            y: Y expression for a parametric plot. When omitted, ``x`` is
                treated as the Y expression and the x-coordinate becomes the
                loop variable.
            variable: Sampling variable name. Leading backslash is optional.
            domain: Plot domain as ``(start, end)`` or ``"start:end"``.
            samples: Optional sample count.
            smooth: If ``True``, add the ``smooth`` path option.
            tikz_command: Path command to use, typically ``"draw"``.
            label: Internal label used in serialization/copy workflows.
            comment: Optional comment prepended in the TikZ output.
            layer: Layer index.
            options: Flag-style TikZ options.
            **kwargs: Keyword-style TikZ options.
        """
        normalized_options = normalize_options(options)
        if smooth and "smooth" not in [str(option) for option in normalized_options]:
            normalized_options.append("smooth")

        normalized_kwargs = dict(kwargs)
        normalized_kwargs["variable"] = self._normalize_variable(variable)
        if domain is not None:
            normalized_kwargs["domain"] = self._normalize_domain(domain)
        if samples is not None:
            normalized_kwargs["samples"] = samples

        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=normalized_options,
            **normalized_kwargs,
        )
        self._x = str(x)
        self._y = None if y is None else str(y)
        self._tikz_command = tikz_command

    @staticmethod
    def _normalize_variable(variable: str) -> str:
        return variable if variable.startswith("\\") else f"\\{variable}"

    @staticmethod
    def _normalize_domain(domain: tuple[Any, Any] | str) -> str:
        if isinstance(domain, str):
            return domain
        return f"{domain[0]}:{domain[1]}"

    @property
    def x(self) -> str:
        """Primary expression string supplied to the plot."""
        return self._x

    @property
    def y(self) -> str | None:
        """Optional second expression for parametric plots."""
        return self._y

    @property
    def tikz_command(self) -> str:
        """TikZ path command used to render this plot."""
        return self._tikz_command

    @property
    def is_parametric(self) -> bool:
        """Whether the plot uses separate x/y expressions."""
        return self._y is not None

    def _render_plot_coordinate(self) -> str:
        if self._y is None:
            variable = self.kwargs["variable"]
            return f"({{{variable}}}, {{{self._x}}})"
        return f"({{{self._x}}}, {{{self._y}}})"

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the plain TikZ ``plot`` command."""
        options = self.tikz_options(output_unit)
        plot_str = f"\\{self._tikz_command}"
        if options:
            plot_str += f"[{options}]"
        plot_str += f" plot {self._render_plot_coordinate()};\n"
        return self.add_comment(plot_str)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this plot to a plain dictionary."""
        d = super().to_dict()
        d.update(
            {
                "type": "TikzPlot",
                "x": self._x,
                "y": self._y,
                "tikz_command": self._tikz_command,
            }
        )
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized TikzPlot data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TikzPlot":
        """Reconstruct a :class:`TikzPlot` from a dictionary."""
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized TikzPlot data must deserialize to a dict.")
        kwargs = restored.get("kwargs", {})
        if not isinstance(kwargs, dict):
            raise TypeError("Serialized TikzPlot kwargs must deserialize to a dict.")
        return cls(
            x=restored["x"],
            y=restored.get("y"),
            tikz_command=restored.get("tikz_command", "draw"),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            options=restored.get("options"),
            **kwargs,
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
        options: OptionInput | None = None,
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
        serialized = serialize_tikz_value(d)
        if not isinstance(serialized, dict):
            raise TypeError("Serialized Plot3D data must remain a dict.")
        return serialized

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
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized Plot3D data must deserialize to a dict.")
        nodes_data = restored.get("nodes", [])
        x = [n["x"] for n in nodes_data]
        y = [n["y"] for n in nodes_data]
        z = [n["z"] for n in nodes_data]
        kwargs = restored.get("kwargs", {})
        if not isinstance(kwargs, dict):
            raise TypeError("Serialized Plot3D kwargs must deserialize to a dict.")
        return cls(
            x=x,
            y=y,
            z=z,
            cycle=restored.get("cycle", False),
            label=restored.get("label", ""),
            comment=restored.get("comment"),
            layer=restored.get("layer", 0),
            center=restored.get("center", False),
            options=restored.get("options"),
            **kwargs,
        )

    def _copy_init_kwargs(self) -> dict[str, Any]:
        return {
            "x": [self._copy_value(node.x) for node in self.nodes],
            "y": [self._copy_value(node.y) for node in self.nodes],
            "z": [self._copy_value(node.z) for node in self.nodes],
            "cycle": self._copy_value(self.cycle),
            "label": self._copy_value(self.label),
            "comment": self._copy_value(self.comment),
            "layer": self._copy_value(self.layer),
            "center": self._copy_value(self.center),
            "options": self._copy_value(self.options),
            **self._copy_value(self.kwargs),
        }
