import tikzfigure
from tikzfigure import TikzFigure, colors, decorations, marks, patterns, shapes, styles
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.core.plot import Plot2D


def test_option_object_modules_exported_from_package():
    for module_name in ["patterns", "decorations", "marks", "shapes"]:
        assert hasattr(tikzfigure, module_name)
        assert module_name in tikzfigure.__all__


def test_node_accepts_shape_and_pattern_objects():
    node = Node(
        0,
        0,
        shape=shapes.circle,
        pattern=patterns.north_east_lines,
        pattern_color=colors.blue,
        fill=colors.white,
    )

    tikz = node.to_tikz()

    assert "shape=circle" in tikz
    assert "pattern=north east lines" in tikz
    assert "pattern color=blue" in tikz


def test_draw_accepts_decoration_object():
    fig = TikzFigure()

    path = fig.draw(
        [(0, 0), (2, 0)],
        options=[styles.decorate],
        decoration=decorations.snake,
        color=colors.red,
    )

    tikz = path.to_tikz()

    assert "decorate" in tikz
    assert "decoration=snake" in tikz
    assert "color=red" in tikz


def test_plot_accepts_mark_object():
    plot = Plot2D(
        x=[0, 1, 2],
        y=[0, 1, 4],
        color=colors.blue,
        mark=marks.square,
    )

    assert plot.kwargs["mark"] == marks.square
    assert "mark=square" in plot.tikz_options()


def test_node_serialization_preserves_shape_and_pattern_objects():
    node = Node(
        0,
        0,
        shape=shapes.star,
        pattern=patterns.checkerboard,
        pattern_color=colors.orange,
    )

    data = node.to_dict()

    assert data["kwargs"]["shape"] == {
        "__tikzfigure_serialized_type__": "TikzShape",
        "shape_spec": "star",
    }
    assert data["kwargs"]["pattern"] == {
        "__tikzfigure_serialized_type__": "TikzPattern",
        "pattern_spec": "checkerboard",
    }

    restored = Node.from_dict(data)

    assert restored.kwargs["shape"] == shapes.star
    assert restored.kwargs["pattern"] == patterns.checkerboard
    assert restored.kwargs["pattern_color"] == colors.orange


def test_path_serialization_preserves_decoration_object():
    fig = TikzFigure()

    path = fig.draw(
        [(0, 0), (1, 0)],
        options=[styles.decorate],
        decoration=decorations.coil,
    )

    data = path.to_dict()

    assert data["kwargs"]["decoration"] == {
        "__tikzfigure_serialized_type__": "TikzDecoration",
        "decoration_spec": "coil",
    }

    restored = TikzPath.from_dict(data)

    assert restored.kwargs["decoration"] == decorations.coil


def test_plot_serialization_preserves_mark_object():
    plot = Plot2D(x=[0, 1], y=[1, 0], mark=marks.diamond_filled)

    data = plot.to_dict()

    assert data["kwargs"]["mark"] == {
        "__tikzfigure_serialized_type__": "TikzMark",
        "mark_spec": "diamond*",
    }

    restored = Plot2D.from_dict(data)

    assert restored.kwargs["mark"] == marks.diamond_filled
