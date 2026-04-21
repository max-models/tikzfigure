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


def test_loop_context_target_is_usable_as_variable_and_builder():
    fig = TikzFigure()

    with fig.loop("i", range(3)) as i:
        i.node((2 * i, 0), content=i)

    tikz = fig.generate_tikz()

    assert str(i) == "\\i"
    assert i.var == i
    assert "\\foreach \\i in {0,1,...,2}{" in tikz
    assert "\\node () at ({2 * \\i}, {0}) {\\i};" in tikz


def test_figure_methods_attach_to_active_loop_context():
    fig = TikzFigure()

    with fig.loop("i", range(3)) as i:
        fig.node((2 * i, 0), content=i)

    tikz = fig.generate_tikz()

    assert "\\foreach \\i in {0,1,...,2}{" in tikz
    assert "\\node (node0) at ({2 * \\i}, {0}) {\\i};" in tikz


def test_figure_plot_attaches_to_active_loop_context():
    from tikzfigure.math import Var

    fig = TikzFigure()
    theta = Var("theta")

    with fig.loop("i", range(3)) as i:
        fig.plot(i * theta, variable="theta", domain=(0, 1), samples=5)

    tikz = fig.generate_tikz()

    assert "\\foreach \\i in {0,1,...,2}{" in tikz
    assert "variable=\\theta, domain=0:1, samples=5" in tikz
    assert "plot ({\\theta}, {(\\i * \\theta)});" in tikz
