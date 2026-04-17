from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.plot import Plot2D
from tikzfigure.options import OptionInput


class Axis2D(TikzObject):
    """A 2-D pgfplots axis environment with one or more plots.

    Manages axis configuration (labels, limits, grid, ticks, legend).
    Rendering as \\begin{axis}...\\end{axis} with multiple \\addplot
    commands is implemented in to_tikz() (Task 5) and serialization is
    implemented in to_dict()/from_dict() (Task 6).
    """

    def __init__(
        self,
        xlabel: str = "",
        ylabel: str = "",
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        grid: bool = True,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        width: str | int | float | None = None,
        height: str | int | float | None = None,
        options: OptionInput | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a 2D axis.

        Args:
            xlabel: Label for x-axis. Defaults to "".
            ylabel: Label for y-axis. Defaults to "".
            xlim: (min, max) tuple for x-axis limits, or None for auto.
            ylim: (min, max) tuple for y-axis limits, or None for auto.
            grid: Enable grid lines. Defaults to True.
            label: Unique identifier (inherited from TikzObject).
            comment: Optional comment prepended in output.
            layer: Layer index. Defaults to 0.
            width: Width of the axis as a string (e.g., "8cm"), number in cm,
                or None for auto. Defaults to None.
            height: Height of the axis as a string (e.g., "6cm"), number in cm,
                or None for auto. Defaults to None.
            options: Flag-style pgfplots options.
            **kwargs: Keyword-style pgfplots options.
        """
        if options is None:
            options = []

        super().__init__(
            label=label,
            comment=comment,
            layer=layer,
            options=options,
            **kwargs,
        )

        # Validate limits
        self._validate_limits(xlim, "xlim")
        self._validate_limits(ylim, "ylim")

        self._xlabel = xlabel
        self._ylabel = ylabel
        self._xlim = xlim
        self._ylim = ylim
        self._grid = grid
        self._width: str | None = self._normalize_dimension(width, "width")
        self._height: str | None = self._normalize_dimension(height, "height")
        self._plots: list[Plot2D] = []
        self._ticks: dict[str, tuple[list[float], list[str] | None]] = {}
        self._legend_pos: str | None = None

    @staticmethod
    def _normalize_dimension(
        value: str | int | float | None, param_name: str
    ) -> str | None:
        """Normalize dimension input to pgfplots format string.

        Args:
            value: String (e.g., "8cm"), number (e.g., 8), or None
            param_name: Name of parameter ("width", "height") for error messages

        Returns:
            Normalized string (e.g., "8cm") or None

        Raises:
            TypeError: If value is invalid type
            ValueError: If string format invalid or number out of range
        """
        if value is None:
            return None

        if isinstance(value, str):
            # Validate: must contain a unit suffix
            valid_units = ["cm", "pt", "mm", "ex", "in"]
            if not any(value.endswith(unit) for unit in valid_units):
                raise ValueError(
                    f'{param_name} string must include a unit (e.g., "8cm"), got "{value}"'
                )
            return value

        if isinstance(value, (int, float)):
            # Validate: must be positive
            if value <= 0:
                raise ValueError(f"{param_name} must be positive, got {value}")
            return f"{value}cm"

        raise TypeError(
            f"{param_name} must be a string, number, or None, got {type(value).__name__}"
        )

    def _validate_limits(self, limits: tuple[float, float] | None, name: str) -> None:
        """Validate axis limits format.

        Args:
            limits: (min, max) tuple or None
            name: Axis name for error message ("xlim" or "ylim")

        Raises:
            ValueError: If limits is not a 2-tuple of numbers or None
        """
        if limits is not None:
            if not isinstance(limits, tuple) or len(limits) != 2:
                raise ValueError(
                    f"{name} must be a (min, max) tuple or None, got {limits}"
                )
            if not all(isinstance(v, (int, float)) for v in limits):
                raise ValueError(f"{name} values must be numeric, got {limits}")

    @property
    def xlabel(self) -> str:
        """X-axis label."""
        return self._xlabel

    @property
    def ylabel(self) -> str:
        """Y-axis label."""
        return self._ylabel

    @property
    def xlim(self) -> tuple[float, float] | None:
        """X-axis limits as (min, max) or None."""
        return self._xlim

    @property
    def ylim(self) -> tuple[float, float] | None:
        """Y-axis limits as (min, max) or None."""
        return self._ylim

    @property
    def grid(self) -> bool:
        """Whether grid is enabled."""
        return self._grid

    @property
    def width(self) -> str | None:
        """Return the axis width as a pgfplots-compatible string."""
        return self._width

    @property
    def height(self) -> str | None:
        """Return the axis height as a pgfplots-compatible string."""
        return self._height

    @property
    def plots(self) -> list[Plot2D]:
        """List of Plot2D objects in this axis."""
        return self._plots

    def set_xlabel(self, label: str) -> None:
        """Set x-axis label.

        Args:
            label: The label text.
        """
        self._xlabel = label

    def set_ylabel(self, label: str) -> None:
        """Set y-axis label.

        Args:
            label: The label text.
        """
        self._ylabel = label

    def set_xlim(self, min_val: float, max_val: float) -> None:
        """Set x-axis limits.

        Args:
            min_val: Minimum x value.
            max_val: Maximum x value.

        Raises:
            TypeError: If values are not numeric.
        """
        self._validate_limits((min_val, max_val), "xlim")
        self._xlim = (min_val, max_val)

    def set_ylim(self, min_val: float, max_val: float) -> None:
        """Set y-axis limits.

        Args:
            min_val: Minimum y value.
            max_val: Maximum y value.

        Raises:
            TypeError: If values are not numeric.
        """
        self._validate_limits((min_val, max_val), "ylim")
        self._ylim = (min_val, max_val)

    def set_grid(self, enabled: bool) -> None:
        """Enable or disable grid.

        Args:
            enabled: True to show grid, False to hide.
        """
        self._grid = enabled

    def set_ticks(
        self,
        axis: str,
        positions: list[float],
        labels: list[str] | None = None,
    ) -> None:
        """Configure ticks for an axis.

        Args:
            axis: "x" or "y".
            positions: List of tick positions (must be non-empty).
            labels: Optional list of tick labels. If provided, must match
                positions length. If None, positions are used as labels.

        Raises:
            ValueError: If axis is not "x" or "y", if positions is empty,
                or if labels length doesn't match positions length.
        """
        if axis not in ("x", "y"):
            raise ValueError(f"axis must be 'x' or 'y', got {axis}")
        if not positions:
            raise ValueError("positions list cannot be empty")
        if labels is not None and len(labels) != len(positions):
            raise ValueError(
                f"labels length ({len(labels)}) must match "
                f"positions length ({len(positions)})"
            )
        self._ticks[axis] = (positions, labels)

    def set_legend(self, position: str = "north east") -> None:
        """Configure legend.

        Args:
            position: Legend position (e.g., "north east", "north west",
                "south east", "south west", "center").
        """
        self._legend_pos = position

    def add_plot(
        self,
        x: list[float] | None = None,
        y: list[float] | None = None,
        func: str | None = None,
        label: str = "",
        **kwargs: Any,
    ) -> Plot2D:
        """Add a plot to this axis.

        Args:
            x: List of x values. Mutually exclusive with func.
            y: List of y values. Mutually exclusive with func.
            func: PGF function string (e.g., "sin(x)", "x^2"). Mutually exclusive with x/y.
            label: Plot label for legend. Defaults to "".
            **kwargs: Keyword-style pgfplots options (e.g., color="red").

        Returns:
            The newly created Plot2D object.

        Raises:
            ValueError: If neither (x, y) nor func is provided, or both are provided.
        """
        plot = Plot2D(x=x, y=y, func=func, label=label, **kwargs)
        self._plots.append(plot)
        return plot

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the pgfplots axis environment.

        Returns:
            A complete \\begin{axis}...\\end{axis} block with all plots.
        """
        # Build axis options
        axis_opts = [str(option) for option in self.options]

        # Add axis labels if provided
        if self._xlabel:
            axis_opts.append(f"xlabel={self._xlabel}")
        if self._ylabel:
            axis_opts.append(f"ylabel={self._ylabel}")

        # Add limits if provided
        if self._xlim is not None:
            axis_opts.append(f"xmin={self._xlim[0]}")
            axis_opts.append(f"xmax={self._xlim[1]}")
        if self._ylim is not None:
            axis_opts.append(f"ymin={self._ylim[0]}")
            axis_opts.append(f"ymax={self._ylim[1]}")

        # Add grid setting
        axis_opts.append(f"grid={'true' if self._grid else 'false'}")

        # Add width and height if specified
        if self._width:
            axis_opts.append(f"width={self._width}")
        if self._height:
            axis_opts.append(f"height={self._height}")

        # Add legend position if set
        if self._legend_pos is not None:
            axis_opts.append(f"legend pos={self._legend_pos}")

        # Add user kwargs (converted with underscore → space)
        for k, v in self.kwargs.items():
            axis_opts.append(f"{k.replace('_', ' ')}={str(v)}")

        axis_opts_str = ", ".join(axis_opts)

        # Build plot commands
        plot_tikz = ""
        plot_labels = []

        for plot in self._plots:
            if plot.is_function:
                # Function-based plot: use pgfplots function notation
                plot_tikz += (
                    f"\\addplot[{plot.tikz_options(output_unit)}] {{{plot.func}}};\n"
                )
            else:
                # Data-based plot: use coordinates
                coords_str = " ".join(f"({x},{y})" for x, y in zip(plot.x, plot.y))
                plot_tikz += f"\\addplot[{plot.tikz_options(output_unit)}] coordinates {{{coords_str}}};\n"
            if plot.label:
                plot_labels.append(plot.label)

        # Build legend if plots have labels
        legend_tikz = ""
        if plot_labels and self._legend_pos is not None:
            legend_labels = ", ".join(plot_labels)
            legend_tikz = f"\\legend{{{legend_labels}}}\n"

        # Assemble full axis
        axis_tikz = f"\\begin{{axis}}[{axis_opts_str}]\n"
        axis_tikz += plot_tikz
        axis_tikz += legend_tikz
        axis_tikz += "\\end{axis}\n"

        # Add comment if present
        axis_tikz = self.add_comment(axis_tikz)

        return axis_tikz

    def to_dict(self) -> dict[str, Any]:
        """Serialize this axis to a plain dictionary.

        Returns:
            A dictionary with all axis state and plots.
        """
        return {
            "type": "Axis2D",
            "xlabel": self._xlabel,
            "ylabel": self._ylabel,
            "xlim": self._xlim,
            "ylim": self._ylim,
            "grid": self._grid,
            "width": self._width,
            "height": self._height,
            "plots": [plot.to_dict() for plot in self._plots],
            "ticks": self._ticks,
            "legend_pos": self._legend_pos,
            "options": self.options,
            "kwargs": self.kwargs,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Axis2D":
        """Reconstruct an Axis2D from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Axis2D instance.
        """
        axis = cls(
            xlabel=d.get("xlabel", ""),
            ylabel=d.get("ylabel", ""),
            xlim=d.get("xlim"),
            ylim=d.get("ylim"),
            grid=d.get("grid", True),
            width=d.get("width"),
            height=d.get("height"),
            options=d.get("options"),
            **d.get("kwargs", {}),
        )

        # Restore plots
        for plot_dict in d.get("plots", []):
            plot = Plot2D.from_dict(plot_dict)
            axis._plots.append(plot)

        # Restore ticks
        axis._ticks = d.get("ticks", {})

        # Restore legend position
        axis._legend_pos = d.get("legend_pos")

        return axis
