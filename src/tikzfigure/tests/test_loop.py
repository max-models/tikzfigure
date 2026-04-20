from tikzfigure import TikzFigure
from tikzfigure.core.loop import Loop


def test_loop_renders_python_range_with_tikz_ellipsis():
    loop = Loop("i", range(1, 11))

    assert "\\foreach \\i in {1,2,...,10}" in loop.to_tikz()


def test_loop_renders_stepped_range_with_tikz_ellipsis():
    loop = Loop("i", range(0, 11, 2))

    assert "\\foreach \\i in {0,2,...,10}" in loop.to_tikz()


def test_loop_round_trips_range_rendering_through_figure_dict():
    fig = TikzFigure()
    loop = fig.loop("i", range(1, 11))
    loop.node((0, 0), label="A", content=r"\i")

    restored = TikzFigure.from_dict(fig.to_dict())

    assert restored.generate_tikz() == fig.generate_tikz()
    assert "\\foreach \\i in {1,2,...,10}" in restored.generate_tikz()
