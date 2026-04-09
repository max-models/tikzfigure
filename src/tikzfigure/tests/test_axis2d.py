import pytest

from tikzfigure import TikzFigure
from tikzfigure.core.axis import Axis2D
from tikzfigure.core.plot import Plot2D


class TestPlot2D:
    def test_plot2d_basic_construction(self):
        """Test Plot2D stores x, y data and label."""
        x = [0, 1, 2]
        y = [0, 1, 4]
        plot = Plot2D(x=x, y=y, label="data1")

        assert plot.x == x
        assert plot.y == y
        assert plot.label == "data1"

    def test_plot2d_with_options(self):
        """Test Plot2D accepts options and kwargs."""
        plot = Plot2D(
            x=[0, 1, 2],
            y=[0, 1, 4],
            label="test",
            options=["thick"],
            color="red",
            mark="*",
        )

        assert plot.options == ["thick"]
        assert plot.kwargs["color"] == "red"
        assert plot.kwargs["mark"] == "*"

    def test_plot2d_tikz_options(self):
        """Test Plot2D.tikz_options renders correctly."""
        plot = Plot2D(
            x=[0, 1], y=[0, 1], options=["thick"], color="red", line_width="2pt"
        )

        options_str = plot.tikz_options
        assert "thick" in options_str
        assert "color=red" in options_str
        assert "line width=2pt" in options_str

    def test_plot2d_serialization_round_trip(self):
        """Test serialization and deserialization round trip."""
        plot1 = Plot2D(x=[0, 1, 2], y=[0, 1, 4], label="test", comment="My data")
        d = plot1.to_dict()
        plot2 = Plot2D.from_dict(d)

        assert plot2.x == plot1.x
        assert plot2.y == plot1.y
        assert plot2.label == plot1.label
        assert plot2.comment == plot1.comment


