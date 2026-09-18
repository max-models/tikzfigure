import pytest

from tikzfigure import TikzFigure
from tikzfigure.codegen import (
    CodegenError,
    figure_to_python,
    literal,
    main,
    run_generated_code,
    tikz_to_python,
)
from tikzfigure.parser.catalogue import load_catalogue
from tikzfigure.tests.test_tikz_catalogue import CATALOGUE


def roundtrip(fig: TikzFigure) -> TikzFigure:
    """Generate Python for *fig*, run it and return the rebuilt figure."""
    return run_generated_code(figure_to_python(fig))


def test_generated_code_is_readable():
    fig = TikzFigure(figure_setup="scale=2")
    fig.add_variable("R", 1.5)
    fig.colorlet("soft", "blue!20")
    a = fig.add_node(0, 0, label="a", content="A", fill="soft")
    fig.add_node(2, 0, label="b", content="B")
    fig.draw([a, "b"], options=["->"], color="gray")

    assert fig.to_python().splitlines() == [
        "from tikzfigure import TikzFigure",
        "",
        "fig = TikzFigure(figure_setup='scale=2')",
        "fig.add_variable('R', 1.5)",
        "fig.colorlet('soft', 'blue!20')",
        "fig.add_node(0, 0, label='a', content='A', fill='soft')",
        "fig.add_node(2, 0, label='b', content='B')",
        "fig.draw(['a', 'b'], options=['->'], color='gray')",
    ]


def test_name_and_header_options():
    fig = TikzFigure()
    fig.add_node(0, 0, label="a")
    # to_python() verifies the code (with its imports) before returning it.
    code = fig.to_python(name="figure", header=False)
    assert code.startswith("figure = TikzFigure()")
    assert "import" not in code

    with_header = fig.to_python(name="figure")
    assert with_header.endswith(code)
    assert (
        run_generated_code(with_header, name="figure").generate_tikz()
        == fig.generate_tikz()
    )


@pytest.mark.parametrize(
    "value",
    ["plain", r"\draw (0,0);", 'quote"d', 3, 1.5, None, True, ["a", 1], ("x", 2)],
)
def test_literals_round_trip(value):
    assert eval(literal(value)) == value


def test_literal_rejects_unknown_objects():
    with pytest.raises(CodegenError, match="cannot render"):
        literal(object())


# ---------------------------------------------------------------------- #
# Figures built through the Python API


def test_nodes_paths_shapes_and_coordinates():
    fig = TikzFigure()
    fig.add_node(0, 0, label="a", content="A", shape="circle", minimum_width="2cm")
    fig.add_node(content="floating", right="of a")
    fig.add_coordinate("mid", 1, 1)
    fig.add_coordinate("calc", at="$(a)!0.5!(mid)$")
    fig.draw(["a", "mid", (2, 2)], options=["thick"], cycle=True, comment="path")
    fig.filldraw(["a.north", "mid"], fill="red")
    fig.circle((0, 0), radius="1cm", color="blue")
    fig.rectangle((0, 0), (1, 1), fill="gray!20")
    assert roundtrip(fig).generate_tikz() == fig.generate_tikz()


def test_scopes_loops_layers_and_raw():
    fig = TikzFigure()
    fig.add_node(0, 0, label="a", layer=1)
    fig.add_raw(r"\draw[red] (0,0) -- (1,1);")
    with fig.add_scope(options=["red"], xshift="1cm") as scope:
        scope.add_node(1, 1, label="in_scope")
        with scope.add_loop("i", range(1, 4)) as loop:
            loop.add_node(r"\i", 0)
            loop.draw([(0, 0), (r"\i", 1)])
    fig.draw(["a", "in_scope"], layer=1)
    assert roundtrip(fig).generate_tikz() == fig.generate_tikz()


def test_loop_over_range_stays_a_range():
    fig = TikzFigure()
    with fig.add_loop("i", range(0, 10, 2)) as loop:
        loop.add_node(r"\i", 0)
    assert "range(0, 10, 2)" in fig.to_python()
    assert roundtrip(fig).generate_tikz() == fig.generate_tikz()


def test_options_that_methods_rewrite_fall_back_to_constructors():
    # draw() re-emits ``arrows`` as a flag option, in front of ``color``, so
    # a plain draw() call cannot reproduce this option order.
    fig = TikzFigure.from_tikz_code(
        "\\begin{tikzpicture}\n"
        "\\node (a) at (0, 0) {};\n"
        "\\node (b) at (1, 0) {};\n"
        "\\draw[color=gray, arrows=->] (a) to (b);\n"
        "\\end{tikzpicture}"
    )
    code = fig.to_python()
    assert "TikzPath(" in code
    assert run_generated_code(code).generate_tikz() == fig.generate_tikz()


def test_styles_libraries_packages_and_functions():
    fig = TikzFigure(extra_packages=["amsmath"], document_setup=r"\newcommand{\x}{1}")
    fig.usetikzlibrary("calc", "positioning")
    fig.add_style("box", options=["draw"], fill="red!20")
    fig.declare_function("sq", ["x"], "x*x")
    fig.add_node(0, 0, label="a", options=["box"])
    rebuilt = roundtrip(fig)
    assert rebuilt.generate_standalone() == fig.generate_standalone()


def test_verification_failure_raises(monkeypatch):
    fig = TikzFigure()
    fig.add_node(0, 0, label="a", content="A")
    monkeypatch.setattr(
        "tikzfigure.codegen._FigureCodegen.build", lambda self: "fig = TikzFigure()"
    )
    with pytest.raises(CodegenError, match="does not reproduce"):
        fig.to_python()
    assert (
        fig.to_python(verify=False)
        == "from tikzfigure import TikzFigure\n\nfig = TikzFigure()\n"
    )


def test_axes_are_not_supported_yet():
    fig = TikzFigure()
    fig.axis2d(xlabel="x")
    with pytest.raises(CodegenError, match="axes or subfigures"):
        fig.to_python()


# ---------------------------------------------------------------------- #
# TikZ source -> Python


def test_tikz_to_python_pipeline():
    source = """\\begin{tikzpicture}
    \\node[draw] (a) at (0, 0) {A};
    \\draw[->] (a) -- (2, 1);
\\end{tikzpicture}"""
    code = tikz_to_python(source)
    assert "fig.add_node(0, 0, label='a', content='A', options=['draw'])" in code
    rebuilt = run_generated_code(code)
    assert rebuilt.generate_tikz() == TikzFigure.from_tikz_code(source).generate_tikz()


def test_cli_writes_python_file(tmp_path, capsys):
    source = tmp_path / "figure.tikz"
    source.write_text(
        "\\begin{tikzpicture}\n\\draw (0,0) -- (1,1);\n\\end{tikzpicture}"
    )
    assert main([str(source)]) == 0
    assert "fig.draw(" in capsys.readouterr().out

    output = tmp_path / "figure.py"
    assert main([str(source), "-o", str(output), "--name", "picture"]) == 0
    assert output.read_text().startswith("from tikzfigure import TikzFigure")


@pytest.mark.skipif(not CATALOGUE.is_dir(), reason="tikz_catalogue/ not available")
@pytest.mark.parametrize(
    "entry",
    load_catalogue(CATALOGUE) if CATALOGUE.is_dir() else [],
    ids=lambda e: e.name,
)
def test_catalogue_entries_generate_equivalent_python(entry):
    figure = TikzFigure.from_tikz_code(entry.source)
    # figure_to_python() verifies the generated code reproduces the figure.
    code = figure_to_python(figure)
    assert run_generated_code(code).generate_tikz() == figure.generate_tikz()
