import tikzfigure
from tikzfigure import TikzFigure, units
from tikzfigure.core.coordinate import TikzCoordinate
from tikzfigure.core.node import Node
from tikzfigure.core.path import TikzPath
from tikzfigure.units import TikzDimension


def test_tikz_dimension_str():
    assert str(TikzDimension(2.5, "cm")) == "2.5cm"
    assert str(TikzDimension(1, "pt")) == "1pt"
    assert str(TikzDimension(10.0, "mm")) == "10mm"


def test_unit_multiplication():
    d = 2.5 * units.cm
    assert isinstance(d, TikzDimension)
    assert d.value == 2.5
    assert d.unit == "cm"


def test_unit_right_multiplication():
    d = units.cm * 2.5
    assert isinstance(d, TikzDimension)
    assert d.value == 2.5
    assert d.unit == "cm"


def test_all_units_exist():
    for name in ["cm", "mm", "pt", "bp", "in_", "ex", "em", "pc", "dd", "cc", "sp"]:
        assert hasattr(units, name)


def test_conversion_cm_to_pt():
    d = TikzDimension(1.0, "cm")
    result = d.to("pt")
    assert isinstance(result, TikzDimension)
    assert result.unit == "pt"
    assert abs(result.value - 28.4527) < 0.001


def test_conversion_pt_to_cm():
    d = TikzDimension(28.4527, "pt")
    result = d.to("cm")
    assert result.unit == "cm"
    assert abs(result.value - 1.0) < 0.001


def test_conversion_mm_to_pt():
    d = TikzDimension(10.0, "mm")
    result = d.to("pt")
    assert abs(result.value - 28.4527) < 0.001


def test_str_integer_value():
    d = TikzDimension(2, "cm")
    assert str(d) == "2cm"


def test_str_float_value():
    d = TikzDimension(2.5, "cm")
    assert str(d) == "2.5cm"


def test_str_whole_float_value():
    d = TikzDimension(2.0, "cm")
    assert str(d) == "2cm"


def test_tikz_options_method_no_unit():
    n = Node(x=0, y=0, minimum_width="2cm")
    assert "minimum width=2cm" in n.tikz_options()


def test_tikz_options_method_with_tikz_dimension():
    n = Node(x=0, y=0, minimum_width=TikzDimension(2.5, "cm"))
    assert "minimum width=2.5cm" in n.tikz_options()


def test_tikz_options_with_output_unit():
    n = Node(x=0, y=0, minimum_width=TikzDimension(1.0, "cm"))
    opts = n.tikz_options(output_unit="pt")
    assert "minimum width=" in opts
    assert "pt" in opts


def test_coordinate_to_tikz_with_dimension():
    c = TikzCoordinate(2.5 * units.cm, 1.0 * units.cm)
    result = c.to_tikz()
    assert result == "({2.5cm}, {1cm})"


def test_coordinate_to_tikz_output_unit():
    c = TikzCoordinate(1.0 * units.cm, 0.0 * units.cm)
    result = c.to_tikz(output_unit="pt")
    assert "pt" in result
    assert "28" in result  # 1cm = 28.4527pt


def test_coordinate_value_accepts_tikz_dimension():
    d = 2.5 * units.cm
    c = TikzCoordinate(d, 1.0 * units.cm)
    assert c.x is d


def test_node_to_tikz_with_dimension_options():
    n = Node(x=0, y=0, label="n1", minimum_width=2.5 * units.cm)
    tikz = n.to_tikz()
    assert "minimum width=2.5cm" in tikz


def test_node_to_tikz_with_dimension_coords():
    n = Node(x=2.5 * units.cm, y=1.0 * units.cm, label="n1")
    tikz = n.to_tikz()
    assert "2.5cm" in tikz
    assert "1cm" in tikz


def test_node_to_tikz_output_unit():
    n = Node(
        x=1.0 * units.cm, y=0.0 * units.cm, label="n1", minimum_width=1.0 * units.cm
    )
    tikz = n.to_tikz(output_unit="pt")
    assert "cm" not in tikz
    assert "pt" in tikz


def test_path_to_tikz_output_unit_for_inline_coordinates():
    path = TikzPath(
        nodes=[
            TikzCoordinate(1.0 * units.cm, 0.0 * units.cm),
            TikzCoordinate(0.0 * units.cm, 1.0 * units.cm),
        ]
    )
    tikz = path.to_tikz(output_unit="pt")
    assert "pt" in tikz
    assert "cm" not in tikz


def test_generate_tikz_default_unit():
    fig = TikzFigure()
    fig.add_node(x=0, y=0, label="n1", minimum_width=2.5 * units.cm)
    tikz = fig.generate_tikz()
    assert "minimum width=2.5cm" in tikz


def test_generate_tikz_output_unit_pt():
    fig = TikzFigure()
    fig.add_node(x=0, y=0, label="n1", minimum_width=1.0 * units.cm)
    tikz = fig.generate_tikz(output_unit="pt")
    assert "cm" not in tikz.split("tikzpicture")[1]
    assert "pt" in tikz


def test_generate_tikz_plain_string_unchanged():
    fig = TikzFigure()
    fig.add_node(x=0, y=0, label="n1", minimum_width="2.5cm")
    tikz = fig.generate_tikz(output_unit="pt")
    assert "minimum width=2.5cm" in tikz


def test_units_exported_from_package():
    assert hasattr(tikzfigure, "units")
    assert "units" in tikzfigure.__all__