class TestAxis2D:
    def test_axis2d_basic_construction(self):
        """Test Axis2D constructor and basic properties."""
        axis = Axis2D(
            xlabel="X Label", ylabel="Y Label", xlim=(0, 10), ylim=(0, 20), grid=True
        )

        assert axis.xlabel == "X Label"
        assert axis.ylabel == "Y Label"
        assert axis.xlim == (0, 10)
        assert axis.ylim == (0, 20)
        assert axis.grid is True

    def test_axis2d_defaults(self):
        """Test Axis2D with default values."""
        axis = Axis2D()

        assert axis.xlabel == ""
        assert axis.ylabel == ""
        assert axis.xlim is None
        assert axis.ylim is None
        assert axis.grid is True

    def test_axis2d_plots_list(self):
        """Test Axis2D has empty plots list on construction."""
        axis = Axis2D()
        assert axis.plots == []

    def test_axis2d_invalid_xlim_tuple(self):
        """Test that invalid xlim raises ValueError."""
        with pytest.raises(ValueError):
            Axis2D(xlim=(0, 10, 20))  # 3-tuple instead of 2-tuple

    def test_axis2d_invalid_xlim_non_numeric(self):
        """Test that non-numeric xlim raises ValueError."""
        with pytest.raises(ValueError):
            Axis2D(xlim=("a", "b"))  # Non-numeric values

    def test_axis2d_invalid_ylim_type(self):
        """Test that non-tuple ylim raises ValueError."""
        with pytest.raises(ValueError):
            Axis2D(ylim=[0, 10])  # List instead of tuple

    def test_axis2d_set_xlabel(self):
        """Test set_xlabel method."""
        axis = Axis2D()
        axis.set_xlabel("Time (s)")
        assert axis.xlabel == "Time (s)"

    def test_axis2d_set_ylabel(self):
        """Test set_ylabel method."""
        axis = Axis2D()
        axis.set_ylabel("Voltage (V)")
        assert axis.ylabel == "Voltage (V)"

    def test_axis2d_set_xlim(self):
        """Test set_xlim method."""
        axis = Axis2D()
        axis.set_xlim(0, 100)
        assert axis.xlim == (0, 100)

    def test_axis2d_set_ylim(self):
        """Test set_ylim method."""
        axis = Axis2D()
        axis.set_ylim(-10, 10)
        assert axis.ylim == (-10, 10)

    def test_axis2d_set_grid(self):
        """Test set_grid method."""
        axis = Axis2D(grid=True)
        axis.set_grid(False)
        assert axis.grid is False

    def test_axis2d_set_ticks(self):
        """Test set_ticks method."""
        axis = Axis2D()
        axis.set_ticks("x", [0, 25, 50, 75, 100])
        assert "x" in axis._ticks
        assert axis._ticks["x"][0] == [0, 25, 50, 75, 100]
        assert axis._ticks["x"][1] is None

    def test_axis2d_set_ticks_with_labels(self):
        """Test set_ticks with custom labels."""
        axis = Axis2D()
        axis.set_ticks("y", [0, 1, 2], labels=["Low", "Med", "High"])
        assert axis._ticks["y"][0] == [0, 1, 2]
        assert axis._ticks["y"][1] == ["Low", "Med", "High"]

    def test_axis2d_set_legend(self):
        """Test set_legend method."""
        axis = Axis2D()
        axis.set_legend(position="north west")
        assert axis._legend_pos == "north west"

    def test_axis2d_set_xlim_validation(self):
        """Test that set_xlim validates input."""
        axis = Axis2D()
        with pytest.raises(ValueError):
            axis.set_xlim("a", "b")  # Non-numeric

    def test_axis2d_set_ylim_validation(self):
        """Test that set_ylim validates input."""
        axis = Axis2D()
        with pytest.raises(ValueError):
            axis.set_ylim(None, 10)  # Non-numeric

    def test_axis2d_set_ticks_empty_positions(self):
        """Test that set_ticks rejects empty positions."""
        axis = Axis2D()
        with pytest.raises(ValueError):
            axis.set_ticks("x", [])

    def test_axis2d_set_ticks_label_mismatch(self):
        """Test that set_ticks validates label/position lengths match."""
        axis = Axis2D()
        with pytest.raises(ValueError):
            axis.set_ticks("y", [0, 1, 2], labels=["A", "B"])  # 3 positions, 2 labels

    def test_axis2d_add_plot(self):
        """Test add_plot creates and registers Plot2D."""
        axis = Axis2D()
        plot = axis.add_plot([0, 1, 2], [0, 1, 4], label="data")

        assert isinstance(plot, Plot2D)
        assert plot.x == [0, 1, 2]
        assert plot.y == [0, 1, 4]
        assert plot.label == "data"
        assert len(axis.plots) == 1
        assert axis.plots[0] is plot

    def test_axis2d_add_multiple_plots(self):
        """Test adding multiple plots to same axis."""
        axis = Axis2D()
        plot1 = axis.add_plot([0, 1, 2], [0, 1, 4], label="y=x²", color="red")
        plot2 = axis.add_plot([0, 1, 2], [0, 2, 4], label="y=2x", color="blue")

        assert len(axis.plots) == 2
        assert axis.plots[0] is plot1
        assert axis.plots[1] is plot2
        assert plot1.kwargs["color"] == "red"
        assert plot2.kwargs["color"] == "blue"

    def test_axis2d_to_tikz_basic(self):
        """Test basic to_tikz output."""
        axis = Axis2D(xlabel="X", ylabel="Y")
        axis.add_plot([0, 1, 2], [0, 1, 4])

        tikz = axis.to_tikz()

        assert "\\begin{axis}" in tikz
        assert "\\end{axis}" in tikz
        assert "xlabel=X" in tikz
        assert "ylabel=Y" in tikz
        assert "\\addplot" in tikz
        assert "coordinates" in tikz
        assert "(0,0)" in tikz
        assert "(1,1)" in tikz
        assert "(2,4)" in tikz

    def test_axis2d_to_tikz_with_limits(self):
        """Test to_tikz with axis limits."""
        axis = Axis2D(xlim=(0, 10), ylim=(0, 20))
        axis.add_plot([0, 10], [0, 20])

        tikz = axis.to_tikz()

        assert "xmin=0" in tikz
        assert "xmax=10" in tikz
        assert "ymin=0" in tikz
        assert "ymax=20" in tikz

    def test_axis2d_to_tikz_with_grid(self):
        """Test to_tikz with grid setting."""
        axis = Axis2D(grid=True)
        axis.add_plot([0, 1], [0, 1])
        tikz_with_grid = axis.to_tikz()
        assert "grid=true" in tikz_with_grid

        axis2 = Axis2D(grid=False)
        axis2.add_plot([0, 1], [0, 1])
        tikz_no_grid = axis2.to_tikz()
        assert "grid=false" in tikz_no_grid

    def test_axis2d_to_tikz_multiple_plots(self):
        """Test to_tikz with multiple plots."""
        axis = Axis2D()
        axis.add_plot([0, 1], [0, 1], label="plot1", color="red")
        axis.add_plot([0, 1], [1, 0], label="plot2", color="blue")

        tikz = axis.to_tikz()

        # Both plots should be present
        addplot_count = tikz.count("\\addplot")
        assert addplot_count == 2
        assert "color=red" in tikz
        assert "color=blue" in tikz

    def test_axis2d_to_tikz_with_legend(self):
        """Test to_tikz with legend."""
        axis = Axis2D()
        axis.add_plot([0, 1], [0, 1], label="A")
        axis.add_plot([0, 1], [1, 0], label="B")
        axis.set_legend(position="north east")

        tikz = axis.to_tikz()

        assert "legend pos=north east" in tikz
        assert "\\legend{A, B}" in tikz


