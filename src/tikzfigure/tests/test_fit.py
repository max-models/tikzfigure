import pytest

from tikzfigure.core.figure import TikzFigure
from tikzfigure.core.fit import Fit, FitLibrary


def test_fit_to_tikz_basic():
    fit = Fit(targets=["a", "b"], label="box")
    tikz = fit.to_tikz()
    assert "\\node[fit=(a)(b)] (box) {};\n" == tikz


def test_fit_with_options_and_content():
    fit = Fit(
        targets=["a", "b"],
        label="box",
        content="Group",
        options=["draw", "dashed"],
        inner_sep="5pt",
    )
    tikz = fit.to_tikz()
    assert "fit=(a)(b), draw, dashed, inner sep=5pt" in tikz
    assert "{Group}" in tikz


def test_fit_requires_at_least_one_target():
    with pytest.raises(ValueError):
        Fit(targets=[])


def test_fit_library_build_fit_value():
    assert FitLibrary.build_fit_value(["a", "b.north"]) == "(a)(b.north)"


def test_fit_to_dict_from_dict_round_trip():
    fit = Fit(
        targets=["a", "b.north"],
        label="box",
        content="Group",
        options=["draw"],
        inner_sep="5pt",
    )
    restored = Fit.from_dict(fit.to_dict())
    assert restored.to_dict() == fit.to_dict()
    assert restored.to_tikz() == fit.to_tikz()


def test_figure_add_fit_registers_library_and_resolves_nodes():
    fig = TikzFigure()
    a = fig.add_node((0, 0), content="A")
    b = fig.add_node((2, 1), content="B")
    fit = fig.add_fit([a, b], options=["draw", "dashed"])

    assert "fit" in fig.tikz_libraries
    assert fit.targets == [a.label, b.label]
    assert fit.label != ""

    tikz = fig.generate_tikz()
    assert f"fit=({a.label})({b.label})" in tikz


def test_figure_add_fit_accepts_label_strings_with_anchor():
    fig = TikzFigure()
    fig.add_node((0, 0), label="x", content="X")
    fig.add_coordinate("c1", (1, 1))
    fit = fig.add_fit(["x.north", "c1"], label="box")
    assert fit.targets == ["x.north", "c1"]


def test_figure_add_fit_rejects_unknown_label():
    fig = TikzFigure()
    fig.add_node((0, 0), label="x", content="X")
    with pytest.raises(ValueError):
        fig.add_fit(["does-not-exist"])


def test_figure_add_fit_rejects_non_list_targets():
    fig = TikzFigure()
    fig.add_node((0, 0), label="x", content="X")
    with pytest.raises(ValueError):
        fig.add_fit("x")


def test_figure_fit_serialization_round_trip():
    fig = TikzFigure()
    a = fig.add_node((0, 0), content="A")
    b = fig.add_node((2, 1), content="B")
    fig.add_fit([a, b], label="box", options=["draw"])

    data = fig.to_dict()
    restored = TikzFigure.from_dict(data)
    assert restored.to_dict() == data
    assert restored.generate_tikz() == fig.generate_tikz()


def test_figure_add_fit_second_auto_label_increments_counter():
    fig = TikzFigure()
    a = fig.add_node((0, 0), content="A", label="a")
    first = fig.add_fit([a])
    second = fig.add_fit([a])
    assert first.label != second.label
    assert int(second.label[len("node") :]) == int(first.label[len("node") :]) + 1
