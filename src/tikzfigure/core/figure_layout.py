from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tikzfigure.core.axis import Axis2D
from tikzfigure.core.constants import TAB

if TYPE_CHECKING:
    from tikzfigure.core.figure import TikzFigure


class FigureLayoutMixin:
    _subfigure_rows: int | None
    _subfigure_cols: int | None
    _subfigure_position: int
    _subfigure_axes: list[tuple[Axis2D, float]]
    _subfigure_grid: dict[tuple[int, int], tuple[Any, float] | tuple[Any, float, str]]

    def subfigure_axis(
        self,
        xlabel: str = "",
        ylabel: str = "",
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        grid: bool = True,
        width: float = 0.45,
        height: str | int | float | None = None,
        comment: str | None = None,
        **kwargs: Any,
    ) -> Axis2D:
        """Create a 2D axis for side-by-side subfigure layout."""
        if not (0 < width <= 1.0):
            raise ValueError(
                f"subfigure width must be in range (0.0, 1.0], got {width}"
            )

        axis = Axis2D(
            xlabel=xlabel,
            ylabel=ylabel,
            xlim=xlim,
            ylim=ylim,
            grid=grid,
            height=height,
            label="",
            comment=comment,
            layer=0,
            **kwargs,
        )
        if self._subfigure_rows is not None:
            assert self._subfigure_cols is not None
            if self._subfigure_position >= self._subfigure_rows * self._subfigure_cols:
                raise ValueError(
                    f"Subfigure grid ({self._subfigure_rows}x{self._subfigure_cols}) is full. "
                    f"Cannot add more axes."
                )

            row = self._subfigure_position // self._subfigure_cols
            col = self._subfigure_position % self._subfigure_cols
            self._subfigure_grid[(row, col)] = (axis, width)
            self._subfigure_position += 1
        else:
            self._subfigure_axes.append((axis, width))

        return axis

    def add_subfigure(
        self,
        width: float = 0.45,
        height: str | int | float | None = None,
    ) -> "TikzFigure":
        """Create a subfigure using the full TikZ API in grid layout."""
        if width <= 0 or width > 1.0:
            raise ValueError(f"width must be in range (0.0, 1.0], got {width}")

        if self._subfigure_rows is None:
            raise ValueError(
                "add_subfigure() can only be used with grid layout. "
                "Create figure with rows and cols: TikzFigure(rows=2, cols=2)"
            )
        assert self._subfigure_cols is not None

        if self._subfigure_position >= self._subfigure_rows * self._subfigure_cols:
            raise ValueError(
                f"Subfigure grid ({self._subfigure_rows}x{self._subfigure_cols}) is full. "
                f"Cannot add more subfigures."
            )

        height_str: str | None = None
        if height is not None:
            if isinstance(height, str):
                if not any(
                    height.endswith(unit) for unit in ["cm", "pt", "mm", "ex", "in"]
                ):
                    raise ValueError(
                        f'height string must include a unit (e.g., "6cm"), got "{height}"'
                    )
                height_str = height
            elif isinstance(height, (int, float)):
                if height <= 0:
                    raise ValueError(f"height must be positive, got {height}")
                height_str = f"{height}cm"
            else:
                raise TypeError(
                    f"height must be a string, number, or None, got {type(height).__name__}"
                )

        row = self._subfigure_position // self._subfigure_cols
        col = self._subfigure_position % self._subfigure_cols

        from tikzfigure.core.figure import TikzFigure

        subfig = TikzFigure(ndim=2)
        subfig._is_bare_subfigure = True
        self._subfigure_grid[(row, col)] = (subfig, width, height_str or "None")
        self._subfigure_position += 1

        return subfig

    def _render_axis_in_groupplot(self, axis: Axis2D) -> str:
        axis_tikz = axis.to_tikz()
        axis_tikz = axis_tikz.replace("\\begin{tikzpicture}\n", "")
        axis_tikz = axis_tikz.replace("\\end{tikzpicture}", "")
        axis_tikz = axis_tikz.strip()
        axis_tikz = axis_tikz.replace("\\begin{axis}[", "\\nextgroupplot[")

        has_function = any(plot.is_function for plot in axis.plots)
        if has_function and axis.xlim:
            xmin, xmax = axis.xlim
            axis_tikz = axis_tikz.replace(
                "\\nextgroupplot[",
                f"\\nextgroupplot[domain={xmin}:{xmax}, ",
                1,
            )

        axis_tikz = axis_tikz.replace("\\end{axis}", "")
        axis_lines = axis_tikz.split("\n")
        return "\n".join([TAB + line for line in axis_lines]) + "\n"

    def _render_groupplot_grid(self, num_rows: int, num_cols: int) -> str:
        group_opts = (
            f"group style={{"
            f"group size={num_cols} by {num_rows}, "
            f"horizontal sep=1.5cm, "
            f"vertical sep=2cm"
            f"}}"
        )
        result = f"\\begin{{groupplot}}[{group_opts}]\n"

        for row in range(num_rows):
            for col in range(num_cols):
                if (row, col) in self._subfigure_grid:
                    item_data = self._subfigure_grid[(row, col)]
                    if isinstance(item_data[0], Axis2D):
                        result += self._render_axis_in_groupplot(item_data[0])

        result += "\\end{groupplot}\n"
        return result

    def _render_mixed_grid(self, num_rows: int, num_cols: int) -> str:
        textwidth_cm = 14.0
        h_sep = 2.0
        v_sep = 2.0
        default_height = 6.0

        from tikzfigure.core.figure import TikzFigure

        col_widths: list[float] = []
        for col in range(num_cols):
            max_w = 0.0
            for row in range(num_rows):
                if (row, col) in self._subfigure_grid:
                    w = self._subfigure_grid[(row, col)][1]
                    max_w = max(max_w, w * textwidth_cm)
            col_widths.append(max_w if max_w > 0 else 7.0)

        x_offsets = [0.0]
        for c in range(num_cols - 1):
            x_offsets.append(x_offsets[-1] + col_widths[c] + h_sep)

        row_heights: list[float] = []
        for row in range(num_rows):
            max_h = default_height
            for col in range(num_cols):
                if (row, col) in self._subfigure_grid:
                    item_data = self._subfigure_grid[(row, col)]
                    if (
                        len(item_data) == 3
                        and isinstance(item_data[0], TikzFigure)
                        and item_data[2] != "None"
                    ):
                        h_str = str(item_data[2])
                        if h_str.endswith("cm"):
                            max_h = max(max_h, float(h_str[:-2]))
            row_heights.append(max_h)

        y_offsets = [0.0]
        for r in range(num_rows - 1):
            y_offsets.append(y_offsets[-1] - row_heights[r] - v_sep)

        result = ""
        for row in range(num_rows):
            for col in range(num_cols):
                if (row, col) not in self._subfigure_grid:
                    continue

                item_data = self._subfigure_grid[(row, col)]
                item: Axis2D | TikzFigure
                if len(item_data) == 2 and isinstance(item_data[0], Axis2D):
                    item = item_data[0]
                    width = item_data[1]
                    height_str = "None"
                else:
                    assert len(item_data) == 3
                    item = item_data[0]
                    width = item_data[1]
                    height_str = item_data[2]

                x = x_offsets[col]
                y = y_offsets[row]
                width_cm = f"{width * textwidth_cm:.1f}cm"

                if isinstance(item, Axis2D):
                    result += f"\\begin{{scope}}[xshift={x:.1f}cm, yshift={y:.1f}cm]\n"
                    axis_tikz = item.to_tikz()
                    if not item._width:
                        axis_tikz = axis_tikz.replace(
                            "\\begin{axis}[",
                            f"\\begin{{axis}}[width={width_cm}, ",
                        )
                    has_function = any(plot.is_function for plot in item.plots)
                    if has_function and item.xlim:
                        xmin, xmax = item.xlim
                        axis_tikz = axis_tikz.replace(
                            "\\begin{axis}[",
                            f"\\begin{{axis}}[domain={xmin}:{xmax}, ",
                            1,
                        )
                    for line in axis_tikz.split("\n"):
                        if line.strip():
                            result += f"{TAB}{line}\n"
                    result += "\\end{scope}\n"
                elif isinstance(item, TikzFigure):
                    result += f"\\begin{{scope}}[xshift={x:.1f}cm, yshift={y:.1f}cm]\n"
                    for layer_label, layer in item._layers.layers.items():
                        if isinstance(layer_label, int):
                            for tikz_obj in layer.items:
                                tikz_content = tikz_obj.to_tikz()
                                for line in tikz_content.split("\n"):
                                    if line.strip():
                                        result += f"{TAB}{line}\n"
                    result += "\\end{scope}\n"

        return result

    @staticmethod
    def generate_subfigures(
        figures: list["TikzFigure"],
        labels: list[str] | None = None,
        widths: list[float] | None = None,
        spacing: str = "0.5cm",
    ) -> str:
        if not figures:
            raise ValueError("Must provide at least one figure")

        if labels is not None and len(labels) != len(figures):
            raise ValueError(
                f"labels length ({len(labels)}) must match figures length "
                f"({len(figures)})"
            )

        if widths is not None and len(widths) != len(figures):
            raise ValueError(
                f"widths length ({len(widths)}) must match figures length "
                f"({len(figures)})"
            )

        if widths is None:
            num_figs = len(figures)
            available_width = 1.0 - (num_figs - 1) * 0.05
            width_each = available_width / num_figs
            widths = [width_each] * num_figs

        latex_code = "\\begin{figure}\n"

        for i, fig in enumerate(figures):
            width = widths[i]
            label = labels[i] if labels else ""
            tikz_code = fig.generate_tikz(skip_header=True)
            tikz_code = tikz_code.replace("\\begin{figure}", "").replace(
                "\\end{figure}", ""
            )

            latex_code += f"{TAB}\\begin{{subfigure}}{{{width}\\textwidth}}\n"
            latex_code += f"{TAB * 2}\\centering\n"
            latex_code += f"{TAB * 2}{tikz_code}\n"

            if label:
                latex_code += f"{TAB * 2}\\label{{{label}}}\n"

            latex_code += f"{TAB}\\end{{subfigure}}\n"

            if i < len(figures) - 1:
                latex_code += f"{TAB}\\hspace{{{spacing}}}\n"

        latex_code += "\\end{figure}\n"
        return latex_code
