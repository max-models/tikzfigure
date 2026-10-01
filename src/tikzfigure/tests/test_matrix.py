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
