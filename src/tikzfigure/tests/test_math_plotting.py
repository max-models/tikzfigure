from tikzfigure import TikzFigure, colors
from tikzfigure.core.plot import TikzPlot
from tikzfigure.math import Var, cos, exp, func, ln, sin


def test_tikz_plot_renders_regular_function():
    plot = TikzPlot(
        x=sin(Var("x")),
        variable="x",
        domain=(-180, 180),
        samples=80,
        smooth=True,
        options=[colors.red],
    )

    assert plot.to_tikz() == (
        "\\draw[red, smooth, variable=\\x, domain=-180:180, samples=80] "
        "plot ({\\x}, {sin(\\x)});\n"
    )


def test_figure_round_trips_declared_functions_and_expression_plots():
    fig = TikzFigure()
    fig.variable("scale", 1.25)
    arcth = fig.declare_function(
        "arcth",
        "x",
        0.5 * ln((1 + Var("x")) / (1 - Var("x"))),
    )
    th = fig.declare_function(
        "th",
        "x",
        (1 - exp(-2 * Var("x"))) / (1 + exp(-2 * Var("x"))),
    )

    theta = Var("theta")

    with fig.loop("r", [0, 1, 2]) as r:
        fig.plot(
            Var("scale") * arcth(th(r) * cos(theta)),
            Var("scale") * arcth(th(r) * sin(theta)),
            variable="theta",
            domain=(0, 360),
            samples=100,
            smooth=True,
            options=[colors.Azure4],
        )

    data = fig.to_dict()
    restored = TikzFigure.from_dict(data)
    tikz = restored.generate_tikz()

    assert restored.generate_tikz() == fig.generate_tikz()
    assert "\\pgfkeys{/pgf/declare function={arcth(\\x) =" in tikz
    assert "\\pgfkeys{/pgf/declare function={th(\\x) =" in tikz
    assert "\\foreach \\r in {0,1,2}{" in tikz
    assert (
        "\\draw[Azure4, smooth, variable=\\theta, domain=0:360, samples=100] plot "
        "({(\\scale * arcth((th(\\r) * cos(\\theta))))}, "
        "{(\\scale * arcth((th(\\r) * sin(\\theta))))});"
    ) in tikz


def test_math_func_helper_builds_custom_calls():
    assert str(func("arcth", Var("x"))) == "arcth(\\x)"
    assert str(exp(Var("y"))) == "exp(\\y)"


def test_declared_function_is_callable_and_func_accepts_it():
    fig = TikzFigure()
    th = fig.declare_function(
        "th",
        "x",
        (1 - exp(-2 * Var("x"))) / (1 + exp(-2 * Var("x"))),
    )

    assert str(th(Var("x"))) == "th(\\x)"
    assert str(func(th, Var("x"))) == "th(\\x)"


def test_declared_function_validates_argument_count():
    fig = TikzFigure()
    th = fig.declare_function("th", "x", Var("x"))

    try:
        th()
    except ValueError as exc:
        assert "expects 1 argument" in str(exc)
    else:
        raise AssertionError(
            "DeclaredFunction should reject the wrong number of arguments."
        )
