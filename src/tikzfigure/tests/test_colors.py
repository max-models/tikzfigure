import tikzfigure
from tikzfigure import TikzFigure, colors
from tikzfigure.colors import TikzColor
from tikzfigure.core.node import Node


def test_colors_exported_from_package():
    assert hasattr(tikzfigure, "colors")
    assert "colors" in tikzfigure.__all__


def test_common_xcolor_names_are_available():
    assert str(colors.red) == "red"
    assert str(colors.ProcessBlue) == "ProcessBlue"
    assert str(colors.AliceBlue) == "AliceBlue"
    assert str(colors.blue1) == "Blue1"


def test_color_mix_expression():
    mixed = colors.red.mix(colors.blue, 10)
    assert isinstance(mixed, TikzColor)
    assert str(mixed) == "red!10!blue"


def test_color_mix_default_percent_is_half():
    mixed = colors.red.mix(colors.blue)
    assert str(mixed) == "red!50!blue"


def test_color_mix_fractional_percent():
    mixed = colors.red.mix(colors.blue, 0.25)
    assert str(mixed) == "red!25!blue"


def test_color_mix_chain_expression():
    mixed = colors.red.mix(colors.blue, 10).mix(colors.white, 0.25)
    assert str(mixed) == "red!10!blue!25!white"


def test_node_accepts_tikz_color():
    node = Node(0, 0, fill=colors.red.mix(colors.blue, 10), draw=colors.ProcessBlue)
    tikz = node.to_tikz()
    assert "fill=red!10!blue" in tikz
    assert "draw=ProcessBlue" in tikz


def test_node_to_dict_stringifies_tikz_color():
    node = Node(0, 0, fill=colors.red, draw=colors.AliceBlue)
    data = node.to_dict()
    assert data["kwargs"]["fill"] == "red"
    assert data["kwargs"]["draw"] == "AliceBlue"


def test_colorlet_accepts_tikz_color():
    fig = TikzFigure()
    fig.colorlet("accent", colors.ProcessBlue.mix(colors.white, 20))
    tikz = fig.generate_tikz()
    assert "\\colorlet{accent}{ProcessBlue!20!white}" in tikz


def test_generate_standalone_enables_xcolor_name_sets():
    fig = TikzFigure()
    latex = fig.generate_standalone()
    assert "\\PassOptionsToPackage{dvipsnames,svgnames,x11names}{xcolor}" in latex
