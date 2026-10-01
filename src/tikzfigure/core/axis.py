from collections.abc import Callable
from typing import Any

from tikzfigure.core.base import TikzObject
from tikzfigure.core.coordinate import (
    Coordinate,
    CoordinateTuple2D,
    CoordinateTuple3D,
    CoordinateValue,
    TikzCoordinate,
)
from tikzfigure.core.graphics import AxisGraphics
from tikzfigure.core.plot import Plot2D
from tikzfigure.core.raw import RawTikz
from tikzfigure.core.serialization import deserialize_tikz_value, serialize_tikz_value
from tikzfigure.core.spy import Spy, SpyLibrary
from tikzfigure.options import OptionInput


def _braced(text: str) -> str:
    """``text`` as an option value: in braces if it has ``,``, ``=``, ``[`` or ``]``.

    Without braces pgfplots would split the value at a comma, or read ``=``
    and brackets as option syntax.
    """
    if any(char in text for char in ",=[]") or text != text.strip():
        return "{" + text + "}"
    return text


class Axis2D(TikzObject):
    """A 2-D pgfplots axis environment with one or more plots.

    Manages axis configuration (labels, title, limits, grid, ticks, legend).
    Renders as \\begin{axis}...\\end{axis}: the plots, images
    (:meth:`add_graphics`) and raw code (:meth:`add_raw`) in the order they
    were added, then coordinates and spies.
    """

    def __init__(
        self,
        xlabel: str = "",
        ylabel: str = "",
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        xlog: bool = False,
        ylog: bool = False,
        grid: bool | str | None = True,
        label: str = "",
        comment: str | None = None,
        layer: int = 0,
        width: str | float | None = None,
        height: str | float | None = None,
        title: str = "",
        options: OptionInput | None = None,
        library_loader: Callable[[str], None] | None = None,
        spy_scope_enabler: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a 2D axis.

        Args:
            xlabel: Label for x-axis. Defaults to "".
            ylabel: Label for y-axis. Defaults to "".
            xlim: (min, max) tuple for x-axis limits, or None for auto.
            ylim: (min, max) tuple for y-axis limits, or None for auto.
            xlog: Whether to use logarithmic scaling on the x-axis.
            ylog: Whether to use logarithmic scaling on the y-axis.
            grid: Enable grid lines. Pass ``True`` / ``False`` for the usual
                pgfplots values, a string such as ``"major"``, or ``None`` to
                write no ``grid`` option (e.g. to give ``xmajorgrids`` in
                ``options``).
            label: Unique identifier (inherited from TikzObject).
            comment: Optional comment prepended in output.
            layer: Layer index. Defaults to 0.
            width: Width of the axis as a string (e.g., "8cm"), number in cm,
                or None for auto. Defaults to None.
            height: Height of the axis as a string (e.g., "6cm"), number in cm,
                or None for auto. Defaults to None.
            title: Title above the axis. Defaults to "".
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
        self._validate_log_flag(xlog, "xlog")
        self._validate_log_flag(ylog, "ylog")

        self._xlabel = xlabel
        self._ylabel = ylabel
        self._title = title
        self._xlim = xlim
        self._ylim = ylim
        self._xlog = xlog
        self._ylog = ylog
        self._grid = grid
        self._width: str | None = self._normalize_dimension(width, "width")
        self._height: str | None = self._normalize_dimension(height, "height")
        self._plots: list[Plot2D] = []
        self._items: list[Coordinate | Spy] = []
        self._extras: list[AxisGraphics | RawTikz] = []
        # ("plot", index) and ("extra", index) in the order they were added
        self._order: list[tuple[str, int]] = []
        self._ticks: dict[str, tuple[list[float], list[str] | None]] = {}
        self._legend_pos: str | None = None
        self._legend_style: dict[str, Any] = {}
        self._library_loader = library_loader
        self._spy_scope_enabler = spy_scope_enabler

    @staticmethod
    def _normalize_dimension(value: str | float | None, param_name: str) -> str | None:
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

    @staticmethod
    def _validate_log_flag(value: bool, name: str) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"{name} must be a bool, got {type(value).__name__}")

    @property
    def xlabel(self) -> str:
        """X-axis label."""
        return self._xlabel

    @property
    def ylabel(self) -> str:
        """Y-axis label."""
        return self._ylabel

    @property
    def title(self) -> str:
        """Title above the axis."""
        return self._title

    @property
    def xlim(self) -> tuple[float, float] | None:
        """X-axis limits as (min, max) or None."""
        return self._xlim

    @property
    def ylim(self) -> tuple[float, float] | None:
        """Y-axis limits as (min, max) or None."""
        return self._ylim

    @property
    def xlog(self) -> bool:
        """Whether the x-axis is logarithmic."""
        return self._xlog

    @property
    def ylog(self) -> bool:
        """Whether the y-axis is logarithmic."""
        return self._ylog

    @property
    def grid(self) -> bool | str | None:
        """Grid setting for pgfplots."""
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

    @property
    def items(self) -> list[Coordinate | Spy]:
        """List of non-plot commands rendered inside this axis."""
        return self._items

    @property
    def extras(self) -> list[AxisGraphics | RawTikz]:
        """Images and raw code rendered between the plots, in order."""
        return self._extras

    def files(self) -> dict[str, bytes]:
        """The image files this axis needs written next to its TikZ code."""
        files: dict[str, bytes] = {}
        for extra in self._extras:
            if isinstance(extra, AxisGraphics):
                files.update(extra.files())
        return files

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

    def set_title(self, title: str) -> None:
        """Set the title above the axis.

        Args:
            title: The title text.
        """
        self._title = title

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

    def set_xlog(self, enabled: bool) -> None:
        """Enable or disable logarithmic scaling on x-axis."""
        self._validate_log_flag(enabled, "enabled")
        self._xlog = enabled

    def set_ylog(self, enabled: bool) -> None:
        """Enable or disable logarithmic scaling on y-axis."""
        self._validate_log_flag(enabled, "enabled")
        self._ylog = enabled

    def set_grid(self, enabled: bool | str | None) -> None:
        """Set the pgfplots grid mode.

        Args:
            enabled: ``True`` / ``False``, a pgfplots grid mode string such
                as ``"major"`` or ``"both"``, or ``None`` for no ``grid``
                option.
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

    def set_legend(
        self,
        position: str | None = "north east",
        *,
        at: tuple[float, float] | None = None,
        anchor: str | None = None,
        columns: int | None = None,
        style: OptionInput | None = None,
    ) -> None:
        """Configure legend.

        Plots with a label get a legend entry; plots without one are left
        out of the legend (``forget plot``).

        Args:
            position: Legend position (e.g., "north east", "north west",
                "south east", "south west", "outer north east"). Ignored
                when ``at`` is given.
            at: The legend's position in axis description coordinates,
                ``(0, 0)`` the lower left and ``(1, 1)`` the upper right
                corner of the axis, instead of ``position``.
            anchor: The point of the legend placed at ``at``, e.g.
                "south west". Defaults to "north east".
            columns: The number of legend columns.
            style: Further ``legend style`` options, e.g. ``["draw=none"]``
                or ``"font=\\small"``.
        """
        if at is not None:
            position = None
        if position is None and at is None:
            at, anchor = (1.0, 1.0), anchor or "north east"
        self._legend_pos = position if position is not None else ""
        self._legend_style = {
            "at": None if at is None else (float(at[0]), float(at[1])),
            "anchor": anchor,
            "columns": columns,
            "style": (
                []
                if style is None
                else ([style] if isinstance(style, str) else list(style))
            ),
        }

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
        self._order.append(("plot", len(self._plots) - 1))
        return plot

    def add_graphics(
        self,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
        path: str | None = None,
        data: bytes | None = None,
        filename: str | None = None,
        comment: str | None = None,
        plot_options: list[str] | None = None,
        **kwargs: Any,
    ) -> AxisGraphics:
        """Place an image in the axis, its edges at the given data coordinates.

        Renders as ``\\addplot graphics``. Give an existing file as ``path``,
        or the image bytes as ``data``: the figure then writes them as
        ``filename`` next to the TikZ code when it compiles or saves it
        (see :meth:`TikzFigure.savefig`).

        Args:
            xmin, xmax, ymin, ymax: Data coordinates of the image edges.
            path: An existing image file.
            data: Image bytes, e.g. a PNG.
            filename: File name for ``data``; derived from the bytes if
                omitted.
            comment: Optional comment prepended in the TikZ output.
            plot_options: Options of the ``\\addplot`` itself, e.g.
                ``["forget plot"]`` to leave the image out of the legend.
            **kwargs: Further ``\\addplot graphics`` options.

        Returns:
            The new :class:`AxisGraphics`.
        """
        graphics = AxisGraphics(
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            path=path,
            data=data,
            filename=filename,
            comment=comment,
            plot_options=plot_options,
            **kwargs,
        )
        self._extras.append(graphics)
        self._order.append(("extra", len(self._extras) - 1))
        return graphics

    def add_raw(self, tikz_code: str) -> RawTikz:
        """Insert verbatim code inside the axis, after what was added so far.

        Use it for commands that need the axis coordinate system, e.g.
        ``\\node at (axis cs:1,2) {peak};``.

        Args:
            tikz_code: The code, written as given.

        Returns:
            The new :class:`RawTikz`.
        """
        raw = RawTikz(tikz_code)
        self._extras.append(raw)
        self._order.append(("extra", len(self._extras) - 1))
        return raw

    def _sequence(self) -> list[Plot2D | AxisGraphics | RawTikz]:
        """Plots and extras in the order they were added."""
        seen_plots: set[int] = set()
        seen_extras: set[int] = set()
        sequence: list[Plot2D | AxisGraphics | RawTikz] = []
        for kind, index in self._order:
            if kind == "plot" and index < len(self._plots):
                seen_plots.add(index)
                sequence.append(self._plots[index])
            elif kind == "extra" and index < len(self._extras):
                seen_extras.add(index)
                sequence.append(self._extras[index])
        # plots or extras appended to the lists directly
        sequence.extend(p for i, p in enumerate(self._plots) if i not in seen_plots)
        sequence.extend(e for i, e in enumerate(self._extras) if i not in seen_extras)
        return sequence

    def add_coordinate(
        self,
        label: str,
        x: (
            CoordinateValue
            | CoordinateTuple2D
            | CoordinateTuple3D
            | TikzCoordinate
            | None
        ) = None,
        y: CoordinateValue | None = None,
        z: CoordinateValue | None = None,
        at: str | None = None,
        comment: str | None = None,
    ) -> Coordinate:
        """Add a named coordinate inside the axis environment."""
        coord = Coordinate(
            label=label,
            x=x,
            y=y,
            z=z,
            at=at,
            layer=self.layer if self.layer is not None else 0,
            comment=comment,
        )
        self._items.append(coord)
        return coord

    def add_spy(
        self,
        on: Any,
        *,
        comment: str | None = None,
        options: OptionInput | None = None,
        magnification: float | None = None,
        lens: OptionInput | str | None = None,
        lens_kwargs: dict[str, Any] | None = None,
        size: str | object | None = None,
        width: str | object | None = None,
        height: str | object | None = None,
        connect_spies: bool = False,
        at: Any = None,
        node_label: str | None = None,
        node_options: OptionInput | None = None,
        node_style: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Spy:
        """Add a ``\\spy`` command inside the axis environment."""
        if self._library_loader is not None:
            self._library_loader("spy")
        if self._spy_scope_enabler is not None:
            self._spy_scope_enabler()

        spy_options, spy_kwargs = SpyLibrary.build_command_parts(
            options=options,
            magnification=magnification,
            lens=lens,
            lens_kwargs=lens_kwargs,
            size=size,
            width=width,
            height=height,
            connect_spies=connect_spies,
            **kwargs,
        )
        spy = Spy(
            on=on,
            at=at,
            node_label=node_label,
            node_options=node_options,
            node_style=node_style,
            comment=comment,
            layer=self.layer if self.layer is not None else 0,
            options=spy_options,
            **spy_kwargs,
        )
        self._items.append(spy)
        return spy

    def axis_options(self, output_unit: str | None = None) -> list[str]:
        """The options of the ``axis`` environment, as a list."""
        axis_opts = [str(option) for option in self.options]

        if self._title:
            axis_opts.append(f"title={_braced(self._title)}")
        if self._xlabel:
            axis_opts.append(f"xlabel={_braced(self._xlabel)}")
        if self._ylabel:
            axis_opts.append(f"ylabel={_braced(self._ylabel)}")

        if self._xlim is not None:
            axis_opts.append(f"xmin={self._xlim[0]}")
            axis_opts.append(f"xmax={self._xlim[1]}")
        if self._ylim is not None:
            axis_opts.append(f"ymin={self._ylim[0]}")
            axis_opts.append(f"ymax={self._ylim[1]}")
        if self._xlog:
            axis_opts.append("xmode=log")
        if self._ylog:
            axis_opts.append("ymode=log")

        for axis_name in ("x", "y"):
            if axis_name in self._ticks:
                positions, labels = self._ticks[axis_name]
                axis_opts.append(
                    f"{axis_name}tick={{{','.join(str(p) for p in positions)}}}"
                )
                if labels is not None:
                    tick_labels = ",".join("{" + str(label) + "}" for label in labels)
                    axis_opts.append(f"{axis_name}ticklabels={{{tick_labels}}}")

        if isinstance(self._grid, str):
            axis_opts.append(f"grid={self._grid}")
        elif self._grid is not None:
            axis_opts.append(f"grid={'major' if self._grid else 'none'}")

        if self._width:
            axis_opts.append(f"width={self._width}")
        if self._height:
            axis_opts.append(f"height={self._height}")

        if self._legend_pos:
            axis_opts.append(f"legend pos={self._legend_pos}")
        legend_style = self._legend_style_options()
        if legend_style:
            axis_opts.append(f"legend style={{{', '.join(legend_style)}}}")
        if self._legend_style.get("columns"):
            axis_opts.append(f"legend columns={self._legend_style['columns']}")

        for k, v in self.kwargs.items():
            value = ("true" if v else "false") if isinstance(v, bool) else str(v)
            axis_opts.append(f"{k.replace('_', ' ')}={value}")
        return axis_opts

    def _legend_style_options(self) -> list[str]:
        style = self._legend_style
        options = []
        if style.get("at") is not None:
            x, y = style["at"]
            options.append(f"at={{({x:g},{y:g})}}")
            options.append(f"anchor={style.get('anchor') or 'north east'}")
        options.extend(str(option) for option in style.get("style", []))
        return options

    @property
    def _has_legend(self) -> bool:
        return self._legend_pos is not None

    def to_tikz(self, output_unit: str | None = None) -> str:
        """Generate the pgfplots axis environment.

        Returns:
            A complete \\begin{axis}...\\end{axis} block with all plots.
        """
        axis_opts_str = ", ".join(self.axis_options(output_unit))
        sequence = self._sequence()
        plots = [element for element in sequence if isinstance(element, Plot2D)]
        labelled = [plot for plot in plots if plot.label]
        # every plot labelled: one \legend; otherwise entries after the labelled
        # plots, and the others left out of the legend
        per_plot = self._has_legend and labelled and len(labelled) < len(plots)

        body = ""
        for element in sequence:
            if isinstance(element, Plot2D):
                extra = ["forget plot"] if per_plot and not element.label else []
                body += element.to_addplot(output_unit, extra)
                if per_plot and element.label:
                    body += f"\\addlegendentry{{{element.label}}}\n"
            else:
                body += element.to_tikz(output_unit)

        item_tikz = "".join(item.to_tikz(output_unit) for item in self._items)

        legend_tikz = ""
        if labelled and self._has_legend and not per_plot:
            legend_labels = ", ".join(_braced(plot.label) for plot in labelled)
            legend_tikz = f"\\legend{{{legend_labels}}}\n"

        axis_tikz = f"\\begin{{axis}}[{axis_opts_str}]\n"
        axis_tikz += body
        axis_tikz += item_tikz
        axis_tikz += legend_tikz
        axis_tikz += "\\end{axis}\n"

        return self.add_comment(axis_tikz)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this axis to a plain dictionary.

        Returns:
            A dictionary with all axis state and plots.
        """
        serialized = serialize_tikz_value(
            {
                "type": "Axis2D",
                "xlabel": self._xlabel,
                "ylabel": self._ylabel,
                "title": self._title,
                "xlim": self._xlim,
                "ylim": self._ylim,
                "xlog": self._xlog,
                "ylog": self._ylog,
                "grid": self._grid,
                "width": self._width,
                "height": self._height,
                "plots": [plot.to_dict() for plot in self._plots],
                "items": [item.to_dict() for item in self._items],
                "extras": [extra.to_dict() for extra in self._extras],
                "order": [list(entry) for entry in self._order],
                "ticks": self._ticks,
                "legend_pos": self._legend_pos,
                "legend_style": self._legend_style,
                "options": self.options,
                "kwargs": self.kwargs,
            }
        )
        if not isinstance(serialized, dict):
            raise TypeError("Serialized axis data must remain a dict.")
        return serialized

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Axis2D":
        """Reconstruct an Axis2D from a dictionary.

        Args:
            d: Dictionary as produced by to_dict().

        Returns:
            A new Axis2D instance.
        """
        restored = deserialize_tikz_value(d)
        if not isinstance(restored, dict):
            raise TypeError("Serialized axis data must deserialize to a dict.")
        kwargs = restored.get("kwargs", {})
        if not isinstance(kwargs, dict):
            raise TypeError("Serialized axis kwargs must deserialize to a dict.")
        axis = cls(
            xlabel=restored.get("xlabel", ""),
            ylabel=restored.get("ylabel", ""),
            title=restored.get("title", ""),
            xlim=restored.get("xlim"),
            ylim=restored.get("ylim"),
            xlog=restored.get("xlog", False),
            ylog=restored.get("ylog", False),
            grid=restored.get("grid", True),
            width=restored.get("width"),
            height=restored.get("height"),
            options=restored.get("options"),
            **kwargs,
        )

        # Restore plots
        for plot_dict in restored.get("plots", []):
            plot = Plot2D.from_dict(plot_dict)
            axis._plots.append(plot)

        for item_dict in restored.get("items", []):
            if not isinstance(item_dict, dict):
                raise TypeError("Serialized axis items must deserialize to dicts.")
            item_type = item_dict.get("type")
            if item_type == "Coordinate":
                axis._items.append(Coordinate.from_dict(item_dict))
            elif item_type == "Spy":
                coordinate_lookup: dict[str, Coordinate] = {}
                for item in axis._items:
                    if not isinstance(item, Coordinate):
                        continue
                    label = item.label
                    if isinstance(label, str) and label != "":
                        coordinate_lookup[label] = item
                axis._items.append(
                    Spy.from_dict(item_dict, node_lookup=coordinate_lookup)
                )
            else:
                raise ValueError(f"Unknown serialized axis item type: {item_type!r}")

        for extra_dict in restored.get("extras", []):
            if extra_dict.get("type") == "AxisGraphics":
                axis._extras.append(AxisGraphics.from_dict(extra_dict))
            elif extra_dict.get("type") == "RawTikz":
                axis._extras.append(RawTikz.from_dict(extra_dict))
            else:
                raise ValueError(
                    f"Unknown serialized axis extra type: {extra_dict.get('type')!r}"
                )
        axis._order = [
            (str(kind), int(index)) for kind, index in restored.get("order", [])
        ]

        # Restore ticks
        axis._ticks = restored.get("ticks", {})

        # Restore legend position
        axis._legend_pos = restored.get("legend_pos")
        axis._legend_style = restored.get("legend_style", {}) or {}

        return axis

    def _copy_init_kwargs(self) -> dict[str, Any]:
        init_kwargs = super()._copy_init_kwargs()
        init_kwargs["_plots"] = [plot.copy() for plot in self._plots]
        init_kwargs["_items"] = [item.copy() for item in self._items]
        init_kwargs["_extras"] = [extra.copy() for extra in self._extras]
        init_kwargs["_order"] = list(self._order)
        init_kwargs["_ticks"] = self._copy_value(self._ticks)
        init_kwargs["_legend_pos"] = self._copy_value(self._legend_pos)
        init_kwargs["_legend_style"] = self._copy_value(self._legend_style)
        return init_kwargs

    def _copy_from_init_kwargs(self, init_kwargs: dict[str, Any]) -> "Axis2D":
        plots = init_kwargs.pop("_plots", [])
        items = init_kwargs.pop("_items", [])
        extras = init_kwargs.pop("_extras", [])
        order = init_kwargs.pop("_order", [])
        ticks = init_kwargs.pop("_ticks", {})
        legend_pos = init_kwargs.pop("_legend_pos", None)
        legend_style = init_kwargs.pop("_legend_style", {})

        axis = type(self)(**init_kwargs)
        axis._plots = plots
        axis._items = items
        axis._extras = extras
        axis._order = order
        axis._ticks = ticks
        axis._legend_pos = legend_pos
        axis._legend_style = legend_style or {}
        return axis

    coordinate = add_coordinate
    spy = add_spy
