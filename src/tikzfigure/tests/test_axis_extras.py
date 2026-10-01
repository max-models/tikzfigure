"""Axis titles, ticks, legends, images, raw code and point options of pgfplots axes."""

import math

import pytest

from tikzfigure import TikzFigure
from tikzfigure.core.axis import Axis2D
from tikzfigure.core.graphics import AxisGraphics
from tikzfigure.core.plot import Plot2D, format_number

PNG = b"\x89PNG\r\n\x1a\n" + b"not really an image"


class TestTitleLabelsAndTicks:
    def test_title_is_an_axis_option(self):
        axis = Axis2D(title="Energy")
        assert "title=Energy" in axis.to_tikz()

    def test_set_title(self):
        axis = Axis2D()
        axis.set_title("Later")
        assert axis.title == "Later"
        assert "title=Later" in axis.to_tikz()

    def test_texts_with_commas_or_equals_are_braced(self):
        axis = Axis2D(xlabel="time, s", ylabel="a=b", title="[x]")
        tikz = axis.to_tikz()
        assert "xlabel={time, s}" in tikz
        assert "ylabel={a=b}" in tikz
        assert "title={[x]}" in tikz

    def test_plain_texts_are_not_braced(self):
        tikz = Axis2D(xlabel="$x$").to_tikz()
        assert "xlabel=$x$" in tikz

    def test_ticks_are_rendered(self):
        axis = Axis2D()
        axis.set_ticks("x", [0, 1, 2], ["a", "b, c", "d"])
        axis.set_ticks("y", [0.5, 1.5])
        tikz = axis.to_tikz()
        assert "xtick={0,1,2}" in tikz
        assert "xticklabels={{a},{b, c},{d}}" in tikz
        assert "ytick={0.5,1.5}" in tikz
        assert "yticklabels" not in tikz

    def test_grid_none_writes_no_grid_option(self):
        axis = Axis2D(grid=None, options=["xmajorgrids"])
        tikz = axis.to_tikz()
        assert "grid=" not in tikz
        assert "xmajorgrids" in tikz


class TestLegend:
    def test_all_labelled_plots_use_one_legend_command(self):
        axis = Axis2D()
        axis.add_plot([0, 1], [0, 1], label="a")
        axis.add_plot([0, 1], [1, 0], label="b, c")
        axis.set_legend()
        tikz = axis.to_tikz()
        assert "\\legend{a, {b, c}}" in tikz
        assert "forget plot" not in tikz

    def test_unlabelled_plots_are_left_out_of_a_legend(self):
        axis = Axis2D()
        axis.add_plot([0, 1], [0, 1], label="data")
        axis.add_plot([0, 1], [1, 0])
        axis.set_legend()
        tikz = axis.to_tikz()
        assert "\\addlegendentry{data}" in tikz
        assert tikz.count("forget plot") == 1
        assert "\\legend{" not in tikz

    def test_legend_at_a_point(self):
        axis = Axis2D()
        axis.add_plot([0, 1], [0, 1], label="a")
        axis.set_legend(
            at=(0.1, 0.9), anchor="north west", columns=2, style="draw=none"
        )
        tikz = axis.to_tikz()
        assert "legend style={at={(0.1,0.9)}, anchor=north west, draw=none}" in tikz
        assert "legend columns=2" in tikz
        assert "legend pos" not in tikz

    def test_without_set_legend_there_is_none(self):
        axis = Axis2D()
        axis.add_plot([0, 1], [0, 1], label="a")
        tikz = axis.to_tikz()
        assert "\\legend" not in tikz
        assert "\\addlegendentry" not in tikz