class TestAxis2DSerialization:
    def test_axis2d_to_dict(self):
        """Test Axis2D.to_dict serialization."""
        axis = Axis2D(xlabel="X", ylabel="Y", xlim=(0, 10), ylim=(0, 20), grid=True)
        axis.add_plot([0, 1, 2], [0, 1, 4], label="plot1", color="red")

        d = axis.to_dict()

        assert d["type"] == "Axis2D"
        assert d["xlabel"] == "X"
        assert d["ylabel"] == "Y"
        assert d["xlim"] == (0, 10)
        assert d["ylim"] == (0, 20)
        assert d["grid"] is True
        assert len(d["plots"]) == 1
        assert d["plots"][0]["label"] == "plot1"

    def test_axis2d_from_dict(self):
        """Test Axis2D.from_dict deserialization."""
        d = {
            "type": "Axis2D",
            "xlabel": "X",
            "ylabel": "Y",
            "xlim": (0, 10),
            "ylim": (0, 20),
            "grid": True,
            "plots": [
                {
                    "type": "Plot2D",
                    "x": [0, 1, 2],
                    "y": [0, 1, 4],
                    "label": "plot1",
                    "options": [],
                    "kwargs": {"color": "red"},
                }
            ],
            "ticks": {},
            "legend_pos": None,
            "options": [],
            "kwargs": {},
        }

        axis = Axis2D.from_dict(d)

        assert axis.xlabel == "X"
        assert axis.ylabel == "Y"
        assert axis.xlim == (0, 10)
        assert axis.ylim == (0, 20)
        assert axis.grid is True
        assert len(axis.plots) == 1
        assert axis.plots[0].label == "plot1"
        assert axis.plots[0].kwargs["color"] == "red"

    def test_axis2d_round_trip(self):
        """Test serialization and deserialization round trip."""
        axis1 = Axis2D(xlabel="Time", ylabel="Temp", grid=False)
        axis1.add_plot([1, 2, 3], [10, 20, 30], label="sensor1")

        d = axis1.to_dict()
        axis2 = Axis2D.from_dict(d)

        assert axis2.xlabel == axis1.xlabel
        assert axis2.ylabel == axis1.ylabel
        assert axis2.grid == axis1.grid
        assert len(axis2.plots) == len(axis1.plots)


