import tikzfigure
from tikzfigure import TikzFigure


def test_libraries_module_not_exported_from_package():
    assert not hasattr(tikzfigure, "libraries")
    assert "libraries" not in tikzfigure.__all__


def test_usetikzlibrary_registers_unique_libraries():
    fig = TikzFigure()
    fig.usetikzlibrary("calc", "intersections, positioning", "calc")

    assert fig.tikz_libraries == ["calc", "intersections", "positioning"]


def test_generate_standalone_includes_registered_tikz_libraries():
    fig = TikzFigure()
    fig.usetikzlibrary("arrows.meta", "calc", "intersections")

    latex = fig.generate_standalone()

    assert "\\usetikzlibrary{arrows.meta,calc,intersections}" in latex


def test_tikz_libraries_round_trip_through_dict():
    fig = TikzFigure()
    fig.usetikzlibrary("calc", "positioning")

    data = fig.to_dict()
    fig2 = TikzFigure.from_dict(data)

    assert data["tikz_libraries"] == ["calc", "positioning"]
    assert fig2.tikz_libraries == ["calc", "positioning"]
