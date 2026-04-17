import tikzfigure
from tikzfigure import TikzFigure, arrows, styles, units
from tikzfigure.arrows import TikzArrow
from tikzfigure.options import normalize_options
from tikzfigure.styles import TikzStyle


def test_styles_and_arrows_exported_from_package():
    assert hasattr(tikzfigure, "styles")
    assert hasattr(tikzfigure, "arrows")
    assert hasattr(tikzfigure, "options")
    assert "styles" in tikzfigure.__all__
    assert "arrows" in tikzfigure.__all__
    assert "options" in tikzfigure.__all__


def test_public_option_normalizer_accepts_single_values_and_sequences():
    assert normalize_options(styles.dashed) == [styles.dashed]
    assert normalize_options((styles.dashed, arrows.forward)) == [
        styles.dashed,
        arrows.forward,
    ]


def test_common_style_tokens_are_available():
    assert isinstance(styles.dashed, TikzStyle)
    assert isinstance(styles.thick, TikzStyle)
    assert str(styles.densely_dashed) == "densely dashed"
    assert str(styles.line_width(3 * units.pt)) == "line width=3pt"


def test_common_arrow_tokens_are_available():
    assert isinstance(arrows.forward, TikzArrow)
    assert str(arrows.forward) == "->"
    assert str(arrows.stealth) == "-stealth"


def test_draw_accepts_style_tokens_in_options():
    fig = TikzFigure()
    path = fig.draw(
        [(0, 0), (1, 0)],
        options=[styles.dashed, styles.line_width(2 * units.pt)],
    )

    assert "\\draw[dashed, line width=2pt] (0, 0) to (1, 0);" in path.to_tikz()


def test_draw_accepts_arrow_objects():
    fig = TikzFigure()
    path = fig.draw([(0, 0), (1, 0)], arrows=arrows.stealth, color="black")

    assert "\\draw[-stealth, color=black] (0, 0) to (1, 0);" in path.to_tikz()


def test_line_accepts_style_values_for_caps_and_joins():
    fig = TikzFigure()
    line = fig.line((0, 0), (1, 0), line_cap=styles.round, line_join=styles.bevel)

    assert (
        "\\draw[line cap=round, line join=bevel] ({0}, {0}) -- ({1}, {0});"
        in line.to_tikz()
    )


def test_line_accepts_style_tokens_in_options():
    fig = TikzFigure()
    line = fig.line((0, 0), (1, 0), options=[styles.dashed], color="green")

    assert "\\draw[dashed, color=green] ({0}, {0}) -- ({1}, {0});" in line.to_tikz()


def test_path_builder_accepts_style_objects():
    fig = TikzFigure()
    a = fig.add_node(x=0, y=0, label="A")
    b = fig.add_node(x=1, y=0, label="B")
    c = fig.add_node(x=2, y=0, label="C")

    path = fig.draw(a.to(b).to(c, options=styles.bend_left(), looseness=1.2))

    assert "\\draw (A) to (B) to[bend left, looseness=1.2] (C);" in path.to_tikz()