class TestPlotOptions:
    def test_cycle_closes_the_path(self):
        plot = Plot2D(x=[0, 1, 1], y=[0, 0, 1], cycle=True)
        assert plot.to_addplot().rstrip().endswith("-- cycle;")

    def test_meta_values_follow_each_point(self):
        plot = Plot2D(x=[0, 1], y=[2, 3], meta=[0.5, 1.5])
        assert "(0,2) [0.5] (1,3) [1.5]" in plot.to_addplot()

    def test_meta_needs_one_value_per_point(self):
        with pytest.raises(ValueError):
            Plot2D(x=[0, 1], y=[2, 3], meta=[0.5])

    def test_precision_rounds_coordinates(self):
        plot = Plot2D(x=[1 / 3], y=[2 / 3], precision=3)
        assert "(0.333,0.667)" in plot.to_addplot()

    def test_extra_options(self):
        plot = Plot2D(x=[0], y=[0], color="red")
        assert "\\addplot[color=red, forget plot]" in plot.to_addplot(
            extra_options=["forget plot"]
        )

    def test_round_trip(self):
        plot = Plot2D(x=[0, 1], y=[1, 2], cycle=True, meta=[3, 4], precision=4)
        restored = Plot2D.from_dict(plot.to_dict())
        assert restored.to_addplot() == plot.to_addplot()

    @pytest.mark.parametrize(
        "value, precision, expected",
        [
            (3, None, "3"),
            (0.1, None, "0.1"),
            (1 / 3, 2, "0.33"),
            (float("nan"), None, "nan"),
            (math.inf, None, "inf"),
            (-math.inf, 3, "-inf"),
        ],
    )
    def test_format_number(self, value, precision, expected):
        assert format_number(value, precision) == expected

    def test_format_number_of_numpy_scalars(self):
        numpy = pytest.importorskip("numpy")
        assert format_number(numpy.float64(0.25)) == "0.25"
        assert format_number(numpy.int64(4)) == "4"


class TestGraphicsAndRaw:
    def test_graphics_from_data(self):
        axis = Axis2D()
        image = axis.add_graphics(0, 1, -1, 2, data=PNG, plot_options=["forget plot"])
        tikz = axis.to_tikz()
        assert (
            f"\\addplot[forget plot] graphics[xmin=0.0, xmax=1.0, ymin=-1.0, ymax=2.0] "
            f"{{{image.filename}}};" in tikz
        )
        assert axis.files() == {image.filename: PNG}

    def test_equal_images_share_a_file_name(self):
        assert (
            AxisGraphics(0, 1, 0, 1, data=PNG).filename
            == AxisGraphics(0, 2, 0, 2, data=PNG).filename
        )

    def test_graphics_from_a_path(self):
        axis = Axis2D()
        axis.add_graphics(0, 1, 0, 1, path="figures/mesh.png")
        assert "{figures/mesh.png};" in axis.to_tikz()
        assert axis.files() == {}

    def test_graphics_need_a_path_or_data(self):
        with pytest.raises(ValueError):
            AxisGraphics(0, 1, 0, 1)
        with pytest.raises(ValueError):
            AxisGraphics(0, 1, 0, 1, path="a.png", data=PNG)

    def test_elements_are_rendered_in_the_order_added(self):
        axis = Axis2D()
        axis.add_graphics(0, 1, 0, 1, data=PNG)
        axis.add_plot([0, 1], [0, 1])
        axis.add_raw("\\node at (axis cs:0.5,0.5) {here};")
        tikz = axis.to_tikz()
        assert tikz.index("graphics") < tikz.index("coordinates") < tikz.index("here")

    def test_round_trip_and_copy_keep_extras_and_order(self):
        axis = Axis2D(title="t")
        axis.add_plot([0, 1], [0, 1])
        axis.add_graphics(0, 1, 0, 1, data=PNG, filename="a.png")
        axis.add_raw("% raw")
        axis.set_legend(at=(0.5, 0.5))
        assert Axis2D.from_dict(axis.to_dict()).to_tikz() == axis.to_tikz()
        assert axis.copy().to_tikz() == axis.to_tikz()


class TestFigureFiles:
    def figure(self):
        fig = TikzFigure()
        axis = fig.axis2d(xlim=(0, 1), ylim=(0, 1))
        axis.add_graphics(0, 1, 0, 1, data=PNG, filename="mesh.png")
        return fig

    def test_files_of_every_axis(self):
        assert self.figure().files() == {"mesh.png": PNG}

    def test_saving_tikz_writes_the_images_next_to_it(self, tmp_path):
        self.figure().savefig(tmp_path / "figure.tikz")
        assert (tmp_path / "figure.tikz").read_text().count("mesh.png") == 1
        assert (tmp_path / "mesh.png").read_bytes() == PNG

    def test_saving_tex_writes_a_standalone_document(self, tmp_path):
        self.figure().savefig(tmp_path / "figure.tex")
        text = (tmp_path / "figure.tex").read_text()
        assert text.startswith("\\documentclass")
        assert "\\usepackage{pgfplots}" in text
        assert (tmp_path / "mesh.png").exists()

    def test_web_compilation_cannot_include_images(self, tmp_path):
        with pytest.raises(RuntimeError, match="image files"):
            self.figure().compile_pdf(tmp_path / "f.pdf", use_web_compilation=True)
