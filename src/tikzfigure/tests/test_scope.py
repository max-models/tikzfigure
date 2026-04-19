from tikzfigure import TikzFigure, arrows, styles
from tikzfigure.core.scope import Scope


def test_scope_context_renders_local_options_and_nested_items():
    fig = TikzFigure()
    axes = fig.add_style("axes")

    with fig.scope(options=[axes], xshift="1cm") as scope:
        a = scope.node((0, 0), label="A", content="A")
        b = scope.node((1, 0), label="B", content="B")
        scope.draw([a, b], arrows=arrows.forward)

    tikz = fig.generate_tikz()

    assert isinstance(scope, Scope)
    assert "\\begin{scope}[axes, xshift=1cm]" in tikz
    assert "\\draw[->] (A) to (B);" in tikz
    assert "\\end{scope}" in tikz


def test_scope_can_resolve_outer_labels_and_register_inner_nodes():
    fig = TikzFigure()
    outer = fig.node((0, 0), label="outer", content="O")

    with fig.scope(yshift="1cm") as scope:
        inner = scope.node((1, 0), label="inner", content="I")
        scope.draw(["outer", inner], color="blue")

    assert fig.layers.get_node("inner") is inner
    tikz = fig.generate_tikz()
    assert "\\draw[color=blue] (outer) to (inner);" in tikz
    assert outer.label == "outer"


def test_scope_round_trips_through_figure_dict():
    fig = TikzFigure()
    with fig.scope(options=[styles.dashed], xshift="1cm", comment="local") as scope:
        left = scope.node((0, 0), label="L", content="L")
        right = scope.node((1, 0), label="R", content="R")
        scope.draw([left, right], color="red")

    data = fig.to_dict()
    fig2 = TikzFigure.from_dict(data)

    assert data["layers"][0][0]["type"] == "Scope"
    assert fig2.generate_tikz() == fig.generate_tikz()


def test_scope_alias_and_nested_scope_work():
    fig = TikzFigure()
    outer = fig.scope(options=[styles.dotted])
    inner = outer.scope(xshift="2cm")
    inner.raw("% nested")

    tikz = fig.generate_tikz()

    assert isinstance(outer, Scope)
    assert isinstance(inner, Scope)
    assert "\\begin{scope}[dotted]" in tikz
    assert "\\begin{scope}[xshift=2cm]" in tikz
    assert "% nested" in tikz
