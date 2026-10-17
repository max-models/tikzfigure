import pytest

from tikzfigure.core.figure import TikzFigure
from tikzfigure.core.matrix import Matrix


def test_matrix_to_tikz_basic():
    matrix = Matrix(
        rows=[["A", "B"], ["C", "D"]],
        label="m",
        row_sep="5pt",
        column_sep="1cm",
    )
    tikz = matrix.to_tikz()
    assert "\\matrix[row sep=5pt, column sep=1cm] (m) {" in tikz
    assert "A & B \\\\" in tikz
    assert "C & D \\\\" in tikz


def test_matrix_cell_style_and_per_cell_options():
    matrix = Matrix(
        rows=[["A", {"content": "B", "fill": "red!20"}]],
        label="m",
        cell_style="draw, minimum size=8mm",
    )
    tikz = matrix.to_tikz()
    assert "nodes={draw, minimum size=8mm}" in tikz
    assert "|[fill=red!20]| B" in tikz


def test_matrix_at_coordinate():
    matrix = Matrix(rows=[["A"]], x=1, y=2, label="m")
    tikz = matrix.to_tikz()
    assert "at ({1}, {2})" in tikz


def test_matrix_cell_addressing():
    matrix = Matrix(rows=[["A", "B"], ["C", "D"]], label="m")
    assert matrix.cell(1, 1) == "m-1-1"
    assert matrix.cell(2, 2) == "m-2-2"
    assert matrix.num_rows == 2
    assert matrix.num_cols == 2


def test_matrix_cell_requires_label():
    matrix = Matrix(rows=[["A"]])
    with pytest.raises(ValueError):
        matrix.cell(1, 1)


def test_matrix_cell_out_of_range():
    matrix = Matrix(rows=[["A", "B"]], label="m")
    with pytest.raises(ValueError):
        matrix.cell(2, 1)


def test_matrix_to_dict_from_dict_round_trip():
    matrix = Matrix(
        rows=[["A", "B"], [{"content": "C", "fill": "red"}, "D"]],
        x=0,
        y=0,
        label="m",
        row_sep="5pt",
        column_sep="1cm",
        cell_style="draw, minimum size=8mm",
    )
    restored = Matrix.from_dict(matrix.to_dict())
    assert restored.to_dict() == matrix.to_dict()
    assert restored.to_tikz() == matrix.to_tikz()


def test_figure_add_matrix_registers_library_and_auto_labels():
    fig = TikzFigure()
    matrix = fig.add_matrix([["A", "B"], ["C", "D"]])
    assert "matrix" in fig._tikz_libraries
    assert matrix.label != ""

    fig.add_coordinate("c11", at=matrix.cell(1, 1))
    fig.add_coordinate("c22", at=matrix.cell(2, 2))
    fig.draw(["c11", "c22"])
    tikz = fig.generate_tikz()
    assert "\\matrix" in tikz
    assert f"({matrix.cell(1, 1)})" in tikz


def test_figure_matrix_serialization_round_trip():
    fig = TikzFigure()
    matrix = fig.add_matrix(
        [["A", "B"], ["C", "D"]],
        label="m",
        row_sep="5pt",
        cell_style="draw",
    )
    fig.add_coordinate("c11", at=matrix.cell(1, 1))
    fig.draw(["c11"])

    data = fig.to_dict()
    restored = TikzFigure.from_dict(data)
    assert restored.to_dict() == data
    assert restored.generate_tikz() == fig.generate_tikz()


def test_figure_add_matrix_second_auto_label_increments_counter():
    fig = TikzFigure()
    fig.add_matrix([["A"]])
    second = fig.add_matrix([["B"]])
    assert second.label == "node1"


def test_matrix_arrows_connect_cells_with_labels():
    matrix = Matrix(
        rows=[["V^0", "V^1"], ["H^1", "L^2"]],
        label="d",
        options="matrix of math nodes",
    )
    matrix.arrow((1, 1), (1, 2), label=r"$\nabla$").arrow(
        (2, 1),
        (1, 1),
        label=r"$\pi^0$",
        label_position="left",
        label_options="font=\\scriptsize",
        options="dashed",
        color="blue",
    )
    tikz = matrix.to_tikz()
    assert tikz.index("\\matrix") < tikz.index("\\draw")
    assert "\\draw[->] (d-1-1) to node[above] {$\\nabla$} (d-1-2);" in tikz
    assert (
        "\\draw[->, dashed, color=blue] (d-2-1) to "
        "node[left, font=\\scriptsize] {$\\pi^0$} (d-1-1);"
    ) in tikz
    assert len(matrix.arrows) == 2


def test_matrix_arrow_without_label_and_to_named_nodes():
    first = Matrix(rows=[["A", "B"]], label="m")
    second = Matrix(rows=[["C"]], label="n")
    first.arrow((1, 2), second.cell(1, 1), arrows="<-").arrow("m-1-1.east", (1, 2))
    tikz = first.to_tikz()
    assert "\\draw[<-] (m-1-2) to (n-1-1);" in tikz
    assert "\\draw[->] (m-1-1.east) to (m-1-2);" in tikz


def test_matrix_arrow_validates_cells():
    with pytest.raises(ValueError):
        Matrix(rows=[["A", "B"]], label="m").arrow((1, 1), (2, 1))
    with pytest.raises(ValueError):
        Matrix(rows=[["A", "B"]]).arrow((1, 1), (1, 2))


def test_matrix_arrows_round_trip():
    matrix = Matrix(rows=[["A", "B"], ["C", "D"]], label="m")
    matrix.arrow((1, 1), (1, 2), label="f", label_options=["sloped"], bend_left=20)
    matrix.arrow((2, 1), "m-1-1", options="dashed")
    restored = Matrix.from_dict(matrix.to_dict())
    assert restored.to_dict() == matrix.to_dict()
    assert restored.to_tikz() == matrix.to_tikz()
    assert "bend left=20" in restored.to_tikz()


def test_figure_matrix_arrows_render_in_the_document():
    fig = TikzFigure()
    matrix = fig.add_matrix(
        [["A", "B"]], label="m", options="matrix of math nodes", column_sep="1cm"
    )
    matrix.arrow((1, 1), (1, 2), label="$f$")
    assert "\\draw[->] (m-1-1) to node[above] {$f$} (m-1-2);" in fig.generate_tikz()