class TestTikzFigureAxis2D:
    def test_tikzfigure_axis2d_method(self):
        """Test TikzFigure.axis2d creates and registers Axis2D."""
        fig = TikzFigure()
        axis = fig.axis2d(xlabel="X", ylabel="Y")

        assert isinstance(axis, Axis2D)
        assert axis.xlabel == "X"
        assert axis.ylabel == "Y"
        assert len(fig.axes) == 1
        assert fig.axes[0] is axis

    def test_tikzfigure_multiple_axes(self):
        """Test TikzFigure can hold multiple axes."""
        fig = TikzFigure()
        axis1 = fig.axis2d(xlabel="Time")
        axis2 = fig.axis2d(xlabel="Distance")

        assert len(fig.axes) == 2
        assert fig.axes[0] is axis1

    def test_tikzfigure_generate_tikz_with_axis(self):
        """Test that generate_tikz includes axes rendering."""
        fig = TikzFigure()
        axis = fig.axis2d(xlabel="X", ylabel="Y")
        axis.add_plot([0, 1, 2], [0, 1, 4])

        tikz = fig.generate_tikz()

        assert "\\begin{axis}" in tikz
        assert "\\end{axis}" in tikz
        assert "xlabel=X" in tikz
        assert "ylabel=Y" in tikz
        assert "\\addplot" in tikz


class TestTikzFigureSerialization:
    def test_tikzfigure_to_dict_with_axes(self):
        """Test TikzFigure.to_dict serializes axes."""
        fig = TikzFigure()
        axis = fig.axis2d(xlabel="X")
        axis.add_plot([0, 1], [0, 1])
        d = fig.to_dict()

        assert "axes" in d
        assert len(d["axes"]) == 1
        assert d["axes"][0]["type"] == "Axis2D"

    def test_tikzfigure_from_dict_with_axes(self):
        """Test TikzFigure.from_dict reconstructs axes."""
        fig1 = TikzFigure()
        axis1 = fig1.axis2d(xlabel="Time", ylabel="Temp")
        axis1.add_plot([0, 1, 2], [10, 20, 30], label="sensor1")
        d = fig1.to_dict()

        fig2 = TikzFigure.from_dict(d)

        assert len(fig2.axes) == 1
        assert fig2.axes[0].xlabel == "Time"
        assert fig2.axes[0].ylabel == "Temp"
        assert len(fig2.axes[0].plots) == 1
        assert fig2.axes[0].plots[0].label == "sensor1"


class TestAxis2DIntegration:
    def test_full_workflow(self):
        """Test complete workflow: create figure, add axis, plots, generate TikZ."""
        fig = TikzFigure()

        # Create axis with configuration
        ax = fig.axis2d(
            xlabel="Time (s)", ylabel="Amplitude", xlim=(0, 10), ylim=(-1, 1), grid=True
        )

        # Add multiple plots
        ax.add_plot(
            [0, 1, 2, 3, 4, 5],
            [0, 0.5, 0.866, 1, 0.866, 0.5],
            label="sin(x)",
            color="red",
            mark="*",
        )
        ax.add_plot(
            [0, 1, 2, 3, 4, 5],
            [1, 0.866, 0.5, 0, -0.5, -0.866],
            label="cos(x)",
            color="blue",
            mark="square",
        )

        # Configure legend
        ax.set_legend(position="north east")

        # Generate TikZ
        tikz = fig.generate_tikz()

        # Verify structure
        assert "\\begin{axis}" in tikz
        assert "\\end{axis}" in tikz
        assert "xlabel=Time (s)" in tikz
        assert "ylabel=Amplitude" in tikz
        assert "xmin=0" in tikz
        assert "xmax=10" in tikz
        assert "ymin=-1" in tikz
        assert "ymax=1" in tikz
        assert "grid=true" in tikz
        assert "legend pos=north east" in tikz

        # Verify plots
        assert tikz.count("\\addplot") == 2
        assert "color=red" in tikz
        assert "color=blue" in tikz
        assert "mark=*" in tikz
        assert "mark=square" in tikz
        assert "sin(x)" in tikz
        assert "cos(x)" in tikz
        assert "\\legend{sin(x), cos(x)}" in tikz

        # Verify coordinates
        assert "(0,0)" in tikz
        assert "(1,0.5)" in tikz

    def test_axis_without_legend(self):
        """Test axis renders correctly without legend."""
        fig = TikzFigure()
        ax = fig.axis2d()
        ax.add_plot([0, 1], [0, 1])  # No label

        tikz = fig.generate_tikz()

        # Should not have legend command since no plot labels
        assert "\\legend" not in tikz
