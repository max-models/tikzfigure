import pytest

from tikzfigure.core.figure import TikzFigure
from tikzfigure.core.matrix import MatrixLibrary
from tikzfigure.core.spy import SpyLibrary
from tikzfigure.core.tikz_library import (
    AnimationsLibrary,
    ArrowsMetaLibrary,
    TikzLibrary,
)


def test_subclassing_requires_name():
    with pytest.raises(TypeError):

        class _NoName(TikzLibrary):
            pass


def test_subclass_registers_itself():
    assert TikzLibrary.registry["matrix"] is MatrixLibrary
    assert TikzLibrary.registry["spy"] is SpyLibrary
    assert TikzLibrary.registry["arrows.meta"] is ArrowsMetaLibrary
    assert TikzLibrary.registry["animations"] is AnimationsLibrary


def test_str_and_equality():
    assert str(MatrixLibrary()) == "matrix"
    assert MatrixLibrary() == "matrix"
    assert MatrixLibrary() == MatrixLibrary()
    assert MatrixLibrary() != SpyLibrary()
    assert MatrixLibrary() != 5
    assert hash(MatrixLibrary()) == hash("matrix")


def test_ensure_registers_library_on_figure():
    fig = TikzFigure()
    MatrixLibrary.ensure(fig)
    SpyLibrary.ensure(fig)
    assert "matrix" in fig.tikz_libraries
    assert "spy" in fig.tikz_libraries
    # Idempotent.
    MatrixLibrary.ensure(fig)
    assert fig.tikz_libraries.count("matrix") == 1


def test_usetikzlibrary_accepts_library_classes_and_instances():
    fig = TikzFigure()
    fig.usetikzlibrary(MatrixLibrary)
    fig.usetikzlibrary(SpyLibrary())
    assert fig.tikz_libraries == ["matrix", "spy"]


def test_animations_library_ensure_registers_on_figure():
    fig = TikzFigure()
    AnimationsLibrary.ensure(fig)
    assert "animations" in fig.tikz_libraries
    assert AnimationsLibrary() == "animations"


def test_add_matrix_and_spy_auto_register_via_library_classes():
    fig = TikzFigure()
    fig.add_matrix([["A"]])
    assert "matrix" in fig.tikz_libraries

    fig2 = TikzFigure()
    fig2.add_node((0, 0), label="a")
    fig2.add_node((1, 1), label="b")
    fig2.add_spy(on="a")
    assert "spy" in fig2.tikz_libraries
